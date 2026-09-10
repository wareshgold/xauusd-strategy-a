from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .demo_recovery_fingerprint import RecoveryFingerprint, fingerprint


class BatchDecision(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    REQUIRE_REVIEW = "REQUIRE_REVIEW"


@dataclass(frozen=True)
class BatchAudit:
    decisions: tuple[BatchDecision, ...]
    fingerprints: tuple[str, ...]

    @property
    def deterministic(self) -> bool:
        return len(set(self.fingerprints)) == len(self.fingerprints)


def audit_batch(states: list[RecoveryFingerprint]) -> BatchAudit:
    fps = tuple(fingerprint(state) for state in states)
    decisions = tuple(BatchDecision.PASS for _ in states)
    return BatchAudit(decisions, fps)


def guard_batch(*, journal_valid: bool, sequence_valid: bool, recovered: bool, reconciliation_match: bool) -> BatchDecision:
    if not journal_valid or not sequence_valid:
        return BatchDecision.BLOCK
    if not recovered or not reconciliation_match:
        return BatchDecision.REQUIRE_REVIEW
    return BatchDecision.PASS
