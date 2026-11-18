"""One recording in, one card out: speech-to-text -> extraction -> checks -> PDF -> review sheet.

    python -m tccc.pipeline recording.wav [more.wav ...] [--out out/live]

The production path for new recordings (no ground truth needed). tccc.run is the evaluation path.
"""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .config import FALLBACK_MODEL, LLM_MODEL, OUT, SECOND, SECOND_MODEL, STT_MODEL  # noqa: F401  (re-exported)
from .extract import TWO, ask, combine
from .fill_pdf import fill, read_back
from .openrouter import guard_budget, load_key
from .score import norm
from .stt import transcribe
from .validate import check_card, missing_critical, to_card


def review_sheet(card, flags, transcript):
    filled = {k: v for k, v in card.items() if v and k not in ("file", "injury_boxes")}
    return (f"# {card['file']}\n\n## Ask the sender\n" + "".join(f"- {x}\n" for x in missing_critical(card) or ["nothing missing"])
            + "\n## Check these\n" + "".join(f"- {x}\n" for x in flags or ["nothing flagged"])
            + "\n## Card\n" + "".join(f"- {k}: {v}\n" for k, v in filled.items())
            + f"- injury_boxes: {', '.join(card['injury_boxes']) or 'none'}\n\n## Transcript\n{transcript.replace(TWO, '').strip()}\n")


def finish(file, reply, transcript, out: Path, pdf=True):
    """Model reply -> checked card -> PDF (read back to verify) -> card JSON + review sheet. Shared with tccc.run."""
    stem = Path(file).stem
    for sub in ("cards", "predictions", "review"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    card, flags = to_card(file, reply, transcript)
    flags += [f"SCHEMA: {p}" for p in check_card(card)]
    if pdf:
        back = read_back(fill(card, out / "cards" / f"{stem}.pdf"))
        flags += [f"PDF: {k} reads back as '{back[k]}', expected '{card.get(k)}'"
                  for k in back if k != "file" and norm(back[k]) != norm(card.get(k))]
    (out / "predictions" / f"{stem}.json").write_text(json.dumps(card, indent=1))
    (out / "review" / f"{stem}.md").write_text(review_sheet(card, flags, transcript))
    return card, flags


def process(wav: Path, out: Path, key=None):
    """One new recording through every step; each step's output is saved next to the card."""
    key = key or load_key()
    (out / "transcripts").mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(2) as pool:  # both listens at once
        first = pool.submit(transcribe, key, STT_MODEL, wav, keyterms=True)
        second = pool.submit(transcribe, key, SECOND_MODEL, wav, chat=True) if SECOND else None
        (text, (cost_a, _)), (b, (cost_b, _)) = first.result(), second.result() if second else ("", (0.0, 0.0))
    b = "" if b.startswith("__ERROR__") else b
    if text.startswith("__ERROR__"):  # first listen failed: read the second alone rather than an error message
        if not b:
            raise RuntimeError(f"{wav.name}: both listens failed ({text[:120]})")
        text, b = b, ""
    text = combine(text, b)
    (out / "transcripts" / f"{wav.stem}.txt").write_text(text)
    try:
        reply, cost_c = ask(LLM_MODEL, text, key)
    except Exception:  # noqa: BLE001  one retry on the runner-up model, so no card is lost to an API error
        reply, cost_c = ask(FALLBACK_MODEL, text, key)
    card, flags = finish(wav.name, reply, text, out)
    return dict(file=wav.name, card=card, flags=flags, ask=missing_critical(card), pdf=str(out / "cards" / f"{wav.stem}.pdf"),
                cost=cost_a + cost_b + cost_c)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("recordings", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=OUT / "live")
    a = ap.parse_args()
    missing = [str(w) for w in a.recordings if not w.exists()]
    if missing:
        raise SystemExit(f"recording not found: {', '.join(missing)}")
    key = load_key()
    guard_budget(key)
    print(f"Listening with {STT_MODEL} and {SECOND_MODEL}, reading with {LLM_MODEL}...")
    total = 0.0
    with ThreadPoolExecutor(8) as pool:  # each casualty is independent: 50 cards take about as long as one
        for r in pool.map(lambda w: process(w, a.out, key), a.recordings):
            total += r["cost"]
            print(f"{r['file']}: {len(r['flags'])} to check, {len(r['ask'])} to ask, ${r['cost']:.4f} -> {r['pdf']}")
    print(f"\n{len(a.recordings)} card(s), ${total:.4f} spent. Outputs in {a.out}/: cards/ (PDF), predictions/ (card JSON),"
          f" review/ (what to ask and check), transcripts/ (both listens).")


if __name__ == "__main__":
    main()
