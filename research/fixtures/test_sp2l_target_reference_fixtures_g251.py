from research.fixtures.sp2l_target_reference_fixtures_g251 import (
    Decision,
    fixtures,
    ordered_bullish_targets,
    terminal_tp_is_reference,
    TargetCase,
)


def test_source_reference_targets_preserve_bullish_order_only():
    cases = fixtures()
    for case in cases:
        if case.direction == "bullish":
            assert ordered_bullish_targets(case) is case.expected_tp_order


def test_bearish_target_mirror_is_not_frozen():
    case = next(case for case in fixtures() if case.case_id == "T2")
    assert ordered_bullish_targets(case) is Decision.UNKNOWN


def test_terminal_tp_selection_remains_separate_from_reference_geometry():
    cases = {case.case_id: case for case in fixtures()}
    assert terminal_tp_is_reference(cases["T1"]) is Decision.UNKNOWN
    assert terminal_tp_is_reference(cases["T3"]) is Decision.PASS
    assert terminal_tp_is_reference(cases["T4"]) is Decision.PASS
    assert terminal_tp_is_reference(cases["T5"]) is Decision.FAIL


def test_bullish_order_fixture_does_not_encode_r_multiple():
    case = TargetCase("R_FREE", "bullish", 100.0, 99.0, 101.0, 101.1, None,
                      Decision.PASS, Decision.UNKNOWN)
    assert ordered_bullish_targets(case) is Decision.PASS
