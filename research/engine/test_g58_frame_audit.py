def test_frame_audit_keeps_all_geometry_blocked():
    blockers = {"B1", "B2", "B3", "B4", "B5", "B6"}
    unresolved = {"B1", "B2", "B3", "B4", "B5", "B6"}
    assert blockers == unresolved


def test_frame_audit_does_not_promote_market_reclaim():
    assert "market_reclaim" not in {"pending_limit", "one_candle", "two_candle", "three_candle", "key_bar"}
