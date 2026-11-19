"""Model reply -> full card, checked in code. Anything that fails a check is dropped (blank) and flagged.

Checks: known field, format (times, doses, dropdown labels), plausible range, and evidence: the quoted words
must be in the transcript and the value's digits must appear in it. Derived: tq_extremity, injury boxes.
"""
import re

from .extract import AVPU, BOOLS, PAIN, ROUTES, TEXTS
from .injury import VALID as BOXES, boxes_from_notes
from .textnorm import spoken_to_digits, squash

RANGES = {"pulse": (20, 250), "bp_systolic": (40, 260), "bp_diastolic": (20, 160), "resp_rate": (2, 70),
          "spo2": (50, 100)}
MED_SLOTS = ("analgesic", "antibiotic", "other_med", "fluid", "blood")
LIMB_TQ = ("tq_right_arm_", "tq_left_arm_", "tq_right_leg_", "tq_left_leg_")


def _words(text):
    return re.findall(r"[a-z0-9]+", spoken_to_digits(text))


def label(field: str) -> str:
    """tq_right_leg_time -> 'Tourniquet right leg time': field names a medic can read."""
    words = field.replace("tq_", "tourniquet_").replace("signs_", "obs set ").replace("bp_", "BP ").replace("spo2", "SpO2")
    words = words.replace("_", " ").replace("other med", "drug").strip()
    return words[:1].upper() + words[1:]


def supported(value: str, evidence: str, transcript: str) -> bool:
    """Evidence words mostly present in the transcript, and every number in the value said somewhere."""
    have = set(_words(transcript))
    ev = _words(evidence or value)  # no quote given: the value's own words and digits must be in the transcript
    sq = squash(transcript) + " " + squash(transcript.replace("/", ""))  # "10/12" can be a time (1012) or BP (10 over 12)
    if not ev or (sum(w in have for w in ev) / len(ev) < 0.7 and squash(evidence) not in sq):
        return False
    return all(n in sq or n.lstrip("0") in sq for n in re.findall(r"\d+", value))


def clean(field, v):
    """Normalise one text value to the card format; None if it cannot be made valid."""
    v = re.sub(r"\s+", " ", str(v)).strip()
    if field.endswith("_time") or field == "time":
        d = re.sub(r"\D", "", v).zfill(4)
        return d if len(d) == 4 and int(d[:2]) < 24 and int(d[2:]) < 60 else None
    if field.endswith("_avpu"):
        return next((o for o in AVPU if o[0] == v[:1].upper()), None)
    if field.endswith("_pain"):
        n = re.match(r"\d+", v)
        return PAIN[int(n.group())] if n and int(n.group()) <= 10 else None
    if field.endswith("_route"):
        return v.upper() if v.upper() in ROUTES else None
    if field.endswith(("_dose", "_volume")):
        return re.sub(r"(\d)\s*([a-zA-Z])", r"\1 \2", v)
    m = re.match(r"signs_\d_(.+)", field)
    if m and m.group(1) in RANGES:
        n = re.match(r"\d+", v)
        lo, hi = RANGES[m.group(1)]
        if not n or not lo <= int(n.group()) <= hi:
            return None
        return v.lower() if m.group(1) == "pulse" else n.group()
    if field == "unit":  # "One Royal Welsh" -> "1 Royal Welsh"
        first, _, rest = v.partition(" ")
        n = spoken_to_digits(first)
        return f"{n} {rest}" if n.isdigit() and rest else v
    return v


def to_card(file: str, reply: dict, transcript: str) -> tuple:
    card = {"file": file, **{f: False for f in BOOLS}, **{f: "" for f in TEXTS}}
    flags = [str(x) for x in reply.get("flags") or []]
    for field, item in (reply.get("fields") or {}).items():
        value, evidence = (item + [""])[:2] if isinstance(item, list) else (item, "")
        if field in BOOLS:
            ticked = value is True or str(value).lower() == "true"
            if ticked and not supported("", evidence, transcript):  # a tick needs words from the recording too
                flags.append(f"{label(field)}: ticked without words from the recording to back it, so it was left unticked")
                continue
            card[field] = ticked
            continue
        if field not in TEXTS or value in (None, "", False):
            flags.append(f"dropped unknown field {field}") if field not in TEXTS else None
            continue
        v = clean(field, value)
        if v is None:
            flags.append(f"{label(field)}: heard '{value}', which is not a valid value, so it was left blank")
        elif not supported(v, evidence, transcript):
            flags.append(f"{label(field)}: heard '{value}' but could not match it to the recording, so it was left blank")
        else:
            card[field] = v
    for i in range(1, 5):  # systolic must exceed diastolic
        s, d = card[f"signs_{i}_bp_systolic"], card[f"signs_{i}_bp_diastolic"]
        if s and d and int(s) <= int(d):
            flags.append(f"signs_{i} BP {s}/{d} implausible, left blank")
            card[f"signs_{i}_bp_systolic"] = card[f"signs_{i}_bp_diastolic"] = ""
    if any(card[p + k] for p in LIMB_TQ for k in ("type", "time")):
        card["tq_extremity"] = True
    card["notes"] = str(reply.get("notes") or "").strip()
    card["injury_boxes"] = sorted(boxes_from_notes(card["notes"]))
    return card, flags


def check_card(card: dict) -> list:
    """Schema check before the PDF is written: every field, right type, valid dropdown and box names."""
    problems = [f"missing {f}" for f in BOOLS + TEXTS if f not in card]
    problems += [f"{f} not true/false" for f in BOOLS if not isinstance(card.get(f), bool)]
    problems += [f"{f} not text" for f in TEXTS if not isinstance(card.get(f), str)]
    for f in TEXTS:
        v = card.get(f)
        if v and (f.endswith(("_time", "_avpu", "_pain", "_route")) or f == "time") and clean(f, v) != v:
            problems.append(f"{f} '{v}' not in card format")
    problems += [f"unknown body box {b}" for b in card.get("injury_boxes", []) if b not in BOXES]
    return problems


def missing_critical(card: dict) -> list:
    """What a surgeon needs but the handover did not give: ask the sender, never guess."""
    ask = []
    if not any(card[k] for k in ("name", "last4", "battle_roster")):
        ask.append("casualty identity (name / last four / battle roster)")
    if not any(card[k] for k in ("evac_urgent", "evac_priority", "evac_routine")):
        ask.append("evac category")
    for limb in ("right_arm", "left_arm", "right_leg", "left_leg"):
        if card[f"tq_{limb}_type"] and not card[f"tq_{limb}_time"]:
            ask.append(f"tourniquet time, {limb.replace('_', ' ')}")
    if card["tq_extremity"] and not any(card[p + k] for p in LIMB_TQ for k in ("type", "time")):
        ask.append("tourniquet: limb, type and time")
    meds = [k for k in card if k.endswith("_name") and k[:-5].rstrip("_0123456789") in MED_SLOTS]
    for k in meds:
        if card[k]:
            base, item = k[:-5], card[k]
            for part in ("dose" if not base.startswith(("fluid", "blood")) else "volume", "route", "time"):
                if not card.get(f"{base}_{part}"):
                    ask.append(f"{item}: {part}")
    if any(card[f"signs_1_{v}"] for v in ("pulse", "resp_rate", "spo2")) and not card["signs_1_time"]:
        ask.append("time of first observations")
    return ask
