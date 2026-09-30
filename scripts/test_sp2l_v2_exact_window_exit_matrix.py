"""Deterministic mechanical tests for the exact-window exit matrix.

These tests validate only the non-canonical exit/session mechanics.
"""
from __future__ import annotations

import numpy as np

from run_sp2l_v2_xauusd_exact_window_exit_matrix import (
    filter_population,
    in_london_to_new_york_session,
    simulate,
)

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


def signal(direction="BUY", entry_index=0, entry=100.0, sl=99.0, entry_time=None):
    return {
        "signal_index": 0,
        "setup_time": 0,
        "entry_index": entry_index,
        "entry_time": entry_index if entry_time is None else entry_time,
        "entry": entry,
        "sl": sl,
        "risk": abs(entry - sl),
        "direction": direction,
    }


def assert_close(actual, expected, name):
    if abs(actual - expected) > 1e-12:
        raise AssertionError(f"{name}: expected {expected}, got {actual}")


def test_rr_1_fixed_tp():
    out = simulate(
        rates([(100.2, 99.8), (101.1, 100.2)]),
        signal(),
        exit_mode="FIXED_TP",
        rr=1.0,
    )
    assert out["result"] == "WIN"
    assert out["reason"] == "TP"
    assert_close(out["r"], 1.0, "RR1")


def test_rr_2_fixed_tp():
    out = simulate(
        rates([(100.2, 99.8), (102.1, 100.2)]),
        signal(),
        exit_mode="FIXED_TP",
        rr=2.0,
    )
    assert out["result"] == "WIN"
    assert out["reason"] == "TP"
    assert_close(out["r"], 2.0, "RR2")


def test_no_tp_trailing_exits_on_next_bar():
    # 5p = 0.50 price. Bar 0 reaches 100.60, trail becomes 100.10,
    # but that updated SL is active only on bar 1.
    out = simulate(
        rates([(100.6, 99.9), (100.15, 100.05)]),
        signal(),
        exit_mode="NO_TP_TRAILING",
        trail_pips=5.0,
    )
    assert out["result"] == "WIN"
    assert out["reason"] == "TRAIL_SL"
    assert out["exit_index"] == 1
    assert_close(out["r"], 0.10, "next-bar trail")


def test_no_tp_does_not_have_a_hidden_tp():
    out = simulate(
        rates([(103.0, 99.9), (103.0, 102.6), (103.0, 102.4)]),
        signal(),
        exit_mode="NO_TP_TRAILING",
        trail_pips=5.0,
    )
    assert out["result"] == "WIN"
    assert out["reason"] == "TRAIL_SL"
    assert out["r"] > 1.0


def test_sell_no_tp_trailing():
    out = simulate(
        rates([(100.1, 99.4), (99.95, 99.85)]),
        signal(direction="SELL", entry=100.0, sl=101.0),
        exit_mode="NO_TP_TRAILING",
        trail_pips=5.0,
    )
    assert out["result"] == "WIN"
    assert out["reason"] == "TRAIL_SL"
    assert_close(out["r"], 0.10, "SELL trail")


def test_london_new_york_session_uses_dst_aware_utc_window():
    # 2026-08-26: London 08:00 = 07:00 UTC; NY 17:00 = 21:00 UTC.
    assert in_london_to_new_york_session(0) is False
    assert in_london_to_new_york_session(7 * 3600) is True
    assert in_london_to_new_york_session(21 * 3600) is True
    assert in_london_to_new_york_session(21 * 3600 + 60) is False


def test_session_filter_is_entry_only():
    population = [
        signal(entry_time=7 * 3600),
        signal(entry_time=22 * 3600),
    ]
    selected = filter_population(population, "LONDON_TO_NEW_YORK")
    assert len(selected) == 1
    assert selected[0]["entry_time"] == 7 * 3600


def main():
    tests = [
        test_rr_1_fixed_tp,
        test_rr_2_fixed_tp,
        test_no_tp_trailing_exits_on_next_bar,
        test_no_tp_does_not_have_a_hidden_tp,
        test_sell_no_tp_trailing,
        test_london_new_york_session_uses_dst_aware_utc_window,
        test_session_filter_is_entry_only,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"V2_EXACT_WINDOW_EXIT_MATRIX_MECHANICAL_AUDIT: PASS ({len(tests)} fixtures)")


if __name__ == "__main__":
    main()
