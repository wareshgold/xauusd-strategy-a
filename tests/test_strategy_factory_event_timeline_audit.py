from strategy_factory.event_timeline_audit import (
    LifecycleEvent,
    TimelineStatus,
    audit_event_timeline,
)


def test_monotonic_distinct_timestamps_report_only_diagnostic_order():
    findings = audit_event_timeline([
        LifecycleEvent("e1", "ORDER_PLACED", 100, 1),
        LifecycleEvent("e2", "DEAL_IN", 101, 2),
    ])
    assert len(findings) == 1
    assert findings[0].status is TimelineStatus.ORDERED
    assert "NOT_PROOF_OF_CAUSAL_ORDER" in findings[0].detail


def test_same_millisecond_events_are_ambiguous_and_not_sorted():
    events = [
        LifecycleEvent("deal", "DEAL_IN", 100, 9),
        LifecycleEvent("order", "ORDER_UPDATE", 100, 4),
    ]
    findings = audit_event_timeline(events)
    same_time = next(x for x in findings if x.status is TimelineStatus.SAME_TIME_AMBIGUOUS)
    assert same_time.event_ids == ("deal", "order")
    assert same_time.source_rows == (9, 4)


def test_timestamp_regression_is_flagged_without_reordering():
    findings = audit_event_timeline([
        LifecycleEvent("later", "X", 200, 1),
        LifecycleEvent("earlier", "Y", 100, 2),
    ])
    regression = next(x for x in findings if x.status is TimelineStatus.TIME_REGRESSION)
    assert regression.event_ids == ("later", "earlier")
    assert regression.source_rows == (1, 2)


def test_missing_timestamp_is_not_inferred():
    findings = audit_event_timeline([LifecycleEvent("e1", "DEAL_IN", None, 1)])
    assert findings[0].status is TimelineStatus.MISSING_TIME


def test_duplicate_event_ids_are_reported_not_deduplicated():
    findings = audit_event_timeline([
        LifecycleEvent("e1", "DEAL_IN", 100, 1),
        LifecycleEvent("e1", "DEAL_OUT", 101, 2),
    ])
    duplicate = next(x for x in findings if x.status is TimelineStatus.DUPLICATE_EVENT_ID)
    assert duplicate.source_rows == (1, 2)


def test_empty_event_id_is_invalid():
    findings = audit_event_timeline([LifecycleEvent("", "UNKNOWN", 100, 1)])
    assert any(x.status is TimelineStatus.INVALID_EVENT_ID for x in findings)


def test_empty_input_is_explicitly_diagnostic_not_execution_evidence():
    findings = audit_event_timeline([])
    assert findings[0].status is TimelineStatus.ORDERED
    assert "NOT_PROOF_OF_CAUSAL_ORDER" in findings[0].detail
