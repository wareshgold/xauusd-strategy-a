from research.fixtures.sp2l_target_reference_fixtures_g251 import (
    Decision,
    fixtures,
    risk,
    terminal_tp_is_reference,
    tp1_reference,
    tp2_reference,
)


def test_source_reference_targets_are_one_r_and_two_r_for_bullish_cases():
    cases = fixtures()
    for case in cases:
        if case.direction == "bullish":
            assert tp1_reference(case) is case.expected_tp1
            assert tp2_reference(case) is case.expected_tp2


def test_bearish_target_mirror_is_not_frozen():
    case = next(case for case in fixtures() if case.case_id == "T2")
    assert tp1_reference(case) is Decision.UNKNOWN
    assert tp2_reference(case) is Decision.UNKNOWN


def test_terminal_tp_selection_remains_separate_from_reference_geometry():
    cases = {case.case_id: case for case in fixtures()}
    assert terminal_tp_is_reference(cases["T1"]) is Decision.UNKNOWN
    assert terminal_tp_is_reference(cases["T3"]) is Decision.PASS
    assert terminal_tp_is_reference(cases["T4"]) is Decision.PASS
    assert terminal_tp_is_reference(cases["T5"]) is Decision.FAIL


def test_risk_is_absolute_entry_stop_distance():
    assert risk(100.0, 90.0) == 10.0
    assert risk(90.0, 100.0) == 10.0
    assert risk(None, 100.0) is None
