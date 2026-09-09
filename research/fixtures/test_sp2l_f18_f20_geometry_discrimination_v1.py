from sp2l_f18_f20_geometry_discrimination_v1 import (
    AnchorModel,
    LegMeasurement,
    TriggerForm,
    abcd_equal,
    candidate_anchor_points,
    entry_leg2_separated,
    leg2_projection_candidate,
    trigger_candidate,
)


def test_trigger_family_is_source_observed_and_market_reclaim_is_negative():
    for form in (
        TriggerForm.ONE_CANDLE,
        TriggerForm.TWO_CANDLE,
        TriggerForm.THREE_CANDLE,
        TriggerForm.KEY_BAR,
    ):
        assert trigger_candidate(form).confirms_pending_limit
    assert not trigger_candidate(TriggerForm.MARKET_RECLAIM).confirms_pending_limit


def test_abcd_fixture_preserves_exact_magnitude_relationship_without_tolerance():
    assert abcd_equal(100.0, 100.0)
    assert not abcd_equal(100.0, 100.01)


def test_competing_abcd_anchor_models_remain_representable():
    values = {
        "A_wick": 10, "B_wick": 30, "C_wick": 20, "D_wick": 40,
        "A_body": 12, "B_body": 28, "C_body": 22, "D_body": 38,
        "A_pivot": 11, "B_pivot": 29, "C_pivot": 21, "D_pivot": 39,
    }
    assert candidate_anchor_points(values, AnchorModel.WICK) != candidate_anchor_points(values, AnchorModel.BODY)
    assert candidate_anchor_points(values, AnchorModel.BODY) != candidate_anchor_points(values, AnchorModel.STRUCTURAL_PIVOT)


def test_entry_is_not_leg2_start_when_source_example_separates_levels():
    m = LegMeasurement(entry=1900.0, leg2_start=1912.0, leg1_magnitude=20.0, leg2_magnitude=20.0)
    assert entry_leg2_separated(m)


def test_leg2_projection_is_a_candidate_only():
    assert leg2_projection_candidate(1900.0, 20.0, +1) == 1920.0
    assert leg2_projection_candidate(1900.0, 20.0, -1) == 1880.0
