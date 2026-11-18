# TCCC card pipeline. `make` lists the targets. Everything is free unless marked PAID.
PY    ?= python3
VENV  := .venv
BIN   := $(VENV)/bin
MODEL ?= google/gemini-3.8-flash
PORT  := 8000

.PHONY: help setup app stop test eval cards pipeline bakeoff relisten diagram clean

help:  ## list the targets
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*## "}{printf "  make %-10s %s\n", $$1, $$2}'

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

eval: setup  ## score held-out, then all 50, from cached replies (free)
	$(BIN)/python -m tccc.run $(MODEL) --split heldout
	$(BIN)/python -m tccc.run $(MODEL) --split all

cards: setup  ## rebuild all 50 PDF cards and review sheets from cache (free)
	$(BIN)/python -m tccc.run $(MODEL) --split all --pdf

pipeline: setup  ## PAID: one new recording, e.g. make pipeline FILE=../recordings/handover-isa.wav -> out/live/
	@test -n "$(FILE)" || { echo "usage: make pipeline FILE=path/to/recording.wav"; exit 1; }
	$(BIN)/python -m tccc.pipeline $(FILE)

bakeoff: setup  ## PAID: speech-to-text bake-off on the shortlist (fetches only missing transcripts)
	$(BIN)/python -m tccc.experiments.stt_bakeoff

relisten: setup  ## simulate a third listen from cached transcripts (free)
	$(BIN)/python -m tccc.experiments.relisten

diagram: setup  ## redraw docs/how-it-works.svg
	$(BIN)/python docs/diagram.py

clean:  ## remove Python caches (keeps .venv, cards and cached model replies)
	find . -name __pycache__ -not -path './$(VENV)/*' -prune -exec rm -rf {} +
	rm -rf .pytest_cache
