from scripts.sp2l_lifecycle_query_diagnostics import (
    query_snapshot_with_diagnostics,
)


def test_query_exception_is_reported_once_and_not_as_none():
    failures = []
    successes = []

    def operation():
        raise RuntimeError("history unavailable")

    result = query_snapshot_with_diagnostics(
        operation=operation,
        query="history_orders_get_for_pending_lifecycle",
        symbol="XAUUSD.ecn",
        log_failure=lambda *args: failures.append(args),
        mark_success=successes.append,
        last_error=lambda: "should-not-be-read",
    )

    assert result is None
    assert len(failures) == 1
    assert failures[0] == (
        "history_orders_get_for_pending_lifecycle",
        "XAUUSD.ecn",
        "RuntimeError: history unavailable",
    )
    assert successes == []


def test_none_snapshot_reports_mt5_last_error_once():
    failures = []
    successes = []

    result = query_snapshot_with_diagnostics(
        operation=lambda: None,
        query="history_orders_get_for_pending_lifecycle",
        symbol="XAUUSD.ecn",
        log_failure=lambda *args: failures.append(args),
        mark_success=successes.append,
        last_error=lambda: "(-1, 'terminal disconnected')",
    )

    assert result is None
    assert failures == [(
        "history_orders_get_for_pending_lifecycle",
        "XAUUSD.ecn",
        "MT5 returned None; last_error=(-1, 'terminal disconnected')",
    )]
    assert successes == []


def test_successful_snapshot_marks_query_healthy():
    failures = []
    successes = []
    snapshot = ({"ticket": 123},)

    result = query_snapshot_with_diagnostics(
        operation=lambda: snapshot,
        query="history_orders_get_for_pending_lifecycle",
        symbol="XAUUSD.ecn",
        log_failure=lambda *args: failures.append(args),
        mark_success=successes.append,
        last_error=lambda: "should-not-be-read",
    )

    assert result is snapshot
    assert failures == []
    assert successes == ["history_orders_get_for_pending_lifecycle"]
