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

## What's already built and verified

| Module | Status |
|---|---|
| `tccc/score.py` | Done. Per field: correct / wrong / invented / missed / blank_ok. Headline = F1 on filled fields; also precision, invented values per card, safety-critical subset, per-group table, injury-box F1, naive accuracy vs empty-card baseline. Verified: ground truth vs itself = 100%; empty card = 0% F1, 84.5% naive. |
| `tccc/fill_pdf.py` | Done. `fill(card, out.pdf)` and `read_back(pdf)`. Checkboxes on-state is `/1`. Removes XFA, sets NeedAppearances. Verified: all 50 golden cards fill -> read back -> rescore with zero errors, and render correctly. |
| `tccc/textnorm.py` | Spoken numbers -> digits; `categorized_recall()` checks whether ground-truth values appear in a transcript. |
| `tccc/stt_bakeoff.py` | Speech-to-text benchmark via OpenRouter `/api/v1/audio/transcriptions`. 21 recordings across conditions (radio, heavy noise, two speakers, corrections, clean). Current flagship models only. Reports % of ground-truth values found by category (vitals, times, doses, ids, names, drugs/kit), cost per audio hour, median seconds per recording. Caches transcripts in `transcripts/<model>/`. |
| `transcripts/local__parakeet/` | Offline baseline (Parakeet, CPU, no network): 74% of values found overall; radio 65%, heavy noise 61%, two speakers 43%, clean 89%. |

Commands:
```bash
python3 -m tccc.stt_bakeoff --list                 # transcription models this key can use, with prices
python3 -m tccc.stt_bakeoff                        # benchmark, prints two tables
python3 -m tccc.stt_bakeoff --models <id> --all    # chosen model on all 50 recordings
python3 -m tccc.score <predictions_dir>            # score cards (one JSON per recording, ground-truth shape)
```

OpenRouter transcription request: `{"model", "input_audio": {"data": <base64>, "format": "wav"}, "language": "en",
"temperature": 0}`; response `{"text", "usage": {"seconds", "cost"}}`. No top-level prompt field; vocabulary hints
only via provider options (e.g. `provider.options.groq.prompt`).

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

## Plan (one step at a time; Rasal decides at each decision point)

1. **Speech-to-text choice.** Run `stt_bakeoff`, show Rasal both tables, he picks the model (best accuracy on the
   hard conditions at a sensible cost). Then transcribe all 50 with it.
2. **Dev / held-out split.** 25 / 25, fixed and written down (e.g. alternate files in sorted order). Tune prompts on
   dev only. Report held-out first, then all 50.
3. **Extraction** (`tccc/extract.py`): one OpenRouter chat-completions call per transcript, temperature 0, strict
   JSON schema in the ground-truth shape plus `evidence` (exact transcript words) per filled field and `flags`.
   Prompt carries the rules above. Compare two strong models on dev; pick by the scorer.
4. **Validation in code** (`tccc/validate.py`): formats, ranges (SpO2 50-100, systolic > diastolic, plausible
   pulse/resp), dropdown snapping, evidence must appear in the transcript or the value is dropped and flagged,
   derived checkboxes (`tq_extremity`).
5. **Injury boxes:** map the injury locations to the 163 box names in `field_map.json` (lookup, not free choice).
6. **Pipeline runner** (`tccc/run.py`): recording -> transcript -> card JSON -> validate -> PDF. Outputs
   `out/predictions/*.json`, `out/cards/*.pdf`, `out/review/*.md` (flagged fields for a medic to check).
7. **Score** with `tccc.score`, break down by group and condition, attribute each error to transcription (true value
   not in transcript) or extraction (it was there).
8. **README for a founder** + `AI_LOG.md` (what was delegated to AI tools, what was reviewed or rewritten, where we
   pushed back, with concrete examples).

## Working rules

- Show data, then let Rasal decide at decision points (model choice, scope cuts). Short, clear updates.
- Simple beats clever: fixed pipeline, no agent loops, no frameworks, no UI until the core is scored.
- Safety first: a blank field + flag beats a confident wrong value.
- Never print or commit the API key. Repo stays private.
- **Spend:** The provided OpenRouter key is only for pipeline inference (speech-to-text, extraction), run at the
  end on the cheapest model that holds accuracy (`openai/gpt-5.6-luna` preferred). No Opus or premium models on
  it. Development uses our own Claude Code. Tune offline against cached replies in `out/raw/`.
- Docs and README: plain, warm, human tone; no em dashes.
- Commit after each working step with a clear message.
