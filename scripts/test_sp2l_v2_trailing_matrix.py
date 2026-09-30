"""Deterministic mechanical audit for the V2 forensic trailing simulator.

NON_CANONICAL_FORENSIC test only. These fixtures validate execution semantics,
not Strategy A geometry or trading rules.
"""
from __future__ import annotations

import numpy as np

from run_sp2l_v2_xauusd_3month_rr_trailing_matrix import simulate


DTYPE = [
    ("time", "i8"),
    ("open", "f8"),
    ("high", "f8"),
    ("low", "f8"),
    ("close", "f8"),
]


def rates(rows):
    out = np.zeros(len(rows), dtype=DTYPE)
    for i, (high, low) in enumerate(rows):
        out[i] = (i, 100.0, high, low, 100.0)
    return out


def signal(direction="BUY", entry_index=0, entry=100.0, sl=99.0):
    return {
        "signal_index": 0,
        "direction": direction,
        "setup_time": 0,
        "entry_index": entry_index,
        "entry_time": entry_index,
        "entry": entry,
        "sl": sl,
        "risk": abs(entry - sl),
    }


def assert_close(actual, expected, name):
    if abs(actual - expected) > 1e-12:
        raise AssertionError(f"{name}: expected {expected}, got {actual}")


def test_tp_without_trailing():
    r = rates([(100.4, 99.8), (101.1, 100.2)])
    out = simulate(r, signal(), rr=1.0, trail_pips=5.0)
    assert out["result"] == "WIN"
    assert out["reason"] == "TP"
    assert_close(out["r"], 1.0, "tp R")
    assert out["trailing_activated"] is False


def test_same_bar_sl_tp_is_ambiguous():
    r = rates([(101.1, 98.9)])
    out = simulate(r, signal(), rr=1.0, trail_pips=5.0)
    assert out["result"] == "AMBIGUOUS"
    assert out["reason"] == "SL_AND_TP_SAME_BAR"


def test_trailing_activates_only_after_favorable_move_and_next_bar_exit():
    # 5 pips = 0.50 price. Bar 0 reaches 100.60, activating trailing.
    # The resulting SL is 100.10, but must NOT be active on bar 0.
    r = rates([(100.6, 99.9), (100.15, 100.05)])
    out = simulate(r, signal(), rr=3.0, trail_pips=5.0)
    assert out["result"] == "WIN"
    assert out["reason"] == "TRAIL_SL"
    assert_close(out["r"], 0.10, "next-bar trailing R")
    assert out["exit_index"] == 1
    assert out["trailing_activated"] is True


def test_trailing_never_moves_backward_for_buy():
    # First favorable extreme activates at 100.70 -> SL 100.20.
    # Later high is lower; SL must remain 100.20.
    r = rates([(100.7, 99.9), (100.65, 100.15), (100.25, 100.19)])
    out = simulate(r, signal(), rr=5.0, trail_pips=5.0)
    assert out["result"] == "WIN"
    assert out["reason"] == "TRAIL_SL"
    assert_close(out["r"], 0.20, "monotonic BUY trailing R")


def test_sell_trailing_direction_and_next_bar_activation():
    # 5 pips = 0.50. Bar 0 reaches 99.40, activating SELL trail at 99.90.
    r = rates([(100.1, 99.4), (99.95, 99.85)])
    out = simulate(r, signal("SELL", entry=100.0, sl=101.0), rr=3.0, trail_pips=5.0)
    assert out["result"] == "WIN"
    assert out["reason"] == "TRAIL_SL"
    assert_close(out["r"], 0.10, "SELL next-bar trailing R")
    assert out["exit_index"] == 1
    assert out["trailing_activated"] is True


def test_trailing_does_not_extend_tp():
    # RR=1 TP is 101.0. Even after a large favorable move, TP remains 101.0.
    r = rates([(100.7, 99.9), (101.05, 100.5)])
    out = simulate(r, signal(), rr=1.0, trail_pips=5.0)
    assert out["result"] == "WIN"
    assert out["reason"] == "TP"
    assert_close(out["r"], 1.0, "fixed TP R")


def main():
    tests = [
        test_tp_without_trailing,
        test_same_bar_sl_tp_is_ambiguous,
        test_trailing_activates_only_after_favorable_move_and_next_bar_exit,
        test_trailing_never_moves_backward_for_buy,
        test_sell_trailing_direction_and_next_bar_activation,
        test_trailing_does_not_extend_tp,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"V2_TRAILING_MATRIX_MECHANICAL_AUDIT: PASS ({len(tests)} fixtures)")


if __name__ == "__main__":
    main()
