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

from . import extract
from .config import OUT, slug
from .score import group_of, norm, report, score
from .textnorm import squash, spoken_to_digits
from .pipeline import finish
from .validate import clean


def heard(value, transcript):
    """Could the true value be read off this transcript? Numbers digit-for-digit, words as words."""
    v, sq, words = str(value).lower(), squash(transcript), spoken_to_digits(transcript)
    nums = re.findall(r"\d+", v)
    if nums:
        return all(n in sq for n in nums)
    toks = re.findall(r"[a-z]+", v)
    return any(re.search(rf"\b{t}\b", words) for t in toks)  # whole words, so "iv" must really be said


def kind(err):
    """What kind of problem: the recurring patterns to fix or monitor."""
    p, t = str(err["pred"] or ""), str(err["truth"] or "")
    if err["outcome"] == "invented":
        return "made up"
    if err["outcome"] == "missed":
        return "left blank"
    if p.isdigit() and t.isdigit() and len(p) == len(t):
        return "digit off"
    if err["field"].endswith(("name", "unit")):
        return "name/unit spelling"
    return "wrong value"


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
    out = OUT / slug(a.model) / a.split
    preds, raws, texts = {}, {}, {}
    for f in names:
        stem = f.replace(".wav", "")
        texts[f] = extract.transcript(stem)  # evidence is checked against everything the model was given
        p = raw_dir / f"{stem}.json"
        raws[f] = json.loads(p.read_text()) if p.exists() else {}
        preds[f], _ = finish(f, raws[f], texts[f], out, pdf=a.pdf)  # same code path as live recordings

    s = score({f: preds[f] for f in names}, files=names)
    stages, by_group_stage = Counter(), Counter()
    for e in s["errors"]:
        st = stage(e, texts[e["file"]], raws[e["file"]])
        e["stage"], e["kind"] = st, kind(e)
        stages[st] += 1
        by_group_stage[(group_of(e["field"]), st)] += 1
    lines = [f"# {a.model} on {a.split} ({len(names)} cards)", "", report(s), "",
             "## Where the errors come from", ""]
    lines += [f"- {k}: {v}" for k, v in stages.most_common()]
    lines += ["", "## Kinds of problem", ""]
    lines += [f"- {k}: {n}" for k, n in Counter(e["kind"] for e in s["errors"]).most_common()]
    lines += ["", "## Errors by group and stage", ""]
    lines += [f"- {g} / {st}: {n}" for (g, st), n in sorted(by_group_stage.items(), key=lambda x: -x[1])]
    lines += ["", "## Every error", "", "| file | field | stage | kind | predicted | truth |", "|---|---|---|---|---|---|"]
    lines += [f"| {e['file'][9:12]} | {e['field']} | {e['stage']} | {e['kind']} | {e['pred']} | {e['truth']} |"
              for e in s["errors"]]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    (out / "score.json").write_text(json.dumps(s, indent=1, default=str))
    ledger = OUT / "runs.jsonl"
    transcripts = extract.TRANSCRIPTS.name + (f"+{extract.SECOND}" if extract.SECOND else "")
    entry = json.dumps(dict(model=a.model, split=a.split, prompt=raw_dir.name, transcripts=transcripts,
                                 f1=s["overall"]["f1"], precision=s["overall"]["precision"], recall=s["overall"]["recall"],
                                 critical_f1=s["critical"]["f1"], invented=s["overall"].get("invented", 0),
                                 boxes_f1=s["injury_boxes"]["f1"], stages=dict(stages), errors=s["errors"]), default=str)
    if entry not in (ledger.read_text().splitlines() if ledger.exists() else []):  # re-scoring the same run adds nothing
        with ledger.open("a") as fh:
            fh.write(entry + "\n")
    print("\n".join(lines[:lines.index("## Errors by group and stage")]))


if __name__ == "__main__":
    main()
