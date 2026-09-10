from __future__ import annotations

from dataclasses import dataclass

from .demo_observability import DemoHealth


@dataclass(frozen=True)
class DemoStatusReport:
    health: DemoHealth
    open_orders: int
    journal_events: int
    last_sequence: int | None


def build_report(health: DemoHealth, *, open_orders: int, journal_events: int, last_sequence: int | None) -> DemoStatusReport:
    if open_orders < 0 or journal_events < 0:
        raise ValueError("counts cannot be negative")
    return DemoStatusReport(health, open_orders, journal_events, last_sequence)
