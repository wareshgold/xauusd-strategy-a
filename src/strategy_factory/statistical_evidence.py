from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .research_record import ResearchRecord
from .statistics import StatisticalValidationResult


class StatisticalEvidenceError(ValueError):
    """Raised when statistical evidence cannot be bound reproducibly."""


@dataclass(frozen=True)
class StatisticalEvidence:
    """Immutable statistical evidence bound to one accepted research record."""

    evidence_revision: str
    run_id: str
    run_fingerprint: str
    research_record_fingerprint: str
    dataset_id: str
    dataset_role: str
    strategy_id: str
    strategy_revision: str
    statistical_result: StatisticalValidationResult
    fingerprint: str

    @staticmethod
    def _payload(values: dict[str, Any]) -> bytes:
        return json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

    def as_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        self.validate()
        data = {
            "evidence_revision": self.evidence_revision,
            "run_id": self.run_id,
            "run_fingerprint": self.run_fingerprint,
            "research_record_fingerprint": self.research_record_fingerprint,
            "dataset_id": self.dataset_id,
            "dataset_role": self.dataset_role,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "statistical_result": self.statistical_result.as_dict(),
        }
        if include_fingerprint:
            data["fingerprint"] = self.fingerprint
        return data

    def validate(self) -> None:
        if not self.run_id or not self.run_fingerprint:
            raise StatisticalEvidenceError("statistical evidence identity is incomplete")
        self.statistical_result.validate()
        expected = hashlib.sha256(self._payload(self.as_dict(include_fingerprint=False))).hexdigest()
        if self.fingerprint != expected:
            raise StatisticalEvidenceError("statistical evidence fingerprint mismatch")


def bind_statistical_evidence(
    record: ResearchRecord,
    result: StatisticalValidationResult,
    *,
    evidence_revision: str = "STATISTICAL-EVIDENCE-1",
) -> StatisticalEvidence:
    """Bind descriptive statistics to the exact immutable research record."""
    record.validate()
    result.validate()
    if result.role.value != record.dataset_role:
        raise StatisticalEvidenceError("statistical role does not match research record dataset role")

    evidence = StatisticalEvidence(
        evidence_revision=evidence_revision,
        run_id=record.run_id,
        run_fingerprint=record.run_fingerprint,
        research_record_fingerprint=record.fingerprint,
        dataset_id=record.dataset_id,
        dataset_role=record.dataset_role,
        strategy_id=record.strategy_id,
        strategy_revision=record.strategy_revision,
        statistical_result=result,
        fingerprint="",
    )
    fingerprint = hashlib.sha256(evidence._payload(evidence.as_dict(include_fingerprint=False))).hexdigest()
    return StatisticalEvidence(**{**evidence.__dict__, "fingerprint": fingerprint})


def validate_statistical_evidence_binding(
    evidence: StatisticalEvidence,
    record: ResearchRecord,
) -> None:
    evidence.validate()
    record.validate()
    if evidence.run_id != record.run_id:
        raise StatisticalEvidenceError("statistical evidence run_id does not match research record")
    if evidence.run_fingerprint != record.run_fingerprint:
        raise StatisticalEvidenceError("statistical evidence run fingerprint does not match research record")
    if evidence.research_record_fingerprint != record.fingerprint:
        raise StatisticalEvidenceError("statistical evidence is not bound to research record")
    if evidence.dataset_id != record.dataset_id or evidence.dataset_role != record.dataset_role:
        raise StatisticalEvidenceError("statistical evidence dataset identity does not match research record")
    if evidence.strategy_id != record.strategy_id or evidence.strategy_revision != record.strategy_revision:
        raise StatisticalEvidenceError("statistical evidence strategy identity does not match research record")
