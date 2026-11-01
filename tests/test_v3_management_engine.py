import pytest

from strategy_factory.v3_management_engine import (
    V3ManagementReplayEngine, normalize_management_spec, replay_management_trade,
)
from strategy_factory.v3_exit_engine import V3ExitEngineError


def candidate():
    return {"entry_idx": 0, "theoretical_entry": 100.0, "risk": 5.0, "sl": 95.0,
            "direction": "BUY", "trigger_time": 1800000000, "signal_time_utc": "t0"}


def bars(rows):
    return tuple({"time": 1800000000 + i * 60, "open": o, "high": h, "low": l, "close": c}
                 for i, (o, h, l, c) in enumerate(rows))


def run(spec, rows):
    return replay_management_trade(candidate(), bars(rows), normalize_management_spec(spec),
                                   mt5_point=0.01, contract_size=100, volume=0.01)


def test_fixed_rr_and_no_target_are_distinct_and_reproducible():
    data = [(100, 100, 100, 100), (100, 111, 94, 105)]
    fixed = run({"mode": "FIXED_RR", "rr": 2}, data)
    no_target = run({"mode": "NO_TARGET"}, data)
    assert fixed["reason"] == "SL_AND_TP_SAME_BAR" and fixed["ambiguous"]
    assert no_target["reason"] == "SL" and no_target["realized_usd"] == -5.0


def test_break_even_update_only_applies_from_next_completed_bar():
    data = [(100, 100, 100, 100), (100, 106, 99.5, 105), (105, 106, 99.9, 101)]
    row = run({"mode": "BREAK_EVEN", "rr": 10, "activation_r": 1}, data)
    assert row["break_even_activated"] is True
    assert row["reason"] == "BREAK_EVEN_SL"
    assert row["realized_R"] == 0


def test_r_trailing_and_time_exit():
    trail = run({"mode": "TRAILING_R", "rr": 10, "activation_r": 1, "distance_r": 0.5},
                [(100, 100, 100, 100), (100, 106, 101, 105), (105, 106, 102, 103)])
    timed = run({"mode": "TIME_EXIT", "max_bars": 2},
                [(100, 100, 100, 100), (100, 102, 99, 101), (101, 103, 100, 102)])
    assert trail["reason"] == "TRAIL_SL"
    assert timed["reason"] == "TIME_EXIT" and timed["bars_held"] == 2


def test_invalid_management_parameters_fail_closed():
    with pytest.raises(V3ExitEngineError):
        normalize_management_spec({"mode": "TRAILING_R", "activation_r": 1})
    with pytest.raises(V3ExitEngineError):
        normalize_management_spec({"mode": "TIME_EXIT", "max_bars": 0})


def test_management_engine_pairs_same_frozen_population():
    data = bars([(100, 100, 100, 100), (100, 106, 99.5, 105), (105, 106, 99.9, 101)])
    engine = V3ManagementReplayEngine(bars=data, population=[candidate()], mt5_point=.01,
                                      contract_size=100, volume=.01, session_fingerprint="fixed-session")
    a = engine.evaluate({"mode": "FIXED_RR", "rr": 10})
    b = engine.evaluate({"mode": "BREAK_EVEN", "rr": 10, "activation_r": 1})
    assert engine.compare(a, b)["paired_trade_count"] == 1
