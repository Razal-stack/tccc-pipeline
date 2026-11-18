"""Reproduce the published scores from the cached model replies: no network, nothing written to out/."""
import json

import pytest

from tccc import extract, pipeline, score

pytestmark = pytest.mark.golden


def scored(monkeypatch, tmp_path, split):
    names = extract.SPLITS[split]

    def no_key():
        raise RuntimeError("no key in tests")
    monkeypatch.setattr(extract, "load_key", no_key)  # an uncached reply would need the API: fail instead
    try:
        raw_dir = extract.run(pipeline.LLM_MODEL, names)
    except Exception:  # noqa: BLE001
        pytest.skip("cache missing")
    cards = {}
    for f in names:
        stem = f.replace(".wav", "")
        reply = json.loads((raw_dir / f"{stem}.json").read_text())
        cards[f], _ = pipeline.finish(f, reply, extract.transcript(stem), tmp_path, pdf=False)
    return score.score(cards, files=names)


def test_heldout_headline_numbers(monkeypatch, tmp_path):
    s = scored(monkeypatch, tmp_path, "heldout")
    assert round(s["overall"]["f1"], 3) == 0.938
    assert round(s["overall"]["precision"], 3) == 0.976
    assert round(s["critical"]["f1"], 3) == 0.968
    assert s["overall"]["invented"] == 2


def test_all_fifty_f1(monkeypatch, tmp_path):
    s = scored(monkeypatch, tmp_path, "all")
    assert s["cards"] == 50
    assert round(s["overall"]["f1"], 3) == 0.947
