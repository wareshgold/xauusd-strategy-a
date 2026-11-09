from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from strategy_factory.v3_management_engine import normalize_management_spec, replay_management_trade
from strategy_factory.v3_step_lock_engine import replay_step_lock_no_tp
from run_sp2l_v3_offline_management_matrix import build_specs, replay_step_lock_with_tp


def candidate():
    return {
        "entry_idx": 0, "theoretical_entry": 100.0, "risk": 5.0, "sl": 95.0,
        "direction": "BUY", "trigger_time": 1800000000,
        "signal_time_utc": "2027-01-15T08:00:00+00:00",
    }


def bars(rows):
    return tuple({
        "time": 1800000000 + i * 60,
        "open": o, "high": h, "low": l, "close": c,
    } for i, (o, h, l, c) in enumerate(rows))


def test_grid_is_single_batch_with_expected_variant_count_and_unique_specs():
    specs = build_specs()
    assert len(specs) == 261
    labels = [row["label"] for row in specs]
    assert len(labels) == len(set(labels))
    assert sum(row["family"] == "TRAILING_NO_TP" for row in specs) == 110
    assert sum(row["family"] == "FIXED_TP4_PLUS_TRAILING" for row in specs) == 110


def test_no_target_break_even_and_zero_activation_trailing_are_valid():
    be = normalize_management_spec({
        "mode": "BREAK_EVEN", "rr": None, "activation_r": 1.0, "offset_r": 0.0,
    })
    trail = normalize_management_spec({
        "mode": "TRAILING_R", "rr": None, "activation_r": 0.0, "distance_r": 0.5,
    })
    hybrid = normalize_management_spec({
        "mode": "BREAK_EVEN_TRAILING", "rr": None, "be_activation_r": 0.5,
        "be_offset_r": 0.0, "trail_activation_r": 1.0, "trail_distance_r": 0.5,
    })
    assert be["rr"] is None
    assert trail["activation_r"] == 0.0
    assert hybrid["rr"] is None

    result = replay_management_trade(
        candidate(), bars([(100, 100, 100, 100), (100, 106, 101, 105)]),
        trail, mt5_point=0.01, contract_size=100, volume=0.01,
    )
    assert result["initial_tp"] is None
    assert result["trailing_activated"] is True


def test_step_lock_no_tp_locks_to_break_even_then_exits_next_bar():
    result = replay_step_lock_no_tp(
        candidate(),
        bars([(100, 100, 100, 100), (100, 106, 101, 105), (105, 106, 99.9, 101)]),
        contract_size=100, volume=0.01,
    )
    assert result["reason"] == "STEP_LOCK_SL"
    assert result["realized_R"] == 0.0
    assert result["highest_milestone_R"] == 1


def test_step_lock_with_tp_exits_at_target():
    result = replay_step_lock_with_tp(
        candidate(), list(bars([(100, 100, 100, 100), (100, 111, 99, 110)])),
        rr=2.0, contract_size=100, volume=0.01,
    )
    assert result["reason"] == "TP"
    assert result["realized_R"] == 2.0
    assert result["ambiguous"] is False


def test_step_lock_with_tp_flags_same_bar_stop_and_target_as_ambiguous():
    result = replay_step_lock_with_tp(
        candidate(), list(bars([(100, 100, 100, 100), (100, 111, 94, 105)])),
        rr=2.0, contract_size=100, volume=0.01,
    )
    assert result["reason"] == "SL_AND_TP_SAME_BAR"
    assert result["ambiguous"] is True
    assert result["realized_R"] is None


def test_runner_source_has_no_mt5_connection_or_live_runner_dependency():
    source = (ROOT / "scripts" / "run_sp2l_v3_offline_management_matrix.py").read_text(encoding="utf-8")
    assert "import MetaTrader5" not in source
    assert "mt5.initialize" not in source
    assert "order_send" not in source
    assert "live_runner" in source
