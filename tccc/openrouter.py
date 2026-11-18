"""OpenRouter access: the API key, one HTTP call, and a hard spend cap checked against the key's real usage.

    python3 -m tccc.openrouter      # check the key works and show spend against the cap (free; never prints the key)
"""
import json
import sys
import urllib.error
import urllib.request

from .config import BUDGET, setting

API = "https://openrouter.ai/api/v1"
NO_KEY = ("No OpenRouter key found. To run live, copy .env.example to .env in the repo folder and set "
          "OPENROUTER_API_KEY=sk-or-..., or export OPENROUTER_API_KEY in your shell. "
          "Looking at the 50 cached cards needs no key: make app.")


def load_key():
    """Environment variable, then the repo's .env, then ../.env. Exits with a plain message if none is set."""
    key = setting("OPENROUTER_API_KEY")
    if not key:
        sys.exit(NO_KEY)
    return key


def call(path, key, body=None, timeout=180):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def guard_budget(key):
    """Refuse to start paid calls once the key's real usage reaches the cap."""
    used = call("/key", key)["data"]["usage"]
    if used >= BUDGET:
        sys.exit(f"budget cap reached: ${used:.2f} used of ${BUDGET:.2f} (set TCCC_BUDGET_USD to change)")
    print(f"spend so far ${used:.2f} of ${BUDGET:.2f} cap")


def check():
    """Key info only (a free call): does the key work, how much is used, how much room is left under the cap."""
    key = load_key()
    try:
        d = call("/key", key)["data"]
    except urllib.error.HTTPError as e:
        sys.exit(f"The key was rejected by OpenRouter (HTTP {e.code}). Check OPENROUTER_API_KEY in .env.")
    limit = d.get("limit")
    print("Key works.")
    print(f"Used so far: ${d['usage']:.2f}" + (f" of the key's ${limit:.2f} limit" if limit else ""))
    print(f"Spend cap for this project: ${BUDGET:.2f} (TCCC_BUDGET_USD); room left: ${max(BUDGET - d['usage'], 0):.2f}")
    print("A live card costs about 1.3 cents; all 50 about $0.65.")


if __name__ == "__main__":
    check()
