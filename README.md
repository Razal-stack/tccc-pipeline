# TCCC cards from recorded handovers

Fifty casualties came through, and each one needs a TCCC card before the vehicle arrives. This project listens to
the recorded handover for each casualty and fills in the card for you: a PDF ready to print, plus a one-page sheet
telling the medic exactly what to double-check and what to ask the sender for.

## How well it works

On the 25 recordings I never looked at while tuning (the honest test):

| What we measure | Score |
|---|---|
| **Accuracy on the fields the handover actually filled (F1)** | **92.4%** |
| Safety-critical fields (drugs, doses, tourniquets, vitals, evac) | 96.2% |
| Of the values it writes, how many are right (precision) | 95.8% |
| Values made up that were never said | 2 in 25 cards |
| Medications, specifically | 100% |

On all 50 recordings: 94.0% F1, 96.1% on safety-critical fields. All 50 filled PDF cards are in
`out/google__gemini-3.8-flash/all/cards/`.

### How the % is calculated

A blank card already "matches" most of the form, because most fields on any one card are empty. A card that
writes nothing would score 85% if you just counted matching boxes. So that number is useless, and I don't
lead with it.

Instead I only look at the fields that matter: the ones where either the true card or our card has something
written. Each one is either correct, wrong, made up (we wrote something nobody said), or missed (we left it blank
when something was said). Then:

- **Precision**: of everything we wrote, how much was right.
- **Recall**: of everything that should be on the card, how much we got.
- **F1**: one number that balances the two. It only goes up if we are both careful and thorough.

Values are compared after light tidying (so "800mcg" and "800 mcg" count as the same). Free-text notes are not
scored; the body-diagram ticks are scored separately (89% on all 50, 81% on the locked-away 25).

I split the 50 recordings in two before starting: 25 to tune on, 25 locked away. I report the locked-away score
first, because a system always looks better on the examples it was tuned on (it scored 95.3% on those).

## How it works

```
recording -> 1. transcribe -> 2. extract -> 3. check -> 4. body diagram -> 5. PDF + review sheet -> 6. score
```

1. **Transcribe.** ElevenLabs Scribe v2 Medical turns speech into text. I tested six current speech models on the
   hardest recordings (radio, heavy noise, two people talking) and this one caught the most numbers. I also give
   it a list of words to expect (TXA, IV, tourniquet, unit names), which lifted drug and kit words from 90% to 97%.
2. **Extract.** One call to a language model (Gemini 3.8 Flash) reads the transcript and pulls out only the fields
   that were said, each with the exact words it came from. I tested eight models (a ninth failed at the provider);
   this one was the most accurate for the price.
3. **Check.** Plain code, no AI: every value must appear in the transcript, be in the right format, and be
   medically plausible (oxygen saturation 50 to 100, systolic above diastolic). Anything that fails is left blank
   and flagged. A blank box is safer than a confident wrong one.
4. **Body diagram.** The card's body outline has 163 tick boxes. Spoken locations ("left forearm") are mapped to
   box names with a fixed lookup table, so the X lands exactly where the form expects it.
5. **PDF and review sheet.** The card is written into the real DD Form 1380, then read back to make sure every
   field landed. The review sheet lists two things: **Ask the sender** (what a surgeon needs but nobody said, like
   a tourniquet with no time) and **Check these** (anything garbled, corrected, or doubtful).
6. **Score.** Against the ground truth, and every mistake is tagged with the step that caused it.

It costs about 1 US cent and about 10 seconds per card. All 50 cards run in parallel in about a minute.

## What I decided, and why

- **Accuracy first, then cost, then speed.** I chose the most accurate speech model, then the cheapest language
  model that held accuracy.
- **No agent, no chain of AI models.** I measured it: two different strong models agree on 3,411 of 3,425
  fields, and even a perfect referee between them would add only 0.4 points. Their mistakes come from the audio,
  not from reasoning, so a second model can't catch them.
- **No audio clean-up.** I tested noise reduction and radio filters before transcription. Both made things worse
  (69 and 46 numbers caught, against 77 with the raw audio). Modern speech models are trained on noisy audio.
- **No vision model for the PDF.** The body diagram is just named tick boxes, so filling it is exact code.
- **Never guess.** If "TXA" is heard but the route is lost in the static, the route stays blank and gets flagged.

## Where it still goes wrong (honest limits)

- **Some audio is gone.** One radio recording (vdi) is mostly static; one (kdb) is 36 seconds long but only about
  5 seconds of speech survive the noise. No speech model I tested recovers them. Those values stay blank.
- **Names spelled the way they sound.** "Kaur" comes out as "Carr", "Aoife" as "Aoi". Identity is the weakest
  group (85%). In real use the casualty's ID tag or a roster lookup would fix this.
- **The ground truth has a few slips.** For example, one card (roo) leaves out a TXA dose and oxygen that are
  clearly spoken, and two body-diagram entries swap left and right. I did not bend the system to match them, so
  they count against us.
- **One small leak, flagged.** I wrote a list of real UK unit names into the instructions after seeing units in the
  answer key, so the unit field on the held-out set is slightly flattered.

## In the real world

The medic at the casualty collection point hits record during the handover (already happening in this scenario).
About 10 seconds later the card is ready. Instead of writing 138 boxes by hand, they read a short list: the things
to ask the sender over the radio ("say again tourniquet time") and the few flagged values to confirm. They sign
and the card goes with the casualty. Every value on the card can be traced back to the words that were spoken.

Next steps I would build: an offline mode (a local speech model already gets 74% with no network), reading back
missing critical items to the sender in real time, and linking cards to the casualty's ID tag.

## Try it

```bash
python3 -m pip install -r requirements.txt          # reads OPENROUTER_API_KEY from ../.env
python3 -m tccc.pipeline ../recordings/handover-isa.wav   # one new recording -> out/live/ (card, PDF, review)
python3 -m uvicorn tccc.app:app --port 8000          # web app: upload, review cards, see scores and run history
python3 -m tccc.run google/gemini-3.8-flash --split heldout --pdf   # re-run the honest evaluation (cached, free)
```

The web app shows the headline scores, every card with its flags, each card's review sheet beside its PDF (and
its field-by-field score when ground truth exists), and the history of every benchmark run. Upload a new
recording and its card appears in about 10 seconds.

A hard spending cap protects the key: before any paid call the code checks real usage on the key and stops at $7.
The whole project, including every experiment, used $3.90.

More detail: `docs/ARCHITECTURE.md` (every step, how it is scored, every experiment) and `AI_LOG.md` (how I worked
with AI coding tools).
