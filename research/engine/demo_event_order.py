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
    ordered = tuple(sorted(events, key=lambda e: e.sequence))
    expected = 1
    previous_time = None
    for event in ordered:
        if event.sequence != expected:
            raise ValueError("event sequence is not contiguous")
        timestamp = event.timestamp.astimezone(timezone.utc)
        if previous_time is not None and timestamp < previous_time:
            raise ValueError("event timestamp moved backwards")
        previous_time = timestamp
        expected += 1
    return ordered
