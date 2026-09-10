from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256


@dataclass(frozen=True)
class RecoveryJournalEvent:
    sequence: int
    timestamp: datetime
    order_id: str
    event: str
    detail: str = ""
    previous_hash: str = ""

    def canonical(self) -> str:
        ts = self.timestamp.astimezone(timezone.utc).isoformat()
        return f"{self.sequence}|{ts}|{self.order_id}|{self.event}|{self.detail}|{self.previous_hash}"

    @property
    def event_hash(self) -> str:
        return sha256(self.canonical().encode("utf-8")).hexdigest()


class RecoveryJournal:
    def __init__(self) -> None:
        self._events: list[RecoveryJournalEvent] = []

    def append(self, timestamp: datetime, order_id: str, event: str, detail: str = "") -> RecoveryJournalEvent:
        if self._events and timestamp < self._events[-1].timestamp:
            raise ValueError("journal timestamp moved backwards")
        previous = self._events[-1].event_hash if self._events else ""
        item = RecoveryJournalEvent(len(self._events) + 1, timestamp, order_id, event, detail, previous)
        self._events.append(item)
        return item

    def events(self) -> tuple[RecoveryJournalEvent, ...]:
        return tuple(self._events)

    def verify(self) -> bool:
        previous = ""
        last_timestamp: datetime | None = None
        for expected_sequence, item in enumerate(self._events, 1):
            if item.sequence != expected_sequence or item.previous_hash != previous:
                return False
            if last_timestamp is not None and item.timestamp < last_timestamp:
                return False
            if item.event_hash != sha256(item.canonical().encode("utf-8")).hexdigest():
                return False
            previous = item.event_hash
            last_timestamp = item.timestamp
        return True
