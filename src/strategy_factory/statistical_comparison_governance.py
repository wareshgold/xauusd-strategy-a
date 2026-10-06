from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json

from .statistical_comparison_evidence import (
    StatisticalComparisonEvidence,
    StatisticalComparisonEvidenceError,
)
from .statistical_comparison_evidence_ledger import (
    StatisticalComparisonEvidenceLedger,
    StatisticalComparisonEvidenceLedgerError,
)
from .test_contract import DatasetRole


class StatisticalComparisonUsageError(ValueError):
    """Raised when comparison evidence violates dataset-role governance."""


class StatisticalComparisonUsageDisposition(str, Enum):
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class StatisticalComparisonUsage:
    evidence_fingerprint: str
    comparison_fingerprint: str
    dataset_role: DatasetRole
    purpose: str
    disposition: StatisticalComparisonUsageDisposition
    fingerprint: str

    @staticmethod
    def _payload(values: dict[str, object]) -> bytes:
        return json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

    def _fingerprint_payload(self) -> dict[str, object]:
        return {
            "evidence_fingerprint": self.evidence_fingerprint,
            "comparison_fingerprint": self.comparison_fingerprint,
            "dataset_role": self.dataset_role.value,
            "purpose": self.purpose,
            "disposition": self.disposition.value,
        }

    def validate(self) -> None:
        if not self.evidence_fingerprint or not self.comparison_fingerprint:
            raise StatisticalComparisonUsageError("comparison usage identity is incomplete")
        if not self.purpose:
            raise StatisticalComparisonUsageError("comparison usage purpose is required")
        expected = hashlib.sha256(self._payload(self._fingerprint_payload())).hexdigest()
        if self.fingerprint != expected:
            raise StatisticalComparisonUsageError("comparison usage fingerprint mismatch")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {**self._fingerprint_payload(), "fingerprint": self.fingerprint}


class StatisticalComparisonUsageLedger:
    """Role-isolation ledger for multiple-comparison statistical evidence."""

    def __init__(self) -> None:
        self._entries: list[StatisticalComparisonUsage] = []

    def record(
        self,
        evidence: StatisticalComparisonEvidence,
        *,
        ledger: StatisticalComparisonEvidenceLedger,
        purpose: str,
    ) -> StatisticalComparisonUsage:
        try:
            evidence.validate()
        except StatisticalComparisonEvidenceError as exc:
            raise StatisticalComparisonUsageError(str(exc)) from exc
        if not purpose:
            raise StatisticalComparisonUsageError("comparison usage purpose is required")
        if not ledger.contains(evidence):
            raise StatisticalComparisonUsageError("statistical comparison evidence is not registered in ledger")

        role = self._dataset_role(evidence)
        blocked_purposes = {"DEVELOPMENT", "OPTIMIZATION", "PARAMETER_FIT"}
        if role in (DatasetRole.UNTOUCHED_VALIDATION, DatasetRole.FRESH_HOLDOUT) and purpose in blocked_purposes:
            raise StatisticalComparisonUsageError(
                f"{role.value} comparison evidence cannot be used for {purpose}"
            )

        entry = StatisticalComparisonUsage(
            evidence_fingerprint=evidence.fingerprint,
            comparison_fingerprint=evidence.comparison_fingerprint,
            dataset_role=role,
            purpose=purpose,
            disposition=StatisticalComparisonUsageDisposition.ALLOWED,
            fingerprint="",
        )
        fingerprint = hashlib.sha256(
            StatisticalComparisonUsage._payload(entry._fingerprint_payload())
        ).hexdigest()
        entry = StatisticalComparisonUsage(**{**entry.__dict__, "fingerprint": fingerprint})

        for existing in self._entries:
            if existing.evidence_fingerprint == entry.evidence_fingerprint and existing.purpose == entry.purpose:
                return existing
        self._entries.append(entry)
        return entry

    @staticmethod
    def _dataset_role(evidence: StatisticalComparisonEvidence) -> DatasetRole:
        role = getattr(evidence, "dataset_role", None)
        if role is None:
            raise StatisticalComparisonUsageError(
                "statistical comparison evidence has no dataset role; comparison governance requires role-bound evidence"
            )
        try:
            return DatasetRole(role)
        except ValueError as exc:
            raise StatisticalComparisonUsageError("invalid statistical comparison dataset role") from exc

    def entries(self) -> tuple[StatisticalComparisonUsage, ...]:
        return tuple(self._entries)

    def assert_clean(self) -> None:
        for entry in self._entries:
            entry.validate()
            if entry.disposition is StatisticalComparisonUsageDisposition.BLOCKED:
                raise StatisticalComparisonUsageError("comparison usage ledger contains blocked entries")

    def as_dict(self) -> list[dict[str, object]]:
        return [entry.as_dict() for entry in self._entries]
