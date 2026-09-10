from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HealthState(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class DemoHealth:
    state: HealthState
    journal_ok: bool
    reconciliation_ok: bool
    connected: bool
    detail: str = ""


def evaluate_health(*, journal_ok: bool, reconciliation_ok: bool, connected: bool) -> DemoHealth:
    if not journal_ok:
        return DemoHealth(HealthState.BLOCKED, journal_ok, reconciliation_ok, connected, "journal integrity failure")
    if not connected or not reconciliation_ok:
        return DemoHealth(HealthState.DEGRADED, journal_ok, reconciliation_ok, connected, "execution prerequisites not satisfied")
    return DemoHealth(HealthState.HEALTHY, journal_ok, reconciliation_ok, connected)
