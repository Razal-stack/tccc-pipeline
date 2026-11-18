"""Paths and the chosen models, in one place. Each choice is explained in docs/DECISIONS.md."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "out"
TRANSCRIPTS = ROOT / "transcripts"
ENV_FILES = (ROOT / ".env", ROOT.parent / ".env", ROOT.parent / "challenge" / ".env")  # first wins


def setting(name, default=None):
    """Environment variable first, then the first .env file that sets it (an empty value there counts as unset)."""
    if name in os.environ:
        return os.environ[name]
    for env in ENV_FILES:
        if env.exists():
            for line in env.read_text().splitlines():
                k, _, v = line.partition("=")
                v = v.split(" #")[0].strip().strip('"').strip("'")
                if k.strip() == name and v:
                    return v
    return default


def slug(model):
    """'google/gemini-3.8-flash' -> 'google__gemini-3.8-flash' (folder names under out/ and transcripts/)."""
    return model.replace("/", "__")


STT_MODEL = "elevenlabs/scribe-v2-medical"  # best on radio, noise and two speakers
SECOND_MODEL = "qwen/qwen3.8-omni-flash"    # second listen: holds values the first misses; disagreements get flagged
LLM_MODEL = "google/gemini-3.8-flash"       # best held-out F1, fewest made-up values
FALLBACK_MODEL = "openai/gpt-6.1-terra"     # tied on accuracy; used only if the card model errors

PRIMARY_TRANSCRIPTS = TRANSCRIPTS / f"{slug(STT_MODEL)}+keyterms"
SECOND = setting("TCCC_SECOND", slug(SECOND_MODEL))  # second listen on; cached folder for evals ("" env var = off)
BUDGET = float(setting("TCCC_BUDGET_USD", "7"))  # hard cap on the key's total usage, checked before paid calls
