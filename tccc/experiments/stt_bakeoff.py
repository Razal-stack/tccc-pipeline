"""Compare speech-to-text models on the hardest recordings, through OpenRouter.

    python -m tccc.experiments.stt_bakeoff --list                       # show transcription models your key can use
    python -m tccc.experiments.stt_bakeoff                              # run the default shortlist on 21 test files
    python -m tccc.experiments.stt_bakeoff --models a/b c/d --all       # chosen models, all 50 recordings

Needs OPENROUTER_API_KEY (environment, or a .env file in the repo or the task folder)
and the recordings folder (--recordings, default ./recordings or ../recordings).
Transcripts are saved to transcripts/<model>/<recording>.txt, so re-runs only fetch what's missing.
"""
import argparse
import json
import sys
import time
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ..config import ROOT
from ..openrouter import call, guard_budget, load_key
from ..score import TRUTH
from ..stt import transcribe
from ..textnorm import categorized_recall, recall

# Hardest 10 by local-transcription number recall: radio links, heavy noise, two voices.
HARD = ["handover-oqx.wav", "handover-vdi.wav", "handover-kdb.wav", "handover-pbj.wav", "handover-ihg.wav",
        "handover-xqu.wav", "handover-xts.wav", "handover-dgf.wav", "handover-fox.wav", "handover-inj.wav"]
# Correction and retraction traps (see CLAUDE.md) plus two clean files, as a control group.
OTHER = ["handover-aim.wav", "handover-isa.wav", "handover-sfw.wav", "handover-xbf.wav", "handover-ynt.wav",
         "handover-zjl.wav", "handover-jge.wav", "handover-cpx.wav", "handover-lml.wav", "handover-roo.wav",
         "handover-qof.wav"]

# One slot per vendor; each slot lists alternatives (all terms must appear in the model id), best first.
# Best current model per vendor that OpenRouter serves; everything else was dropped to save money.
SHORTLIST = [
    [("scribe-v2-medical",)],             # ElevenLabs, medical vocabulary
    [("scribe-v2",)],                     # ElevenLabs, general
    [("universal-3-6-pro",)],             # AssemblyAI
    [("transcribe-1-pro",)],              # Fish Audio
    [("gemini", "transcribe")],           # Google
    [("gpt-transcribe",)],                # OpenAI
]
MAX_PRICE_PER_SEC = 0.001  # skip anything listed above $3.60 per audio hour (MAI lists 0.1/s; unit unclear)

def list_models(key):
    """Speech-to-text models, plus chat models that accept audio (benchmarked as transcribers)."""
    stt = [(m["id"], m.get("pricing", {})) for m in call("/models?output_modalities=transcription", key)["data"]]
    chat = [(m["id"], m.get("pricing", {})) for m in call("/models", key)["data"]
            if "audio" in (m.get("architecture", {}).get("input_modalities") or [])]
    CHAT.update(i for i, _ in chat)
    return stt + chat


CHAT = set()  # filled by list_models: models reached through the chat endpoint


def pick_shortlist(ids):
    """One model per slot: the first alternative that matches, shortest id wins (no '-turbo'/'-mini' variants)."""
    chosen = []
    for slot in SHORTLIST:
        for terms in slot:
            hits = sorted((i for i in ids if all(t in i.lower() for t in terms) and i not in chosen), key=len)
            if hits:
                chosen.append(hits[0])
                break
    return chosen


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--models", nargs="*")
    ap.add_argument("--all", action="store_true", help="all 50 recordings instead of the 10 hard ones")
    ap.add_argument("--recordings")
    ap.add_argument("--keyterms", action="store_true", help="bias recognition toward domain terms")
    ap.add_argument("--tag", default="", help="label for a preprocessed variant, e.g. deepfilternet")
    a = ap.parse_args()

    key = load_key()
    available = list_models(key)
    if a.list:
        for mid, price in available:
            print(f"{mid:55s} {json.dumps(price)[:100]}")
        return
    ids = [m for m, _ in available]
    models = a.models or pick_shortlist(ids)
    prices = dict(available)
    pricey = [m for m in models if float(prices.get(m, {}).get("prompt") or 0) > MAX_PRICE_PER_SEC and not a.models]
    if pricey:
        print("skipped, listed price too high to benchmark blind:", pricey)
    models = [m for m in models if m not in pricey]
    missing = [m for m in models if m not in ids]
    if missing:
        print("not available on this key:", missing)
    models = [m for m in models if m in ids]
    if not models:
        sys.exit("no models to run; try --list")

    candidates = (ROOT / "recordings", ROOT.parent / "recordings")
    rec_dir = Path(a.recordings) if a.recordings else next((p for p in candidates if p.exists()), None)
    if rec_dir is None:
        sys.exit("recordings folder not found; pass --recordings")
    files = sorted(TRUTH) if a.all else HARD + OTHER
    print(f"models: {models}\nrecordings: {len(files)} from {rec_dir}\n")

    jobs = []
    variant = ("+keyterms" if a.keyterms else "") + (f"+{a.tag}" if a.tag else "")
    for m in models:
        out = ROOT / "transcripts" / (m.replace("/", "__") + variant)
        out.mkdir(parents=True, exist_ok=True)
        for f in files:
            dst = out / f.replace(".wav", ".txt")
            if not dst.exists() or dst.read_text().startswith("__ERROR__"):
                jobs.append((m, rec_dir / f, dst))

    ledger_path = ROOT / "transcripts" / "_costs.json"
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}

    def run(job):
        m, wav, dst = job
        t0 = time.time()
        text, (c, secs) = transcribe(key, m, wav, a.keyterms, chat=m in CHAT)
        with wave.open(str(wav)) as w:
            secs = secs or w.getnframes() / w.getframerate()  # chat models do not report audio length
        wall = time.time() - t0
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text)
        print(f"  {m:40s} {wav.name:22s} {'ERROR' if text.startswith('__ERROR__') else 'ok'}", flush=True)
        return m, wav.name, c, secs, wall

    if jobs:
        guard_budget(key)
    with ThreadPoolExecutor(6) as pool:
        for m, name, c, secs, wall in pool.map(run, jobs):
            ledger.setdefault(m + variant, {})[name] = [c, secs, wall]
            ledger_path.write_text(json.dumps(ledger, indent=1))
    cost = sum(v[0] for per in ledger.values() for v in per.values())

    # report every model with transcripts for all of these files, so numbers stay comparable
    groups = {"hard": [f for f in files if f in HARD], "other": [f for f in files if f not in HARD]}
    cats = ["vitals", "times", "doses", "ids", "names", "drugs_kit"]
    rows = []
    models = sorted(d.name.replace("__", "/", 1) for d in (ROOT / "transcripts").iterdir()
                    if d.is_dir() and all((d / f.replace(".wav", ".txt")).exists() for f in files))
    for m in models:
        d = ROOT / "transcripts" / m.replace("/", "__")
        if not d.exists():
            continue
        nums = {g: [0, 0] for g in groups}
        by_cat = {c: [0, 0] for c in cats}
        errors = 0
        for g, fs in groups.items():
            for f in fs:
                t = d / f.replace(".wav", ".txt")
                text = t.read_text() if t.exists() else "__ERROR__ missing"
                if text.startswith("__ERROR__"):
                    errors += 1
                    text = ""  # a failed transcript counts as nothing found
                r = recall(text, TRUTH[f])
                nums[g][0] += r["nums_hit"]
                nums[g][1] += r["nums"]
                for c, (hit, tot) in categorized_recall(text, TRUTH[f]).items():
                    if c in by_cat:
                        by_cat[c][0] += hit
                        by_cat[c][1] += tot
        rows.append((m, nums, by_cat, errors))

    def per_hour(m):
        per = ledger.get(m, {})
        c, secs = sum(v[0] for v in per.values()), sum(v[1] for v in per.values())
        if m.startswith("local"):
            return "free (local)"
        if secs and c:
            return f"${c / secs * 3600:.2f}"
        price = prices.get(m, {})
        if float(price.get("completion") or 0):
            return "per token (see ledger)"
        listed = float(price.get("prompt") or 0)
        return f"${listed * 3600:.2f} (list price)" if listed else "n/a"

    def median_wall(m):
        walls = sorted(v[2] for v in ledger.get(m, {}).values() if len(v) > 2)
        return f"{walls[len(walls) // 2]:.1f}" if walls else "-"

    def pct(hit, tot):
        return f"{hit}/{tot} ({hit / max(1, tot):.0%})"

    rows.sort(key=lambda r: -(r[1]["hard"][0] / max(1, r[1]["hard"][1])))
    csv_path = ROOT / "transcripts" / "_bakeoff.csv"
    with csv_path.open("w") as fh:
        fh.write("model,hard_files_numbers,other_files_numbers,all_numbers," + ",".join(cats)
                 + ",cost_per_audio_hour,median_s_per_file,errors\n")
        for m, nums, by_cat, errors in rows:
            allh, allt = nums["hard"][0] + nums["other"][0], nums["hard"][1] + nums["other"][1]
            vals = [nums["hard"][0] / max(1, nums["hard"][1]), nums["other"][0] / max(1, nums["other"][1]),
                    allh / max(1, allt)] + [h / max(1, t) for h, t in (by_cat[c] for c in cats)]
            fh.write(f"{m}," + ",".join(f"{v:.3f}" for v in vals) + f",{per_hour(m)},{median_wall(m)},{errors}\n")
    print(f"\nwrote {csv_path.relative_to(ROOT)}")
    print(f"\nTable 1. Numbers found in the transcript (total spent so far ${cost:.4f})")
    print(f"hard = {len(groups['hard'])} radio / heavy noise / two-speaker files; "
          f"other = {len(groups['other'])} correction-trap and clean files\n")
    print("| Model | Hard files | Other files | All | Cost per audio hour | Median s per file | Errors |")
    print("|---|---|---|---|---|---|---|")
    for m, nums, _, errors in rows:
        allh, allt = nums["hard"][0] + nums["other"][0], nums["hard"][1] + nums["other"][1]
        print(f"| {m} | {pct(*nums['hard'])} | {pct(*nums['other'])} | {pct(allh, allt)} | {per_hour(m)} | "
              f"{median_wall(m)} | {errors} |")
    print(f"\nTable 2. Ground-truth values found, by category, all {len(files)} files\n")
    print("| Model | " + " | ".join(cats) + " |")
    print("|---|" + "---|" * len(cats))
    for m, _, by_cat, _ in rows:
        print(f"| {m} | " + " | ".join(f"{h / max(1, t):.0%}" for h, t in (by_cat[c] for c in cats)) + " |")

if __name__ == "__main__":
    main()
