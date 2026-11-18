"""Would a third listen help? Simulated offline from cached bake-off transcripts (free, no API calls).

    python3 -m tccc.experiments.relisten

The proposed loop: when a value on the card was heard by only one of the two listeners, or a true value is missing,
listen again with a third model. This asks two questions of the final cards on all 50 recordings:
  1. Tie-break: for single-listener values, does a third transcript agreeing predict that the value is right?
     And how often would it "confirm" a wrong value (the risk of letting 2-of-3 fill the box)?
  2. Recovery: of the true values the card missed or got wrong, how many does a third transcript contain
     that neither of the first two did (the most a re-listen could add)?
"""
import json

from ..app import confidence, heard_by
from ..config import OUT, TRANSCRIPTS, LLM_MODEL, slug
from ..extract import FILES, transcript
from ..run import heard
from ..score import TRUTH, outcome

THIRD = ["fish-audio__transcribe-1-pro", "assemblyai__universal-3-6-pro", "openai__gpt-transcribe", "google__gemini-4-argon"]


def main():
    cards = {f: json.loads((OUT / slug(LLM_MODEL) / "all" / "predictions" / f.replace(".wav", ".json")).read_text())
             for f in FILES}
    texts = {f: transcript(f[:-4]) for f in FILES}
    single = [(f, k, v) for f in FILES for k, v in confidence(cards[f], texts[f])[1]]
    right = [s for s in single if outcome(s[2], TRUTH[s[0]].get(s[1])) == "correct"]
    print(f"Single-listener values on all 50: {len(single)}, {len(right)} correct ({len(right) / len(single):.1%})\n")

    errors = [(f, k, t) for f in FILES for k, t in TRUTH[f].items()
              if isinstance(t, str) and t and k not in ("file", "notes") and outcome(cards[f].get(k), t) in ("missed", "wrong")]
    lost = [(f, k, t) for f, k, t in errors if not heard(t, texts[f])]
    print(f"Text values missed or wrong: {len(errors)}; not in either transcript: {len(lost)}\n")

    print("third listener                  | confirms right | confirms wrong | right if confirmed | recovers lost")
    any_rec = set()
    for m in THIRD:
        third = {f: (TRANSCRIPTS / m / f.replace(".wav", ".txt")).read_text() for f in FILES}
        conf = [s for s in single if heard_by(s[2], third[s[0]])]
        ok = [s for s in conf if s in right]
        rec = [e for e in lost if heard(e[2], third[e[0]])]
        any_rec.update(rec)
        print(f"{m:31} | {len(ok):3} of {len(right):3}     | {len(conf) - len(ok):3} of {len(single) - len(right):3}     |"
              f" {len(ok) / len(conf) if conf else 0:17.0%} | {len(rec):3} of {len(lost)}")
    print(f"\nAny of the four third listeners recovers {len(any_rec)} of {len(lost)} lost values:")
    for f, k, t in sorted(any_rec):
        print(f"  {f[9:12]} {k}: {t}")


if __name__ == "__main__":
    main()
