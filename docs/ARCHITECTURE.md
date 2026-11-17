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

## Results so far (dev, 25 cards)

| Extraction model | Prompt | F1 filled fields | Invented per card | Cost for 25 |
|---|---|---|---|---|
| anthropic/claude-opus-5.5 | v2 | 93.0% | 0.16 | $0.95 |
| google/gemini-3.8-flash | v2 | 93.3% | 0.20 | $0.16 |
| z-ai/glm-5.3 | v1 | 91.2% | 0.48 | n/a |
| anthropic/claude-sonnet-5.5 | v1 | 90.9% | 0.52 | $0.47 |
| anthropic/claude-haiku-5.5 | v1 | 88.5% | 1.16 | $0.03 |
| openai/gpt-5-nano | v2 | 85.4% | 0.60 | $0.10 |

Speech-to-text (21 test files): Scribe v2 Medical found 85% of numbers on hard audio, 92% overall, $0.22/hour.
