from __future__ import annotations

from dataclasses import dataclass

from .demo_event_order import OrderedEvent, order_events


@dataclass(frozen=True)
class ReplayAudit:
    ordered: tuple[OrderedEvent, ...]
    valid: bool


def audit_replay(events: list[OrderedEvent]) -> ReplayAudit:
    ordered = order_events(events)
    return ReplayAudit(ordered=ordered, valid=True)
