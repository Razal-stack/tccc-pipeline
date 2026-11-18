from tccc.injury import VALID, boxes_for, boxes_from_notes, locations


def test_left_forearm_boxes():
    assert boxes_for("left forearm") == {"Ant_Left_Middle_Lateral_Forearm", "Ant_Left_Middle_Medial_Forearm"}


def test_back_of_flips_to_the_posterior_boxes():
    assert all(b.startswith("Post_") for b in boxes_for("back of left forearm"))


def test_unknown_location_gives_no_boxes():
    assert boxes_for("spleen") == set()


def test_results_are_always_valid_box_names():
    for loc in ("left forearm", "both legs", "chest", "face", "right hip", "abdomen", "neck", "back", "left hand"):
        assert boxes_for(loc) <= VALID


def test_locations_come_from_the_injuries_segment_only():
    notes = "Injuries: left forearm: fragment wound; the right thigh: GSW; time found 0215"
    assert locations(notes) == ["left forearm", "right thigh"]
    assert len(boxes_from_notes(notes)) > len(boxes_for("left forearm"))


def test_notes_without_injuries_give_nothing():
    assert boxes_from_notes("time found 0215; jaw thrust") == []
    assert boxes_from_notes("") == []
