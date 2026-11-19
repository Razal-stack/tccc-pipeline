"""Turn the answer key into plain-English MIST-style handover scripts (free, no API calls).

    python3 -m tccc.experiments.handover_scripts

Writes one speakable .txt per card under out/handover-scripts/, plus INDEX.md.
Speak the scripts aloud (phone, macOS `say`, ElevenLabs, etc.), then run
`make live FILE=...` to draft a card. Not part of the scoring pipeline.
"""
from pathlib import Path
from typing import Optional

from ..config import OUT
from ..score import TRUTH

DEST = OUT / "handover-scripts"

MECH = {
    "mechanism_artillery": "artillery",
    "mechanism_blunt": "blunt trauma",
    "mechanism_burn": "burn",
    "mechanism_fall": "fall",
    "mechanism_grenade": "grenade",
    "mechanism_gsw": "gunshot wound",
    "mechanism_ied": "IED",
    "mechanism_landmine": "landmine",
    "mechanism_mvc": "motor vehicle collision",
    "mechanism_rpg": "RPG",
    "mechanism_other": "other mechanism",
}

TQ_LIMB = {
    "tq_right_arm": "right arm",
    "tq_left_arm": "left arm",
    "tq_right_leg": "right leg",
    "tq_left_leg": "left leg",
}

DRESSING = {
    "dressing_hemostatic": "hemostatic dressing",
    "dressing_pressure": "pressure dressing",
    "dressing_other": "other dressing",
}

AIRWAY = {
    "airway_intact": "airway intact",
    "airway_npa": "NPA",
    "airway_cric": "cricothyroidotomy",
    "airway_et_tube": "ET tube",
    "airway_sga": "SGA",
}

BREATHING = {
    "breathing_o2": "oxygen",
    "breathing_needle_d": "needle decompression",
    "breathing_chest_tube": "chest tube",
    "breathing_chest_seal": "chest seal",
}

EVAC = (
    ("evac_urgent", "urgent, Cat A"),
    ("evac_priority", "priority, Cat B"),
    ("evac_routine", "routine, Cat C"),
)

MED_GROUPS = (
    ("fluid", "Fluid"),
    ("blood", "Blood"),
    ("analgesic", "Analgesic"),
    ("antibiotic", "Antibiotic"),
    ("other_med", "Other medication"),
)


_DIGITS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")


def _spoken_time(t: str) -> str:
    """'0715' -> 'zero seven fifteen' so TTS and readers say four digits clearly."""
    if not t or len(t) != 4 or not t.isdigit():
        return t
    h1, h2, m1, m2 = (int(c) for c in t)
    hour = f"{_DIGITS[h1]} {_DIGITS[h2]}"
    if m1 == 0 and m2 == 0:
        minute = "hundred"
    elif m1 == 0:
        minute = f"zero {_DIGITS[m2]}"
    elif m1 == 1:
        teens = ("ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
                 "sixteen", "seventeen", "eighteen", "nineteen")
        minute = teens[m2]
    else:
        tens = ("", "", "twenty", "thirty", "forty", "fifty")
        minute = tens[m1] if m2 == 0 else f"{tens[m1]}-{_DIGITS[m2]}"
    return f"{hour} {minute}"


def _avpu(v: str) -> str:
    return v.split(" - ", 1)[0] if " - " in v else v


def _pain(v: str) -> str:
    return v  # already "8 Horrible" style; speak as written


def _identity(card: dict) -> list[str]:
    parts = []
    if card.get("battle_roster"):
        parts.append(f"Battle roster {card['battle_roster']}")
    name = card.get("name") or ""
    last4 = card.get("last4") or ""
    if name and last4:
        parts.append(f"Casualty {name}, last four {last4}")
    elif name:
        parts.append(f"Casualty {name}")
    elif last4:
        parts.append(f"Last four {last4}")
    if card.get("gender_m"):
        parts.append("male")
    elif card.get("gender_f"):
        parts.append("female")
    if card.get("service"):
        parts.append(card["service"])
    if card.get("unit"):
        parts.append(card["unit"])
    if not parts:
        return []
    # First clause is the lead; rest join as extras
    lead, *rest = parts
    if rest:
        return [f"{lead}, {', '.join(rest)}."]
    return [f"{lead}."]


def _mechanism(card: dict) -> list[str]:
    mechs = [label for key, label in MECH.items() if card.get(key)]
    other = (card.get("mechanism_other_text") or "").strip()
    if other and "other mechanism" in mechs:
        mechs = [other if m == "other mechanism" else m for m in mechs]
    elif other:
        mechs.append(other)
    if not mechs:
        return []
    when = []
    if card.get("date"):
        when.append(card["date"])
    if card.get("time"):
        when.append(f"time of wounding {_spoken_time(card['time'])}")
    hit = " and ".join(mechs)
    if when:
        return [f"Mechanism: {hit}, {', '.join(when)}."]
    return [f"Mechanism: {hit}."]


def _injuries(card: dict) -> list[str]:
    notes = (card.get("notes") or "").strip()
    if not notes:
        return []
    # Prefer the Injuries: prefix when present; otherwise speak the whole notes line.
    if notes.lower().startswith("injuries:"):
        body = notes[len("Injuries:"):].strip()
        return [f"Injuries: {body}."] if body else []
    return [f"Notes: {notes}."]


def _vitals_line(card: dict, n: int) -> Optional[str]:
    p = f"signs_{n}_"
    if not any(card.get(p + k) for k in ("time", "pulse", "bp_systolic", "resp_rate", "spo2", "avpu", "pain")):
        return None
    bits = []
    if card.get(p + "time"):
        bits.append(f"at {_spoken_time(card[p + 'time'])}")
    if card.get(p + "pulse"):
        bits.append(f"pulse {card[p + 'pulse']}")
    sys, dia = card.get(p + "bp_systolic"), card.get(p + "bp_diastolic")
    if sys and dia:
        bits.append(f"blood pressure {sys} over {dia}")
    elif sys:
        bits.append(f"systolic {sys}")
    if card.get(p + "resp_rate"):
        bits.append(f"respirations {card[p + 'resp_rate']}")
    if card.get(p + "spo2"):
        bits.append(f"sats {card[p + 'spo2']} percent")
    if card.get(p + "avpu"):
        bits.append(f"AVPU {_avpu(card[p + 'avpu'])}")
    if card.get(p + "pain"):
        bits.append(f"pain {_pain(card[p + 'pain'])}")
    label = "Vitals" if n == 1 else "Repeat vitals"
    return f"{label}: {', '.join(bits)}."


def _tourniquets(card: dict) -> list[str]:
    lines = []
    for key, limb in TQ_LIMB.items():
        typ = card.get(f"{key}_type") or ""
        tim = card.get(f"{key}_time") or ""
        if not typ and not tim:
            continue
        bits = [f"Tourniquet on {limb}"]
        if typ:
            bits.append(typ)
        if tim:
            bits.append(f"applied at {_spoken_time(tim)}")
        lines.append(" ".join(bits) + ".")
    extras = []
    if card.get("tq_junctional"):
        extras.append("junctional")
    if card.get("tq_truncal"):
        extras.append("truncal")
    if card.get("tq_type"):
        extras.append(card["tq_type"])
    if extras:
        lines.append(f"Tourniquet notes: {', '.join(extras)}.")
    return lines


def _flag_treatments(card: dict) -> list[str]:
    items = []
    for key, label in DRESSING.items():
        if card.get(key):
            items.append(label)
    if card.get("dressing_type"):
        items.append(card["dressing_type"])
    for key, label in AIRWAY.items():
        if card.get(key):
            items.append(label)
    if card.get("airway_type"):
        items.append(card["airway_type"])
    for key, label in BREATHING.items():
        if card.get(key):
            items.append(label)
    if card.get("breathing_type"):
        items.append(card["breathing_type"])
    for flag, label in (
        ("combat_pill_pack", "combat pill pack"),
        ("eye_shield", "eye shield"),
        ("eye_shield_right", "eye shield right"),
        ("eye_shield_left", "eye shield left"),
        ("splint", "splint"),
        ("hypothermia_prevention", "hypothermia prevention"),
    ):
        if card.get(flag):
            items.append(label)
    if card.get("hypothermia_prevention_type"):
        items.append(card["hypothermia_prevention_type"])
    if not items:
        return []
    return [f"Treatment: {', '.join(items)}."]


def _med_line(prefix: str, card: dict, n: int, label: str) -> Optional[str]:
    name = card.get(f"{prefix}_{n}_name") or ""
    if not name:
        return None
    bits = [f"{label}: {name}"]
    dose = card.get(f"{prefix}_{n}_dose") or card.get(f"{prefix}_{n}_volume") or ""
    route = card.get(f"{prefix}_{n}_route") or ""
    tim = card.get(f"{prefix}_{n}_time") or ""
    if dose:
        bits.append(dose)
    if route:
        bits.append(f"via {route}")
    if tim:
        bits.append(f"at {_spoken_time(tim)}")
    return " ".join(bits) + "."


def _medications(card: dict) -> list[str]:
    lines = []
    for prefix, label in MED_GROUPS:
        for n in (1, 2, 3):
            if prefix in ("fluid", "blood", "antibiotic", "other_med") and n > 2:
                continue
            if prefix == "analgesic" and n > 3:
                continue
            line = _med_line(prefix, card, n, label)
            if line:
                lines.append(line)
    return lines


def _evac(card: dict) -> list[str]:
    for key, label in EVAC:
        if card.get(key):
            return [f"Evacuation: {label}."]
    return []


def _allergies(card: dict) -> list[str]:
    a = (card.get("allergies") or "").strip()
    return [f"Allergies: {a}."] if a else []


def _responder(card: dict) -> list[str]:
    name = card.get("first_responder_name") or ""
    last4 = card.get("first_responder_last4") or ""
    if name and last4:
        return [f"First responder {name}, last four {last4}."]
    if name:
        return [f"First responder {name}."]
    if last4:
        return [f"First responder last four {last4}."]
    return []


def script_for(card: dict) -> str:
    """One plain-English, speakable handover from a ground-truth card."""
    lines = []  # type: List[str]
    lines += _identity(card)
    lines += _mechanism(card)
    lines += _injuries(card)
    for n in (1, 2, 3, 4):
        v = _vitals_line(card, n)
        if v:
            lines.append(v)
    lines += _tourniquets(card)
    lines += _flag_treatments(card)
    lines += _medications(card)
    lines += _evac(card)
    lines += _allergies(card)
    # If notes did not start with Injuries:, _injuries already emitted them.
    # Extra context already in that line; skip duplicating.
    lines += _responder(card)
    return "\n".join(lines) + ("\n" if lines else "")


def stem_of(file: str) -> str:
    return Path(file).stem  # handover-isa.wav -> handover-isa


def write_all(dest: Path = DEST) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    index = ["# Handover scripts", "",
             "Plain-English MIST-style scripts generated from `data/output-true-values.json`.",
             "Speak one aloud (or TTS it), then `make live FILE=your.wav`.",
             "",
             "| Stem | File |",
             "|---|---|"]
    for file in sorted(TRUTH):
        stem = stem_of(file)
        text = script_for(TRUTH[file])
        (dest / f"{stem}.txt").write_text(text)
        index.append(f"| `{stem}` | `{stem}.txt` |")
    (dest / "INDEX.md").write_text("\n".join(index) + "\n")
    return dest


def main() -> None:
    dest = write_all()
    n = len(list(dest.glob("handover-*.txt")))
    print(f"Wrote {n} scripts + INDEX.md to {dest}")


if __name__ == "__main__":
    main()
