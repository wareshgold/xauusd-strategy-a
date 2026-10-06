from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any

from .statistical_evidence import StatisticalEvidence, StatisticalEvidenceError
from .test_contract import DatasetRole


class StatisticalUsageError(ValueError):
    """Raised when statistical evidence violates dataset-role governance."""


class StatisticalUsageDisposition(str, Enum):
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class StatisticalUsage:
    evidence_fingerprint: str
    run_id: str
    dataset_id: str
    dataset_role: DatasetRole
    purpose: str
    disposition: StatisticalUsageDisposition
    fingerprint: str

    @staticmethod
    def _payload(values: dict[str, Any]) -> bytes:
        return json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

    def _fingerprint_payload(self) -> dict[str, Any]:
        return {
            "evidence_fingerprint": self.evidence_fingerprint,
            "run_id": self.run_id,
            "dataset_id": self.dataset_id,
            "dataset_role": self.dataset_role.value,
            "purpose": self.purpose,
            "disposition": self.disposition.value,
        }

    def validate(self) -> None:
        if not self.evidence_fingerprint or not self.run_id or not self.dataset_id:
            raise StatisticalUsageError("statistical usage identity is incomplete")
        if not self.purpose:
            raise StatisticalUsageError("statistical usage purpose is required")
        expected = hashlib.sha256(self._payload(self._fingerprint_payload())).hexdigest()
        if self.fingerprint != expected:
            raise StatisticalUsageError("statistical usage fingerprint mismatch")

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {**self._fingerprint_payload(), "fingerprint": self.fingerprint}


class StatisticalUsageLedger:
    """Role-isolation ledger for descriptive statistical evidence."""

    def __init__(self) -> None:
        self._entries: list[StatisticalUsage] = []

    def record(self, evidence: StatisticalEvidence, *, purpose: str) -> StatisticalUsage:
        evidence.validate()
        if not purpose:
            raise StatisticalUsageError("statistical usage purpose is required")

        role = DatasetRole(evidence.dataset_role)
        blocked_purposes = {"DEVELOPMENT", "OPTIMIZATION", "PARAMETER_FIT"}
        if role in (DatasetRole.UNTOUCHED_VALIDATION, DatasetRole.FRESH_HOLDOUT) and purpose in blocked_purposes:
            raise StatisticalUsageError(
                f"{role.value} statistical evidence cannot be used for {purpose}"
            )

        entry = StatisticalUsage(
            evidence_fingerprint=evidence.fingerprint,
            run_id=evidence.run_id,
            dataset_id=evidence.dataset_id,
            dataset_role=role,
            purpose=purpose,
            disposition=StatisticalUsageDisposition.ALLOWED,
            fingerprint="",
        )
        fingerprint = hashlib.sha256(StatisticalUsage._payload(entry._fingerprint_payload())).hexdigest()
        entry = StatisticalUsage(**{**entry.__dict__, "fingerprint": fingerprint})
        self._entries.append(entry)
        return entry

    def entries(self) -> tuple[StatisticalUsage, ...]:
        return tuple(self._entries)

    def assert_clean(self) -> None:
        for entry in self._entries:
            entry.validate()
            if entry.disposition is StatisticalUsageDisposition.BLOCKED:
                raise StatisticalUsageError("usage ledger contains blocked entries")

    def as_dict(self) -> list[dict[str, Any]]:
        return [entry.as_dict() for entry in self._entries]
