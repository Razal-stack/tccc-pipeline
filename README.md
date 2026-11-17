# TCCC card pipeline (work in progress)

Turns recorded casualty handovers into filled TCCC cards (DD Form 1380), and measures how accurate they are.

## Status

| Step | State |
|---|---|
| Scorer (`tccc/score.py`) | Done. Ground truth scores 100% against itself; an empty card scores 0% F1 / 84.5% naive accuracy |
| PDF filler (`tccc/fill_pdf.py`) | Done. All 50 golden cards round-trip (fill, read back, rescore) with zero errors |
| Speech-to-text comparison (`tccc/stt_bakeoff.py`) | Ready to run on a machine that can reach OpenRouter |
| Extraction (transcript to card) | Next |

## Setup

```bash
cd tccc-pipeline
python3 -m pip install -r requirements.txt
```

The scripts find `OPENROUTER_API_KEY` in your environment or in the `.env` one folder up (the task folder), and the
recordings in `../recordings`.

## Run the speech-to-text comparison

```bash
python3 -m tccc.stt_bakeoff --list      # what transcription models this key can use
python3 -m tccc.stt_bakeoff             # current flagship models x 21-recording benchmark (radio, noise, two speakers, corrections, clean)
python3 -m tccc.stt_bakeoff --models openai/gpt-transcribe deepgram/nova-3 --all   # chosen models, all 50
```

Transcripts land in `transcripts/<model>/`. Re-runs only fetch what's missing. `local__parakeet` is an offline
baseline (Parakeet on CPU, no network): 74% of ground-truth values found on the benchmark set (65% radio, 61% heavy noise, 43% two speakers, 89% clean).

## Score a set of predicted cards

```bash
python3 -m tccc.score predictions/      # one JSON per recording, same shape as output-true-values.json
```
