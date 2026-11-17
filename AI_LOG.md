# How I used AI coding tools

I worked with Claude Code (in the terminal) as the main pair, and gave it one self-contained job as a separate
worker agent. Development ran on my own Claude subscription; The provided OpenRouter key was used only for the
pipeline's own inference (speech-to-text and card extraction), under a hard spending cap.

## What I delegated

- **Benchmark and pipeline scaffolding.** Scorer, PDF filler, speech-to-text benchmark, extraction, validation,
  runner, web app. I set the design (fixed chain, blank over guess, evidence for every value, dev / held-out split)
  and reviewed each piece against real outputs before moving on.
- **The body-diagram mapper, to a separate worker agent.** Brief: build it from the 25 tuning recordings only,
  report held-out honestly, list anything odd in the ground truth. It came back at 94% held-out and pointed out
  that the answer key swaps left and right on two cards. I kept its mapper and did not "fix" the held-out misses,
  because that would have been tuning on the test set.

## What I reviewed, and where I pushed back

- **Model choices were driven by data, not reputation.** The first speech benchmark shortlist was full of older
  models (GPT-4o transcribe, Whisper). I cut it to the current flagship from each vendor and dropped the rest to
  save money. For extraction I dropped Anthropic models from the final comparison once a cheaper model matched
  them: Gemini 3.8 Flash beat Opus 5.5 at a sixth of the cost.
- **Spending.** An early Opus comparison run cost $0.95 before I set the rule. After that: no premium models on the
  client's key, every reply cached so nothing is paid for twice, and a budget guard that checks the key's real
  usage before any paid call.
- **Ideas I proposed that the data rejected.** I asked about a verifier model, a multi-model vote, audio
  clean-up and a vision model for the PDF. Each was tested cheaply first:
  - verifier or vote: at most +0.4 points, because both models make the same mistakes;
  - noise reduction: made transcription worse (77 numbers caught raw, 69 denoised, 46 radio-filtered);
  - vision model: not needed, the body diagram is named tick boxes filled by code.
  What the data did support, and what we kept: speech-to-text key terms (drug and kit words 90% to 97%) and
  targeted prompt rules (body-diagram accuracy on the tuning set 87% to 97%).

## Bugs caught by checking real outputs, not by trusting the code

- **"BP 100/64" read as 164.** The spoken-number helper treated "100 64" like "one hundred sixty-four". It was
  silently dropping correct blood pressures and under-crediting some speech models in the benchmark. Found by
  reading why a correct value had been flagged.
- **Blank text on the PDF.** Every automated check passed (the PDF read back perfectly), but when I rendered a card
  as an image, the text fields were empty in macOS Preview: only the ticks showed. The filler relied on the viewer
  to draw text, which Preview and phone viewers don't do. Fixed by drawing the text into the PDF, matching how the
  golden cards do it.
- **Evidence check too strict.** "last 42771" (speech-to-text merging "last four 2771") failed the
  word-by-word check. Loosened to also accept the digits found inside the transcript.
- **Error blame wrong for short words.** "IV" was counted as present in a transcript because two-letter words were
  skipped. Fixed to match whole words.

## Honesty notes

- The unit-name list in the prompt is general knowledge, but I wrote it after seeing units in the answer key, so
  the held-out score on that one field is slightly flattered.
- Every prompt rule was written from errors on the 25 tuning recordings; the held-out 25 were run once at the end.
