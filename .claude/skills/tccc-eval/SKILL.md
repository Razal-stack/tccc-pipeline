---
name: tccc-eval
description: Run, score and improve the TCCC card pipeline step by step without wasting OpenRouter spend. Use when re-scoring, tuning the prompt or validation, or producing final cards.
---

Read `CLAUDE.md`, `docs/ARCHITECTURE.md` and `docs/DECISIONS.md` first.

## Loop (free unless the prompt or model changes)

1. `make test` first: unit tests plus the golden check that cached held-out still scores 93.8%.
2. Re-score from cache: `.venv/bin/python -m tccc.run <model> --split dev` (or `make eval` for held-out and all 50).
   Cached replies in `out/raw/<model>/<prompt hash>/` mean validation, body-map and scoring changes cost nothing.
3. Open `out/<model>/dev/report.md`. Read "Where the errors come from", then the error table.
4. Fix the step the error belongs to:
   - `transcription` -> nothing in extraction can help; note it (see the re-listen idea, ADR-16 in `docs/DECISIONS.md`).
   - `extraction` -> a general rule in `PROMPT` (`tccc/extract.py`). Never a rule keyed to one file.
   - `validation` -> loosen the check in `tccc/validate.py`.
   - `invented` -> tighten a rule or the evidence check.
5. Body map: `.venv/bin/python -m tccc.injury` (dev / held-out / all F1).
6. A prompt edit changes the hash, so the next run pays for new replies. Batch prompt edits before re-running.
7. Chosen models and paths live in `tccc/config.py`. Experiments live in `tccc/experiments/`.

## Rules

- Tune on dev only. Held-out is run once, at the end, and reported first.
- The provided OpenRouter key: final inference only, cheapest model that holds accuracy. No Opus or premium
  models. Check spend in each run's "new spend" line. The cap is `TCCC_BUDGET_USD` (default $7).
- Safety first: blank + flag beats a confident wrong value.

## Final run

`make cards` (all 50 PDFs from cache) or `.venv/bin/python -m tccc.run <model> --split heldout --pdf`. Cards land
in `out/<model>/<split>/cards/`, review sheets in `review/`.
