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
    assert out["x2"] is None or out["x2"]["entry"] == bars[5]["open"]


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
    assert out["x2_status"] == "CANCELLED"


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
