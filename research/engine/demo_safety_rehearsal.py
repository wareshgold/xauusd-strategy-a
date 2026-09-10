from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .demo_observability import DemoHealth, HealthState


class RehearsalResult(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class SafetyRehearsal:
    health: DemoHealth
    result: RehearsalResult
    reason: str


def rehearse(health: DemoHealth) -> SafetyRehearsal:
    if health.state is not HealthState.HEALTHY:
        return SafetyRehearsal(health, RehearsalResult.BLOCK, health.detail or "health prerequisites not satisfied")
    return SafetyRehearsal(health, RehearsalResult.PASS, "all demo safety prerequisites satisfied")
