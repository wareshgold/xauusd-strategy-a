"""Tests for USD activation and configured pip-price conversion."""
import sys
import types
sys.modules.setdefault("MetaTrader5", types.ModuleType("MetaTrader5"))
from scripts.run_sp2l_v3_xauusd_usd_activation_matrix import price_move_for_profit_usd, pip_distance_to_price


def test_usd_threshold_conversion_uses_contract_and_volume():
    assert price_move_for_profit_usd(0.5, 100, 0.01) == 0.5
    assert price_move_for_profit_usd(1.0, 100, 0.01) == 1.0
    assert price_move_for_profit_usd(3.0, 100, 0.01) == 3.0


def test_pip_distance_uses_explicit_configured_price_convention():
    assert pip_distance_to_price(5, 0.1) == 0.5
    assert pip_distance_to_price(50, 0.1) == 5.0


def test_invalid_conversion_inputs_fail_closed():
    import pytest
    with pytest.raises(ValueError):
        price_move_for_profit_usd(1.0, 0, 0.01)
    with pytest.raises(ValueError):
        pip_distance_to_price(5, 0)

def test_tp_exit_records_at_least_guaranteed_tp_mfe_without_intrabar_overshoot():
    import numpy as np
    from scripts import run_sp2l_v3_xauusd_trailing_matrix as engine

    bars = np.array([
        (1, 101.0, 99.0),
        (2, 111.0, 100.0),
        (3, 112.0, 101.0),
    ], dtype=[("time", "i8"), ("high", "f8"), ("low", "f8")])
    candidate = {
        "direction": "BUY", "theoretical_entry": 100.0, "sl": 95.0,
        "tp": 110.0, "risk": 5.0, "trigger_time": 1,
    }

    row = engine.simulate_one(bars, candidate, 0, None, None)

    assert row["reason"] == "TP"
    assert row["exit_time"] == 2
    assert row["max_favorable_price"] == 10.0
