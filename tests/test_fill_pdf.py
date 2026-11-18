import json
from pathlib import Path

import pytest

from tccc.fill_pdf import fill, read_back
from tccc.score import TRUTH, norm

FIELD_MAP = json.loads((Path(__file__).resolve().parent.parent / "data" / "field_map.json").read_text())
FIRST = sorted(TRUTH)[0]
FULLEST = max(TRUTH, key=lambda f: sum(norm(v) is not None for v in TRUTH[f].values()))


@pytest.mark.parametrize("name", [FIRST, FULLEST])
def test_filled_card_reads_back_identically(tmp_path, name):
    truth = TRUTH[name]
    back = read_back(fill(truth, tmp_path / "card.pdf"))
    wrong = {k: (back[k], truth[k]) for k in FIELD_MAP["fields"] if norm(back[k]) != norm(truth.get(k))}
    assert wrong == {}
    assert back["injury_boxes"] == sorted(truth["injury_boxes"])


def test_blank_card_reads_back_blank(tmp_path):
    back = read_back(fill({}, tmp_path / "blank.pdf"))
    assert all(norm(v) is None for k, v in back.items() if k != "injury_boxes")
    assert back["injury_boxes"] == []
