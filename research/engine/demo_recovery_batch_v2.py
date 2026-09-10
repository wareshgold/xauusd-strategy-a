from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .demo_recovery_batch_audit import BatchDecision


class ProductionDecision(str, Enum):
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class BatchProductionBoundary:
    audit_decision: BatchDecision


def production_decision(value: BatchProductionBoundary) -> ProductionDecision:
    # Recovery auditing never authorizes production execution.
    return ProductionDecision.BLOCK
