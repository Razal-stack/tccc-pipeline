"""Compare speech-to-text models on the hardest recordings, through OpenRouter.

    python -m tccc.stt_bakeoff --list                       # show transcription models your key can use
    python -m tccc.stt_bakeoff                              # run the default shortlist on the 10 hard files
    python -m tccc.stt_bakeoff --models a/b c/d --all       # chosen models, all 50 recordings

Needs OPENROUTER_API_KEY (environment, or a .env file in the repo or the task folder)
and the recordings folder (--recordings, default ./recordings or ../challenge/recordings).
Transcripts are saved to transcripts/<model>/<recording>.txt, so re-runs only fetch what's missing.
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .score import TRUTH
from .textnorm import recall

ROOT = Path(__file__).resolve().parent.parent
API = "https://openrouter.ai/api/v1"

# Hardest 10 by local-transcription number recall: radio links, heavy noise, two voices.
HARD = ["handover-oqx.wav", "handover-vdi.wav", "handover-kdb.wav", "handover-pbj.wav", "handover-ihg.wav",
        "handover-xqu.wav", "handover-xts.wav", "handover-dgf.wav", "handover-fox.wav", "handover-inj.wav"]

# One slot per vendor; each slot lists alternatives (all terms must appear in the model id), best first.
SHORTLIST = [
    [("gpt-transcribe",)],                # OpenAI, newest
    [("gpt-4o-transcribe",)],             # OpenAI, previous
    [("gpt-4o-mini-transcribe",)],        # OpenAI, cheap
    [("gemini", "transcribe")],           # Google
    [("mai-transcribe-2",)],              # Microsoft, newest
    [("mai-transcribe",)],                # Microsoft, previous
    [("nova-3",)],                        # Deepgram, telephony-strong
    [("voxtral-small",)],                 # Mistral, flagship
    [("voxtral-mini",)],                  # Mistral, cheap
    [("elevenlabs",)],                    # ElevenLabs Scribe, if listed
    [("whisper-large-v3",)],              # baseline
]

VOCAB = ("Expected vocabulary: NATO alphabet (Alpha, Bravo, Charlie ... Juliet, Sierra, Zulu), MIST, TCCC, battle roster, "
         "last four, CAT tourniquet, SOFTT-W, NPA, cric, needle decompression, chest seal, TXA, ketamine, fentanyl, "
         "lozenge, OTFC, morphine, ertapenem, moxifloxacin, Hartmann's, Plasma-Lyte, whole blood, IO, IV, IM, "
         "Cat A, T1, urgent, priority, routine, AVPU, sats, resps, obs, GSW, IED, RPG.")


def load_key():
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"]
    for env in (ROOT / ".env", ROOT.parent / ".env", ROOT.parent / "challenge" / ".env", Path.cwd() / ".env"):
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("OPENROUTER_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("OPENROUTER_API_KEY not found: set it or put it in .env")


def call(path, key, body=None, timeout=180):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def list_models(key):
    data = call("/models?output_modalities=transcription", key)["data"]
    return [(m["id"], m.get("pricing", {})) for m in data]


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


def transcribe(key, model, wav: Path):
    body = {"model": model, "input_audio": {"data": base64.b64encode(wav.read_bytes()).decode(), "format": "wav"},
            "language": "en", "temperature": 0}
    if "whisper" in model:
        body["provider"] = {"options": {"groq": {"prompt": VOCAB}}}
    for attempt in range(3):
        try:
            r = call("/audio/transcriptions", key, body)
            u = r.get("usage") or {}
            return r.get("text", ""), (u.get("cost") or 0.0, u.get("seconds") or 0.0)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:300]
            if e.code in (429, 502, 503) and attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            return f"__ERROR__ {e.code} {msg}", (0.0, 0.0)
        except Exception as e:  # noqa: BLE001
            if attempt < 2:
                time.sleep(3)
                continue
            return f"__ERROR__ {e}", (0.0, 0.0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--models", nargs="*")
    ap.add_argument("--all", action="store_true", help="all 50 recordings instead of the 10 hard ones")
    ap.add_argument("--recordings")
    a = ap.parse_args()

    key = load_key()
    available = list_models(key)
    if a.list:
        for mid, price in available:
            print(f"{mid:55s} {json.dumps(price)[:100]}")
        return
    ids = [m for m, _ in available]
    models = a.models or pick_shortlist(ids)
    missing = [m for m in models if m not in ids]
    if missing:
        print("not available on this key:", missing)
    models = [m for m in models if m in ids]
    if not models:
        sys.exit("no models to run; try --list")

    rec_dir = Path(a.recordings) if a.recordings else next(
        (p for p in (ROOT / "recordings", ROOT.parent / "recordings", ROOT.parent / "challenge" / "recordings") if p.exists()), None)
    if rec_dir is None:
        sys.exit("recordings folder not found; pass --recordings")
    files = sorted(TRUTH) if a.all else HARD
    print(f"models: {models}\nrecordings: {len(files)} from {rec_dir}\n")

    jobs = []
    for m in models:
        out = ROOT / "transcripts" / m.replace("/", "__")
        out.mkdir(parents=True, exist_ok=True)
        for f in files:
            dst = out / f.replace(".wav", ".txt")
            if not dst.exists() or dst.read_text().startswith("__ERROR__"):
                jobs.append((m, rec_dir / f, dst))

    ledger_path = ROOT / "transcripts" / "_costs.json"
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}

    def run(job):
        m, wav, dst = job
        text, (c, secs) = transcribe(key, m, wav)
        dst.write_text(text)
        print(f"  {m:40s} {wav.name:22s} {'ERROR' if text.startswith('__ERROR__') else 'ok'}", flush=True)
        return m, wav.name, c, secs

    with ThreadPoolExecutor(4) as pool:
        for m, name, c, secs in pool.map(run, jobs):
            ledger.setdefault(m, {})[name] = [c, secs]
    ledger_path.write_text(json.dumps(ledger, indent=1))
    cost = sum(c for per in ledger.values() for c, _ in per.values())

    rows = []
    for m in models + ["local__parakeet"]:
        d = ROOT / "transcripts" / m.replace("/", "__")
        if not d.exists():
            continue
        tot = dict(nums=0, nums_hit=0, terms=0, terms_hit=0, errors=0)
        for f in files:
            t = d / f.replace(".wav", ".txt")
            if not t.exists():
                continue
            text = t.read_text()
            if text.startswith("__ERROR__"):
                tot["errors"] += 1
                continue
            for k, v in recall(text, TRUTH[f]).items():
                tot[k] += v
        rows.append((m, tot))

    def per_hour(m):
        per = ledger.get(m, {})
        c, secs = sum(v[0] for v in per.values()), sum(v[1] for v in per.values())
        return f"${c / secs * 3600:.2f}" if secs and c else ("free (local)" if m.startswith("local") else "n/a")

    print(f"\nCritical-value recall on {len(files)} recordings (total spent so far ${cost:.4f})\n")
    print("| Model | Numbers found | Drug/kit terms found | Cost per audio hour | Errors |")
    print("|---|---|---|---|---|")
    for m, t in sorted(rows, key=lambda r: -r[1]["nums_hit"] / max(1, r[1]["nums"])):
        print(f"| {m} | {t['nums_hit']}/{t['nums']} ({t['nums_hit']/max(1,t['nums']):.0%}) | "
              f"{t['terms_hit']}/{t['terms']} ({t['terms_hit']/max(1,t['terms']):.0%}) | {per_hour(m)} | {t['errors']} |")


if __name__ == "__main__":
    main()
