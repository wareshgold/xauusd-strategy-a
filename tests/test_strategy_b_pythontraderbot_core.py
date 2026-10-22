"""Synthetic, offline-only tests for the Strategy B source-aligned core."""
from scripts.strategy_b_pythontraderbot_core import (
    Setup,
    StrategyBConfig,
    detect_setup,
    evaluate_pending_entry,
)


def buy_fixture():
    return [
        {"time": 0, "open": 98.0, "high": 99.0, "low": 97.0, "close": 98.0},
        {"time": 1, "open": 99.0, "high": 100.0, "low": 98.0, "close": 99.0},
        {"time": 2, "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0},
        {"time": 3, "open": 101.5, "high": 111.0, "low": 101.0, "close": 105.5},
        {"time": 4, "open": 106.0, "high": 108.0, "low": 105.0, "close": 107.0},
        {"time": 5, "open": 106.0, "high": 108.0, "low": 104.0, "close": 107.0},
    ]


def sell_fixture():
    return [
        {"time": 0, "open": 112.0, "high": 113.0, "low": 111.0, "close": 112.0},
        {"time": 1, "open": 111.0, "high": 112.0, "low": 110.0, "close": 111.0},
        {"time": 2, "open": 110.0, "high": 111.0, "low": 108.0, "close": 109.0},
        {"time": 3, "open": 108.5, "high": 109.0, "low": 104.0, "close": 104.5},
        {"time": 4, "open": 104.0, "high": 104.5, "low": 102.5, "close": 103.0},
        {"time": 5, "open": 104.0, "high": 105.0, "low": 102.5, "close": 103.0},
    ]


def test_source_buy_geometry_detects_forming_candle_setup():
    candles = buy_fixture()
    candles[-1]["low"] = 103.9
    setup = detect_setup(candles, broker_point=0.01)
    assert setup is not None
    assert setup.direction == "BUY"
    assert setup.setup_time == 5
    assert setup.sl == 99.0
    assert setup.spike_body == 4.0


def test_source_sell_geometry_detects_forming_candle_setup():
    candles = sell_fixture()
    candles[-1]["high"] = 105.1
    setup = detect_setup(candles, broker_point=0.01)
    assert setup is not None
    assert setup.direction == "SELL"
    assert setup.setup_time == 5
    assert setup.sl == 111.0
    assert setup.spike_body == 4.0


def test_p_gap_is_points_times_actual_symbol_point_and_comparison_is_strict():
    candles = buy_fixture()
    candles[-1]["low"] = 103.9
    # high[-4] = 102, point gap = 100 * .01 = 1; exact boundary is not > 103.
    candles[-2]["low"] = 103.0
    assert detect_setup(candles, broker_point=0.01) is None


def test_pending_buy_entry_tp_and_max_sl_are_source_shaped():
    candles = buy_fixture()
    candles[-1]["low"] = 103.9
    setup = detect_setup(candles, broker_point=0.01)
    assert setup is not None
    candles.append({
        "time": 6, "open": 106.0, "high": 107.0, "low": 103.8, "close": 106.5
    })
    cfg = StrategyBConfig(use_ema_filter=False, use_trend_filter=False)
    candidate = evaluate_pending_entry(candles, setup, broker_point=0.01, config=cfg)
    assert candidate is not None and candidate != "INVALID"
    assert candidate.direction == "BUY"
    assert candidate.entry == 103.8
    assert candidate.sl == 99.0
    assert abs(candidate.risk - 4.8) < 1e-9
    assert abs(candidate.tp - (103.8 + 0.9 * 4.8)) < 1e-9


def test_pending_entry_keeps_setup_when_risk_is_nonpositive():
    candles = buy_fixture()
    candles[-1]["low"] = 103.9
    setup = Setup("BUY", 5, 5, 104.0, 4.0)
    candles.append({
        "time": 6, "open": 106.0, "high": 107.0, "low": 103.8, "close": 106.5
    })
    cfg = StrategyBConfig(use_ema_filter=False, use_trend_filter=False)
    assert evaluate_pending_entry(candles, setup, broker_point=0.01, config=cfg) is None
