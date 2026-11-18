# Experiments

Not part of the pipeline. Each script backs a claim on the Benchmark page or in `docs/DECISIONS.md`.

- `stt_bakeoff.py` (paid, `make bakeoff`): the 19-model speech-to-text comparison behind the choice of Scribe and the
  second listener. Writes `transcripts/<model>/` and `transcripts/_bakeoff.csv`.
- `denoise.py` (local, needs torch): the denoiser test behind "send raw audio" (ADR-02).
- `relisten.py` (free, `make relisten`): replays cached transcripts as a third listener (ADR-16).
