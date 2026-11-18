"""Transcript -> card fields, with one LLM call (OpenRouter chat completions, temperature 0, JSON out).

The model returns only the fields the handover actually filled, each with the exact transcript words it came
from. Code (tccc.validate) expands that to the full card and checks it. Raw replies are cached per model.

    python -m tccc.extract <model> [--split dev|heldout|all]     # writes out/raw/<model>/<name>.json
"""
import argparse
import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor

from .config import OUT, PRIMARY_TRANSCRIPTS as TRANSCRIPTS, SECOND, TRANSCRIPTS as ALL_TRANSCRIPTS, slug
from .score import FIELDS, TRUTH
from .openrouter import call, guard_budget, load_key

TWO = ("You have two transcripts of the same recording from different speech models. Use A by default. Use B where A "
       "is garbled, cut off or a number is unclear. If A and B give different values for the same field and the "
       "recording cannot tell you which is right, leave the field blank and flag it: 'transcripts disagree: A says X, "
       "B says Y'. Quote evidence from whichever transcript you used.")


def combine(a, b=""):
    """What the card model reads: the primary transcript, plus the second listen when there is one."""
    return f"{TWO}\n\nTRANSCRIPT A (medical speech model):\n{a}\n\nTRANSCRIPT B (second listen):\n{b}" if b else a


def transcript(stem):
    b = (ALL_TRANSCRIPTS / SECOND / f"{stem}.txt") if SECOND else None
    return combine((TRANSCRIPTS / f"{stem}.txt").read_text(), b.read_text() if b else "")


FILES = sorted(TRUTH)
SPLITS = {"dev": FILES[0::2], "heldout": FILES[1::2], "all": FILES}  # fixed: even positions dev, odd held-out

BOOLS = [f for f in FIELDS if isinstance(TRUTH[FILES[0]][f], bool)]
TEXTS = [f for f in FIELDS if f not in BOOLS]
AVPU = ["A - Alert", "V - Verbal", "P - Pain", "U - Unresp"]
PAIN = ["0 None", "1 Very Mild", "2 Discomfort", "3 Tolerable", "4 Distressing", "5 Very Distress", "6 Intense",
        "7 Very Intense", "8 Horrible", "9 Excruciating", "10 Unimaginable"]
ROUTES = ["IV", "IO", "IM", "IN", "PO", "PR", "SL", "SQ", "OTFC"]

PROMPT = f"""You fill a TCCC casualty card (DD Form 1380) from a speech-to-text transcript of a casualty handover.
The surgeon downstream trusts this card: a blank field is safe, an invented or wrong value can kill.

Return JSON: {{"fields": {{<field>: [<value>, "<exact transcript words it came from>"]}}, "notes": "<string>", "flags": ["<short issue for a medic to check>"]}}
Include ONLY fields the handover states. Omit everything else. Checkbox fields take true.

Checkbox fields: {", ".join(BOOLS)}
Text fields: {", ".join(TEXTS)}

Formats:
- name/last4 = the casualty. first_responder_name/first_responder_last4 = the person sending the handover
  ("sent by Corporal Jones, last four 3318"; "oh, it's Lance Corporal Byrne, Tom, last four 1662" at the end).
- name and first_responder_name "Last, First" (surname only if that is all that was said). Handovers say names
  military style, rank then SURNAME then first name: "Corporal Ahmed Zain" -> "Ahmed, Zain"; "Private Doyle,
  Sean" -> "Doyle, Sean". Keep the spoken order; do not swap it to "first last". Ranks are not part of the name.
  last4 4 digits. Speech-to-text often merges "last four 8336" into "last 48336": a 5-digit number after "last"
  starting with 4 is "last four" + the 4 digits. battle_roster = initials + last four (e.g. JS4417), ONLY if spoken as a battle
  roster number ("battle roster Papa Kilo 6009" -> PK6009, NATO letters -> initials). Never build it from the name,
  never split it into name/last4.
- date DD-MMM-YY (03-NOV-26). All times 4 digits 24h (0715; "about fifteen hundred" -> 1500; "6:50" -> 0650).
- time = time of wounding/injury only. Other times (time found, etc.) go in notes.
- service as said (Army, RAF, Royal Marines, ...). unit exactly as said, including sub-units and ordinals
  ("B Company, 1 Rifles", "4th Regiment Royal Artillery"); spoken numbers as digits ("One Rifles" -> "1 Rifles").
  Speech-to-text mangles UK unit names. Correct ONLY to a real unit that clearly matches the sounds, e.g.
  "2 Larc" -> 2 Lancs, "45 Commander" -> 45 Commando. Real units include: 1/2/3/4 Rifles, 1/2 Yorks, 1/2 Lancs,
  1 Royal Anglian, 1/2 Royal Welsh, 1/2/3 Para, 1/2 Scots, 1 Irish Guards, 1 Grenadier Guards, 1 Coldstream
  Guards, 1/2 Mercian, 1 Royal Irish, 1 PWRR, 40/42/45 Commando, 29 Commando Royal Artillery, 1 Regiment RMP,
  3 Medical Regiment, 16 Medical Regiment, Tactical Medical Wing, 2/15/34/51 Squadron RAF Regiment.
  Garbled beyond that -> leave blank and flag.
- signs_1_* = first set of obs, signs_2_* = the repeat set, and so on. pulse "<rate> <location>" ("128 radial"),
  or just the rate if no location said. avpu one of {AVPU}. pain one of {PAIN}.
  AVPU from phrasing: alert -> A; responds to voice/verbal -> V; responds to pain -> P; unresponsive -> U. "sats" = spo2, "resps" = resp_rate.
- Doses with a space and unit: "800 mcg", "2 g", "50 mg", "1 unit", "1 L". Routes: {", ".join(ROUTES)}.
  Fentanyl lozenge -> route OTFC. Drug names lower case except TXA; TXA goes in other_med_*.
  Blood products (whole blood, plasma) go in blood_*, crystalloids (Hartmann's, Plasma-Lyte) in fluid_*.
- Tourniquets: tq_<limb>_type (CAT, SOFTT-W) and tq_<limb>_time; also tick tq_extremity for any limb tourniquet.
  More than one tourniquet on the same limb: the card has one slot, so record the most recent one's type and time
  and mention the other in notes.
- Evac: Cat A / T1 / urgent -> evac_urgent; priority -> evac_priority; routine -> evac_routine.
- hypothermia_prevention_type: the kit as said ("blizzard blanket", "HPMK").
- tq_type, dressing_type, airway_type, breathing_type: fill ONLY for an "other" item
  with no checkbox of its own (dressing_other + "cling film"). Brands and device names for ticked items (Celox,
  QuikClot, surgical cric, SAM junctional) are not types: tick the checkbox and put the detail in notes if useful.
- splint = limb splint only. A pelvic binder is not a splint (put it in notes).
- allergies: the allergen ("penicillin"); "no known allergies" / "NKDA" / "none known" -> "NKA".
- mechanism_*: tick each mechanism stated as fact. Suspected or unconfirmed ("we think a mortar, not confirmed")
  is not ticked; put it in notes. Crush, struck by a vehicle, fall of debris -> mechanism_blunt.
  Blast or explosion with no device named -> mechanism_other + mechanism_other_text "blast".

Rules:
- Corrections win: "six fifteen, correction six fifty" -> 0650. "morphine, sorry, ketamine" -> ketamine.
- Retractions: anything withdrawn ("ignore that, that's the other casualty") is not on this card.
- A value said for the wrong vital and corrected ("pulse 28, sorry that's resps") goes to the corrected field.
- Radio read-backs: use the final agreed value.
- Never fill clinical defaults or infer what was not said. A drug withheld or refused is not a dose given.
  No dose said -> leave dose blank. Partly heard or garbled -> leave it blank, mention it in notes and flags.
- Ignore transcription noise tags like [gunfire]. Fix obvious mis-hearings only when the meaning is certain
  ("TXA4", "TXA fee", "TXA-FE" = TXA IV; "radio pulse" = radial pulse); otherwise leave blank and flag.

notes: "Injuries: <location>: <description>; <location>: <description>; <other context>", e.g.
"Injuries: left forearm: fragment wound; right thigh: GSW; time found 0215; jaw thrust". Locations plain and
lower case, one per injury actually described, and as precise as spoken: keep qualifiers IN the location
("right leg above knee: traumatic amputation", "left leg below knee: ...", "right foot to mid-shin: ...",
"left side of face: ..."), not in the description. Do not list a body part that was only mentioned in passing. Put unknowns here ("TQ time unknown").
Leave "Injuries:" out if no injury location was said.
"""


def ask(model, transcript, key):
    body = {"model": model, "temperature": 0, "max_tokens": 8000, "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": PROMPT}, {"role": "user", "content": transcript}]}
    r = call("/chat/completions", key, body, timeout=300)
    text = r["choices"][0]["message"]["content"]
    text = text[text.find("{"): text.rfind("}") + 1]
    return json.loads(text), (r.get("usage") or {}).get("cost", 0.0)


def run(model, names):
    version = hashlib.sha1((PROMPT + TRANSCRIPTS.name + SECOND).encode()).hexdigest()[:8]  # new prompt/transcripts -> new cache
    out = OUT / "raw" / slug(model) / version
    todo = [f for f in names if not (out / f.replace(".wav", ".json")).exists()]
    key = load_key() if todo else None  # fully cached: no key, no calls
    out.mkdir(parents=True, exist_ok=True)

    def one(f):
        dst = out / f.replace(".wav", ".json")
        if dst.exists():
            return 0.0
        for attempt in range(4):
            try:
                reply, cost = ask(model, transcript(f.replace(".wav", "")), key)
                dst.write_text(json.dumps(reply, indent=1))
                return cost
            except Exception as e:  # noqa: BLE001  (402 = credit held by in-flight requests: wait, then retry)
                err = e
                time.sleep(5 * (attempt + 1))
        print(f"  {f}: failed ({err})")
        return 0.0

    if todo:
        guard_budget(key)
    with ThreadPoolExecutor(8) as pool:
        cost = sum(pool.map(one, names))
    print(f"{model}: {len(names)} transcripts, ${cost:.4f} new spend")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("models", nargs="+")
    ap.add_argument("--split", default="dev", choices=SPLITS)
    a = ap.parse_args()
    for m in a.models:
        run(m, SPLITS[a.split])
