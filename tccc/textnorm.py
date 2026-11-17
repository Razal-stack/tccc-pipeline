"""Turn spoken numbers into digits so transcripts can be checked against ground-truth values."""
import re

UNITS = {"zero": 0, "oh": 0, "o": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
         "eight": 8, "nine": 9, "niner": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
         "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}


def spoken_to_digits(text: str) -> str:
    toks = re.findall(r"[a-z]+|\d+", text.lower().replace("-", " "))
    out, i = [], 0
    while i < len(toks):
        w = toks[i]
        if w in TENS:
            v = TENS[w]
            if i + 1 < len(toks) and toks[i + 1] in UNITS and UNITS[toks[i + 1]] < 10:
                v += UNITS[toks[i + 1]]
                i += 1
            out.append(str(v))
        elif w in UNITS and not (w == "o" and (i == 0 or not out or not out[-1].isdigit())):
            out.append(str(UNITS[w]))
        elif w == "hundred" and out and out[-1].isdigit():
            out.append(str(int(out.pop()) * 100))
        else:
            out.append(w)
        i += 1
    s = " ".join(out)
    return re.sub(r"\b(\d)00 (\d{1,2})\b", lambda m: str(int(m.group(1)) * 100 + int(m.group(2))), s)


def squash(text: str) -> str:
    """Digits and letters only, no spaces: '1 4 2 0' and '14 20' both contain '1420'."""
    return re.sub(r"[^a-z0-9]", "", spoken_to_digits(text))


MED_FIELDS = ("analgesic_1_name", "antibiotic_1_name", "other_med_1_name", "blood_1_name", "fluid_1_name",
              "tq_right_leg_type", "tq_left_leg_type", "tq_right_arm_type", "tq_left_arm_type")


def key_values(truth: dict):
    """The numbers and terms a transcript must contain for the card to be fillable."""
    nums = set()
    for k, v in truth.items():
        if isinstance(v, str) and k != "date":
            nums.update(re.findall(r"\d+", v))
    terms = {truth[k].lower().split()[0] for k in MED_FIELDS if truth.get(k)}
    return nums, terms


def recall(transcript: str, truth: dict):
    nums, terms = key_values(truth)
    sq, words = squash(transcript), spoken_to_digits(transcript)
    n_hit = sum(1 for n in nums if n in sq)
    t_hit = sum(1 for t in terms if t in words)
    return dict(nums=len(nums), nums_hit=n_hit, terms=len(terms), terms_hit=t_hit)


CATEGORIES = {
    "ids": ("battle_roster", "last4", "first_responder_last4"),
    "times": ("time", "_time"),
    "vitals": ("_pulse", "_bp_systolic", "_bp_diastolic", "_resp_rate", "_spo2"),
    "doses": ("_dose", "_volume"),
}


def _category(field):
    for cat, keys in CATEGORIES.items():
        for k in keys:
            if field == k or (k.startswith("_") and field.endswith(k)):
                return cat
    return None


def categorized_recall(transcript: str, truth: dict):
    """Per category: (found, total). Numbers are matched digit-for-digit; names and drugs as words."""
    sq, words = squash(transcript), spoken_to_digits(transcript)
    out = {c: [0, 0] for c in list(CATEGORIES) + ["drugs_kit", "names"]}
    for field, v in truth.items():
        if not isinstance(v, str) or not v or field == "date":
            continue
        cat = _category(field)
        if cat:
            for n in re.findall(r"\d+", v):
                out[cat][1] += 1
                out[cat][0] += n in sq
            if cat == "ids":
                letters = re.sub(r"[^a-z]", "", v.lower())  # battle roster letters, e.g. JS from JS4417
                if letters:
                    out[cat][1] += 1
                    out[cat][0] += letters in sq or all(re.search(rf"\b{l}\w*", words) for l in letters)
    for k in MED_FIELDS:
        if truth.get(k):
            out["drugs_kit"][1] += 1
            out["drugs_kit"][0] += truth[k].lower().split()[0] in words
    for k in ("name", "first_responder_name"):
        if truth.get(k):
            for part in re.findall(r"[a-z]+", truth[k].lower()):
                out["names"][1] += 1
                out["names"][0] += part in words
    return out
