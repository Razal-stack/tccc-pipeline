"""One recording in, one card out: speech-to-text -> extraction -> checks -> PDF -> review sheet.

    python -m tccc.pipeline recording.wav [more.wav ...] [--out out/live]

The production path for new recordings (no ground truth needed). tccc.run is the evaluation path.
"""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

from .config import FALLBACK_MODEL, LLM_MODEL, OUT, SECOND, SECOND_MODEL, STT_MODEL  # noqa: F401  (re-exported)
from .extract import TWO, ask, combine
from .fill_pdf import fill, read_back
from .openrouter import guard_budget, load_key
from .score import norm
from .stt import transcribe
from .validate import check_card, missing_critical, to_card


def review_sheet(card: dict, flags: list, transcript: str) -> str:
    filled = {k: v for k, v in card.items() if v and k not in ("file", "injury_boxes")}
    bullets = lambda items, empty: "".join(f"- {x}\n" for x in items or [empty])
    return (f"# {card['file']}\n\n## Ask the sender\n" + bullets(missing_critical(card), "nothing missing")
            + "\n## Check these\n" + bullets(flags, "nothing flagged")
            + "\n## Card\n" + "".join(f"- {k}: {v}\n" for k, v in filled.items())
            + f"- injury_boxes: {', '.join(card['injury_boxes']) or 'none'}\n"
            + f"\n## Transcript\n{transcript.replace(TWO, '').strip()}\n")


def finish(file: str, reply: dict, transcript: str, out: Path, pdf: bool = True) -> tuple:
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


def process(wav: Path, out: Path, key: Optional[str] = None) -> dict:
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
    def safe(w):  # one bad recording must not stop the other casualties' cards
        try:
            return process(w, a.out, key)
        except Exception as e:  # noqa: BLE001
            return dict(file=w.name, error=str(e)[:200], cost=0.0)

    total, failed = 0.0, []
    with ThreadPoolExecutor(8) as pool:  # each casualty is independent: 50 cards take about as long as one
        for r in pool.map(safe, a.recordings):
            total += r["cost"]
            if "error" in r:
                failed.append(r["file"])
                print(f"{r['file']}: FAILED, no card made ({r['error']})")
                continue
            print(f"{r['file']}: {len(r['flags'])} to check, {len(r['ask'])} to ask, ${r['cost']:.4f} -> {r['pdf']}")
    if failed:
        print(f"\n{len(failed)} recording(s) failed and need a card written by hand: {', '.join(failed)}")
    print(f"\n{len(a.recordings)} card(s), ${total:.4f} spent. Outputs in {a.out}/: cards/ (PDF), predictions/ (card JSON),"
          f" review/ (what to ask and check), transcripts/ (both listens).")


if __name__ == "__main__":
    main()
