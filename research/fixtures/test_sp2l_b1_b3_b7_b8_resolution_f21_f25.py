from sp2l_b1_b3_b7_b8_resolution_f21_f25 import (
    Direction,
    GapConstruction,
    OrderAction,
    bearish_geometry_is_universally_source_proven,
    bearish_mirror_abstraction,
    entry_equals_leg2_start_is_canonical,
    exact_stop_ohlc_anchor_is_resolved,
    generic_three_candle_imbalance_is_canonical,
    pending_update,
    production_freeze_allowed,
    source_safe_entry_candidates,
    source_safe_pgap_candidates,
    source_safe_stop_model,
)


def test_pgap_keeps_both_source_constructions():
    assert source_safe_pgap_candidates() == {
        GapConstruction.BREAKOUT_THEN_GAP,
        GapConstruction.GAP_AFTER_STRUCTURAL_SEQUENCE,
    }


def test_generic_fvg_substitution_is_rejected():
    assert generic_three_candle_imbalance_is_canonical() is False


def test_entry_remains_pending_limit_and_anchor_unresolved():
    for direction in (Direction.BULLISH, Direction.BEARISH):
        candidates = source_safe_entry_candidates(direction)
        assert all(c.mechanism == "pending_limit" for c in candidates)
    assert entry_equals_leg2_start_is_canonical() is False


def test_stop_is_structural_but_exact_anchor_is_unresolved():
    assert source_safe_stop_model().value == "structural_invalidation"
    assert exact_stop_ohlc_anchor_is_resolved() is False


def test_pending_update_requires_source_qualified_materiality():
    assert pending_update(False) is OrderAction.KEEP
    assert pending_update(True) is OrderAction.REPLACE
    assert pending_update(None) is OrderAction.UNRESOLVED


def test_bearish_mirror_is_structurally_supported_not_frozen_geometry():
    mirror = bearish_mirror_abstraction()
    assert mirror.direction is Direction.BEARISH
    assert "Lower Highs" in mirror.structure
    assert "Sell Limit" in mirror.entry
    assert "Structural High" in mirror.invalidation
    assert bearish_geometry_is_universally_source_proven() is False


def test_source_resolution_still_blocks_production_freeze():
    assert production_freeze_allowed() is False
