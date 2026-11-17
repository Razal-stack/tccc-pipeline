---
name: tccc-eval
description: Run, score and improve the TCCC card pipeline step by step without wasting OpenRouter spend. Use when re-scoring, tuning the prompt or validation, or producing final cards.
---

Read `CLAUDE.md` and `docs/ARCHITECTURE.md` first.

## Loop (free unless the prompt or model changes)

1. Re-score from cache: `python3 -m tccc.run <model> --split dev`. Cached replies in
   `out/raw/<model>/<prompt hash>/` mean validation, body-map and scoring changes cost nothing.
2. Open `out/<model>/dev/report.md`. Read "Where the errors come from", then the error table.
3. Fix the step the error belongs to:
   - `transcription` -> nothing in extraction can help; note it.
   - `extraction` -> a general rule in `PROMPT` (tccc/extract.py). Never a rule keyed to one file.
   - `validation` -> loosen the check in tccc/validate.py.
   - `invented` -> tighten a rule or the evidence check.
4. Body map: `python3 -m tccc.injury` (dev / held-out / all F1).
5. A prompt edit changes the hash, so the next run pays for new replies. Batch prompt edits before re-running.

## Rules

- Tune on dev only. Held-out is run once, at the end, and reported first.
- The provided OpenRouter key: final inference only, cheapest model that holds accuracy (`openai/gpt-5.6-luna`
  preferred). No Opus or premium models. Check spend in each run's "new spend" line.
- Safety first: blank + flag beats a confident wrong value.

## Final run

`python3 -m tccc.run <model> --split heldout --pdf`, then `--split all --pdf`. Cards land in
`out/<model>/<split>/cards/`, review sheets in `review/`.
