from strategy_factory.x2_pyramiding_engine import replay_x2_signal


def _bars(rows):
    return [dict(time=i * 60, open=o, high=h, low=l, close=c)
            for i, (o, h, l, c) in enumerate(rows)]


def _candidate(direction="BUY"):
    if direction == "BUY":
        return dict(entry_idx=0, theoretical_entry=100.0, sl=99.0, risk=1.0,
                    direction="BUY", trigger_time=0, population_index=7)
    return dict(entry_idx=0, theoretical_entry=100.0, sl=101.0, risk=1.0,
                direction="SELL", trigger_time=0, population_index=7)


def _buy_path():
    # +1R arms on bar 1. Pullback only qualifies on bar 2.
    # Bar 3 confirms by close > prior high; fill is bar 4 open.
    return _bars([
        (100.0, 100.1, 99.9, 100.0),
        (100.0, 101.1, 99.5, 100.8),
        (100.8, 101.2, 100.8, 101.0),
        (101.0, 101.4, 101.0, 101.3),
        (101.4, 101.7, 101.2, 101.6),
        (101.6, 102.0, 101.5, 101.9),
    ])


def test_buy_threshold_pullback_confirmation_and_next_open_fill():
    out = replay_x2_signal(_candidate(), _buy_path(), activation_price=0.5,
                           trail_distance_price=0.3, threshold_r=1.0)
    assert out["x2_status"] == "OPENED"
    assert out["x2"] is not None
    assert out["x2"]["entry"] == 101.4
    assert out["x2"]["initial_sl"] == 100.8
    assert out["x2"]["risk_usd"] <= 100.0
    assert out["x2"]["bars_held"] >= 1


def test_threshold_bar_does_not_also_count_as_pullback_bar():
    bars = _bars([
        (100, 100.1, 99.9, 100),
        (100, 101.1, 99.5, 100.2),
        (100.2, 100.5, 100.1, 100.3),
        (100.3, 101.0, 100.2, 100.9),
        (100.9, 101.2, 100.8, 101.1),
        (101.1, 101.4, 101.0, 101.3),
    ])
    out = replay_x2_signal(_candidate(), bars, activation_price=0.5,
                           trail_distance_price=0.3, threshold_r=1.0)
    # If the threshold bar had been reused as the pullback, this would open earlier.
    assert out["x2"] is None or out["x2"]["entry"] == bars[4]["open"]


def test_sell_is_symmetric():
    bars = _bars([
        (100, 100.1, 99.9, 100),
        (100, 100.5, 98.9, 99.2),
        (99.2, 99.2, 98.8, 99.0),
        (99.0, 99.0, 98.6, 98.7),
        (98.6, 98.8, 98.3, 98.4),
    ])
    out = replay_x2_signal(_candidate("SELL"), bars, activation_price=0.5,
                           trail_distance_price=0.3, threshold_r=1.0)
    assert out["x2_status"] in {"OPENED", "SKIPPED", "CANCELLED"}
    if out["x2"] is not None:
        assert out["x2"]["entry"] < out["x2"]["initial_sl"]


def test_no_x2_when_x1_stops_before_setup_completes():
    bars = _bars([
        (100, 100.1, 99.9, 100),
        (100, 101.1, 99.5, 100.8),
        (100.8, 101.0, 98.9, 99.0),
        (99.0, 99.2, 98.8, 99.0),
    ])
    out = replay_x2_signal(_candidate(), bars, activation_price=0.5,
                           trail_distance_price=0.3, threshold_r=1.0)
    assert out["x2"] is None
    # A pullback alone is not an X2 admission trigger. X1 exits before
    # continuation confirmation, so the setup is cancelled.
    assert out["x2_status"] == "CANCELLED"
    assert out["x2_skip_reason"] == "X1_EXIT_BEFORE_X2"


def test_x1_exit_and_x2_continuation_confirmation_same_bar_are_ambiguous():
    bars = _bars([
        (100.0, 100.1, 99.9, 100.0),
        (100.0, 101.1, 100.9, 101.0),   # threshold; X1 trail -> 100.8
        (101.0, 101.2, 100.85, 101.1),  # pullback arms; X1 trail -> 100.9
        (101.1, 101.4, 100.8, 101.3),   # X1 stop and continuation both possible
    ])
    out = replay_x2_signal(_candidate(), bars, activation_price=0.5,
                           trail_distance_price=0.3, threshold_r=1.0)
    assert out["x2"] is None
    assert out["x2_status"] == "AMBIGUOUS"
    assert out["x2_skip_reason"] == "X1_EXIT_AND_X2_EVENT_SAME_BAR"
    assert out["combined_ambiguous"] is True
    assert out["combined_decisive"] is False
    assert out["combined_gross_usd"] is None


def test_gap_is_ambiguous_and_never_filled():
    bars = _buy_path()
    bars[2]["time"] += 120
    out = replay_x2_signal(_candidate(), bars, activation_price=0.5,
                           trail_distance_price=0.3, threshold_r=1.0)
    assert out["x2"] is None
    assert out["x1"]["ambiguous"]


def test_invalid_parameters_rejected():
    import pytest
    with pytest.raises(ValueError):
        replay_x2_signal(_candidate(), _buy_path(), activation_price=0,
                         trail_distance_price=0.3, threshold_r=1.0)


def test_frozen_risk_must_match_entry_stop():
    import pytest
    c = _candidate()
    c["risk"] = 2.0
    with pytest.raises(ValueError):
        replay_x2_signal(c, _buy_path(), activation_price=0.5,
                         trail_distance_price=0.3, threshold_r=1.0)



def _threshold_path(threshold, pullback_depth=0.25):
    peak = 100.0 + threshold
    return _bars([
        (100.0, 100.1, 99.9, 100.0),
        (100.0, peak, peak - 0.05, peak - 0.05),
        (peak - 0.05, peak, peak - pullback_depth, peak - 0.02),
        (peak - 0.02, peak + 0.3, peak - 0.01, peak + 0.2),
        (peak + 0.2, peak + 0.4, peak + 0.1, peak + 0.3),
    ])


def test_all_three_thresholds_can_arm_and_fill_x2():
    for threshold in (1.0, 1.5, 2.0):
        out = replay_x2_signal(_candidate(), _threshold_path(threshold),
                               activation_price=0.5, trail_distance_price=0.3,
                               threshold_r=threshold)
        assert out["x2_status"] == "OPENED"
        assert out["x2"]["entry"] == _threshold_path(threshold)[4]["open"]


def test_pullback_exactly_quarter_r_qualifies():
    bars = _threshold_path(1.0, pullback_depth=0.25)
    out = replay_x2_signal(_candidate(), bars, activation_price=0.5,
                           trail_distance_price=0.3, threshold_r=1.0)
    assert out["x2_status"] == "OPENED"


def test_pullback_just_below_quarter_r_does_not_qualify():
    bars = _threshold_path(1.0, pullback_depth=0.249)
    # Remove later bars so a later pullback cannot qualify.
    bars = bars[:3]
    out = replay_x2_signal(_candidate(), bars, activation_price=10.0,
                           trail_distance_price=0.3, threshold_r=1.0)
    assert out["x2"] is None
    assert out["x2_status"] == "NOT_TRIGGERED"


def test_x2_rejected_when_x1_consumes_entire_open_risk_budget():
    bars = _threshold_path(1.0)
    out = replay_x2_signal(_candidate(), bars, activation_price=10.0,
                           trail_distance_price=0.3, threshold_r=1.0)
    assert out["x2"] is None
    assert out["x2_status"] == "SKIPPED"
    assert out["x2_skip_reason"] == "X2_SKIPPED_RISK_BUDGET"


def test_x2_entry_bar_can_hit_its_initial_stop():
    bars = _threshold_path(1.0)
    bars[4]["low"] = 100.0
    out = replay_x2_signal(_candidate(), bars, activation_price=0.5,
                           trail_distance_price=0.3, threshold_r=1.0)
    assert out["x2"] is not None
    assert out["x2"]["reason"] == "SL_ON_ENTRY_BAR"
    assert out["x2"]["exit_price"] == out["x2"]["initial_sl"]



def test_x2_trailing_is_independent_and_initial_stop_is_immutable():
    bars = _buy_path()
    bars[5]["low"] = 101.0  # Hits X1's active stop, not X2's initial stop.
    bars[5]["high"] = 102.0  # X2 trail advances only after this bar's stop checks.
    bars.append(dict(time=360, open=101.9, high=102.0, low=101.6, close=101.8))
    out = replay_x2_signal(_candidate(), bars, activation_price=0.5,
                           trail_distance_price=0.3, threshold_r=1.0)
    assert out["x2"] is not None
    assert out["x1"]["exit_price"] == 101.1
    assert out["x2"]["initial_sl"] == 100.8
    assert out["x2"]["final_sl"] == 101.7
    assert out["x2"]["exit_price"] == 101.7
    assert out["x2"]["reason"] == "TRAIL_SL"
    assert out["x2"]["realized_R"] > 0


def test_x2_risk_admission_exactly_at_shared_budget_cap():
    bars = _bars([
        (100.0, 100.1, 99.9, 100.0),
        (100.0, 101.0, 100.9, 100.95),
        (100.95, 101.2, 100.8, 101.1),
        (101.1, 101.3, 101.0, 101.25),
        (101.8, 102.0, 101.1, 101.9),
    ])
    out = replay_x2_signal(_candidate(), bars, activation_price=0.5,
                           trail_distance_price=0.3, threshold_r=1.0)
    assert out["x2_status"] == "OPENED"
    assert out["x1_risk_at_x2_admission_usd"] == 0.0
    assert out["x2_admission_risk_usd"] == 100.0
    assert out["max_combined_open_risk_usd"] == 100.0


def test_next_open_through_x2_stop_is_rejected():
    bars = _threshold_path(1.0)
    bars[4]["open"] = 100.7
    out = replay_x2_signal(_candidate(), bars, activation_price=0.5,
                           trail_distance_price=0.3, threshold_r=1.0)
    assert out["x2"] is None
    assert out["x2_status"] == "SKIPPED"
    assert out["x2_skip_reason"] == "NEXT_OPEN_THROUGH_X2_STOP"
