from strategy_factory.source_execution_fixtures import (
    PendingLimitInputs,
    SourcePathStatus,
    TrailingInputs,
    evaluate_pending_limit_preflight,
    evaluate_trailing_preflight,
)


def test_buy_limit_must_be_below_current_ask():
    result = evaluate_pending_limit_preflight(PendingLimitInputs(
        direction="BUY", entry=2300.0, sl=2298.0, tp=2304.0,
        bid=2300.1, ask=2300.2, stops_level_points=0, point=0.01,
    ))
    assert result.status is SourcePathStatus.REQUEST_ELIGIBLE
    assert result.order_type == "BUY_LIMIT"


def test_buy_limit_at_or_above_ask_is_rejected_by_source_guard():
    result = evaluate_pending_limit_preflight(PendingLimitInputs(
        direction="BUY", entry=2300.2, sl=2298.0, tp=2304.0,
        bid=2300.1, ask=2300.2, stops_level_points=0, point=0.01,
    ))
    assert result.reason == "LIMIT_ENTRY_NOT_PLACEABLE_AT_CURRENT_MARKET"


def test_sell_limit_must_be_above_current_bid():
    result = evaluate_pending_limit_preflight(PendingLimitInputs(
        direction="SELL", entry=2300.3, sl=2302.0, tp=2296.0,
        bid=2300.1, ask=2300.2, stops_level_points=0, point=0.01,
    ))
    assert result.status is SourcePathStatus.REQUEST_ELIGIBLE
    assert result.order_type == "SELL_LIMIT"


def test_nonpositive_risk_or_reward_is_rejected():
    result = evaluate_pending_limit_preflight(PendingLimitInputs(
        direction="BUY", entry=2300.0, sl=2300.0, tp=2304.0,
        bid=2299.9, ask=2300.1, stops_level_points=0, point=0.01,
    ))
    assert result.reason == "INVALID_STOPS_AT_THEORETICAL_ENTRY"


def test_broker_minimum_stop_distance_is_checked_before_send():
    result = evaluate_pending_limit_preflight(PendingLimitInputs(
        direction="BUY", entry=2300.0, sl=2299.8, tp=2300.3,
        bid=2299.7, ask=2299.8, stops_level_points=40, point=0.01,
    ))
    assert result.reason == "BELOW_BROKER_MIN_STOP_DISTANCE"
    assert result.min_stop_distance == 0.4


def test_preflight_pass_does_not_claim_broker_acceptance_or_fill():
    result = evaluate_pending_limit_preflight(PendingLimitInputs(
        direction="BUY", entry=2300.0, sl=2298.0, tp=2304.0,
        bid=2299.8, ask=2299.9, stops_level_points=0, point=0.01,
    ))
    assert result.status is SourcePathStatus.REQUEST_ELIGIBLE
    assert "BROKER_RESULT_UNRESOLVED" in result.reason


def test_buy_trailing_guard_requires_improvement_and_broker_distance():
    result = evaluate_trailing_preflight(TrailingInputs(
        direction="BUY", entry=2300.0, old_sl=2300.2, new_sl=2300.5,
        tp=2304.0, favorable_extreme=2301.0, bid=2300.8, ask=2300.9,
        min_distance=0.1, trail_distance=0.4,
    ))
    assert result.status is SourcePathStatus.REQUEST_ELIGIBLE


def test_buy_trailing_guard_rejects_stop_too_close_to_bid():
    result = evaluate_trailing_preflight(TrailingInputs(
        direction="BUY", entry=2300.0, old_sl=2300.2, new_sl=2300.75,
        tp=2304.0, favorable_extreme=2301.0, bid=2300.8, ask=2300.9,
        min_distance=0.1, trail_distance=0.4,
    ))
    assert result.reason == "BUY_SL_TOO_CLOSE_TO_BID"


def test_sell_trailing_guard_requires_stop_above_ask_plus_distance():
    result = evaluate_trailing_preflight(TrailingInputs(
        direction="SELL", entry=2300.0, old_sl=2300.2, new_sl=2299.5,
        tp=2296.0, favorable_extreme=2299.0, bid=2299.1, ask=2299.2,
        min_distance=0.1, trail_distance=0.4,
    ))
    assert result.reason == "SELL_SL_NOT_ABOVE_BAR_LOW"


def test_invalid_quotes_remain_unresolved_not_guessed():
    result = evaluate_pending_limit_preflight(PendingLimitInputs(
        direction="BUY", entry=2300.0, sl=2298.0, tp=2304.0,
        bid=2300.2, ask=2300.1, stops_level_points=0, point=0.01,
    ))
    assert result.status is SourcePathStatus.UNRESOLVED
    assert result.reason == "INVALID_QUOTE"
