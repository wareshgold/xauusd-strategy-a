from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from typing import Any

from .research_record import ResearchRecord
from .stability import StabilityProfile


class StabilityEvidenceError(ValueError):
    """Raised when stability evidence cannot be bound reproducibly."""


@dataclass(frozen=True)
class StabilityEvidence:
    """Immutable cross-segment stability evidence bound to one research record."""

    evidence_revision: str
    run_id: str
    run_fingerprint: str
    research_record_fingerprint: str
    dataset_id: str
    dataset_role: str
    strategy_id: str
    strategy_revision: str
    stability_profile: StabilityProfile
    fingerprint: str

    @staticmethod
    def _payload(values: dict[str, Any]) -> bytes:
        return json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

    def _fingerprint_payload(self) -> dict[str, Any]:
        return {
            "evidence_revision": self.evidence_revision,
            "run_id": self.run_id,
            "run_fingerprint": self.run_fingerprint,
            "research_record_fingerprint": self.research_record_fingerprint,
            "dataset_id": self.dataset_id,
            "dataset_role": self.dataset_role,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "stability_profile": self.stability_profile.as_dict(),
        }

    def as_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        self.validate()
        data = self._fingerprint_payload()
        if include_fingerprint:
            data["fingerprint"] = self.fingerprint
        return data

    def validate(self) -> None:
        if not self.run_id or not self.run_fingerprint:
            raise StabilityEvidenceError("stability evidence identity is incomplete")
        self.stability_profile.validate()
        expected = hashlib.sha256(self._payload(self._fingerprint_payload())).hexdigest()
        if self.fingerprint != expected:
            raise StabilityEvidenceError("stability evidence fingerprint mismatch")


def bind_stability_evidence(
    record: ResearchRecord,
    profile: StabilityProfile,
    *,
    evidence_revision: str = "STABILITY-EVIDENCE-1",
) -> StabilityEvidence:
    """Bind descriptive stability evidence to the exact immutable research record."""
    record.validate()
    profile.validate()

    evidence = StabilityEvidence(
        evidence_revision=evidence_revision,
        run_id=record.run_id,
        run_fingerprint=record.run_fingerprint,
        research_record_fingerprint=record.fingerprint,
        dataset_id=record.dataset_id,
        dataset_role=record.dataset_role,
        strategy_id=record.strategy_id,
        strategy_revision=record.strategy_revision,
        stability_profile=profile,
        fingerprint="",
    )
    fingerprint = hashlib.sha256(evidence._payload(evidence._fingerprint_payload())).hexdigest()
    return replace(evidence, fingerprint=fingerprint)


def validate_stability_evidence_binding(
    evidence: StabilityEvidence,
    record: ResearchRecord,
) -> None:
    evidence.validate()
    if evidence.run_id != record.run_id:
        raise StabilityEvidenceError("stability evidence run_id does not match research record")
    if evidence.run_fingerprint != record.run_fingerprint:
        raise StabilityEvidenceError("stability evidence run fingerprint does not match research record")
    if evidence.research_record_fingerprint != record.fingerprint:
        raise StabilityEvidenceError("stability evidence is not bound to research record")
    if evidence.dataset_id != record.dataset_id or evidence.dataset_role != record.dataset_role:
        raise StabilityEvidenceError("stability evidence dataset identity does not match research record")
    if evidence.strategy_id != record.strategy_id or evidence.strategy_revision != record.strategy_revision:
        raise StabilityEvidenceError("stability evidence strategy identity does not match research record")
    record.validate()
