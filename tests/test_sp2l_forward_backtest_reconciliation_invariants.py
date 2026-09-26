"""Additional fail-closed invariants for SP2L reconciliation V1.

These tests protect identity/execution boundaries only. They do not establish
Strategy A geometry or execution semantics.
"""

from scripts.sp2l_forward_backtest_reconciliation import reconcile


def report(rows):
    return {"signals_detail": rows}


def candidate(t, direction="BUY", entry=100.0, sl=99.0, tp=101.0):
    return {
        "signal_time": t,
        "direction": direction,
        "entry": entry,
        "sl": sl,
        "tp": tp,
    }


def forward_candidate(t, direction="BUY", entry=100.0, sl=99.0, tp=101.0):
    return {
        "event": "CANDIDATE",
        "signal_id": f"AUTHOR_REPLICA_FT_{t}_{direction}",
        "candidate": {
            "trigger_time": t,
            "direction": direction,
            "theoretical_entry": entry,
            "sl": sl,
            "tp": tp,
        },
    }


def test_duplicate_forward_candidate_identity_is_not_silently_deduplicated():
    events = [
        forward_candidate(100),
        forward_candidate(100),
    ]
    result = reconcile(report([candidate(100)]), events)
    row = result["rows"][0]
    assert row["classification"] == "EXECUTION_MISMATCH"
    assert row["evidence_refs"]["forward_event_count"] == 2


def test_order_attempt_does_not_prove_fill():
    events = [
        forward_candidate(100),
        {
            "event": "ORDER_ATTEMPT",
            "signal_id": "AUTHOR_REPLICA_FT_100_BUY",
        },
    ]
    result = reconcile(report([candidate(100)]), events)
    row = result["rows"][0]
    assert row["classification"] == "EXECUTION_MISMATCH"
    assert row["fill_state"] == "unknown"


def test_order_placed_does_not_invent_fill_or_lifecycle():
    events = [
        forward_candidate(100),
        {
            "event": "ORDER_PLACED",
            "signal_id": "AUTHOR_REPLICA_FT_100_BUY",
        },
    ]
    result = reconcile(report([candidate(100)]), events)
    row = result["rows"][0]
    assert row["classification"] == "MATCH"
    assert row["fill_state"] == "unknown"
    assert row["lifecycle_state"] == "not_proven"


def test_explicit_session_disagreement_is_session_mismatch():
    historical = candidate(100)
    historical["session_eligible"] = True
    forward = forward_candidate(100)
    forward["session_eligible"] = False

    result = reconcile(report([historical]), [forward])
    row = result["rows"][0]
    assert row["classification"] == "SESSION_MISMATCH"
