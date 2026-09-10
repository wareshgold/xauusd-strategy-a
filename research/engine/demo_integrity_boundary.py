from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IntegrityDecision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class IntegrityCheck:
    journal_valid: bool
    sequence_valid: bool
    state_recovered: bool


def decide_integrity(check: IntegrityCheck) -> IntegrityDecision:
    if check.journal_valid and check.sequence_valid and check.state_recovered:
        return IntegrityDecision.ALLOW
    if not check.journal_valid or not check.sequence_valid:
        return IntegrityDecision.BLOCK
    return IntegrityDecision.UNKNOWN
