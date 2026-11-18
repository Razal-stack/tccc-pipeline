"""Experiment: clean the audio with a neural denoiser before speech-to-text. Runs locally, free.

    python3 -m tccc.denoise deepfilternet      # writes out/denoised/deepfilternet/*.wav
    python3 -m tccc.denoise demucs             # Meta's denoiser (DNS64)
    python3 -m tccc.stt_bakeoff --all --keyterms --models elevenlabs/scribe-v2-medical \
        --recordings out/denoised/deepfilternet --tag deepfilternet     # transcribe and compare with raw audio
"""
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECORDINGS = ROOT.parent / "recordings"


def _read(path):
    """wav -> (float tensor [1, samples], sample rate), using the standard library (no audio backend needed)."""
    import numpy as np
    import torch
    with wave.open(str(path)) as w:
        rate, pcm = w.getframerate(), np.frombuffer(w.readframes(w.getnframes()), np.int16)
    return torch.from_numpy(pcm.astype(np.float32) / 32768)[None], rate


def _write(path, audio, rate):
    import numpy as np
    pcm = (audio.squeeze().clamp(-1, 1).numpy() * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(rate), w.writeframes(pcm.tobytes())


def deepfilternet(src: Path, dst: Path):
    """DeepFilterNet3: neural speech enhancement at 48 kHz (our recordings' native rate)."""
    from df.enhance import enhance, init_df
    if not hasattr(deepfilternet, "m"):
        deepfilternet.m = init_df()[:2]
    model, state = deepfilternet.m
    audio, rate = _read(src)
    _write(dst, enhance(model, state, audio), rate)


def demucs(src: Path, dst: Path):
    """Meta's denoiser (DNS64, Demucs architecture) at 16 kHz."""
    import torch
    from denoiser import pretrained
    from torchaudio.functional import resample
    if not hasattr(demucs, "m"):
        demucs.m = pretrained.dns64().eval()
    audio, rate = _read(src)
    with torch.no_grad():
        _write(dst, demucs.m(resample(audio, rate, 16000)[None])[0], 16000)


if __name__ == "__main__":
    method = sys.argv[1]
    out = ROOT / "out" / "denoised" / method
    out.mkdir(parents=True, exist_ok=True)
    for src in sorted(RECORDINGS.glob("*.wav")):
        if not (out / src.name).exists():
            globals()[method](src, out / src.name)
            print(src.name, flush=True)
