"""Pipeline: transcript -> LLM extraction -> validation -> card JSON, PDF and medic review sheet -> score.

    python -m tccc.run <model> [--split dev|heldout|all] [--pdf]

Writes out/<model>/<split>/{predictions/*.json, review/*.md, report.md}, and cards/*.pdf with --pdf.
The report scores the run and attributes every error to a stage:
  transcription - the true value is not in the transcript at all (no extraction could get it)
  extraction    - the value was in the transcript but the model got it wrong or missed it
  validation    - the model had it right and a code check dropped it
  invented      - filled where the truth is blank
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

from . import extract
from .score import TRUTH, group_of, norm, report, score
from .textnorm import squash, spoken_to_digits
from .validate import clean, to_card

ROOT = Path(__file__).resolve().parent.parent


def heard(value, transcript):
    """Could the true value be read off this transcript? Numbers digit-for-digit, words as words."""
    v, sq, words = str(value).lower(), squash(transcript), spoken_to_digits(transcript)
    nums = re.findall(r"\d+", v)
    if nums:
        return all(n in sq for n in nums)
    toks = [t for t in re.findall(r"[a-z]+", v) if len(t) > 2]
    return not toks or any(t in words for t in toks)


def stage(err, transcript, raw):
    if err["outcome"] == "invented":
        return "invented"
    if not isinstance(err["truth"], str) or heard(err["truth"], transcript):
        said = (raw.get("fields") or {}).get(err["field"])
        said = said[0] if isinstance(said, list) else said
        if said not in (None, "") and norm(clean(err["field"], said) if isinstance(said, str) else said) == norm(err["truth"]):
            return "validation"
        return "extraction"
    return "transcription"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--split", default="dev", choices=extract.SPLITS)
    ap.add_argument("--pdf", action="store_true")
    a = ap.parse_args()

    names = extract.SPLITS[a.split]
    raw_dir = extract.run(a.model, names)
    out = ROOT / "out" / a.model.replace("/", "__") / a.split
    for sub in ("predictions", "review", "cards"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    preds, raws, texts = {}, {}, {}
    for f in names:
        stem = f.replace(".wav", "")
        texts[f] = (extract.TRANSCRIPTS / f"{stem}.txt").read_text()
        p = raw_dir / f"{stem}.json"
        raws[f] = json.loads(p.read_text()) if p.exists() else {}
        card, flags = to_card(f, raws[f], texts[f])
        preds[f] = card
        (out / "predictions" / f"{stem}.json").write_text(json.dumps(card, indent=1))
        filled = {k: v for k, v in card.items() if v and k not in ("file", "injury_boxes")}
        (out / "review" / f"{stem}.md").write_text(
            f"# {stem}\n\n## Check these\n" + "".join(f"- {x}\n" for x in flags or ["nothing flagged"])
            + "\n## Card\n" + "".join(f"- {k}: {v}\n" for k, v in filled.items())
            + f"\n## Transcript\n{texts[f]}\n")
        if a.pdf:
            from .fill_pdf import fill
            fill(card, out / "cards" / f"{stem}.pdf")

    s = score({f: preds[f] for f in names}, files=names)
    stages, by_group_stage = Counter(), Counter()
    for e in s["errors"]:
        st = stage(e, texts[e["file"]], raws[e["file"]])
        e["stage"] = st
        stages[st] += 1
        by_group_stage[(group_of(e["field"]), st)] += 1
    lines = [f"# {a.model} on {a.split} ({len(names)} cards)", "", report(s), "",
             "## Where the errors come from", ""]
    lines += [f"- {k}: {v}" for k, v in stages.most_common()]
    lines += ["", "## Errors by group and stage", ""]
    lines += [f"- {g} / {st}: {n}" for (g, st), n in sorted(by_group_stage.items(), key=lambda x: -x[1])]
    lines += ["", "## Every error", "", "| file | field | stage | predicted | truth |", "|---|---|---|---|---|"]
    lines += [f"| {e['file'][9:12]} | {e['field']} | {e['stage']} | {e['pred']} | {e['truth']} |" for e in s["errors"]]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    (out / "score.json").write_text(json.dumps(s, indent=1, default=str))
    print("\n".join(lines[:lines.index("## Errors by group and stage")]))


if __name__ == "__main__":
    main()
