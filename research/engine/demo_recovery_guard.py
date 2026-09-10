from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RecoveryGuardDecision(str, Enum):
    CONTINUE = "CONTINUE"
    BLOCK = "BLOCK"
    REQUIRE_REVIEW = "REQUIRE_REVIEW"


@dataclass(frozen=True)
class RecoveryGuardInput:
    journal_valid: bool
    sequence_valid: bool
    state_recovered: bool
    reconciliation_match: bool


def guard_recovery(value: RecoveryGuardInput) -> RecoveryGuardDecision:
    if not value.journal_valid or not value.sequence_valid:
        return RecoveryGuardDecision.BLOCK
    if not value.state_recovered or not value.reconciliation_match:
        return RecoveryGuardDecision.REQUIRE_REVIEW
    return RecoveryGuardDecision.CONTINUE
