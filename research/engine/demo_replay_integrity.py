from __future__ import annotations

from dataclasses import dataclass

from .demo_recovery_fingerprint import RecoveryFingerprint, fingerprint


@dataclass(frozen=True)
class ReplayIntegrity:
    before: str
    after: str

    @property
    def deterministic(self) -> bool:
        return self.before == self.after


def compare_recovery(before: RecoveryFingerprint, after: RecoveryFingerprint) -> ReplayIntegrity:
    return ReplayIntegrity(fingerprint(before), fingerprint(after))
