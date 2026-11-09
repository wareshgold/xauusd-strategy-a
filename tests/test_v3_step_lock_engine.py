import pytest

from strategy_factory.v3_step_lock_engine import replay_step_lock_no_tp
from strategy_factory.v3_exit_engine import V3ExitEngineError


def candidate(direction="BUY"):
    if direction == "BUY":
        entry, stop = 100.0, 95.0
    else:
        entry, stop = 100.0, 105.0
    return {"entry_idx": 0, "theoretical_entry": entry, "risk": 5.0, "sl": stop,
            "direction": direction, "trigger_time": 1800000000, "signal_time_utc": "t0"}


def bars(rows):
    return tuple({"time": 1800000000 + i * 60, "open": o, "high": h, "low": l, "close": c}
                 for i, (o, h, l, c) in enumerate(rows))


def run(rows, direction="BUY"):
    return replay_step_lock_no_tp(candidate(direction), bars(rows), contract_size=100, volume=0.01)


def test_step_lock_moves_to_entry_then_previous_milestone():
    # Bar 1 reaches +1R; bar 2 reaches +2R; bar 3 touches the +1R locked stop.
    row = run([
        (100, 100, 100, 100),
        (100, 106, 101, 105),
        (105, 111, 102, 110),
        (110, 111, 104.9, 106),
    ])
    assert row["highest_milestone_R"] == 2
    assert row["final_sl"] == 105
    assert row["reason"] == "STEP_LOCK_SL"
    assert row["realized_R"] == 1


def test_multiple_milestones_in_one_bar_lock_highest_crossed_level():
    row = run([(100, 100, 100, 100), (100, 116, 101, 115)])
    assert row["highest_milestone_R"] == 3
    assert row["final_sl"] == 110
    assert row["reason"] == "OPEN_OR_UNRESOLVED"
    assert row["initial_tp"] is None
    assert row["realized_R"] is None


def test_active_stop_and_new_milestone_same_bar_is_ambiguous():
    row = run([
        (100, 100, 100, 100),
        (100, 106, 101, 105),
        (105, 111, 99, 105),
    ])
    assert row["ambiguous"] is True
    assert row["reason"] == "ACTIVE_SL_AND_NEW_MILESTONE_SAME_BAR"
    assert row["realized_R"] is None


def test_sell_side_is_symmetric():
    row = run([
        (100, 100, 100, 100),
        (100, 99, 94, 95),
        (95, 98, 89, 90),
        (90, 95, 89, 94),
    ], direction="SELL")
    assert row["highest_milestone_R"] == 2
    assert row["final_sl"] == 95
    assert row["reason"] == "STEP_LOCK_SL"
    assert row["realized_R"] == 1


def test_entry_bar_is_excluded_and_no_final_tp():
    row = run([(100, 120, 80, 100)])
    assert row["bars_held"] == 0
    assert row["reason"] == "OPEN_OR_UNRESOLVED"
    assert row["initial_tp"] is None


def test_gap_while_open_is_ambiguous():
    row = replay_step_lock_no_tp(
        candidate(),
        (
            {"time": 1800000000, "open": 100, "high": 100, "low": 100, "close": 100},
            {"time": 1800000180, "open": 100, "high": 106, "low": 101, "close": 105},
        ),
        contract_size=100, volume=0.01,
    )
    assert row["ambiguous"] is True
    assert row["reason"] == "M1_GAP_WHILE_OPEN"


def test_frozen_risk_and_stop_direction_are_validated():
    bad_risk = candidate()
    bad_risk["risk"] = 4.0
    with pytest.raises(V3ExitEngineError):
        replay_step_lock_no_tp(bad_risk, bars([(100, 100, 100, 100)]), contract_size=100, volume=0.01)
    bad_stop = candidate()
    bad_stop["sl"] = 105.0
    with pytest.raises(V3ExitEngineError):
        replay_step_lock_no_tp(bad_stop, bars([(100, 100, 100, 100)]), contract_size=100, volume=0.01)
