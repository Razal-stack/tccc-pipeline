# CLAUDE.md: TCCC card pipeline

## What this is

An engineering challenge.
Brief: `../task.md`. Time budget 3-4 hours. They judge: scoping judgment, AI tooling instincts, whether it works
against the ground truth, how AI coding tools were used (what was delegated, reviewed, pushed back on), and how
clearly it's explained to a non-technical founder. Rough edges are fine if stated.

**Goal:** turn 50 recorded casualty handovers (`../recordings/*.wav`) into filled TCCC cards (DD Form 1380, PDF),
and report a % accuracy against `../output-true-values.json` with a clear explanation of how it's calculated.

**Out of scope (per the brief):** auth, deployment, running on a device in the field, production error handling,
web UI. No frameworks or scaffolds until the core pipeline is done and scored.

**Deliverables:** this repo (runs), filled cards for the recordings, accuracy % + method, a short README for a founder.

## Files outside the repo (task folder, one level up)

| Path | What |
|---|---|
| `../task.md` | The brief |
| `../recordings/` | 50 synthetic TTS handovers, 6-61 s, 33 min total, 48 kHz mono |
| `../output-true-values.json` | Ground truth: 138 fields + `injury_boxes` per recording (copy in `data/`) |
| `../golden-cards/` | Ground truth filled into the PDF |
| `../field_map.json` | Field name -> PDF field; `repeated_on_back`; 163 `injury_boxes` (copy in `data/`) |
| `../tccc-card-blank.pdf` | Fillable AcroForm (copy in `data/`) |
| `../.env` | `OPENROUTER_API_KEY`, provided with the brief. **Never print, log or commit it.** |

## Status (2026-11-18): complete, scored, documented, reviewed

Held-out F1 93.8% (precision 97.6%, safety-critical 96.8%, 0.08 invented/card); all 50 F1 94.7%. 50 PDFs in
`out/google__gemini-3.8-flash/all/cards/`, all pass schema and read-back checks. Spend $4.52 of $7 cap (`make check-key`).
Read `README.md` (founder view, quickstart), `docs/ARCHITECTURE.md` (steps, loops, evals), `docs/DECISIONS.md`
(why each choice), `AI_LOG.md`. Older working notes live in git history only.
Commands: `make` (setup, app, test, eval, cards; `pipeline` and `bakeoff` are paid).

| Module | Job |
|---|---|
| `tccc/config.py` | paths and the four chosen models |
| `tccc/openrouter.py` | API key, one HTTP call, hard spend cap (`TCCC_BUDGET_USD`, default 7) checked against real key usage |
| `tccc/stt.py` | Speech-to-text with domain `keyterms` |
| `tccc/extract.py` | Prompt (v5) + one LLM call; replies cached by prompt+transcript hash in `out/raw/` |
| `tccc/validate.py` | Format/range/evidence checks, `check_card` schema, `missing_critical` (ask the sender) |
| `tccc/injury.py` | Notes -> 163 body-diagram boxes (lookup) |
| `tccc/fill_pdf.py` | Fill DD 1380 with drawn text appearances; `read_back` |
| `tccc/pipeline.py` | Production: new recording -> card, PDF, review (`finish` shared with run) |
| `tccc/run.py` | Evaluation: split -> scored report with error stage + kind; appends `out/runs.jsonl` |
| `tccc/app.py` | FastAPI: dashboard, card review beside PDF, upload |
| `tccc/score.py`, `tccc/textnorm.py` | Scorer, number normalising |
| `tccc/experiments/` | `stt_bakeoff` (paid speech benchmark), `denoise` (local, needs torch), `relisten` (free third-listen simulation) |
| `docs/diagram.py`, `tests/` | Draws `docs/how-it-works.svg`; offline pytest suite with golden held-out regression |

Chosen: speech `elevenlabs/scribe-v2-medical` + keyterms, plus a second listen `qwen/qwen3.8-omni-flash`
(`TCCC_SECOND`); extraction `google/gemini-3.8-flash` reading both; fallback `openai/gpt-6.1-terra`. Raw audio, no
denoiser (tested 4). See docs/DECISIONS.md and docs/ARCHITECTURE.md "Experiments behind the choices".

## What the data showed (drives every decision)

1. **The card is mostly blank.** 138 fields, about 22 filled per card (5 to 36); 45 fields never used. An empty card
   scores 84.5% naive accuracy, so naive accuracy is not the headline.
2. **Transcription is the bottleneck, and numbers break first.** Examples from local ASR: "Juliet Sierra 4417" ->
   "Juliet Ciela 4417"; "radial 128" -> "radio drugs at 180pm"; "TXA IV" -> "TXA I4".
3. **Don't chop audio with voice-activity detection.** It dropped most radio speech (oqx: 6 s of 38 s kept). Send
   whole recordings.
4. **The ground truth is strictly literal:**
   - 30 cards have name + last4 but **no** battle roster; 10 have battle roster but **no** name. Never compose or
     decompose IDs.
   - "Fentanyl lozenge", no dose stated (jge) -> route OTFC, dose blank. Normalise words to codes; never fill
     clinical defaults.
   - "Time found 0215" (lml) goes in notes, not `time` (time of wounding).
   - "Fentanyl withheld (opioid allergy)" (cpx) is not a dose given.
   - Partly heard -> blank + a note (vdi notes: "wound (detail not heard)"; pulse "130" with no location).
   - `tq_extremity` is true whenever a limb tourniquet is filled (49/50 consistent).
   - `notes` format: `Injuries: <location>: <description>; <location>: <description>; <other context>`.
5. **Traps in the audio:** retraction ("tourniquet on, no sorry, ignore that, that's the other casualty", aim);
   corrections (isa "six fifteen, correction six fifty"; sfw "morphine... sorry, ketamine 50 mg IM"; xbf "left,
   correction right"; ynt battle roster corrected); misassigned vital (zjl "pulse 28, sorry that's resps");
   radio read-back (oqx); explicit unknown (jge "not sure on the time"); repeat obs -> `signs_2_*` (9 cards);
   spoken numbers ("about fifteen hundred" = 1500; NATO letters -> initials).
6. **Form vs ground truth mismatch:** route dropdown offers IM, IV, PO, PR, SL, SQ, but ground truth uses OTFC (10),
   IO (4), IN (1). Write them as free text (the golden cards do).

## Normalisation rules (match the ground truth's format)

- Names `"Last, First"`; date `DD-MMM-YY` (e.g. `03-NOV-26`); times 4 digits (`0715`).
- Pulse `"<rate> <location>"` (e.g. `128 radial`) or just the rate if location not said.
- AVPU and pain use the PDF dropdown labels, e.g. `A - Alert`, `V - Verbal`, `P - Pain`, `U - Unresp`;
  pain `5 Very Distress`, `7 Very Intense`, `8 Horrible`, `9 Excruciating`. Read the full option lists from the PDF.
- Evac: Cat A / T1 / urgent -> `evac_urgent`. Doses with a space: `800 mcg`, `2 g`, `1 unit`, `1 L`.
- Battle roster = initials + last four (e.g. `JS4417`), only when spoken as such.

## Plan

All eight build steps are done (speech choice, split, extraction, validation, injury boxes, runner, scoring,
docs). Next steps and known limits: `docs/ARCHITECTURE.md` "Known limits and next steps". Before changing anything:
`make test`; after: `make eval` must still give held-out 93.8% unless the change is meant to move it.

## Working rules

- Show data, then let Rasal decide at decision points (model choice, scope cuts). Short, clear updates.
- Simple beats clever: fixed pipeline, no agent loops, no frameworks, no UI until the core is scored.
- Safety first: a blank field + flag beats a confident wrong value.
- Never print or commit the API key. The GitHub repo is public (Rasal's decision, to share with reviewers), so
  scan history for secrets before every push.
- **Spend:** The provided OpenRouter key is only for pipeline inference (speech-to-text, extraction), run at the
  end on the cheapest model that holds accuracy (chosen: `google/gemini-3.8-flash`, see ADR-05). No Opus or premium
  models on it. Development uses our own Claude Code. Tune offline against cached replies in `out/raw/`.
- Docs and README: plain, warm, human tone; no em dashes.
- Commit after each working step with a clear message.
