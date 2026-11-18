"""One command: python3 -m tccc

Rebuilds the 50 cards from the cached results if anything is missing (no API key or calls needed), then opens the
app in the browser: every casualty, its card and PDF, what to ask or check, and the benchmark.
"""
import sys
import threading
import webbrowser

from .pipeline import LLM_MODEL
from .run import ROOT

PORT = 8000


def main():
    try:
        import uvicorn
    except ImportError:
        sys.exit("Missing packages. Run: python3 -m pip install -r requirements.txt")
    cards = ROOT / "out" / LLM_MODEL.replace("/", "__") / "all" / "cards"
    if len(list(cards.glob("*.pdf"))) < 50:
        print("Building the 50 cards from cached results (no API calls)...")
        from . import run
        sys.argv = ["run", LLM_MODEL, "--split", "all", "--pdf"]
        run.main()
    print(f"Opening http://localhost:{PORT}  (Ctrl+C to stop)")
    threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
    uvicorn.run("tccc.app:app", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
