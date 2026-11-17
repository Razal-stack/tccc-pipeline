"""Transcript -> card fields, with one LLM call (OpenRouter chat completions, temperature 0, JSON out).

The model returns only the fields the handover actually filled, each with the exact transcript words it came
from. Code (tccc.validate) expands that to the full card and checks it. Raw replies are cached per model.

    python -m tccc.extract <model> [--split dev|heldout|all]     # writes out/raw/<model>/<name>.json
"""
import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .score import FIELDS, TRUTH
from .stt_bakeoff import API, load_key, call

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = ROOT / "transcripts" / "elevenlabs__scribe-v2-medical"
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
- name "Last, First" (surname only if that is all that was said). Ranks are not part of the name.
  last4 4 digits. Speech-to-text often merges "last four 8336" into "last 48336": a 5-digit number after "last"
  starting with 4 is "last four" + the 4 digits. battle_roster = initials + last four (e.g. JS4417), ONLY if spoken as a battle
  roster number ("battle roster Papa Kilo 6009" -> PK6009, NATO letters -> initials). Never build it from the name,
  never split it into name/last4.
- date DD-MMM-YY (03-NOV-26). All times 4 digits 24h (0715; "about fifteen hundred" -> 1500; "6:50" -> 0650).
- time = time of wounding/injury only. Other times (time found, etc.) go in notes.
- service as said (Army, RAF, Royal Marines, ...). unit as said, title case ("1 Rifles").
- signs_1_* = first set of obs, signs_2_* = the repeat set, and so on. pulse "<rate> <location>" ("128 radial"),
  or just the rate if no location said. avpu one of {AVPU}. pain one of {PAIN}. "sats" = spo2, "resps" = resp_rate.
- Doses with a space and unit: "800 mcg", "2 g", "50 mg", "1 unit", "1 L". Routes: {", ".join(ROUTES)}.
  Fentanyl lozenge -> route OTFC. Drug names lower case except TXA; TXA goes in other_med_*.
  Blood products (whole blood, plasma) go in blood_*, crystalloids (Hartmann's, Plasma-Lyte) in fluid_*.
- Tourniquets: tq_<limb>_type (CAT, SOFTT-W) and tq_<limb>_time; also tick tq_extremity for any limb tourniquet.
- Evac: Cat A / T1 / urgent -> evac_urgent; priority -> evac_priority; routine -> evac_routine.
- tq_type, dressing_type, airway_type, breathing_type, hypothermia_prevention_type: fill ONLY for an "other" item
  with no checkbox of its own (dressing_other + "cling film"). Brands and device names for ticked items (Celox,
  QuikClot, surgical cric, SAM junctional) are not types: tick the checkbox and put the detail in notes if useful.
- allergies as said ("NKA" for no known allergies).
- mechanism_*: tick each mechanism stated. Crush, struck by a vehicle, fall of debris -> mechanism_blunt.
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
lower case (left forearm, right thigh, chest, left buttock). Put unknowns here ("TQ time unknown").
Leave "Injuries:" out if no injury location was said.
"""


def ask(model, transcript, key):
    body = {"model": model, "temperature": 0, "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": PROMPT}, {"role": "user", "content": transcript}]}
    r = call("/chat/completions", key, body, timeout=300)
    text = r["choices"][0]["message"]["content"]
    text = text[text.find("{"): text.rfind("}") + 1]
    return json.loads(text), (r.get("usage") or {}).get("cost", 0.0)


def run(model, names):
    version = hashlib.sha1(PROMPT.encode()).hexdigest()[:8]  # new prompt -> new cache, old replies kept
    key, out = load_key(), ROOT / "out" / "raw" / model.replace("/", "__") / version
    out.mkdir(parents=True, exist_ok=True)

    def one(f):
        dst = out / f.replace(".wav", ".json")
        if dst.exists():
            return 0.0
        for _ in range(2):
            try:
                reply, cost = ask(model, (TRANSCRIPTS / f.replace(".wav", ".txt")).read_text(), key)
                dst.write_text(json.dumps(reply, indent=1))
                return cost
            except Exception as e:  # noqa: BLE001
                err = e
        print(f"  {f}: failed ({err})")
        return 0.0

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
