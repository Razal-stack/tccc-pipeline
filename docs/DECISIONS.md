# Decision record: why the TCCC pipeline looks the way it does

This is the "why" behind `docs/ARCHITECTURE.md` (the "what"). Each decision lists context, options, the choice, the
measured evidence, the cost of the choice, and when to reopen it. Read the competence section, then jump to any ADR.

Numbers come from `README.md`, `docs/archive/experiment-log.md`, `AI_LOG.md`, `out/runs.jsonl`, the bake-off table
and the code. Where sources disagreed, the newer or more specific figure is used (see "Notes on sources" at the end).

## Core competence of this architecture

A casualty card is filled from noisy radio audio, and the next person to read it may act on it. The shape of the
pipeline follows from that.

- **Traceability.** Every value the reader returns comes with the exact words it was taken from. Code checks that
  those words are in the transcript and that the digits in the value were said. Any value can be traced to speech.
- **Safety by abstaining.** A blank box with a flag beats a confident guess. That is why precision (97.6% held-out)
  is watched as closely as accuracy, and why made-up values are counted on their own (2 in 25 cards).
- **Errors isolated per stage, and measurable.** `tccc/run.py` tags every mistake as `transcription` (the true value
  never reached the transcript), `extraction` (it was there, the model missed it), `validation` (the model had it,
  a code check dropped it) or `invented` (written where the truth is blank). We know which step to fix.
- **Cheap, repeatable reruns.** Temperature 0, replies cached on disk, checks and scorer in plain code. Changing a
  validation rule and re-scoring costs $0 and gives the same answer every time.
- **Human in the loop by design.** The system drafts. The medic gets an "Ask the sender" list and a "Check these"
  list, reviews every card and signs it.

Result: held-out F1 93.8% (precision 97.6%, safety-critical fields 96.8%, 2 invented values in 25 cards); all 50
recordings 94.7%.

ADR index: 01 fixed pipeline, 02 raw whole audio, 03 main listener, 04 second listener, 05 reader model, 06 one call
with evidence, 07 validation in code, 08 blank over guess, 09 injury lookup, 10 PDF, 11 cache and spend cap, 12 split
and metric, 13 app, 14 gateway, 15 human in the loop, 16 targeted re-listen (proposed).

---

## ADR-01: Fixed pipeline, not an agent loop

- **Status:** Accepted
- **Context.** Each card is one bounded job: one recording in, one card out. We were tempted by a verifier model, a
  vote, or extra medical-sense rules to catch mistakes.
- **Options considered.** (1) A fixed chain of small steps, one module each. (2) An agent that re-reads, re-listens
  and loops until satisfied. (3) A fixed chain plus a second model as verifier or majority vote.
- **Decision.** A fixed chain. Agents helped build it (a worker agent wrote the body-diagram mapper), not run it.
- **Evidence.**
  - Gemini 3.8 Flash and Opus 5.5 disagreed on only 14 of 3,425 fields on dev (99.6% agreement). A perfect referee
    would lift F1 from 93.3% to 93.7%; a 3-model majority vote gives 93.5%.
  - Extra medical rules (drug doses, timings such as a tourniquet applied before the injury) caught 0 of the 25
    remaining errors. Those are believable misheard values, not impossible ones.
  - Errors come from hearing, not reading. A second reader cannot fix a number that is wrong in the transcript.
- **Trade-offs.** No self-correction: a wrong transcript stays wrong unless a second listener or the medic catches it.
  A loop that re-asks an LLM adds no information the audio did not contain.
- **Revisit when.** Recordings get long or multi-casualty, or a step needs real tool use (such as reading an ID tag).

## ADR-02: Whole raw recording to speech-to-text, no VAD and no denoiser

- **Status:** Accepted
- **Context.** The audio has radio static, gunfire and sometimes two voices. Trimming silence or cleaning noise looked
  like obvious wins.
- **Options considered.** (1) Send each whole recording as it is. (2) Chop with voice-activity detection (VAD).
  (3) Denoise first: spectral gating, radio band-pass, DeepFilterNet3, Meta Denoiser (Demucs).
- **Decision.** Whole raw recording. No VAD, no denoiser.
- **Evidence.**
  - VAD dropped most of the radio speech: on oqx it kept 6 s of 38 s.
  - Scribe plus keyterms on all 50: raw 92.9% (hard audio 86.0%), DeepFilterNet3 91.0% (78.5%), Demucs 91.7%
    (80.2%). Denoisers helped 3 to 5 recordings and hurt 8. The classic filters were worse still (local test on
    9 hard files: raw 77 of 108 numbers, spectral denoise 69, band-pass 46).
  - Modern speech models are trained on noise; denoisers remove cues they use and clip parts of words.
- **Trade-offs.** We send full files, and some models reject large ones. Fallback: resend at 16 kHz mono (a third of
  the size, same words). That is how Deepgram Nova-3 got a fair, low score (62% hard, 71% overall).
- **Revisit when.** The speech model changes, or real field audio has noise unlike the synthetic radio noise.

## ADR-03: Scribe v2 Medical with keyterms as the main listener

- **Status:** Accepted
- **Context.** Transcription is the bottleneck, and numbers break first (call signs, doses, times).
- **Options considered.** 19 models on all 50 recordings: ElevenLabs, AssemblyAI, Deepgram, OpenAI, Google, Mistral,
  xAI, NVIDIA, Qwen, Meta, Fish Audio, a local model, and audio chat models.
- **Decision.** `elevenlabs/scribe-v2-medical`, given keyterms (TXA, IV, tourniquet, unit names).
- **Evidence.**
  - Share of answer-key values present in the transcript: Scribe v2 Medical with keyterms 93% overall, 86% on hard
    audio. Next: Qwen 3.8 Omni Flash 92% (83% hard), Fish Audio and AssemblyAI 91%.
  - Keyterms moved drug and kit words from 90% to 97%.
  - Local Parakeet 80%, Deepgram Nova-3 74%. Three chat models paraphrased instead of transcribing (below 45%).
- **Trade-offs.** One vendor is the main listener. Keyterms bias toward expected words, which helps drugs and kits but
  could favour a listed word over a rare real one.
- **Revisit when.** A new model beats it on the hard-audio column, or the vocabulary changes (other forces or drugs).
  The speech benchmark script makes a rerun cheap. First candidate: the bake-off table now lists Gemini 4 Argon at
  93.6% of values (87.6% on hard audio), slightly above Scribe's 92.9% (86.0%). Argon as the main listener was never
  tested end to end.

## ADR-04: A second independent listener; disagreement becomes a flag

- **Status:** Accepted
- **Context.** Even the best single listener misses values, mostly on noisy recordings. An early free check on cached
  transcripts found a second model recovered only 2 of 10 values Scribe missed, so the question was open.
- **Options considered.** (1) Scribe alone. (2) Scribe plus a second, different speech model; the reader sees both.
  (3) An audio-native LLM as the only listener.
- **Decision.** Add `qwen/qwen3.8-omni-flash`, listening to the same raw audio in parallel. The reader uses transcript
  A by default and B where A is garbled. If they disagree and the recording cannot tell which is right, the box stays
  blank and is flagged ("transcripts disagree: A says X, B says Y").
- **Evidence.**
  - It holds 21 of the 80 values Scribe misses.
  - Held-out F1 92.5% to 93.8%, gap interval +0.2 to +2.8 points (excludes zero: a real gain). Precision 95.8% to
    97.6%. Identity 85% to 89.5%. All 50: 94.0% to 94.7%.
  - Calibrated on all 50: values both listeners heard are 97.9% correct (753 values); single-listener values are 81.1%
    correct (37 values), about nine times the error rate.
  - Qwen 3.8 Omni Flash was best on IDs and costs about a fifth of the price; it adds about $0.03 for all 50.
  - Gemini 4 Argon was also tried as the second listen on dev: F1 95.0% with 12 made-up values, against 95.5% and 4
    for Qwen (`out/runs.jsonl`). A stronger listener that makes the reader invent more is the wrong trade.
- **Trade-offs.** Two listens per recording and a longer reader prompt. Both still miss what every model misses (the vdi
  radio recording, "Kaur" heard as "Carr"). Latency stays about 20 s because the listens run at once.
- **Revisit when.** Flagged disagreements overwhelm the medic, or a stronger second model appears. See ADR-16.

## ADR-05: Gemini 3.8 Flash as the reader, GPT-6.1 Terra as fallback

- **Status:** Accepted
- **Context.** The reader turns transcripts into card fields. Many models are good enough, so reputation should not
  decide it.
- **Options considered.** 14 models on the final prompt (OpenAI, Google, Qwen, GLM, DeepSeek, Mistral), the top three
  again on held-out. An earlier round included Anthropic (Opus 5.5 93.0%, Gemini 3.8 Flash 93.3% on dev, at a sixth of
  the cost).
- **Decision.** `google/gemini-3.8-flash`. If it errors, the live path retries once on `openai/gpt-6.1-terra`, so no card
  is lost to an API failure.
- **Evidence.**
  - On dev the top six are tied inside their 95% intervals: Gemini 4 Argon 95.5%, Gemini 3.8 Flash 95.3%, Gemini 4
    Hydrogen 95.3%, GPT-6.1 Terra 95.2%, DeepSeek V4.1 Flash 95.0%, GLM 5.3 94.6%.
  - Held-out made-up values broke the tie: Gemini 3.8 Flash 2, GPT-6.1 Terra 5, Gemini 4 Argon 9 (F1 92.5%, 91.8%,
    92.4%, single-listener transcripts).
  - Cost for 50 cards on one transcript: Gemini 3.8 Flash $0.34, Terra $0.18, so Terra is $0.16 cheaper. Two and a half
    times the invented values is not worth 16 cents on a casualty card. Qwen 4 Max scored well but made up 12.
- **Trade-offs.** Terra was the best value on dev and fell behind on held-out. The split did its job, but it is a sample of
  25. Not run for budget: Kimi, Grok 4.7, MiniMax, Mistral Medium, Nemotron Ultra.
- **Revisit when.** A larger synthetic test set exists (25-card gaps are inside the noise) or prices change enough to
  matter. Invented values stay the tie-break.

## ADR-06: One LLM call, evidence quotes, temperature 0, filled fields only

- **Status:** Accepted
- **Context.** The form has 138 fields; a typical card fills about 22 (5 to 36) and 45 fields are never used. We need
  structured output we can check.
- **Options considered.** (1) Return all 138 fields. (2) One call per field group. (3) One call returning only the
  fields said, each as `[value, "exact transcript words"]`, plus `notes` and `flags`.
- **Decision.** Option 3, temperature 0, JSON object output. The prompt (v5) carries the formats and the literal
  conventions of ADR-08.
- **Evidence.**
  - Only filled fields come back, so output tokens stay low: about $0.65 for all 50 cards (Scribe $0.15, second listen
    $0.03, Gemini $0.47), 1.3 cents a card.
  - The evidence quote is what makes ADR-07 possible. Without it there is nothing to check a value against.
  - Prompt history on dev (single listener): v2 93.3%, v3 94.3%, v3 with keyterm transcripts 94.5%, v4 95.4%, v5 95.3%.
- **Trade-offs.** The model decides which fields exist, so a forgotten field is silently blank (an `extraction` error in
  the report). Every prompt rule came from dev errors, and the unit-name list was written after seeing units in the answer
  key, so the held-out `unit` field is slightly flattered.
- **Revisit when.** The form changes, or a needed rule hurts held-out results. Then split calls by field group.

## ADR-07: Validation in deterministic code, no AI

- **Status:** Accepted
- **Context.** The reader can be confidently wrong. Rules that need no judgement should not be left to a model.
- **Options considered.** (1) Trust the model's JSON. (2) A second model verifies (rejected, ADR-01). (3) Check every
  value in plain code (`tccc/validate.py`).
- **Decision.** Plain code. A value that fails a check becomes blank and lands in "Check these" in words a medic can read.
- **What it checks.**
  - Format: times as 4 digits with valid hours and minutes, doses with a space and unit, routes from the allowed list,
    AVPU and pain snapped to the PDF dropdown labels.
  - Range: pulse 20 to 250, systolic 40 to 260, diastolic 20 to 160, resp rate 2 to 70, SpO2 50 to 100; systolic must
    exceed diastolic, otherwise both are blanked.
  - Evidence: at least 70% of the quoted words are in the transcript (or the quote matches once spaces are squashed), and
    every number in the value was said.
  - Derived: `tq_extremity` is ticked whenever a limb tourniquet type or time is filled.
- **Evidence.**
  - `validation` is its own error stage, so we see when a check removes a value the model had right.
  - Real outputs exposed three over-strict cases, each fixed and re-scored for free: "BP 100/64" read as 164, "last
    42771" (merged "last four 2771") failing the word check, and a time written "10/12" rejected after "/" was taught
    to mean blood pressure (held-out F1 92.4% to 92.5% from cached replies).
- **Trade-offs.** A check can drop a correct value. We accept that over a wrong value on a card. Ranges are wide on
  purpose: they catch typos, not clinical oddness.
- **Revisit when.** The `validation` error count grows, or the form adds fields with their own formats.

## ADR-08: Blank and flag over guess; literal ground-truth conventions

- **Status:** Accepted
- **Context.** The answer key is strictly literal. A sensible default that was not said counts as wrong, and on a real
  card could be dangerous.
- **Options considered.** (1) Let the model infer and complete (compose names, fill usual doses). (2) Fill only what was
  said, in the form's vocabulary, and flag what was partly heard.
- **Decision.** Option 2, written into the prompt and backed by ADR-07.
- **The conventions.**
  - Never compose or decompose IDs. 30 cards have name and last four but no battle roster; 10 have a roster but no name.
  - No clinical defaults: a fentanyl lozenge with no dose gives route OTFC and a blank dose.
  - A withheld drug is not a dose given ("fentanyl withheld, opioid allergy").
  - "Time found" goes in notes; `time` is the time of wounding only.
  - Partly heard means blank plus a note ("wound (detail not heard)", a pulse with no location).
  - Corrections win ("six fifteen, correction six fifty" is 0650); retractions ("ignore that, that's the other
    casualty") are not on this card.
- **Evidence.** Precision 97.6%, 2 invented values in 25 held-out cards, safety-critical fields 96.8%. Tourniquets, and
  drugs and fluids, are 100% each on held-out.
- **Trade-offs.** We give up recall for precision. Names are the weakest area (spelled the way they sound). We did not bend
  the system to a few answer-key slips (roo omits a TXA dose and oxygen that were spoken; two body-diagram entries swap
  left and right), so they count against us.
- **Revisit when.** The card's readers want proposed values shown as unconfirmed suggestions instead of blanks. That is a
  product decision, not a model one.

## ADR-09: Lookup table for the 163 injury boxes

- **Status:** Accepted
- **Context.** The body diagram has 163 named tick boxes. The reader writes injuries into notes as
  `Injuries: <location>: <description>; ...`. Something must turn "left forearm" into box names.
- **Options considered.** (1) Let the LLM pick box names. (2) A vision model on the PDF. (3) A deterministic lookup from
  location words to box templates (`tccc/injury.py`).
- **Decision.** The lookup: side (left, right or both) plus the first matching region keyword, expanded to box names.
  Unknown locations tick nothing.
- **Evidence.**
  - Output is always a subset of the 163 valid names, so a box can never be misnamed.
  - Body boxes F1: dev 97.0%, held-out 80.5%, all 50 89.0%. Dev rose from 87% to 97% with targeted prompt rules.
  - Conventions (which sub-boxes a "forearm" or "leg" fills) were read off dev only. A worker agent built it from the 25
    tuning recordings, reported held-out honestly, and flagged that the answer key swaps left and right on two cards.
    We kept its mapper and did not fix those misses, since that would be tuning on the test set.
- **Trade-offs.** The gap of about 16 points between dev and held-out shows the conventions are partly fitted to dev. The
  mirroring rule for hip and back copies what dev shows, which may be an answer-key quirk.
- **Revisit when.** More labelled cards exist to learn the conventions properly, or the form's box names change.

## ADR-10: PDF with drawn text appearances, XFA removed, read-back after every fill

- **Status:** Accepted
- **Context.** The blank card is a fillable AcroForm with named fields. Setting values passed every automated check, but
  in macOS Preview the text fields were empty and only the ticks showed.
- **Options considered.** (1) Set values and rely on the viewer (`NeedAppearances`). (2) Draw each text value into the
  field's appearance stream, as the golden cards do. (3) A vision model that reads the form and decides where to write.
- **Decision.** Option 2 (11 pt Helvetica), keep `NeedAppearances` on, delete the XFA layer (it would override AcroForm
  values in Acrobat), and read the PDF back after every fill.
- **Evidence.**
  - Preview and phone viewers ignore `NeedAppearances`. The bug was found by rendering a card as an image, not by
    read-back, so read-back alone is not a visual check.
  - Filling was verified on all 50 golden cards with zero errors before any model output was used; all 50 filled cards
    pass the schema and read-back checks. A mismatch becomes a "PDF:" flag on the review sheet.
  - No vision model: the fields are named, so filling is exact code, and accuracy is decided before the PDF.
- **Trade-offs.** Drawn text is limited to Latin-1 characters. Routes the dropdown lacks (OTFC, IO, IN) are written as free
  text, as the golden cards do.
- **Revisit when.** The form version changes, or a viewer we must support behaves differently.

## ADR-11: Caching and a hard spend cap

- **Status:** Accepted
- **Context.** The brief provided one OpenRouter key for pipeline inference only. A runaway loop or a repeated benchmark must
  not burn the budget.
- **Options considered.** (1) Trust ourselves. (2) Count spend in our own code. (3) Cache every reply, and check the key's
  real usage before any paid call.
- **Decision.** Option 3.
  - Cache: `out/raw/<model>/<hash>/<file>.json`, where the hash is the first 8 characters of a sha1 over the prompt text
    plus the transcript folder names. A new prompt or transcript set gives a new cache. A fully cached run needs no key.
  - Cap: `guard_budget` reads the key's real usage from `/key` and stops at `TCCC_BUDGET_USD` (default $7, key limit $10).
- **Evidence.**
  - Re-scoring and changing validation cost $0 (the "10/12" fix above).
  - An early Opus comparison cost $0.95 before the rule existed. After it: no premium models on the client key.
  - Total spend on the provided key is $4.52, under the cap (read from the key itself with `make check-key`).
  - A real bug: credit is reserved for every request in flight, so parallel jobs with no output limit on reasoning models
    were refused and showed up as blank cards (77% that was really 92%). Fixed with output limits and waiting retries.
- **Trade-offs.** The hash uses folder names, not transcript contents, so editing a transcript in place does not invalidate
  the cache. The cap is checked before a batch starts, not per request.
- **Revisit when.** The pipeline serves real traffic, where per-request limits, backoff and spend alerts matter.

## ADR-12: Fixed dev / held-out split; F1 on filled fields, not naive accuracy

- **Status:** Accepted
- **Context.** Most of a card is blank, so counting matching boxes misleads: a card that writes nothing scores about 85%.
  We also needed a score that tuning could not quietly inflate.
- **Options considered.** (1) Naive field accuracy on all 50. (2) F1 on fields where the truth or our card has something,
  tuned and scored on the same 50. (3) The same F1 with a fixed split chosen before tuning and intervals on comparisons.
- **Decision.** Option 3.
  - Split: sort the file names; even positions are dev (25), odd are held-out (25) (`SPLITS` in `tccc/extract.py`). All
    tuning on dev. Held-out run once, reported first, then all 50.
  - Each field is correct, wrong, invented (written, never said) or missed. F1 balances precision and recall.
  - 95% intervals by bootstrap: 2,000 resamples of cards, with a paired interval on the gap between two models.
- **Evidence.**
  - Held-out caught a wrong choice: GPT-6.1 Terra looked best on value on dev and fell behind.
  - Intervals showed the top six readers were tied, and confirmed the second listen as a real gain (+0.2 to +2.8).
  - Limits are written down: every prompt rule came from dev, the unit list slightly flatters one held-out field, and the
    answer key has a few slips we did not tune to.
- **Trade-offs.** 25 cards per half is small, so intervals are wide. Free-text notes are not scored. The all-50 number
  includes the tuning half and flatters a little.
- **Revisit when.** A larger synthetic set exists. Then use a fresh held-out set, not the current one again.

## ADR-13: Minimal FastAPI app, server-rendered HTML, no frontend framework

- **Status:** Accepted
- **Context.** The brief puts web UI, auth and deployment out of scope. A reviewer still needs to see a card beside its PDF,
  and a medic needs the to-do lists in one place.
- **Options considered.** (1) Command line and markdown only. (2) A frontend framework with its own build. (3) One small
  FastAPI file rendering HTML on the server.
- **Decision.** Option 3 (`tccc/app.py`): a dashboard with a status per card (Complete, Missing information, Needs
  checking), each card in MIST order beside the filled PDF, a benchmark page, a "how it works" page, and upload of a new
  recording. `make app` (or `python3 -m tccc`) opens it from cached results with no key.
- **Evidence.** The app counts "ask" and "check" items live from the cards, so the README's time estimate tracks the real
  review load (118 items across the 50 cards).
- **Trade-offs.** Not a product: no auth, no persistence beyond files, one big file that is fine to read but not to grow.
  The time-saved numbers are planning assumptions, not measurements.
- **Revisit when.** A real medic workflow is timed and the UI itself becomes the thing being evaluated.

## ADR-14: OpenRouter as the single gateway

- **Status:** Accepted
- **Context.** The benchmarks span many vendors, speech and text. Separate SDKs and keys would be most of the work.
- **Options considered.** (1) Each vendor's own SDK and key. (2) One gateway, one key, one HTTP helper
  (`tccc/openrouter.py`, plain `urllib`).
- **Decision.** OpenRouter.
- **Evidence.**
  - 19 speech models and 14 reader models were compared through the same code path.
  - Spend is measurable in one place, the key's `usage`, which also drives the cap in ADR-11.
- **Trade-offs.** Some vendor features lag or are missing (Deepgram Flux is not offered; Deepgram Nova-3 looked like it
  failed on 11 of 21 files, which was the size cap, fixed by the 16 kHz resend). A gateway is one more thing that can
  fail, hence the fallback reader in ADR-05.
- **Revisit when.** We pick one vendor for production (contracts, data handling, latency) or need a feature the gateway
  does not pass through.

## ADR-15: The human is the loop

- **Status:** Accepted
- **Context.** Even with two listeners and checks in code, some values are garbled, corrected or missing. The system cannot
  ask the casualty, but a person can ask the sender.
- **Options considered.** (1) Auto-fill everything and show a confidence number. (2) A review sheet per card with two lists,
  and the medic signs.
- **Decision.** Option 2. Each card gets:
  - **Ask the sender** (`missing_critical` in `tccc/validate.py`): casualty identity, evac category, tourniquet time or limb
    and type, drug dose, route or time, time of first observations. Never guessed, only asked for.
  - **Check these**: values dropped by a check, transcript disagreements, schema or PDF read-back problems.
  - Per-value confidence (did both listeners hear it), with transcripts and quoted words beside the card.
- **Evidence.** Both-heard values are 97.9% correct and single-listener values 81.1% (ADR-04), so the medic knows where to
  look first. The 50 cards hold 118 things to ask or check.
- **Trade-offs.** It relies on the medic's attention at a busy point, and some questions cannot be answered (a sender who has
  left); those stay flagged on the card. Review time (1 to 2 minutes a card, 0.5 to 1.5 per item) is an untimed assumption.
- **Revisit when.** A tabletop exercise with medics gives real timings, or voice prompts back to the sender are built.

## ADR-16: Targeted re-listen for uncertain values

- **Status:** Proposed, not built
- **Context.** ADR-04 turns disagreement into a blank and a flag. That is safe, but it throws away values a closer listen
  might settle. Single-listener values are 81.1% correct, so knowing which values are uncertain is real signal.
- **Options considered.** (1) Leave as is: disagreement is a flag. (2) An LLM that re-reads the transcript or re-asks the
  question: rejected, it adds no new information about the audio (ADR-01). (3) Re-transcribe only the time window around the
  uncertain value, with a third model or a constrained prompt (digits only, a closed list of drugs or units).
- **Decision (sketch).**
  - Trigger: a value on the card was heard by only one listener, or the two listeners disagree.
  - Action: a third speech model listens. Start with the whole recording (simple, about $0.19 for all 50 with Gemini 4
    Argon); move to just the disputed seconds once the first listener returns word timestamps.
  - Rule: a value the third listen confirms is marked "confirmed by 2 of 3" and leaves the medic's check list. A value
    only the third listen heard never goes on the card by itself; it goes to the medic as a suggestion ("a third listen
    heard 1422 for the left leg tourniquet time, please confirm"). So the invented-value risk does not rise.
  - Explicitly not an LLM re-asking loop. Every vote is a fresh acoustic listen, so a value is backed by audio and not by a
    model's second opinion.
- **Evidence (simulated offline, free).** `python3 -m tccc.experiments.relisten` replays cached bake-off transcripts as
  the third listener, on all 50 final cards. 37 values were heard by only one listener (81.1% right). With Gemini 4
  Argon as the third listener, 23 of them are confirmed and 96% of those are right (22 right, 1 wrong), so the check
  list for these values shrinks from 37 to 14. AssemblyAI confirms fewer (16, 94% right). For recall, at most 9 of the
  34 values both listeners lost appear in any third transcript (an upper bound, matched by digits), which would move
  all-50 recall from 92.1% to 92.9% at most. 33 of the 50 cards would trigger it. Full table in `docs/REVIEW.md`.
- **Trade-offs.** A third listener to pay for and wait on (it can run in parallel with the reader). One wrong value in
  the simulation would have been confirmed, so "confirmed" lowers priority on the check list; it does not hide the
  value. Windowed re-listening needs word timestamps and care at the window edges (ADR-02's lesson).
- **Revisit when.** Build it behind a flag next, and measure on held-out: check-list items removed, wrong values
  confirmed. The expected gain is review time, not headline F1.

---

## What would change these decisions

- **Offline or forward use.** A local speech model already captures 80% of values with no network. If a device must work
  offline, ADR-03 and ADR-04 change, and the fallback in ADR-05 matters more.
- **Longer recordings.** Today's run 7 to 61 seconds. Beyond a few minutes, files would be shrunk and then split at pauses,
  which reopens ADR-02.
- **A larger synthetic test set.** New handover scripts with known answers, voiced by text-to-speech with radio noise added.
  With hundreds of cards the ties in ADR-05 and the box gap in ADR-09 would resolve, and a fresh held-out set could be used.
- **Real timed medics.** The time-saved figures are assumptions. Real timings change what review load is acceptable, and
  could change ADR-08 (blank versus suggested values) and ADR-15.
- **Real audio.** The recordings are synthetic with simulated radio noise. Real speech, accents and equipment may move the
  denoiser and listener results.
- **A different form or force.** New fields, units or drug lists change the keyterms, prompt conventions and injury lookup.

## Notes on sources

- **Spend.** Older notes said $3.90 and then $4.24. The key's own usage, read on 18 Nov 2026, is $4.52; that is used.
- **Offline model.** The experiment log has an early "74% of values" for a local model and a later benchmark with local
  Parakeet at 80%. This record uses 80%.
- **Gemini 4 Argon as a listener.** The archived notes say 90%; the bake-off table (`transcripts/_bakeoff.csv`, the
  later source) says 93.6%. This record uses the table.
- **Held-out F1.** 92.5% is the single-listener result, 93.8% the final result with the second listen. Both are labelled.
- **Held-out body boxes.** 80.5% as in the architecture doc; the README rounds it to 81%.
- **Empty card.** `CLAUDE.md` says 84.5%, the README 85%. This record says about 85%.
