# Architecture and evals

A fixed chain of small steps. Each step has one job, one module and its own score, so when a card is wrong we can
say which step lost the value. Why each piece was chosen, with the evidence, is in [DECISIONS.md](DECISIONS.md).

## The chain, and where the loops are

```
recording.wav (whole, raw: no cutting, no denoising)
   |
   +--> Listen A: ElevenLabs Scribe v2 Medical + key terms ---+     tccc/stt.py
   +--> Listen B: Qwen 3.8 Omni Flash (independent) ----------+     (both at once)
                                                              v
   Read: Gemini 3.8 Flash, one call, temperature 0, JSON              tccc/extract.py
         only the fields that were said, each with the words it came from;
         listeners disagree on a value -> blank + flag
                                                              v
   Check in code, no AI: evidence in transcript, format,              tccc/validate.py
         dropdowns, ranges, schema; derived ticks. Fails -> blank + flag
                                                              v
   Body boxes by lookup (163 names)                                    tccc/injury.py
   PDF with drawn text, then read back and compared                    tccc/fill_pdf.py
                                                              v
   Review sheet: Ask the sender / Check these / heard by one listener  tccc/pipeline.py
                                                              v
   HUMAN LOOP (built): the medic asks the sender for what is missing,  tccc/app.py
   re-listens to flagged values, corrects, signs. Nothing is attached unchecked.

   RE-LISTEN LOOP (proposed, not built): a value heard by only one listener, or disputed,
   gets a third listen; confirmed by 2 of 3 -> drops off the check list; still never fills a blank.
```

There is deliberately no automated loop that asks the language model again. A second reader agreed with the first
on 99.6% of fields, and extra medical rules caught none of the remaining errors: they come from hearing, not
reading. The re-listen loop targets hearing; its offline simulation is in [DECISIONS.md](DECISIONS.md) (ADR-16).

## Two entry points, one code path

| Path | Command | What it does |
|---|---|---|
| Production | `python3 -m tccc.pipeline file.wav` or upload in the app | listen twice, read, check, PDF, review sheet into `out/live/` |
| Evaluation | `python3 -m tccc.run <model> --split heldout` | same `finish()` on cached transcripts and replies, then scores into `out/<model>/<split>/` |

Both call `pipeline.finish()`, so the evaluated code is the code that runs on a new recording.

## Modules

| Module | Job |
|---|---|
| `tccc/config.py` | paths and the four chosen models |
| `tccc/openrouter.py` | API key, one HTTP call, hard spend cap checked against the key's real usage |
| `tccc/stt.py` | speech-to-text with key terms; resend at 16 kHz if a model rejects the file size |
| `tccc/extract.py` | the prompt, one model call, cache by prompt + transcript hash, the fixed dev / held-out split |
| `tccc/validate.py` | format, range and evidence checks, schema check, `missing_critical` (ask the sender) |
| `tccc/injury.py` | notes to body-diagram boxes, lookup table |
| `tccc/fill_pdf.py` | fill DD 1380 with drawn text appearances, `read_back` |
| `tccc/pipeline.py` | production path and the shared `finish()` |
| `tccc/run.py` | evaluation: score, tag every error with its stage and kind, append to `out/runs.jsonl` |
| `tccc/score.py`, `tccc/textnorm.py` | scorer; spoken numbers to digits |
| `tccc/app.py` | FastAPI app: casualty list, card beside PDF, how it works, benchmark, guide, upload |
| `tccc/experiments/` | `stt_bakeoff` (paid), `denoise` (local, needs torch), `relisten` (free simulation) |
| `docs/diagram.py` | draws `docs/how-it-works.svg` |
| `tests/` | offline unit tests and the golden held-out regression |

## How each step is scored

| Step | Eval | Where it shows |
|---|---|---|
| Listen | share of answer-key numbers and terms that reach the transcript, by category and by hard vs other audio | `transcripts/_bakeoff.csv` |
| Read | F1, precision, recall per field group; errors where the value was in the transcript are tagged `extraction` | `out/<model>/<split>/report.md` |
| Check | values the model had right but a check dropped are tagged `validation`; every drop is a flag | `report.md`, `review/*.md` |
| Body boxes | set F1 on dev, held-out, all | `python3 -m tccc.injury` |
| Whole card | F1 on filled fields, safety-critical F1, invented per card, naive accuracy beside the empty-card baseline, 95% bootstrap interval | `report.md`, `score.json`, `out/runs.jsonl` |
| Code | unit tests, plus a golden test that the cached held-out run still scores 93.8% | `make test` |

Error stages in every report:
- `transcription`: the true value is not in either transcript, so no reader could get it. Fix upstream.
- `extraction`: it was in the transcript and the model missed or mangled it. Fix the prompt or the model.
- `validation`: the model had it and a code check removed it. Loosen that check.
- `invented`: filled where the truth is blank. The dangerous one; tighten rules or evidence checks.

## Honest evaluation

- Fixed split, made before any tuning: file names sorted, even positions are dev (25, used for tuning), odd
  positions are held-out (25, scored once at the end). `SPLITS` in `tccc/extract.py`.
- Held-out is reported first; all 50 includes the tuning half.
- Known answer-key oddities, not tuned to: roo omits TXA and oxygen that are clearly spoken; aim ticks GSW though
  only a grenade is mentioned; hip and upper back boxes swap left and right on two cards.
- One small leak, stated: the list of real UK unit names in the prompt was written after seeing answer-key units.

## Current results (prompt v5, Scribe + key terms and Qwen second listen, Gemini 3.8 Flash)

| Set | F1 | Precision | Safety-critical F1 | Invented | Body boxes F1 |
|---|---|---|---|---|---|
| Held-out 25 | 93.8% | 97.6% | 96.8% | 2 (0.08 a card) | 80.5% |
| All 50 | 94.7% | 97.5% | 96.4% | 6 (0.12 a card) | 89% |

Reproduce for free: `make eval`. Every model call is cached in `out/raw/<model>/<prompt hash>/` and
`transcripts/<model>/`, so re-scoring, changing checks or the body map costs nothing. A prompt edit changes the
hash and the next run pays for new replies.

## Cost and spend control

- Before any paid call (command line or app upload) the code reads the key's real usage and stops at
  `TCCC_BUDGET_USD` (default $7).
- The final pipeline costs about $0.65 for all 50 recordings: Scribe $0.15, second listen $0.03, Gemini reading both
  transcripts $0.47.
- The model returns only the roughly 22 filled fields, not all 138, which keeps output tokens low.

## Experiments behind the choices

Each row backs a claim on the Benchmark page or in [DECISIONS.md](DECISIONS.md). The code is in `tccc/experiments/`.

| Question | What was run | Result |
|---|---|---|
| Which speech model? | 19 models on all 50 recordings (`stt_bakeoff`, paid), scored by share of answer-key values in the transcript | Scribe v2 Medical + key terms 93% (hard audio 86%); Qwen 3.8 Omni Flash 92% (83%); Fish Audio and AssemblyAI 91%; local Parakeet 80%; Deepgram Nova-3 74%. Full table: `transcripts/_bakeoff.csv` |
| Key terms? | Scribe with and without a domain word list | drug and kit words 90% to 97% |
| Clean the audio first? | DeepFilterNet3 and Meta Denoiser on all 50 (`denoise`, local), spectral gating and band-pass on 9 hard files | raw 92.9% (hard 86.0%), DeepFilterNet3 91.0% (78.5%), Demucs 91.7% (80.2%); classic filters worse still. Raw audio kept |
| Which reader? | 14 models on the frozen prompt, dev set, 95% intervals; top three on held-out | top six tied (94.6% to 95.5%); held-out made-up values Gemini 3.8 Flash 2, Terra 5, Argon 9 |
| A second reader as verifier? | Gemini and Opus 5.5 side by side on dev, from cache | 14 of 3,425 fields differ; a perfect referee adds 0.4 points |
| A second listener? | Scribe plus Qwen, reader sees both, disagreements flagged | held-out 92.5% to 93.8% (gap interval +0.2 to +2.8); Argon as second listener invented more (12 vs 4 on dev) |
| A third listener? | cached bake-off transcripts replayed (`relisten`, free) | confirms 23 of 37 single-listener values at 96% right; see ADR-16 |
| Prompt versions | v2 to v5 on dev, single listener | 93.3%, 94.3%, 94.5% (with key-term transcripts), 95.4%, 95.3% (body boxes 87% to 97%) |

Any benchmarked reader can be re-scored for free from its cached replies, for example
`TCCC_SECOND= .venv/bin/python -m tccc.run qwen/qwen4-max --split dev` (an empty `TCCC_SECOND` selects the
single-listener transcripts those runs used). Early runs on older prompts (including the Anthropic models) are in
`out/runs.jsonl`.

## Known limits and next steps

- **Lost audio stays lost.** vdi is mostly static and kdb keeps about 5 seconds of speech; no model recovers them.
  The card asks the medic, which is the right answer.
- **Names are spelled as they sound** ("Kaur" heard as "Carr"). The ID tag settles it; the card asks for it.
- **Small test set.** 25 held-out cards give wide intervals. Next: write new handover scripts with known answers,
  voice them with text-to-speech, add radio noise, and test on hundreds of cards with a fresh held-out set.
- **Third listen** (ADR-16): build behind a flag and measure on held-out; expected gain is review time.
- **Offline use.** A local speech model already captures 80% of values; forward use would need it.
- **The production path reads the field list from the answer-key file** (`data/output-true-values.json`). Moving
  it to `field_map.json` changes the prompt text and so the cache hash, so it waits for the next prompt change.
- **One "was this heard?" check, not three.** Evidence, error stages and confidence each use a slightly different
  matcher; merging them means re-calibrating the 97.9% / 81.1% confidence split.
- **Demo-grade app.** Uploads are processed inside the request (about 20 seconds) with no file type or size check;
  no auth. `tccc/stt.py` uses `audioop`, removed in Python 3.13 (fine on 3.9 to 3.12).
- **Time saved is an assumption.** A short timed tabletop exercise with medics would replace it with numbers.
