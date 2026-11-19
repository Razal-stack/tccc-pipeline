# TCCC card pipeline. `make` lists the targets. Everything is free unless marked PAID.
PY    ?= python3
VENV  := .venv
BIN   := $(VENV)/bin
MODEL ?= google/gemini-3.8-flash
PORT  := 8000
RECORDINGS ?= ../recordings

.PHONY: help setup app stop test lint eval cards check-key live live-all bakeoff relisten handover-scripts diagram clean

help:  ## list the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*## "}{printf "  make %-10s %s\n", $$1, $$2}'

setup: $(VENV)/.installed  ## create .venv and install everything (free)

$(VENV)/.installed: requirements.txt requirements-dev.txt
	$(PY) -m venv $(VENV)
	$(BIN)/python -m pip install -q --upgrade pip
	$(BIN)/python -m pip install -q -r requirements-dev.txt
	@touch $@

app: setup stop  ## open the app on http://localhost:8000 (builds cards from cache if missing; free; Ctrl+C stops)
	$(BIN)/python -m tccc

stop:  ## stop anything already serving on port 8000
	@pid=$$(lsof -ti tcp:$(PORT) -sTCP:LISTEN 2>/dev/null); [ -z "$$pid" ] || { kill $$pid; sleep 1; echo "stopped $$pid"; }

test: setup  ## offline unit tests + golden held-out regression (free, no network)
	$(BIN)/python -m pytest -q

lint: setup  ## ruff (style and bugs) and vulture (unused code)
	$(BIN)/ruff check .
	$(BIN)/vulture tccc --min-confidence 70

eval: setup  ## score held-out, then all 50, from cached replies (free)
	$(BIN)/python -m tccc.run $(MODEL) --split heldout
	$(BIN)/python -m tccc.run $(MODEL) --split all

cards: setup  ## rebuild all 50 PDF cards and review sheets from cache (free)
	$(BIN)/python -m tccc.run $(MODEL) --split all --pdf

check-key: setup  ## check your OpenRouter key works and show spend vs the cap (free; never prints the key)
	@$(BIN)/python -m tccc.openrouter

live: setup  ## PAID ~1.3 cents: one recording end to end, e.g. make live FILE=../recordings/handover-isa.wav -> out/live/
	@test -n "$(FILE)" || { echo "usage: make live FILE=path/to/recording.wav"; exit 1; }
	@$(BIN)/python -m tccc.pipeline $(FILE)

live-all: setup  ## PAID ~$0.65: all 50 recordings with fresh calls into out/live-all/ (cache untouched), then score
	@ls $(RECORDINGS)/*.wav >/dev/null 2>&1 || { echo "no recordings in $(RECORDINGS) (set RECORDINGS=...)"; exit 1; }
	@read -p "This makes fresh paid calls for all 50 recordings (about \$$0.65 on your key). Type yes to go on: " a; [ "$$a" = yes ]
	@$(BIN)/python -m tccc.pipeline $(RECORDINGS)/*.wav --out out/live-all
	@$(BIN)/python -m tccc.score out/live-all/predictions

bakeoff: setup  ## PAID: speech-to-text bake-off on the shortlist (fetches only missing transcripts)
	$(BIN)/python -m tccc.experiments.stt_bakeoff

relisten: setup  ## simulate a third listen from cached transcripts (free)
	$(BIN)/python -m tccc.experiments.relisten

handover-scripts: setup  ## write speakable MIST scripts from the answer key into out/handover-scripts/ (free)
	$(BIN)/python -m tccc.experiments.handover_scripts

diagram: setup  ## redraw docs/how-it-works.svg
	$(BIN)/python docs/diagram.py

clean:  ## remove Python caches (keeps .venv, cards and cached model replies)
	find . -name __pycache__ -not -path './$(VENV)/*' -prune -exec rm -rf {} +
	rm -rf .pytest_cache
