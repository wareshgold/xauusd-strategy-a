from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .demo_gate_safety import DemoExecutionDecision, DemoGateSafety
from .demo_reconciliation import ReconciliationResult, ReconciliationState


class RecoveryAction(str, Enum):
    CONTINUE = "CONTINUE"
    BLOCK = "BLOCK"
    REQUIRE_REVIEW = "REQUIRE_REVIEW"


@dataclass(frozen=True)
class RecoveryDecision:
    reconciliation: ReconciliationResult
    action: RecoveryAction
    execution: DemoExecutionDecision


def recover(safety: DemoGateSafety, reconciliation: ReconciliationResult) -> RecoveryDecision:
    if reconciliation.state is ReconciliationState.MATCH:
        execution = safety.decision(reconciliation)
        return RecoveryDecision(
            reconciliation,
            RecoveryAction.CONTINUE if execution is DemoExecutionDecision.ALLOW else RecoveryAction.BLOCK,
            execution,
        )
    return RecoveryDecision(reconciliation, RecoveryAction.REQUIRE_REVIEW, DemoExecutionDecision.BLOCK)
