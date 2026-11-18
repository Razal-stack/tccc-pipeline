"""Paths and the chosen models, in one place. Each choice is explained in docs/DECISIONS.md."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "out"
TRANSCRIPTS = ROOT / "transcripts"


def slug(model):
    """'google/gemini-3.8-flash' -> 'google__gemini-3.8-flash' (folder names under out/ and transcripts/)."""
    return model.replace("/", "__")


STT_MODEL = "elevenlabs/scribe-v2-medical"  # best on radio, noise and two speakers
SECOND_MODEL = "qwen/qwen3.8-omni-flash"    # second listen: holds values the first misses; disagreements get flagged
LLM_MODEL = "google/gemini-3.8-flash"       # best held-out F1, fewest made-up values
FALLBACK_MODEL = "openai/gpt-6.1-terra"     # tied on accuracy; used only if the card model errors

PRIMARY_TRANSCRIPTS = TRANSCRIPTS / f"{slug(STT_MODEL)}+keyterms"
SECOND = os.environ.get("TCCC_SECOND", slug(SECOND_MODEL))  # cached second-listen folder ("" = off)
