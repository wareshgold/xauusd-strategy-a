from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class OrderedEvent:
    sequence: int
    timestamp: datetime
    event: str
    order_id: str


def order_events(events: list[OrderedEvent]) -> tuple[OrderedEvent, ...]:
    """Return events in authoritative sequence order.

    Sequence, not timestamp, defines event order. Timestamps are normalized to
    UTC for validation/inspection but are deliberately not used to reorder or
    reject a contiguous event stream.
    """
    ordered = tuple(sorted(events, key=lambda e: e.sequence))
    expected = 1
    for event in ordered:
        if event.sequence != expected:
            raise ValueError("event sequence is not contiguous")
        if event.timestamp.tzinfo is None or event.timestamp.utcoffset() is None:
            raise ValueError("event timestamp must be timezone-aware")
        event.timestamp.astimezone(timezone.utc)
        expected += 1
    return ordered
