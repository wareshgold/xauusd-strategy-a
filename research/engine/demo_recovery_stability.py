from __future__ import annotations

from dataclasses import dataclass

from .demo_recovery_fingerprint import RecoveryFingerprint, fingerprint
from .demo_recovery_guard import RecoveryGuardDecision, RecoveryGuardInput, guard_recovery


@dataclass(frozen=True)
class RecoveryStability:
    fingerprints: tuple[str, ...]

    @property
    def stable(self) -> bool:
        return bool(self.fingerprints) and len(set(self.fingerprints)) == 1


def repeated_fingerprint(value: RecoveryFingerprint, repetitions: int) -> RecoveryStability:
    if repetitions < 1:
        raise ValueError("repetitions must be positive")
    return RecoveryStability(tuple(fingerprint(value) for _ in range(repetitions)))


def recovery_gate(value: RecoveryGuardInput) -> RecoveryGuardDecision:
    return guard_recovery(value)
