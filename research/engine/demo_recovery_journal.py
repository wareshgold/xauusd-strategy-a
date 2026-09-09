from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RecoveryJournalEvent:
    sequence: int
    timestamp: datetime
    order_id: str
    event: str
    detail: str = ""


class RecoveryJournal:
    def __init__(self) -> None:
        self._events: list[RecoveryJournalEvent] = []

    def append(self, timestamp: datetime, order_id: str, event: str, detail: str = "") -> RecoveryJournalEvent:
        item = RecoveryJournalEvent(len(self._events) + 1, timestamp, order_id, event, detail)
        self._events.append(item)
        return item

    def events(self) -> tuple[RecoveryJournalEvent, ...]:
        return tuple(self._events)
