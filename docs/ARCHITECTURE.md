# Architecture and evals

A fixed chain of small steps. Each step has one job, one module, and its own score, so when a card is wrong we
can say which step lost the value.

```
recording.wav
  1. Transcribe   tccc/stt_bakeoff.py   ElevenLabs Scribe v2 Medical via OpenRouter, whole file, cached
  2. Extract      tccc/extract.py       one LLM call, returns only fields heard + exact words as evidence, cached
  3. Validate     tccc/validate.py      formats, dropdowns, ranges, evidence must be in the transcript
  4. Body map     tccc/injury.py        injury locations in notes -> body-diagram boxes, lookup table
  5. Output       tccc/run.py           card JSON, filled PDF (tccc/fill_pdf.py), medic review sheet
  6. Score        tccc/score.py         against the ground truth, with every error tagged to a step
```

Why not an agent: each card is one bounded extraction. A fixed chain is cheaper, gives the same answer every
time, and is easy to score. Agents were used to build it (a worker agent wrote the body map), not to run it.

## How each step is scored

| Step | Eval | Where it shows |
|---|---|---|
| 1 Transcribe | % of ground-truth numbers and terms present in the transcript, by category (vitals, times, doses, ids, names, drugs) and by condition (hard audio vs other) | `transcripts/_bakeoff.csv` |
| 2 Extract | F1 / precision / recall per field group; errors where the value WAS in the transcript are tagged `extraction` | `out/<model>/<split>/report.md` |
| 3 Validate | values the model had right but a check dropped are tagged `validation`; every drop is a flag in the review sheet | `report.md`, `review/*.md` |
| 4 Body map | set F1 on injury boxes (dev, held-out, all) | `python3 -m tccc.injury` |
| 6 Score | headline F1 on filled fields, safety-critical F1, invented values per card, naive accuracy vs empty card | `report.md`, `score.json` |

Error stages in every report:
- `transcription`: the true value is not in the transcript, so no extractor could get it. Fix upstream (audio, STT).
- `extraction`: it was in the transcript and the model missed or mangled it. Fix the prompt or the model.
- `validation`: the model had it, a code check removed it. Loosen that check.
- `invented`: filled where the truth is blank. The dangerous one; tighten rules or evidence checks.

## Honest evaluation

- Fixed split: sorted file names, even positions are dev (25), odd are held-out (25). All tuning on dev.
- Report held-out first, then all 50.
- Known ground-truth oddities (not tuned to): roo truth omits TXA and oxygen that are clearly spoken; aim truth
  ticks GSW though only a grenade is mentioned; hip and upper back boxes swap left and right on two cards.

## Cost control

- Development runs on our own Claude Code. The provided OpenRouter key is only for pipeline inference.
- Transcripts and LLM replies are cached on disk (`transcripts/`, `out/raw/<model>/<prompt hash>/`), so a re-run
  only pays for what changed, and validation or scoring changes cost nothing.
- The model returns only the ~22 filled fields, not all 138, which keeps output tokens low.

## Early extraction comparison (dev, 25 cards, prompts v1/v2)

| Extraction model | Prompt | F1 filled fields | Invented per card | Cost for 25 |
|---|---|---|---|---|
| anthropic/claude-opus-5.5 | v2 | 93.0% | 0.16 | $0.95 |
| google/gemini-3.8-flash | v2 | 93.3% | 0.20 | $0.16 |
| z-ai/glm-5.3 | v1 | 91.2% | 0.48 | n/a |
| anthropic/claude-sonnet-5.5 | v1 | 90.9% | 0.52 | $0.47 |
| anthropic/claude-haiku-5.5 | v1 | 88.5% | 1.16 | $0.03 |
| openai/gpt-5-nano | v2 | 85.4% | 0.60 | $0.10 |

Speech-to-text (21 test files): Scribe v2 Medical found 85% of numbers on hard audio, 92% overall, $0.22/hour.

## Road to 95% (plan, nothing run yet)

Where dev F1 stands (Gemini 3.8 Flash, 93.3%): 25 extraction errors, 22 transcription errors, 5 invented.
Ceiling with today's transcripts and perfect extraction: about 97-98%. So the gap is mostly extraction.

Checked for free against cached transcripts: a second speech-to-text model recovers only 2 of 10 values Scribe
missed (Fish Audio, AssemblyAI on ihg). The rest are lost by every model (vdi radio, "Kaur" heard as "Carr").
Speech-to-text stays Scribe v2 Medical. Deepgram nova-3 failed on 11 of 21 files through OpenRouter, and Deepgram
Flux is not offered there.

Experiments, cheapest first:
1. Free: fix the remaining extraction patterns in code or prompt (e.g. "no known allergies" -> NKA).
2. Text-model bake-off on dev, one run each, about $0.35 total: openai/gpt-5.6-luna, qwen/qwen3.5-flash,
   deepseek/deepseek-v4-flash, z-ai/glm-5.3, google/gemini-3.8-flash as the baseline. No Anthropic models.
3. Free after step 2: field-level vote across the best 2-3 cheap models, using cached replies. Agree -> fill;
   disagree -> blank + flag. Raises precision (fewer invented values) at no extra cost.
4. Optional, about $0.20: add a second transcript (Fish Audio) to the prompt for hard-audio files only.
5. Final: chosen setup once on held-out (reported first), then all 50 with PDFs.

Not doing:
- A vision model for the PDF. Filling the PDF is plain code writing to named form fields, already verified on
  all 50 golden cards with zero errors. Accuracy is decided before the PDF, so a vision model would add cost and
  nothing else.
- An audio-native LLM instead of speech-to-text (e.g. gemini-omni-1.2-flash). No strict JSON output on
  OpenRouter, higher price, and the missing values are ones no listener recovered.

## Do we need a verifier model? (measured, free, from cached replies)

On dev, Gemini 3.8 Flash and Opus 5.5 disagree on only 14 of 3,425 fields. Even a perfect referee picking the
right one of the two would lift F1 from 93.3% to 93.7%; a 3-model majority vote gives 93.5%. The models make the
same mistakes, so the errors are systematic: a second model cannot catch an error both share.

Of the errors both models make, about 20 are beyond any text model (wrong numbers in the transcript, unreadable
radio, misspelled names, ground-truth quirks). The rest are conventions, fixed in the prompt:
hypothermia kit names, UK unit names misheard ("2 Larc" -> 2 Lancs), drug/kit words lost by speech-to-text.

Decision:
- Primary path: one cheap model + code checks (as now), better prompt (v3: conventions + domain vocabulary).
- Upstream: speech-to-text keyword biasing (Scribe key terms: unit names, drugs, IV/IO) if OpenRouter passes it.
- Verifier, cheapest useful form: a second cheap model runs independently; code compares field by field; only
  disagreements (about 0.5 fields per card) go to a small referee call, and anything still unsure is left blank
  and flagged for the medic. Worth it for safety flags, not for the headline number.

## Getting the most out of the audio (measured, free)

- Ceiling across 7 speech-to-text models on the 21 test files: Scribe alone catches 78% of literal values on hard
  audio, any of the 7 models 84%. Clean audio: 93% vs 96%. The losses concentrate in a few recordings (kdb: 36 s
  of audio, about 5 s transcribed by every model; vdi radio).
- Audio clean-up before speech-to-text, tested locally on 9 hard files with the offline model (free):
  raw 77/108 numbers, loudness-normalised 78, spectral denoise 69, voice band-pass 46. Clean-up hurts: modern
  models are trained on noise and classic filters remove cues they use. Decision: send raw audio, no DSP layer.
- Voice-activity chopping was already ruled out (drops radio speech).

## Prompt v3 (written, not yet run)

Adds: UK unit names for correcting known mis-hearings, first responder name order, AVPU phrasing, NKA wording,
hypothermia kit names. Caveat for honesty: the unit list is general domain knowledge, but it was written after
seeing ground-truth units, so the held-out score on the `unit` field is slightly optimistic.

## How this would be used (beyond the benchmark)

Who: a medic or team leader at a casualty collection point, many casualties, little time, gloves on.
Flow:
1. Record the handover on a phone or radio log (already happening in the scenario).
2. Card is ready in about 10 s: filled PDF plus a one-page review sheet.
3. The review sheet lists only what needs a human: flagged fields (garbled, corrected, unsupported), with the
   transcript words beside each. Everything else is pre-filled. The medic checks the flags, not the whole card.
4. Medic signs; the card travels with the casualty.
Design choices that follow: blanks over guesses; every value traceable to spoken words; flags short and plain;
works per casualty, so 50 cards are 50 independent jobs (parallel, about a minute in total).
Later, not now: offline fallback (the local model gets 74% of values, no network), a simple review screen,
linking cards to casualty IDs, and voice prompts to the sender for missing critical fields ("say again TQ time").


## Final results (prompt v5, keyterm transcripts, Gemini 3.8 Flash)

| Set | F1 | Safety-critical F1 | Invented per card | Body boxes F1 |
|---|---|---|---|---|
| Held-out 25 (run once) | 92.4% | 96.2% | 0.08 | 80.5% |
| Dev 25 (tuned on) | 95.3% | 96.1% | 0.20 | 97.0% |
| All 50 | 94.0% | 96.1% | 0.14 | 89.0% |

Prompt history on dev (Gemini 3.8 Flash): v2 93.3% -> v3 94.3% -> v3 + keyterm transcripts 94.5% -> v4 95.4%
-> v5 95.3% (body boxes 87% -> 97%). Other models on v3: GPT-5.6 Luna 91.7%, DeepSeek V4 Flash 88.1%,
Qwen 3.5 Flash failed (provider errors).

Extra layers added after the first full run:
- PDF read-back after every fill, and text appearances drawn into the PDF (Preview showed blank fields otherwise).
- `missing_critical`: an "Ask the sender" list per card (identity, evac, tourniquet time, drug dose/route/time).
- Error kinds per run (left blank, digit off, spelling, wrong, made up) and a run ledger for later tuning.
