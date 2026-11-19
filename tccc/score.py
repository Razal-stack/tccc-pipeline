"""Score predicted TCCC cards against the ground truth.

Headline metric: precision / recall / F1 over the fields the handover actually filled.
Every field prediction is one of:
  correct    - matches truth (both filled and equal)
  wrong      - filled, truth filled with something else
  invented   - filled, truth blank          (the dangerous one)
  missed     - blank, truth filled
  blank_ok   - both blank (not counted in precision/recall)

Notes are free text and scored separately; injury boxes get set-based F1.
Naive accuracy (all fields) is reported next to the empty-card baseline to show why it isn't the headline.

    python -m tccc.score predictions_dir/          # one <name>.json per recording
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

from .config import DATA

TRUTH = {r["file"]: r for r in json.loads((DATA / "output-true-values.json").read_text())}
SKIP = {"file", "injury_boxes", "notes"}
FIELDS = [k for k in next(iter(TRUTH.values())) if k not in SKIP]

CRITICAL_PREFIXES = ("analgesic_", "antibiotic_", "other_med_", "blood_", "fluid_", "tq_", "evac_", "signs_")
CRITICAL_EXACT = {"allergies"}

GROUPS = {
    "identity": ("battle_roster", "name", "last4", "gender_", "date", "time", "service", "unit", "allergies",
                 "first_responder_"),
    "evac": ("evac_",),
    "mechanism": ("mechanism_",),
    "tourniquets": ("tq_",),
    "vital_signs": ("signs_",),
    "treatments": ("dressing_", "airway_", "breathing_", "combat_pill_pack", "eye_shield", "splint",
                   "hypothermia_"),
    "medications": ("fluid_", "blood_", "analgesic_", "antibiotic_", "other_med_"),
}


def group_of(field):
    for g, prefixes in GROUPS.items():
        if field.startswith(prefixes):
            return g
    return "other"


def is_critical(field):
    return field in CRITICAL_EXACT or field.startswith(CRITICAL_PREFIXES)


def norm(v):
    """Normalise a value for comparison. Blank/False/None all mean 'not filled'."""
    if v is None or v is False or v == "":
        return None
    if v is True:
        return True
    s = str(v).strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"(\d)\s*(mcg|mg|g|ml|l|unit|units)\b", r"\1 \2", s)  # 800mcg -> 800 mcg
    s = re.sub(r"^(\d{1,2}):?(\d{2})$", lambda m: f"{int(m.group(1)):02d}{m.group(2)}", s)  # 9:05 -> 0905
    s = s.rstrip(".")
    return s or None


OUTCOMES = ("correct", "wrong", "invented", "missed", "blank_ok")


def outcome(pred, truth):
    p, t = norm(pred), norm(truth)
    if t is None and p is None:
        return "blank_ok"
    if t is None:
        return "invented"
    if p is None:
        return "missed"
    return "correct" if p == t else "wrong"


def prf(c):
    filled_pred = c["correct"] + c["wrong"] + c["invented"]
    filled_truth = c["correct"] + c["wrong"] + c["missed"]
    p = c["correct"] / filled_pred if filled_pred else 1.0
    r = c["correct"] / filled_truth if filled_truth else 1.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def bootstrap(per_card, other=None, n=2000, seed=0):
    """95% interval for F1 by resampling cards. With `other` (same cards, another model): interval on the gap.
    A model is only 'better' when the gap interval excludes zero."""
    import random
    rnd, files = random.Random(seed), sorted(per_card)
    def f1(cards, counts):
        return prf(sum((counts[f] for f in cards), Counter()))[2]
    draws = sorted(f1(c, per_card) - (f1(c, other) if other else 0)
                   for c in ([rnd.choice(files) for _ in files] for _ in range(n)))
    return draws[int(n * .025)], draws[int(n * .975)]


def score_card(pred: dict, truth: dict) -> tuple:
    per_field = {f: outcome(pred.get(f), truth.get(f)) for f in FIELDS}
    pb, tb = set(pred.get("injury_boxes") or []), set(truth.get("injury_boxes") or [])
    boxes = dict(tp=len(pb & tb), fp=len(pb - tb), fn=len(tb - pb))
    return per_field, boxes


def score(preds: dict, files: Optional[list] = None) -> dict:
    """preds: {file: card_dict}. Files with no prediction count as an empty card. files: subset to score."""
    truths = {f: TRUTH[f] for f in (files or TRUTH)}
    total, critical = Counter(), Counter()
    by_group, by_file = defaultdict(Counter), {}
    errors = []
    boxes = Counter()
    for file, truth in sorted(truths.items()):
        pred = preds.get(file, {})
        per_field, b = score_card(pred, truth)
        boxes.update(b)
        fc = Counter(per_field.values())
        by_file[file] = fc
        for f, o in per_field.items():
            total[o] += 1
            by_group[group_of(f)][o] += 1
            if is_critical(f):
                critical[o] += 1
            if o in ("wrong", "invented", "missed"):
                errors.append(dict(file=file, field=f, outcome=o, pred=pred.get(f), truth=truth.get(f)))
    n_cells = sum(total.values())
    naive = (total["correct"] + total["blank_ok"]) / n_cells
    empty_baseline = sum(1 for t in truths.values() for f in FIELDS if norm(t.get(f)) is None) / n_cells
    bp = boxes["tp"] / (boxes["tp"] + boxes["fp"]) if boxes["tp"] + boxes["fp"] else 1.0
    br = boxes["tp"] / (boxes["tp"] + boxes["fn"]) if boxes["tp"] + boxes["fn"] else 1.0
    return dict(
        cards=len(truths), predicted=len([f for f in truths if f in preds]),
        overall=dict(zip(("precision", "recall", "f1"), prf(total)), **{**dict.fromkeys(OUTCOMES, 0), **total}),
        critical=dict(zip(("precision", "recall", "f1"), prf(critical)), **{**dict.fromkeys(OUTCOMES, 0), **critical}),
        groups={g: dict(zip(("precision", "recall", "f1"), prf(c)), **c) for g, c in by_group.items()},
        injury_boxes=dict(precision=bp, recall=br, f1=2 * bp * br / (bp + br) if bp + br else 0.0, **boxes),
        naive_accuracy=naive, empty_card_baseline=empty_baseline, f1_interval=bootstrap(by_file), by_file=by_file,
        invented_per_card=total["invented"] / len(truths),
        errors=errors,
    )


def report(s) -> str:
    o, c = s["overall"], s["critical"]
    lines = [
        f"Cards scored: {s['cards']} ({s['predicted']} with predictions)",
        "",
        f"F1 on filled fields:      {o['f1']:.1%}  (precision {o['precision']:.1%}, recall {o['recall']:.1%}; "
        f"95% interval {s['f1_interval'][0]:.1%} to {s['f1_interval'][1]:.1%})",
        f"Safety-critical fields:   {c['f1']:.1%}  (precision {c['precision']:.1%}, recall {c['recall']:.1%})",
        f"Invented values:          {o.get('invented', 0)} total, {s['invented_per_card']:.2f} per card",
        f"Injury boxes F1:          {s['injury_boxes']['f1']:.1%}",
        f"Naive field accuracy:     {s['naive_accuracy']:.1%}  (an empty card scores {s['empty_card_baseline']:.1%})",
        "",
        "| Group | F1 | Precision | Recall | Correct | Wrong | Invented | Missed |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for g, v in sorted(s["groups"].items(), key=lambda kv: kv[1]["f1"]):
        lines.append(f"| {g} | {v['f1']:.1%} | {v['precision']:.1%} | {v['recall']:.1%} | {v.get('correct',0)} | "
                     f"{v.get('wrong',0)} | {v.get('invented',0)} | {v.get('missed',0)} |")
    return "\n".join(lines)


def load_dir(d: Path) -> dict:
    preds = {}
    for p in Path(d).glob("*.json"):
        card = json.loads(p.read_text())
        preds[card.get("file") or p.stem + ".wav"] = card
    return preds


if __name__ == "__main__":
    s = score(load_dir(sys.argv[1]))
    print(report(s))
    Path(sys.argv[1], "_score.json").write_text(json.dumps(s, indent=2, default=str))
