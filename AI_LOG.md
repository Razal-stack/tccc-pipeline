# How I used AI tools on this

## Summary

I used Claude Code heavily, and that is why this moved fast. When my Claude Code limit ran out near the end, I
switched to Cursor for the final streamlining. The split was simple: I made the decisions, and the AI did a lot of
the typing, the research legwork and the parallel runs. I checked everything it produced against real outputs and
the answer key before I accepted it.

Development ran on my own subscriptions. The provided OpenRouter key was used only for the pipeline's own inference
(speech-to-text and card reading), under a hard spending cap.

## What I did myself

These are the inputs and decisions that shaped the pipeline.

- **Listened to all 50 recordings first.** Before any code, I played them all and wrote down what would be hard:
  radio crackle, corrections ("six fifteen, correction six fifty"), retractions ("ignore that, that's the other
  casualty"), radio read-backs, a vital given under the wrong name ("pulse 28, sorry that's resps"), numbers that
  break first, and NATO letters spoken for initials. That list became the checklist the whole project was tested
  against.
- **Explored OpenRouter by hand.** I tried several speech and language models myself, uploaded a few audio files,
  looked at what came back, and iterated before deciding what to automate.
- **Moved from a few hard cases to all 50.** I started with small scripts on the hard recordings and a handful of
  models. Then I realised a few hard cases are not enough to choose a model fairly. I asked for every candidate to
  be benchmarked across all 50 recordings, with a fixed dev / held-out split made before any tuning, so the choice
  is measured and honest.
- **Model research and the final choices.** I picked the speech model (ElevenLabs Scribe v2 Medical with key
  terms), the second listener (Qwen 3.8 Omni Flash) and the reader (Gemini 3.8 Flash), from the benchmark numbers
  and cost, not from reputation.
- **Orchestration and architecture.** A fixed pipeline, not an agent loop. Two independent listeners, and when
  they disagree the value is flagged, not guessed. The reader quotes the exact words behind every value it fills,
  and leaves a field blank rather than guess. The real loop is the human one: the medic asks the sender, re-listens
  and signs.
- **How evaluation works.** Score only the fields that were filled (an empty card already scores 84.5% on naive
  accuracy, so that number means nothing). Report held-out first. Tag every error as hearing or reading, so we know
  which step to fix.
- **What the medic sees.** I decided what to ask the sender, what to check, and what the frontend should show
  (urgent casualties first, the card beside the PDF, the answer key beside the card).
- **Spend.** Kept it on cheap models and cached every reply so nothing is paid for twice.

## What I used AI for

- **Claude Code wrote the functional code from my spec** (the scorer, PDF filler, speech-to-text benchmark,
  extraction, validation, runner, web app), ran the evals, and spun up several worker agents in parallel for the
  bake-offs, the large benchmarks, the PDF filling and the frontend. I reviewed each piece against real outputs
  before moving on.
- **A separate worker agent built the body-diagram mapper.** My brief: build it from the 25 tuning recordings only,
  report held-out honestly, and list anything odd in the ground truth. It came back at 94% held-out and pointed
  out that the answer key swaps left and right on two cards. I kept its mapper and did not "fix" the held-out
  misses, because that would be tuning on the test set.
- **Agents for research legwork:** which speech and language models were worth testing, TCCC form conventions
  (dropdown labels, route options), and which denoisers exist.
- **Cursor, with its agents, for the final streamlining:** reviewing the code, refactoring (paths and chosen models
  into `tccc/config.py`, experiments into `tccc/experiments/`), adding unit and golden tests, the one-command run,
  scripts and docs.

## How I reviewed and pushed back

I read the cards against the answer key, checked outputs rather than trusting that the code was right, and
questioned claims that sounded good.

- **Claims I questioned.**
  - The "Time it saves" estimate assumed a 5 to 8 minute manual card. I challenged that as not measured. It was
    reworded as a planning assumption, widened by hand to 5 to 12 minutes, with what is excluded and how to measure
    it stated.
  - I asked for the denoisers to be named, not just called "denoisers" (four were tested).
  - I asked for the benchmark groups and the "25 unseen recordings" to be explained clearly: how the split was
    made, which files are in it, and what the grey bars mean.
- **Model choices were driven by data, not reputation.** The first speech benchmark shortlist was full of older
  models (GPT-4o transcribe, Whisper). I cut it to the current flagship from each vendor and dropped the rest to
  save money. For extraction I dropped Anthropic models from the final comparison once a cheaper model matched
  them: Gemini 3.8 Flash beat Opus 5.5 at a sixth of the cost.
- **Spending.** An early Opus comparison run cost $0.95 before I set the rule. After that: no premium models on the
  client's key, every reply cached, and a budget guard that checks the key's real usage before any paid call.
- **Ideas I proposed that the data rejected.** I asked about a verifier model, a multi-model vote, audio clean-up
  and a vision model for the PDF. Each was tested cheaply first:
  - verifier or vote: at most +0.4 points, because both models make the same mistakes;
  - noise reduction: made transcription worse (77 numbers caught raw, 69 denoised, 46 radio-filtered);
  - vision model: not needed, the body diagram is named tick boxes filled by code.

  What the data did support, and what we kept: speech-to-text key terms (drug and kit words 90% to 97%) and
  targeted prompt rules (body-diagram accuracy on the tuning set 87% to 97%).
- **Assumptions the benchmarks overturned.** Denoising (which seemed obviously useful) made noisy audio worse, and
  GPT-6.1 Terra (best value on the tuning set) fell behind Gemini on the locked-away set. The held-out split is
  what caught that.
- **Statistics before claims.** I added 95% intervals by resampling cards. They showed the top six card models were
  tied, so the choice became cost and safety, and they confirmed the second listen as a real gain (+0.2 to +2.8).

## Bugs the review caught, by checking real outputs

- **"BP 100/64" read as 164.** The spoken-number helper treated "100 64" like "one hundred sixty-four". It was
  silently dropping correct blood pressures and under-crediting some speech models in the benchmark. Found by
  reading why a correct value had been flagged.
- **Blank text on the PDF.** Every automated check passed (the PDF read back perfectly), but when I rendered a card
  as an image, the text fields were empty in macOS Preview: only the ticks showed. The filler relied on the viewer
  to draw text, which Preview and phone viewers don't do. Fixed by drawing the text into the PDF, matching how the
  golden cards do it.
- **Evidence check too strict.** "last 42771" (speech-to-text merging "last four 2771") failed the word-by-word
  check. Loosened to also accept the digits found inside the transcript.
- **Error blame wrong for short words.** "IV" was counted as present in a transcript because two-letter words were
  skipped. Fixed to match whole words.
- **Models that "failed" for the wrong reason.** Deepgram and Meta only failed because they reject 48 kHz or large
  files. Resending at 16 kHz fixed it, and Deepgram then got a fair (low) score.
- **Blank cards that were really budget refusals.** Credit was reserved for every request in flight. With jobs in
  parallel and no output limit on reasoning models, requests were refused and showed up as blank cards (scores of
  77% that were really 92%). Fixed with output limits, one job at a time, and waiting before retries.
- **Report crash hiding scores.** The report crashed when a model made up zero values (a missing counter), hiding
  two models' scores.
- **Evidence check dropped correct values** when a model returned a value without its quote. It now checks the
  value's own words and digits against the transcript.
- **Times rejected as blood pressure.** Times written "10/12" were rejected after an earlier fix taught the checker
  that "/" means blood pressure.

## Honesty notes

- The unit-name list in the prompt is general knowledge, but I wrote it after seeing units in the answer key, so
  the held-out score on that one field is slightly flattered.
- Every prompt rule was written from errors on the 25 tuning recordings; the held-out 25 were run once at the end.
- The answer key has oddities (for example, left and right swapped on two cards). I noted them and did not tune to
  them.

## Where AI should and should not be used in the product itself

- **AI listens and reads.** Two independent listeners hear the recording, and one reader fills only what was said,
  with the words it came from.
- **Fixed rules check.** Code, not AI, verifies the evidence, formats, ranges and dropdowns, fills the PDF and reads
  it back. Anything that fails becomes a blank plus a flag.
- **The medic decides and signs.** The pipeline never guesses to fill a gap. It tells the medic what to ask the
  sender and what to check, and nothing is attached to a casualty unchecked.
