"""Unit tests for exit chronology and overlapping-trade diagnostics."""
import importlib
import sys
import types

# The matrix's pure simulation helpers do not need a live MT5 terminal.
sys.modules.setdefault("MetaTrader5", types.ModuleType("MetaTrader5"))
matrix = importlib.import_module("scripts.run_sp2l_v3_xauusd_trailing_matrix")


def test_summary_uses_exit_time_not_candidate_order():
    rows = [
        {"trigger_time": 1, "entry_time": 10, "exit_time": 30,
         "realized_R": 2.0, "ambiguous": False, "trailing_activated": True},
        {"trigger_time": 2, "entry_time": 15, "exit_time": 20,
         "realized_R": -1.0, "ambiguous": False, "trailing_activated": False},
        {"trigger_time": 3, "entry_time": 25, "exit_time": 40,
         "realized_R": -1.0, "ambiguous": False, "trailing_activated": True},
    ]

    result = matrix.summarize(rows, dataset_end_time=50)

    # Exit order is -1R, +2R, -1R; drawdown is 1R, not candidate-order 2R.
    assert result["net_R"] == 0.0
    assert result["max_drawdown_R"] == 1.0
    assert result["max_consecutive_losses"] == 1
    assert result["max_concurrent_independent_trades"] == 2
    assert "exit_time" in result["drawdown_basis"]


def test_simulation_records_actual_exit_bar_time_and_next_bar_trailing():
    bars = [
        {"time": 1, "high": 100.0, "low": 99.5},
        {"time": 2, "high": 100.10, "low": 100.00},
        {"time": 3, "high": 100.15, "low": 100.05},
    ]
    candidate = {
        "direction": "BUY",
        "trigger_time": 1,
        "theoretical_entry": 100.0,
        "sl": 99.0,
        "tp": 102.0,
        "risk": 1.0,
    }

    result = matrix.simulate_one(
        bars, candidate, entry_idx=0,
        activation_price=0.05, trail_distance_price=0.02,
    )

    assert result["entry_time"] == 1
    assert result["exit_time"] == 3
    assert result["reason"] == "TRAIL_SL"
    assert abs(result["exit_price"] - 100.08) < 1e-9
    assert result["realized_R"] > 0



def test_no_trailing_baseline_keeps_initial_sl_and_never_activates():
    bars = [
        {"time": 1, "high": 100.0, "low": 99.5},
        {"time": 2, "high": 100.2, "low": 98.9},
    ]
    candidate = {
        "direction": "BUY",
        "trigger_time": 1,
        "theoretical_entry": 100.0,
        "sl": 99.0,
        "tp": 102.0,
        "risk": 1.0,
    }

    result = matrix.simulate_one(
        bars, candidate, entry_idx=0,
        activation_price=None, trail_distance_price=None,
    )

    assert result["reason"] == "SL"
    assert result["final_sl"] == 99.0
    assert result["trailing_activated"] is False
    assert result["realized_R"] == -1.0


def test_zero_activation_still_applies_new_stop_from_next_bar():
    bars = [
        {"time": 1, "high": 100.0, "low": 99.5},
        {"time": 2, "high": 100.10, "low": 100.00},
        {"time": 3, "high": 100.15, "low": 100.05},
    ]
    candidate = {
        "direction": "BUY",
        "trigger_time": 1,
        "theoretical_entry": 100.0,
        "sl": 99.0,
        "tp": 102.0,
        "risk": 1.0,
    }

    result = matrix.simulate_one(
        bars, candidate, entry_idx=0,
        activation_price=0.00, trail_distance_price=0.02,
    )

    assert result["reason"] == "TRAIL_SL"
    assert abs(result["final_sl"] - 100.08) < 1e-9
    assert result["exit_time"] == 3
