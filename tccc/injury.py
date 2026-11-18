"""Map a card's `notes` ("Injuries: <location>: <description>; ...") to body-diagram box names.

Deterministic lookup, no model. Each location phrase -> side (left / right / both) + the first matching
region keyword -> box-name templates. {S} = side, {A} = Ant / Post (front unless "back of" / "posterior").
Conventions (which sub-boxes a "forearm" or "leg" fills) were read off the DEV split only.
Unknown location -> no boxes; output is always a subset of the 163 valid names.

    python -m tccc.injury        # P / R / F1 on dev, held-out, all 50 + held-out mismatches
"""
import json

from .config import DATA

VALID = set(json.loads((DATA / "field_map.json").read_text())["injury_boxes"])
MID = lambda part: [f"{{A}}_{{S}}_Middle_{m}_{part}" for m in ("Lateral", "Medial")]
LL = lambda *lv: [f"{{A}}_{{S}}_{v}_{m}_Lower_Leg" for v in lv for m in ("Lateral", "Medial")]
FACE = ["Chin", "Left_Cheek", "Mouth", "Nose", "Right_Cheek"]
# (keyword, templates, mirror). Order matters: specific phrases first. mirror=True copies DEV, where
# "right hip" -> Left_Hip and "right upper back" -> Left_Upper_Back (see report: likely a truth quirk).
REGIONS = [
    ("above knee", ["{A}_{S}_Distal_Lateral_Thigh", "{A}_{S}_Distal_Medial_Thigh"], False),
    ("below knee", LL("Proximal"), False),
    ("foot to mid-shin", ["{A}_{S}_Foot"] + LL("Distal", "Middle"), False),
    ("upper arm", ["{A}_{S}_Lateral_Bicep", "{A}_{S}_Medial_Bicep"], False),
    ("bicep", ["{A}_{S}_Lateral_Bicep", "{A}_{S}_Medial_Bicep"], False),
    ("forearm", MID("Forearm"), False),
    ("thigh", MID("Thigh"), False), ("femur", MID("Thigh"), False),
    ("calf", [t.replace("{A}", "Post") for t in LL("Middle")], False),
    ("shin", LL("Middle"), False), ("lower leg", LL("Middle"), False),
    ("knee", ["{A}_{S}_Knee"], False),
    ("leg", ["{A}_{S}_Knee"] + MID("Thigh") + LL("Middle"), False),
    ("arm", ["{A}_{S}_Lateral_Bicep", "{A}_{S}_Medial_Bicep", "{A}_{S}_Elbow"] + MID("Forearm"), False),
    *[(k, [f"{{A}}_{{S}}_{k.title()}"], False) for k in ("ankle", "foot", "wrist", "elbow", "shoulder", "thumb", "fingers")],
    ("heel", ["{S}_Heel"], False), ("hand", ["{S}_Palm"], False), ("palm", ["{S}_Palm"], False),
    ("side of face", ["{S}_Cheek"], False), ("cheek", ["{S}_Cheek"], False), ("face", FACE, False),
    ("eye", ["{S}_Eye"], False), ("ear", ["{S}_Ear"], False),
    ("neck", ["{H}Neck"], False), ("head", ["{H}Head"], False),
    ("upper chest", ["{S}_Upper_Chest"], False), ("lower chest", ["{S}_Lower_Chest"], False),
    ("chest", ["{S}_Upper_Chest", "{S}_Lower_Chest"], False),
    ("upper back", ["{S}_Upper_Back"], True), ("middle back", ["{S}_Middle_Back"], True),
    ("lower back", ["{S}_Lower_Back"], True), ("back", ["{S}_Upper_Back", "{S}_Middle_Back", "{S}_Lower_Back"], True),
    ("buttock", ["{S}_Buttock"], False), ("groin", ["{S}_Groin"], False), ("flank", ["{S}_Flank"], False),
    ("hip", ["{S}_Hip"], True), ("pelvis", ["Pelvis"], False), ("genital", ["Genitals"], False),
    ("abdomen", ["{Q}UQ", "{Q}LQ"], False), ("stomach", ["{Q}UQ", "{Q}LQ"], False),
]


def locations(notes: str) -> list[str]:
    """Location phrases from the 'Injuries:' segment (segments without 'loc: desc' are context)."""
    if not notes or "Injuries:" not in notes:
        return []
    segs = notes.split("Injuries:", 1)[1].split(";")
    return [" ".join(w for w in s.split(":", 1)[0].lower().split() if w != "the") for s in segs if ":" in s]


def boxes_for(loc: str) -> set[str]:
    post = any(w in loc for w in ("back of", "posterior"))
    loc = loc.replace("back of", "").replace("posterior", "")
    sides = ["Left"] if "left" in loc else ["Right"] if "right" in loc else ["Left", "Right"]
    for key, templates, mirror in REGIONS:
        if key in loc:
            out = set()
            for s in sides:
                s2 = {"Left": "Right", "Right": "Left"}[s] if mirror and len(sides) == 1 else s
                for t in templates:
                    out.add(t.format(A="Post" if post else "Ant", S=s2, H="Posterior" if post else "Anterior", Q=s2[0]))
            return out & VALID
    return set()


def boxes_from_notes(notes: str) -> list[str]:
    return sorted(set().union(*[boxes_for(l) for l in locations(notes)]))


if __name__ == "__main__":
    recs = sorted(json.loads((DATA / "output-true-values.json").read_text()), key=lambda r: r["file"])
    for name, split in (("dev", recs[0::2]), ("held-out", recs[1::2]), ("all", recs)):
        tp = fp = fn = 0
        for r in split:
            p, t = set(boxes_from_notes(r["notes"])), set(r["injury_boxes"])
            tp, fp, fn = tp + len(p & t), fp + len(p - t), fn + len(t - p)
        pr, rc = tp / max(tp + fp, 1), tp / max(tp + fn, 1)
        print(f"{name:9} P {pr:6.1%}  R {rc:6.1%}  F1 {2 * pr * rc / max(pr + rc, 1e-9):6.1%}  ({len(split)} cards)")
    print("\nheld-out mismatches:")
    for r in recs[1::2]:
        p, t = set(boxes_from_notes(r["notes"])), set(r["injury_boxes"])
        if p != t:
            print(f"  {r['file']}: {r['notes'][:90]}\n    extra {sorted(p - t)}\n    missing {sorted(t - p)}")
