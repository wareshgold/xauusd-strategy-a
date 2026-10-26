from dataclasses import dataclass
from enum import Enum

class TimelineStatus(str, Enum):
    ORDERED = "ORDERED"
    SAME_TIME_AMBIGUOUS = "SAME_TIME_AMBIGUOUS"
    TIME_REGRESSION = "TIME_REGRESSION"
    MISSING_TIME = "MISSING_TIME"
    DUPLICATE_EVENT_ID = "DUPLICATE_EVENT_ID"
    INVALID_EVENT_ID = "INVALID_EVENT_ID"

@dataclass(frozen=True)
class LifecycleEvent:
    event_id: str
    kind: str
    time_msc: int | None
    source_row: int

@dataclass(frozen=True)
class TimelineFinding:
    status: TimelineStatus
    event_ids: tuple[str, ...]
    source_rows: tuple[int, ...]
    time_msc: int | None
    detail: str

def audit_event_timeline(events):
    rows = tuple(events)
    findings = []
    seen = {}
    by_time = {}
    previous = None
    for event in rows:
        seen.setdefault(event.event_id, []).append(event)
        if not event.event_id:
            findings.append(TimelineFinding(TimelineStatus.INVALID_EVENT_ID, (event.event_id,), (event.source_row,), event.time_msc, "EMPTY_EVENT_ID"))
        if event.time_msc is None:
            findings.append(TimelineFinding(TimelineStatus.MISSING_TIME, (event.event_id,), (event.source_row,), None, "EVENT_TIMESTAMP_MISSING"))
        else:
            by_time.setdefault(event.time_msc, []).append(event)
            if previous is not None and previous.time_msc is not None and event.time_msc < previous.time_msc:
                findings.append(TimelineFinding(TimelineStatus.TIME_REGRESSION, (previous.event_id, event.event_id), (previous.source_row, event.source_row), event.time_msc, "INPUT_SEQUENCE_REGRESSION_PRESERVED"))
        previous = event
    for event_id, group in seen.items():
        if event_id and len(group) > 1:
            findings.append(TimelineFinding(TimelineStatus.DUPLICATE_EVENT_ID, tuple(e.event_id for e in group), tuple(e.source_row for e in group), group[0].time_msc, "DUPLICATE_NOT_REMOVED"))
    for stamp, group in by_time.items():
        if len(group) > 1:
            findings.append(TimelineFinding(TimelineStatus.SAME_TIME_AMBIGUOUS, tuple(e.event_id for e in group), tuple(e.source_row for e in group), stamp, "SAME_MILLISECOND_ORDER_UNRESOLVED"))
    if not findings:
        findings.append(TimelineFinding(TimelineStatus.ORDERED, tuple(e.event_id for e in rows), tuple(e.source_row for e in rows), rows[-1].time_msc if rows else None, "NO_ANOMALY_DETECTED_NOT_CAUSAL_PROOF"))
    return tuple(findings)
