# TCCC cards from recorded handovers

Fifty casualties came through, and each one needs a TCCC card before the vehicle arrives. This project listens to
the recorded handover for each casualty and fills in the card: a PDF ready to print, plus a short sheet telling the
medic what to ask the person who handed over, and which values to check.

## How well it works

On the 25 recordings I locked away and never looked at while tuning (the honest test):

| What we measure | Score |
|---|---|
| **Accuracy on the fields the handover actually filled (F1)** | **93.8%** |
| Of the values it writes, how many are right (precision) | 97.6% |
| Safety-critical fields (drugs, doses, tourniquets, vitals, evac) | 96.8% |
| Tourniquets, and drugs and fluids | 100% each |
| Values made up that were never said | 2 in 25 cards |

On all 50 recordings: 94.7% F1, 97.5% precision, 96.4% on safety-critical fields. All 50 filled PDF cards are in
`out/google__gemini-3.8-flash/all/cards/`.

### How the % is calculated

A blank card already "matches" most of the form, because most fields on any one card are empty: a card that writes
nothing would score 85% if you just counted matching boxes. So I only score the fields that matter, the ones where
either the true card or ours has something written. Each is correct, wrong, made up (written but never said) or
missed (left blank when something was said). Then:

- **Precision**: of everything we wrote, how much was right.
- **Recall**: of everything that should be on the card, how much we got.
- **F1**: one number that balances the two. It only goes up if we are both careful and thorough.

Values are compared after light tidying ("800mcg" equals "800 mcg"). Free-text notes are not scored; the
body-diagram ticks are scored separately (89% on all 50, 81% on the locked-away 25).

Before starting, I split the recordings: 25 to tune on, 25 locked away and run once at the end. Every result also
has a 95% interval from resampling the cards, and a change only counts as better when the interval on the gap
excludes zero.

## How it works

![How a recorded handover becomes a TCCC card](docs/how-it-works.svg)

1. **Listen twice.** ElevenLabs Scribe v2 Medical writes the main transcript, told which words to expect (TXA, IV,
   tourniquet, unit names). A second, different model listens to the same raw audio at the same time.
2. **Read.** Gemini 3.8 Flash reads both transcripts and returns only the fields that were said, each with the words
   it came from. Where the two transcripts disagree on a value, it leaves the box blank and flags it
   ("transcripts disagree: A says RE88206, B says RE8826").
3. **Check, in plain code.** Every value must appear in what was heard, be in the right format and be medically
   plausible (oxygen saturation 50 to 100, systolic above diastolic). Anything that fails is left blank and flagged.
   Rules that need no judgement are code, not AI: a limb tourniquet ticks "extremity", body locations map to boxes.
4. **Body diagram.** The card's outline has 163 named tick boxes. Spoken locations ("left forearm") map to them by
   a fixed lookup, so the X lands exactly where the form expects it.
5. **PDF and review sheet.** The card is written into the real DD Form 1380, read back to confirm every field
   landed, and paired with a sheet: **Missing information** (what a surgeon needs but nobody said) and **Needs
   checking** (anything garbled, corrected or in dispute).
6. **Score.** Against the answer key, with every mistake tagged by the step that caused it.

**Time it saves (planning assumptions, not measured).** Nobody has timed medics doing this, so treat these as a
starting point. Each range runs from a calm best case to a busy collection point.

- By hand: 5 to 12 minutes a card. The low end is a quiet desk (listen once, write about 22 boxes, mark the body
  diagram). The high end adds finding the right recording, re-listening through static and corrections, stopping to
  treat, and printing, signing and attaching the card.
- With the system: the medic still reviews every card (1 to 2 minutes each), plus 0.5 to 1.5 minutes for each of the
  118 things the 50 cards ask them to ask or check. The app counts these live from the cards.
- Not included: treating, triage decisions, and waiting for answers that never come (a sender who has left). Those
  stay flagged on the card. Two medics assumes a perfectly even split.

| All 50 cards | 1 medic | 2 medics |
|---|---|---|
| By hand | 4.2 to 10.0 hours (the 3 to 4 hour evacuation window is missed even in the best case) | 2.1 to 5.0 hours |
| With the system, medic reviews every card | 1.8 to 4.6 hours | 0.9 to 2.3 hours |

How to replace the assumptions with numbers: a short tabletop exercise where two or three medics each write 5 cards by
hand and review 5 system cards, timed, with a few planned interruptions.

**Human in the loop.** The system only drafts. It gives the medic what they need to judge each card quickly (the to-do
list, a confidence mark per value, both transcripts, the words behind each value); the medic decides and signs.

**Confidence.** Each value is marked by whether both listeners heard it. Across all 50 cards, values both heard are
97.9% correct; values only one heard are 81.1% correct, about nine times the error rate. The app shows each card's
share of agreed values and names the single-listener values, so the medic knows where to look first.

About 20 seconds and 1 to 2 US cents per card; all 50 run in parallel in about a minute.

## What I tested, and what I decided

I benchmarked every step on our own recordings and answer key, not on vendor claims.

| Question | Tested | Answer |
|---|---|---|
| Which speech model? | 19 models on all 50 recordings: ElevenLabs, AssemblyAI, Deepgram, OpenAI, Google, Mistral, xAI, NVIDIA, Qwen, Meta, Fish Audio, plus audio chat models | **ElevenLabs Scribe v2 Medical**: 93% of values captured, 86% on radio and noise. Deepgram Nova-3 was near the bottom (74%) |
| Clean the audio first? | 4 methods: spectral gating, radio band-pass, DeepFilterNet3, Meta Denoiser (Demucs) | **No.** Every one made hard audio worse (86% fell to 79-80% with the neural denoisers). Modern speech models are trained on noise; denoisers remove parts of words |
| Which model fills the card? | 14 models on the final prompt (OpenAI, Google, Qwen, GLM, DeepSeek, Mistral), the top 3 also on the locked-away set; Anthropic models in an earlier round | **Gemini 3.8 Flash.** The top six are statistically tied (about 95%); Gemini had the best held-out score and fewest made-up values. Qwen 4 Max scored well but made up twice as many |
| A second model to verify? | Two card models side by side | **No.** They make the same mistakes (agree on 99.6% of fields): errors come from the audio, not the reading |
| A second listen? | Scribe plus a second speech model, disagreements flagged | **Yes.** It holds 21 of the 80 values Scribe misses. Held-out F1 92.5% to 93.8% (gap interval +0.2 to +2.8 points), precision 95.8% to 97.6%, identity 85% to 89.5% |
| A vision model for the PDF? | Not needed | The body diagram is named tick boxes; filling it is exact code |

The pattern behind all of it: **the audio is the ceiling, not the AI.** Changing the card model moves the score by
tenths of a point; hearing better moves it by whole points. And on a casualty card, careful beats complete: a
blank box and a flag is safer than a confident guess.

## Where it still goes wrong (honest limits)

- **Some audio is gone.** One radio recording (vdi) is mostly static; another (kdb) is 36 seconds long with about
  5 seconds of speech surviving. No model recovers them.
- **Names spelled the way they sound.** "Kaur" heard as "Carr". The second listen helps (identity 85% to 89.5%),
  and in real use the casualty's ID tag settles it, which is why the card asks for it.
- **The answer key has a few slips.** One card (roo) leaves out a TXA dose and oxygen that are clearly spoken, and
  two body-diagram entries swap left and right. I did not bend the system to match them, so they count against us.
- **One small leak, flagged.** I wrote a list of real UK unit names into the instructions after seeing units in
  the answer key, so the unit field on the locked-away set is slightly flattered.

## In the real world

The medic at the casualty collection point records the handover (already happening in this scenario). About 20
seconds later the card is ready. Instead of writing 138 boxes by hand, they read a short list: what to ask the
sender before they leave ("say again tourniquet time") and the few values in dispute. They sign, and the card is
fastened to the casualty. Every value traces back to the words that were spoken.

What I would build next: a larger test set (write new handover scripts with known answers, voice them with
text-to-speech and add radio noise, so results rest on hundreds of cards, not 50); an offline mode for forward
use (a local speech model already captures 80% with no network); reading missing items back to the sender in real
time; and splitting very long recordings at pauses (not needed here: the longest is 61 seconds).

## Try it

```bash
python3 -m pip install -r requirements.txt
python3 -m tccc            # one command: opens the app with all 50 cards (built from cached results, no key needed)
```

To process new recordings or re-run the models (reads `OPENROUTER_API_KEY` from `../.env`):

```bash
python3 -m tccc.pipeline ../recordings/handover-isa.wav   # one recording -> out/live/ (card, PDF, review sheet)
python3 -m uvicorn tccc.app:app --port 8000          # web app: cards, benchmark, guide; upload a recording
python3 -m tccc.run google/gemini-3.8-flash --split heldout --pdf   # re-run the honest evaluation (cached, free)
```

The web app lists every casualty, most urgent first, with each card's status: **Complete**, **Missing
information** (naming what to ask for) or **Needs checking**. Each card opens in MIST order beside the filled PDF.
A benchmark page shows the results above, and a guide explains how a medic uses it.

A hard spending cap protects the provided key: before any paid call, the code checks the key's real usage and
stops at $7. The pipeline's runs on the provided key have used $4.24.

More detail: `docs/ARCHITECTURE.md` (every step, how it is scored, every experiment) and `AI_LOG.md` (how I worked
with AI coding tools).
