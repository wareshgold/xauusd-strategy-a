"""Tests for deterministic forward/backtest reconciliation."""

from scripts.reconcile_sp2l_forward_backtest import reconcile


def row(t, direction, entry, sl, tp):
    return {
        "trigger_time": t,
        "direction": direction,
        "theoretical_entry": entry,
        "sl": sl,
        "tp": tp,
    }


def test_exact_and_timestamp_mismatch_are_distinct():
    forward = [
        row("2026-09-24T08:48:00Z", "BUY", 4284.00, 4281.00, 4287.00),
        row("2026-09-24T10:32:00Z", "SELL", 4248.92, 4249.28, 4248.56),
    ]
    backtest = [
        row("2026-09-24T08:48:00Z", "BUY", 4284.00, 4281.00, 4287.00),
        row("2026-09-24T13:31:00Z", "SELL", 4248.92, 4249.28, 4248.56),
    ]

    result = reconcile(forward, backtest)

    assert result["classification_counts"] == {
        "EXACT_MATCH": 1,
        "PRICE_MATCH_TIMESTAMP_MISMATCH": 1,
    }


def test_count_equality_does_not_imply_reproducibility():
    forward = [row("A", "BUY", 100, 99, 101)]
    backtest = [row("B", "BUY", 100, 99, 101)]

    result = reconcile(forward, backtest)

    assert result["forward_count"] == result["backtest_count"] == 1
    assert result["classification_counts"] == {
        "PRICE_MATCH_TIMESTAMP_MISMATCH": 1,
    }
