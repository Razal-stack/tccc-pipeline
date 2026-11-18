import pytest

from tccc.validate import BOOLS, TEXTS, check_card, clean, label, missing_critical, supported, to_card


def blank_card(**filled):
    card, _ = to_card("x.wav", {}, "")
    card.update(filled)
    return card


@pytest.mark.parametrize("field, raw, expected", [
    ("time", "9:05", "0905"),
    ("time", "715", "0715"),
    ("time", "2575", None),
    ("tq_left_leg_time", "24:10", None),
    ("signs_1_avpu", "alert", "A - Alert"),
    ("signs_1_avpu", "Pain", "P - Pain"),
    ("signs_1_pain", "7", "7 Very Intense"),
    ("signs_1_pain", "11", None),
    ("analgesic_1_route", "otfc", "OTFC"),
    ("analgesic_1_route", "XYZ", None),
    ("analgesic_1_dose", "800mcg", "800 mcg"),
    ("fluid_1_volume", "1L", "1 L"),
    ("signs_1_spo2", "120", None),
    ("signs_1_spo2", "97", "97"),
    ("signs_1_pulse", "128 Radial", "128 radial"),
    ("signs_1_pulse", "300", None),
    ("unit", "One Rifles", "1 Rifles"),
    ("unit", "B Company, One Rifles", "B Company, One Rifles"),  # only a leading number word is converted
])
def test_clean(field, raw, expected):
    assert clean(field, raw) == expected


def test_supported_needs_evidence_in_the_transcript():
    said = "Pulse one twenty eight radial, sats ninety eight."
    assert supported("128 radial", "pulse one twenty eight radial", said)
    assert not supported("97", "sats 97", said)  # 97 was never said
    assert not supported("128 radial", "heart rate was fast", said)


def test_to_card_drops_and_flags_an_unsupported_value():
    reply = {"fields": {"signs_1_pulse": ["128 radial", "pulse one twenty eight radial"],
                        "signs_1_spo2": ["97", "sats 97"]}}
    card, flags = to_card("x.wav", reply, "Pulse one twenty eight radial, sats ninety eight.")
    assert card["signs_1_pulse"] == "128 radial"
    assert card["signs_1_spo2"] == ""
    assert any("spo2" in f.lower() and "left blank" in f for f in flags)


def test_to_card_flags_unknown_fields_and_invalid_values():
    reply = {"fields": {"shoe_size": ["44", "44"], "time": ["2575", "time 2575"]}, "flags": ["radio noise"]}
    card, flags = to_card("x.wav", reply, "time 2575 shoe size 44")
    assert card["time"] == ""
    assert "dropped unknown field shoe_size" in flags
    assert "radio noise" in flags
    assert any("not a valid value" in f for f in flags)


@pytest.mark.parametrize("field, value, said", [
    ("tq_left_leg_type", "CAT", "CAT tourniquet on the left leg"),
    ("tq_right_arm_time", "0715", "tourniquet right arm at 0715"),
])
def test_limb_tourniquet_ticks_tq_extremity(field, value, said):
    card, _ = to_card("x.wav", {"fields": {field: [value, said]}}, said)
    assert card[field] == value
    assert card["tq_extremity"] is True


def test_no_tourniquet_leaves_tq_extremity_false():
    assert to_card("x.wav", {}, "")[0]["tq_extremity"] is False


def test_systolic_not_above_diastolic_is_blanked():
    reply = {"fields": {"signs_1_bp_systolic": ["80", "BP 80 over 90"], "signs_1_bp_diastolic": ["90", "BP 80 over 90"]}}
    card, flags = to_card("x.wav", reply, "BP 80 over 90")
    assert card["signs_1_bp_systolic"] == card["signs_1_bp_diastolic"] == ""
    assert any("implausible" in f for f in flags)


def test_to_card_expands_every_field_and_passes_check_card():
    card, _ = to_card("x.wav", {"fields": {"evac_urgent": True}}, "")
    assert all(f in card for f in BOOLS + TEXTS)
    assert card["evac_urgent"] is True
    assert check_card(card) == []


def test_check_card_reports_problems():
    card = blank_card(signs_1_avpu="alert", injury_boxes=["Not_A_Box"])
    problems = check_card(card)
    assert any("signs_1_avpu" in p for p in problems)
    assert any("unknown body box" in p for p in problems)


def test_label_is_readable():
    assert label("tq_right_leg_time") == "Tourniquet right leg time"


def test_empty_card_asks_for_identity_and_evac():
    ask = missing_critical(blank_card())
    assert len(ask) == 2
    assert "identity" in ask[0] and "evac" in ask[1]


def test_tourniquet_type_without_time_asks_for_the_time():
    ask = missing_critical(blank_card(tq_left_leg_type="CAT", tq_extremity=True))
    assert "tourniquet time, left leg" in ask


def test_drug_without_dose_route_time_asks_for_each():
    ask = missing_critical(blank_card(analgesic_1_name="ketamine"))
    assert {"ketamine: dose", "ketamine: route", "ketamine: time"} <= set(ask)
    complete = blank_card(analgesic_1_name="ketamine", analgesic_1_dose="50 mg", analgesic_1_route="IM",
                          analgesic_1_time="0720")
    assert not [a for a in missing_critical(complete) if a.startswith("ketamine")]
