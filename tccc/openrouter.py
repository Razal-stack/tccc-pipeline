"""OpenRouter access: the API key, one HTTP call, and a hard spend cap checked against the key's real usage."""
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://openrouter.ai/api/v1"


def load_key():
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"]
    for env in (ROOT / ".env", ROOT.parent / ".env", ROOT.parent / "challenge" / ".env", Path.cwd() / ".env"):
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("OPENROUTER_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("OPENROUTER_API_KEY not found: set it or put it in .env")


def call(path, key, body=None, timeout=180):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


BUDGET = float(os.environ.get("TCCC_BUDGET_USD", "7"))  # hard cap on total spend for this key (key limit is $10)


def guard_budget(key):
    """Refuse to start paid calls once the key's real usage reaches the cap."""
    used = call("/key", key)["data"]["usage"]
    if used >= BUDGET:
        sys.exit(f"budget cap reached: ${used:.2f} used of ${BUDGET:.2f} (set TCCC_BUDGET_USD to change)")
    print(f"spend so far ${used:.2f} of ${BUDGET:.2f} cap")
