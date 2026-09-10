from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .demo_recovery_fingerprint import RecoveryFingerprint, fingerprint


class AuditDecision(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RecoveryAuditBoundary:
    journal_valid: bool
    sequence_valid: bool
    state_recovered: bool
    replay_deterministic: bool
    event_count: int


def decide_audit(value: RecoveryAuditBoundary) -> AuditDecision:
    if value.event_count < 1:
        return AuditDecision.UNKNOWN
    if not value.journal_valid or not value.sequence_valid:
        return AuditDecision.BLOCK
    if not value.state_recovered or not value.replay_deterministic:
        return AuditDecision.BLOCK
    return AuditDecision.PASS


def stable_fingerprint(value: RecoveryFingerprint) -> str:
    return fingerprint(value)
