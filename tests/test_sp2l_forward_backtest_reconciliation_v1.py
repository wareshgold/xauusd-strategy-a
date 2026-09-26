"""Synthetic fail-closed tests for SP2L reconciliation V1.

These fixtures test only the harness classifications. They do not define or
validate Strategy A geometry, timestamp normalization, session rules, or fill
semantics.
"""

from scripts.sp2l_forward_backtest_reconciliation import reconcile


def backtest_report():
    return {
        "research_session_filter": {"enabled": True},
        "signals_detail": [
            {
                "signal_time": 100,
                "direction": "BUY",
                "entry": 100.0,
                "sl": 99.0,
                "tp": 101.0,
            },
            {
                "signal_time": 200,
                "direction": "SELL",
                "entry": 200.0,
                "sl": 201.0,
                "tp": 199.0,
            },
        ],
    }


def event(signal_id, direction, entry, sl, tp, *events):
    rows = [{
        "event": "CANDIDATE",
        "signal_id": signal_id,
        "candidate": {
            "trigger_time": int(signal_id.split("_")[3]),
            "direction": direction,
            "theoretical_entry": entry,
            "sl": sl,
            "tp": tp,
        },
    }]
    rows.extend({"event": name, "signal_id": signal_id} for name in events)
    return rows


def test_exact_candidate_with_order_placed_is_match():
    events = event(
        "AUTHOR_REPLICA_FT_100_BUY",
        "BUY",
        100.0,
        99.0,
        101.0,
        "ORDER_ATTEMPT",
        "ORDER_PLACED",
    )
    result = reconcile(backtest_report(), events)
    assert result["classification_counts"]["MATCH"] == 1
    assert result["classification_counts"]["DATA_GAP"] == 1


def test_exact_candidate_without_execution_is_execution_mismatch():
    events = event(
        "AUTHOR_REPLICA_FT_100_BUY",
        "BUY",
        100.0,
        99.0,
        101.0,
        "ORDER_ATTEMPT",
    )
    result = reconcile(backtest_report(), events)
    row = next(x for x in result["rows"] if x["trigger_time_raw"] == 100)
    assert row["classification"] == "EXECUTION_MISMATCH"


def test_exact_candidate_with_different_levels_is_detector_mismatch():
    events = event(
        "AUTHOR_REPLICA_FT_100_BUY",
        "BUY",
        100.1,
        99.0,
        101.0,
        "ORDER_PLACED",
    )
    result = reconcile(backtest_report(), events)
    row = next(x for x in result["rows"] if x["trigger_time_raw"] == 100)
    assert row["classification"] == "DETECTOR_MISMATCH"


def test_nonmatching_forward_candidates_are_timestamp_unresolved_not_normalized():
    events = event(
        "AUTHOR_REPLICA_FT_999_BUY",
        "BUY",
        100.0,
        99.0,
        101.0,
        "ORDER_PLACED",
    )
    result = reconcile(backtest_report(), events)
    assert result["classification_counts"]["TIMESTAMP_UNRESOLVED"] == 2


def test_no_forward_candidates_is_data_gap():
    result = reconcile(backtest_report(), [])
    assert result["classification_counts"]["DATA_GAP"] == 2
