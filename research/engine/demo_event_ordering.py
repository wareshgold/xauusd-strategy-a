from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderedEvent:
    sequence: int
    event: object


class EventOrderGuard:
    def __init__(self) -> None:
        self._next_sequence = 1

    def accept(self, event: object, sequence: int) -> OrderedEvent:
        if sequence != self._next_sequence:
            raise ValueError(f"out-of-order event: expected {self._next_sequence}, got {sequence}")
        accepted = OrderedEvent(sequence, event)
        self._next_sequence += 1
        return accepted

    @property
    def next_sequence(self) -> int:
        return self._next_sequence
