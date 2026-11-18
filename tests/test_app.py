from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tccc.app import TIME, app, time_rows

PREDICTIONS = Path(__file__).resolve().parent.parent / "out" / "google__gemini-3.8-flash" / "all" / "predictions"
needs_cards = pytest.mark.skipif(not PREDICTIONS.exists(), reason="no predictions folder")


@needs_cards
def test_pages_load():
    client = TestClient(app)
    home = client.get("/")
    assert home.status_code == 200 and "Casualties" in home.text
    assert client.get("/how").status_code == 200
    assert client.get("/benchmark").status_code == 200


@needs_cards
def test_card_page_loads():
    stem = sorted(PREDICTIONS.glob("*.json"))[0].stem
    assert TestClient(app).get(f"/card/eval/{stem}").status_code == 200


def test_time_rows_by_hand_and_with_two_medics():
    rows = {name: vals for name, *vals in time_rows(50, 118)}
    lo, hi = TIME["hand"]
    assert rows["By hand, 1 medic"] == pytest.approx([50 * lo / 60, 50 * hi / 60])
    assert rows["By hand, 2 medics"] == pytest.approx([50 * lo / 120, 50 * hi / 120])
    (rl, rh), (il, ih) = TIME["review"], TIME["item"]
    one = [(50 * rl + 118 * il) / 60, (50 * rh + 118 * ih) / 60]
    assert rows["With the system, 1 medic"] == pytest.approx(one)
    assert rows["With the system, 2 medics"] == pytest.approx([x / 2 for x in one])
