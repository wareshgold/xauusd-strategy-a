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
    ordered = tuple(sorted(events, key=lambda e: (e.timestamp.astimezone(timezone.utc), e.sequence)))
    expected = 1
    for event in ordered:
        if event.sequence != expected:
            raise ValueError("event sequence is not contiguous")
        expected += 1
    return ordered
