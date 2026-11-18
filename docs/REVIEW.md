# Engineering review (18 Nov 2026)

An end-to-end read of the code, evals and docs after the pipeline was scored, followed by a tidy-up. Kept short and
in priority order: what is done well, what was wrong, what changed, what was left and why. Headline numbers were
checked before and after every change: held-out F1 93.8%, all 50 F1 94.7%, $0 spend.

## Done well

1. **Errors are attributed to a stage.** `tccc/run.py` tags every wrong, missed or invented value as
   transcription, extraction, validation or invented. That one feature drove every good decision afterwards
   (for example "the audio is the ceiling, not the reader").
2. **Honest scoring.** Fixed split made before tuning, F1 on filled fields beside the empty-card baseline, bootstrap
   intervals on gaps, held-out reported first.
3. **Safety in code, not in the prompt.** `validate.supported` drops any value whose words or digits are not in the
   transcript; every drop becomes a flag. The model can propose; only code can put a value on the card.
4. **One code path.** Evaluation and live recordings both go through `pipeline.finish()`.
5. **Cheap to rerun.** Replies are cached by prompt + transcript hash, transcripts per model, and a hard spend cap
   reads the key's real usage. Re-scoring costs nothing.
6. **The PDF is verified, not assumed.** Every card is read back and compared field by field.

## Problems found (priority order)

| # | Problem | Evidence | Status |
|---|---|---|---|
| 1 | No unit tests. The only safety net was re-running the eval by hand. | no `tests/` | **Fixed**: offline pytest suite and a golden test that the cached held-out run scores 93.8% |
| 2 | App upload spent money without the spend cap. `pipeline.main` called `guard_budget`, `app.upload` did not. | `tccc/app.py` upload | **Fixed** |
| 3 | `ARCHITECTURE.md` was a lab notebook gone stale: step 1 pointed at the bake-off script, two sections said "plan, nothing run yet" or "written, not yet run", the results table predated the second listen (92.5% not 93.8%), "card ready in about 10 s" (it is about 20 s), offline model 74% vs 80% elsewhere. | old doc | **Fixed**: rewritten as a current-state doc; history kept in `docs/archive/experiment-log.md` |
| 4 | Config scattered: the repo root or data path was worked out in 8 modules; the chosen models lived in `pipeline.py` while the second listen was named again, in folder form, in `extract.py`. | grep `parent.parent` | **Fixed**: `tccc/config.py` |
| 5 | Experiments mixed with the product: `stt_bakeoff.py` (paid), `denoise.py` (needs torch, not in requirements), `diagram.py` (docs tool) sat beside the pipeline modules. | imports: nothing in the pipeline used them | **Fixed**: moved to `tccc/experiments/` and `docs/diagram.py` |
| 6 | Time-saved chart overclaimed: minute rates were assumptions shown as estimates, two medics assumed perfect halving, the by-hand model left out finding recordings, re-listening, interruptions and printing. | `/how` | **Fixed**: labelled as planning assumptions, wider ranges (by hand 5 to 12 min, review 1 to 2 min plus 0.5 to 1.5 min per item), exclusions stated, how to measure it |
| 7 | Benchmark page: "unseen recordings" never explained; grey bars looked like "not used" (they meant below 90%). | `/benchmark` | **Fixed**: split explained with file lists, legend, per-group key with live counts |
| 8 | The production path needs the answer key: `extract.py` builds the field list and checkbox types from `output-true-values.json`, and the split lives in the prompt module. | `extract.py` imports `score.TRUTH` | **Deferred**: the fix changes the prompt text and so the cache hash, which means paying to re-run every reply. Do it with the next prompt change. |
| 9 | Three slightly different "was this heard?" matchers: `validate.supported` (evidence), `run.heard` (error stages), `app.heard_by` (confidence). | three functions | **Deferred**: merging changes the 97.9% / 81.1% confidence calibration and the stage tags; needs a re-calibration pass, not a refactor |
| 10 | Confidence (heard by one listener) is computed in the UI, not the pipeline, so the review sheet a medic prints does not carry it. | `app.confidence` | **Deferred**: small, worth doing with item 9 |
| 11 | Docs disagree on small facts: spend $3.90 (CLAUDE.md) vs $4.24 (README); the bake-off CSV lists Gemini 4 Argon at 93.6% of values (above Scribe's 92.9%) while the older docs say 90%. | CSV, docs | **Partly fixed**: README's later $4.24 used everywhere. Argon: see below |
| 12 | `stt.py` uses `audioop`, removed in Python 3.13. Uploads are processed inside the request with no type or size check. | `stt.py`, `app.py` | **Noted**: fine for 3.9 and a local demo |

**On Gemini 4 Argon as a listener.** The run ledger shows it was tried as the second listen on the tuning set:
F1 95.0% with 12 made-up values, against 95.5% and 4 for Qwen 3.8 Omni Flash, so Qwen stayed. Argon as the main
listener was never tested end to end. It is the first thing to try if hearing needs to improve, and it is the best
third listener in the simulation below.

## The loop question

Should the pipeline loop back when a value is missing or the two listeners disagree? Three options:

**(a) Ask the language model again (an agent loop). Not worth it.** On the tuning set a second reader (Opus 5.5)
disagreed with Gemini on 14 of 3,425 fields (99.6% agreement); even a perfect referee would lift F1 by 0.4 points.
Extra medical rules caught 0 of the 25 remaining errors. The errors come from hearing, so re-reading the same
transcript cannot fix them, and each extra pass is another chance to invent a value.

**(b) Re-listen to the doubtful values with a third model. Worth it later, as a review-time saver.** Simulated
for free with the cached bake-off transcripts (`python3 -m tccc.experiments.relisten`), on all 50 cards:

| Third listener | Single-listener values it confirms (right / wrong) | Right when confirmed | Lost values it holds |
|---|---|---|---|
| Gemini 4 Argon | 22 of 30 / 1 of 7 | 96% | 7 of 34 |
| AssemblyAI Universal | 15 of 30 / 1 of 7 | 94% | 2 of 34 |
| Fish Audio | 10 of 30 / 1 of 7 | 91% | 3 of 34 |
| OpenAI gpt-transcribe | 14 of 30 / 2 of 7 | 88% | 1 of 34 |

What it means: today 37 values on the 50 cards were heard by only one listener, and 81.1% of them are right. With
Argon as a third listener, 23 of those 37 would be confirmed (96% right) and could leave the medic's check list,
which shrinks from 37 values to 14. One wrong value would slip through confirmed, so confirmed values should still be
marked on the card. For recall, at most 9 of the 34 values lost by both listeners appear in any of the four third
transcripts (an upper bound: the match is by digits, and several are times like 1500 that could match the wrong
moment). Even if every one were recovered, all-50 recall would go from 92.1% to 92.9% at most.

Cost: 33 of 50 cards have a single-listener value or a dispute. A whole-recording third listen with Argon is
$0.34 per audio hour, about $0.19 for all 33 minutes of audio. Re-listening to just the disputed seconds would cost
less, but needs word timestamps from the first listener, which our OpenRouter calls do not return today.

Design sketch: after `finish()`, for each single-listener or disputed value, run the third listen (whole file for
now), and mark the value "confirmed by 2 of 3" if the third transcript holds it. A third listen never fills a blank
box on its own: anything it alone recovers goes to the medic as "a third listen heard 1422 for the left leg
tourniquet time, please confirm". So the invented-value risk does not rise.

**(c) The human loop. Already built and stays the main loop.** The "Ask the sender" list (`missing_critical`) and
the "Check these" flags send the medic back to the source: the person handing over, or the recording. It is the
only loop that can recover audio that is gone (vdi, kdb).

**Recommendation.** Now: keep (c) as is; do not build (a). Next: build (b) as a confidence layer on the review
sheet, behind a flag, measured on the held-out set by how many check-list items it removes and how many wrong
values it confirms. Expected gain is review time (about 60% of single-listener checks, 23 of 37), not headline F1.

## Changes made in this review

- Time-saved chart and README: planning assumptions, wider honest ranges, exclusions, even-split caveat, how to measure.
- Benchmark page: held-out split explained (how it was made, which files); grey-bar legend; per-group key.
- `tccc/config.py`; experiments to `tccc/experiments/`; diagram generator to `docs/`.
- Spend cap on app uploads.
- `tests/` (pytest, offline) and `requirements-dev.txt`.
- `Makefile`: one-command setup and run; paid targets clearly labelled.
- Docs: new `ARCHITECTURE.md`, `DECISIONS.md` (why each technology and design choice), this review; old notebook
  archived; README quickstart; skill and CLAUDE.md paths updated.

## Deferred, with reasons

- Schema from `field_map.json` instead of the answer key (item 8): changes the prompt hash, so it costs a full re-run.
- One shared "heard" matcher and confidence in the pipeline (items 9, 10): needs re-calibration.
- Re-listen loop (b): needs a paid run to validate on held-out; designed above.
- Splitting `app.py` (about 680 lines of inline HTML and CSS) into templates: readable as one file for a demo;
  worth it only if the UI grows.
