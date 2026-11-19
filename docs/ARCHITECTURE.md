# Architecture and evals

A fixed chain of small steps. Each step has one job, one module and its own score, so when a card is wrong we can
say which step lost the value. Why each piece was chosen, with the evidence, is in [DECISIONS.md](DECISIONS.md).

Words used throughout: the **first listener** (ElevenLabs Scribe v2 Medical) and the **second listener** (Qwen 3.8
Omni Flash) turn audio into text; the **reader** (Gemini 3.8 Flash) turns the two transcripts into card fields. The
50 recordings are split once into 25 **tuning recordings** and 25 **held-out recordings**.

## Reading the code

Start here if you are opening the repo for the first time. Everything runs offline from the cache (`make test`,
`make eval`, `make app`); nothing below needs an API key until you process a new recording.

**Entry points.** `python3 -m tccc` (or `make app`) starts the web app in `tccc/app.py`. `tccc/pipeline.py` is the
live path: a new recording becomes a card. `tccc/run.py` is the evaluation path: cached transcripts become scored
cards. Both call the same `pipeline.finish()`.

**Reading order**, one job each:

1. `tccc/config.py`: paths, settings and the four chosen models.
2. `tccc/openrouter.py`: the API key, one HTTP call, and the spend cap.
3. `tccc/stt.py`: audio to text through a speech model, with key terms.
4. `tccc/extract.py`: the reader's prompt, one call per recording, the reply cache, the fixed tuning / held-out split.
5. `tccc/validate.py`: the reader's reply becomes a full card; every value is checked in code, failures become flags.
6. `tccc/injury.py`: injury notes to the 163 body-diagram boxes, by lookup.
7. `tccc/fill_pdf.py`: writes the PDF card and reads it back.
8. `pipeline.finish()` in `tccc/pipeline.py`: the steps above in order, plus the review sheet.
9. `tccc/score.py`: compares a card with the answer key (F1 on filled fields).
10. `tccc/run.py`: runs `finish()` over a set of recordings and tags each error with the step that lost it.
11. `tccc/app.py`: the web pages; styles in `tccc/static/app.css`.

`tccc/textnorm.py` (spoken numbers to digits) supports the scorer. **Experiments only**, not on the live path:
`tccc/experiments/` (speech-model bake-off, denoising test, third-listener simulation) and `docs/diagram.py`.

**Tests** live in `tests/`, all offline (`make test`, about 2 seconds). Read `tests/test_golden.py` first: it
replays the cached held-out run through the real code and checks the published 93.8%. Then `tests/test_validate.py`
shows the checks one rule at a time.

**Data in:** `data/` (answer key, field map, blank PDF) and `transcripts/<speech model>/`. **Outputs:**
`out/raw/<reader>/<prompt hash>/` (cached reader replies), `out/<reader>/<split>/` (cards, predictions, review
sheets, `report.md`), `out/live/` (new recordings), `out/runs.jsonl` (one line per scored run).

## The chain, and where the loops are

```
recording.wav (whole, raw: no cutting, no denoising)
   |
   +--> First listener: Scribe v2 Medical + key terms ---+     tccc/stt.py
   +--> Second listener: Qwen 3.8 Omni Flash ------------+     (both at once)
                                                         v
   Reader: Gemini 3.8 Flash, one call, temperature 0, JSON         tccc/extract.py
         only the fields that were said, each with the words it came from;
         listeners disagree on a value -> blank + flag
                                                         v
   Check in code, no AI: evidence in transcript, format,           tccc/validate.py
         dropdowns, ranges, schema; derived ticks. Fails -> blank + flag
                                                         v
   Body boxes by lookup (163 names)                                 tccc/injury.py
   PDF with drawn text, then read back and compared                 tccc/fill_pdf.py
                                                         v
   Review sheet: Ask the sender / Check these / heard by one listener   tccc/pipeline.py
                                                         v
   HUMAN LOOP (built): the medic asks the sender for what is missing,   tccc/app.py
   re-listens to flagged values, corrects, signs. Nothing is attached unchecked.

   RE-LISTEN LOOP (proposed, not built): a value heard by only one listener, or disputed,
   gets a third listen; confirmed by 2 of 3 -> drops off the check list; still never fills a blank.
```

There is deliberately no automated loop that asks the language model again. A second reader agreed with the first
on 99.6% of fields, and extra medical rules caught none of the remaining errors: they come from hearing, not
reading. The re-listen loop targets hearing; its offline simulation is in [DECISIONS.md](DECISIONS.md) under
"Targeted re-listen for uncertain values".

## Two entry points, one code path

| Path | Command | What it does |
|---|---|---|
| Live | `python3 -m tccc.pipeline file.wav` or upload in the app | listen twice, read, check, PDF, review sheet into `out/live/` |
| Evaluation | `python3 -m tccc.run <reader> --split heldout` | same `finish()` on cached transcripts and replies, then scores into `out/<reader>/<split>/` |

Both call `pipeline.finish()`, so the evaluated code is the code that runs on a new recording.

## Prompts

There are three pieces of model-facing text, all inline in the code so a change shows up in review:

| Text | Where | Goes to |
|---|---|---|
| `PROMPT`: the card rules (formats, literal answer-key conventions, evidence quotes, flags) | `tccc/extract.py` | the reader, as the system message |
| `TWO`: how to use two transcripts and when to blank and flag a disagreement | `tccc/extract.py` | the reader, before the transcripts |
| `LISTEN`: transcribe verbatim, keep corrections and numbers as spoken | `tccc/stt.py` | the second listener (an audio chat model) |

The first listener gets no prompt, only `KEYTERMS` (drug, kit and unit names) in `tccc/stt.py`.

**Versioning is the cache.** Reader replies are stored under `out/raw/<reader>/<hash>/`, where the hash covers
`PROMPT` and the names of the transcript folders used. Any edit to `PROMPT` gives a new folder, so old replies are
kept and every score can be traced to the exact prompt. Two inputs are not in the hash: the `TWO` text and the
JSON-mode setting. Changing either without changing `PROMPT` would reuse old replies, so change them together.

**History, scored on the tuning recordings with the first listener only:**

| Version | F1 | What changed |
|---|---|---|
| v1, v2 | v2 93.3% (v1 runs in `out/runs.jsonl`) | first drafts: field list, formats, evidence quotes, blank and flag. Not committed separately, so the v1 to v2 change is not recorded |
| v3 | 94.3% | the literal answer-key conventions (IDs never composed, no clinical defaults, notes format) |
| v3 + key-term transcripts | 94.5% | same prompt, better first-listener transcripts |
| v4 and v5 | 95.4%, 95.3% | spoken name order, unit detail, one tourniquet slot per limb, pelvic binder is not a splint, suspected mechanisms go to notes, precise injury locations (body boxes 87% to 97%) |

**Changing a prompt:** edit the text, run `make eval`, compare with the line for the previous hash in
`out/runs.jsonl`. The edit forces new reader replies: about $0.47 for all 50 recordings, under the spend cap. Tune
on the tuning recordings and look at held-out once at the end.

## Modules

| Module | Job |
|---|---|
| `tccc/config.py` | paths, settings and the four chosen models |
| `tccc/openrouter.py` | API key, one HTTP call, hard spend cap checked against the key's real usage |
| `tccc/stt.py` | speech-to-text with key terms; resend at 16 kHz if a model rejects the file size |
| `tccc/extract.py` | the prompt, one model call, cache by prompt + transcript hash, the fixed tuning / held-out split |
| `tccc/validate.py` | format, range and evidence checks, schema check, `missing_critical` (ask the sender) |
| `tccc/injury.py` | notes to body-diagram boxes, lookup table |
| `tccc/fill_pdf.py` | fill DD 1380 with drawn text appearances, `read_back` |
| `tccc/pipeline.py` | live path and the shared `finish()` |
| `tccc/run.py` | evaluation: score, tag every error with its step and kind, append to `out/runs.jsonl` |
| `tccc/score.py`, `tccc/textnorm.py` | scorer; spoken numbers to digits |
| `tccc/app.py` | FastAPI app: casualty list, card beside PDF, how it works, benchmark, guide, upload |
| `tccc/experiments/` | `stt_bakeoff` (paid), `denoise` (local, needs torch), `relisten` (free simulation) |
| `docs/diagram.py` | draws `docs/how-it-works.svg` |
| `tests/` | offline unit tests and the golden held-out regression |

## How each step is scored

| Step | Eval | Where it shows |
|---|---|---|
| Listen | share of answer-key numbers and terms that reach the transcript, by category and by hard vs other audio | `transcripts/_bakeoff.csv` |
| Read | F1, precision, recall per field group; errors where the value was in the transcript are tagged `extraction` | `out/<reader>/<split>/report.md` |
| Check | values the reader had right but a check dropped are tagged `validation`; every drop is a flag | `report.md`, `review/*.md` |
| Body boxes | set F1 on tuning, held-out, all | `python3 -m tccc.injury` |
| Whole card | F1 on filled fields, safety-critical F1, invented per card, naive accuracy beside the empty-card baseline, 95% bootstrap interval | `report.md`, `score.json`, `out/runs.jsonl` |
| Code | unit tests, plus a golden test that the cached held-out run still scores 93.8% | `make test` |

Error stages in every report:
- `transcription`: the true value is not in either transcript, so no reader could get it. Fix upstream.
- `extraction`: it was in the transcript and the reader missed or mangled it. Fix the prompt or the model.
- `validation`: the reader had it and a code check removed it. Loosen that check.
- `invented`: filled where the truth is blank. The dangerous one; tighten rules or evidence checks.

## Honest evaluation

- Fixed split, made before any tuning: file names sorted, even positions are tuning recordings (25), odd positions
  are held-out (25). `SPLITS` in `tccc/extract.py` (named `dev` and `heldout` in code). Prompts and rules were
  tuned on the tuning recordings only. Held-out was also used to choose between the final two or three tied readers
  (on made-up values), to confirm the second listener, and it prompted one evidence-check fix ("10/12" as a time,
  on ato); it was scored a few times along the way (`out/runs.jsonl`), so it is slightly optimistic.
- Held-out is reported first; all 50 includes the tuning half.
- Known answer-key oddities, not tuned to: roo omits TXA and oxygen that are clearly spoken; aim ticks GSW though
  only a grenade is mentioned; hip and upper back boxes swap left and right on two cards.
- One small leak, stated: the list of real UK unit names in the prompt was written after seeing answer-key units.

## Current results (final prompt, both listeners, Gemini 3.8 Flash as reader)

| Set | F1 | Precision | Recall | Safety-critical F1 | Invented | Body boxes F1 |
|---|---|---|---|---|---|---|
| Held-out 25 | 93.8% | 97.6% | 90.4% | 96.8% | 2 (0.08 a card) | 80.5% |
| All 50 | 94.7% | 97.5% | 92.1% | 96.4% | 6 (0.12 a card) | 89% |

Reproduce for free: `make eval`. Every model call is cached in `out/raw/<reader>/<prompt hash>/` and
`transcripts/<speech model>/`, so re-scoring, changing checks or the body map costs nothing. A prompt edit changes
the hash and the next run pays for new replies.

## Cost and spend control

- Before any paid call (command line or app upload) the code reads the key's real usage and stops at
  `TCCC_BUDGET_USD` (default $7).
- The final pipeline costs about $0.65 for all 50 recordings: first listener $0.15, second listener $0.03, the
  reader with both transcripts $0.47.
- The reader returns only the roughly 22 filled fields, not all 138, which keeps output tokens low.

## Experiments behind the choices

Each row backs a claim on the Benchmark page or in [DECISIONS.md](DECISIONS.md). The code is in `tccc/experiments/`.

| Question | What was run | Result |
|---|---|---|
| Which speech model? | 19 models on all 50 recordings (`stt_bakeoff`, paid), scored by share of answer-key values in the transcript | Scribe v2 Medical + key terms 93% (hard audio 86%); Qwen 3.8 Omni Flash 92% (83%); Fish Audio and AssemblyAI 91%; local Parakeet 80%; Deepgram Nova-3 74%. Full table: `transcripts/_bakeoff.csv` |
| Key terms? | Scribe with and without a domain word list | drug and kit words 90% to 97% |
| Clean the audio first? | DeepFilterNet3 and Meta Denoiser on all 50 (`denoise`, local), spectral gating and band-pass on 9 hard files | raw 92.9% (hard 86.0%), DeepFilterNet3 91.0% (78.5%), Demucs 91.7% (80.2%); classic filters worse still. Raw audio kept |
| Which reader? | 14 models on the frozen prompt, tuning recordings, 95% intervals; top three on held-out | top six tied (94.6% to 95.5%); held-out made-up values Gemini 3.8 Flash 2, Terra 5, Argon 9 |
| A second reader as verifier? | Gemini and Opus 5.5 side by side on the tuning recordings, from cache | 14 of 3,425 fields differ; a perfect referee adds 0.4 points |
| A second listener? | Scribe plus Qwen, reader sees both, disagreements flagged | held-out 92.5% to 93.8% (gap interval +0.2 to +2.8); Argon as second listener invented more (12 vs 4 on tuning) |
| A third listener? | cached bake-off transcripts replayed (`relisten`, free) | confirms 23 of 37 single-listener values at 96% right; see DECISIONS, "Targeted re-listen" |
| Prompt versions | see Prompts above | 93.3% to 95.3% on the tuning recordings |

Any benchmarked reader can be re-scored for free from its cached replies, for example
`TCCC_SECOND= .venv/bin/python -m tccc.run qwen/qwen4-max --split dev` (an empty `TCCC_SECOND` selects the
first-listener-only transcripts those runs used). Early runs on older prompts (including the Anthropic models) are
in `out/runs.jsonl`.

## Known limits and next steps

- **Lost audio stays lost.** vdi is mostly static and kdb keeps about 5 seconds of speech; no model recovers them.
  The card asks the medic, which is the right answer.
- **Names are spelled as they sound** ("Kaur" heard as "Carr"). The ID tag settles it; the card asks for it.
- **Small test set.** 25 held-out cards give wide intervals. Next: write new handover scripts with known answers,
  voice them with text-to-speech, add radio noise, and test on hundreds of cards with a fresh held-out set.
- **Third listener** (DECISIONS, "Targeted re-listen"): build behind a flag and measure on held-out; expected gain
  is review time.
- **Offline use.** NVIDIA Parakeet TDT 0.6B v2 (int8, run on the Mac through sherpa-onnx with no internet) was in
  the same 19-model bake-off: 80% of answer-key values reached its transcript (52% on hard audio), against 93% (86%)
  for Scribe. A device in the field may have no network, so an on-device model like Parakeet is the route to offline
  use, at the cost of about 13 points of hearing accuracy (far more on radio and noise). That is why it is a next
  step and not the default.
- **The live path reads the field list from the answer-key file** (`data/output-true-values.json`). Moving it to
  `field_map.json` changes the prompt text and so the cache hash, so it waits for the next prompt change.
- **One "was this heard?" check, not three.** Evidence, error stages and confidence each use a slightly different
  matcher; merging them means re-calibrating the 97.9% / 81.1% confidence split.
- **Demo-grade app.** Uploads are processed inside the request (about 20 seconds) with no file type or size check;
  no auth. `tccc/stt.py` uses `audioop`, removed in Python 3.13 (fine on 3.9 to 3.12).
- **Time saved is an assumption.** A short timed tabletop exercise with medics would replace it with numbers.
