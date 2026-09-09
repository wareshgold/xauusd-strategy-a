from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .gate_status import GateState, ResearchGateStatus, production_ready


class SafetyState(str, Enum):
    ARMED = "ARMED"
    KILLED = "KILLED"
    BLOCKED = "BLOCKED"


@dataclass
class ExecutionSafety:
    """Fail-closed safety gate for demo execution.

    The kill switch is independent of Strategy A geometry and defaults to KILLED.
    A demo order may execute only when the caller explicitly enables the safety
    state and the supplied research gate is fully production-ready.
    """

    state: SafetyState = SafetyState.KILLED

    def arm(self, status: ResearchGateStatus) -> None:
        if not production_ready(status):
            self.state = SafetyState.BLOCKED
            raise RuntimeError("execution gates are not production-ready")
        self.state = SafetyState.ARMED

    def kill(self) -> None:
        self.state = SafetyState.KILLED

    def allow_execution(self, status: ResearchGateStatus) -> bool:
        return self.state is SafetyState.ARMED and production_ready(status)


CURRENT_RESEARCH_STATUS = ResearchGateStatus(
    source_resolution=GateState.PARTIAL_PASS,
    synthetic_fixtures=GateState.PASS,
    frozen_geometry=GateState.BLOCKED,
    dev_validation=GateState.LOCKED,
    val_validation=GateState.LOCKED,
    fresh_holdout=GateState.LOCKED,
    production=GateState.LOCKED,
)
