from collections import Counter

import pytest

from tccc.score import FIELDS, TRUTH, group_of, is_critical, norm, outcome, prf, score, score_card

TWO_FILES = sorted(TRUTH)[:2]


@pytest.mark.parametrize("pred, truth, expected", [
    ("800 mcg", "800 mcg", "correct"),
    ("500 mcg", "800 mcg", "wrong"),
    ("800 mcg", "", "invented"),
    ("", "800 mcg", "missed"),
    (None, False, "blank_ok"),
    (True, True, "correct"),
    (True, False, "invented"),
])
def test_outcome(pred, truth, expected):
    assert outcome(pred, truth) == expected


def test_norm_treats_blank_values_alike_and_ignores_format_noise():
    assert norm("") is norm(None) is norm(False) is None
    assert norm("800mcg") == norm("800 mcg")
    assert norm("9:05") == norm("0905") == "0905"
    assert norm("  Left   Arm. ") == "left arm"


def test_prf_matches_hand_computation():
    # 6 right, 2 wrong, 2 invented, 4 missed: precision 6/10, recall 6/12, F1 = 2pr/(p+r)
    p, r, f = prf(Counter(correct=6, wrong=2, invented=2, missed=4))
    assert (p, r) == (0.6, 0.5)
    assert f == pytest.approx(2 * 0.6 * 0.5 / 1.1)
    assert prf(Counter()) == (1.0, 1.0, 1.0)  # nothing to fill, nothing filled


def test_field_helpers():
    assert is_critical("analgesic_1_dose") and is_critical("allergies") and not is_critical("unit")
    assert group_of("tq_left_leg_time") == "tourniquets"
    assert group_of("signs_2_pulse") == "vital_signs"


def test_perfect_copy_of_the_truth_scores_one():
    s = score({f: dict(TRUTH[f]) for f in TWO_FILES}, files=TWO_FILES)
    assert s["cards"] == 2
    assert s["overall"]["f1"] == 1.0
    assert s["overall"].get("invented", 0) == 0 and s["overall"].get("wrong", 0) == 0  # absent key = zero
    assert s["injury_boxes"]["f1"] == 1.0
    assert s["errors"] == []


def test_empty_card_has_zero_recall_but_high_naive_accuracy():
    s = score({}, files=TWO_FILES)
    assert s["overall"]["recall"] == 0
    assert s["overall"].get("invented", 0) == 0
    assert s["naive_accuracy"] == s["empty_card_baseline"] > 0.5


def test_score_card_counts_one_invented_field():
    truth = TRUTH[TWO_FILES[0]]
    blank_field = next(f for f in FIELDS if norm(truth[f]) is None and not isinstance(truth[f], bool))
    per_field, boxes = score_card({**truth, blank_field: "made up"}, truth)
    assert per_field[blank_field] == "invented"
    assert Counter(per_field.values())["wrong"] == 0
    assert boxes["fp"] == boxes["fn"] == 0
