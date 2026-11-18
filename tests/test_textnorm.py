from tccc.textnorm import spoken_to_digits, squash


def test_spoken_numbers_become_digits():
    assert squash("pulse one twenty eight") == "pulse128"
    assert spoken_to_digits("about fifteen hundred") == "about 1500"
    assert squash("last four, four four one seven") == "last44417"
    assert spoken_to_digits("niner") == "9"


def test_blood_pressure_slash_is_not_one_number():
    assert "164" not in squash("BP 100/64")
    assert squash("BP 100/64") == "bp100over64"


def test_squash_ignores_spaces_and_punctuation():
    assert squash("1 4 2 0") == squash("14 20") == "1420"
    assert squash("Juliet-Sierra, 4417.") == "julietsierra4417"
