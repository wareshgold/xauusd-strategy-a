from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from typing import Any

from .research_record import ResearchRecord
from .statistical_evidence import StatisticalEvidence, validate_statistical_evidence_binding
from .stability_evidence import StabilityEvidence, validate_stability_evidence_binding


class ResearchEvidenceBundleError(ValueError):
    """Raised when combined statistical/stability evidence is not reproducible."""


@dataclass(frozen=True)
class ResearchEvidenceBundle:
    """Immutable descriptive evidence bundle bound to one research record.

    This object combines statistical and stability evidence without defining
    performance thresholds, canonical rules, or production eligibility.
    """

    bundle_revision: str
    run_id: str
    run_fingerprint: str
    research_record_fingerprint: str
    dataset_id: str
    dataset_role: str
    strategy_id: str
    strategy_revision: str
    statistical_evidence_fingerprint: str
    stability_evidence_fingerprint: str
    fingerprint: str

    @staticmethod
    def _payload(values: dict[str, Any]) -> bytes:
        return json.dumps(
            values, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")

    def _fingerprint_payload(self) -> dict[str, Any]:
        return {
            "bundle_revision": self.bundle_revision,
            "run_id": self.run_id,
            "run_fingerprint": self.run_fingerprint,
            "research_record_fingerprint": self.research_record_fingerprint,
            "dataset_id": self.dataset_id,
            "dataset_role": self.dataset_role,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "statistical_evidence_fingerprint": self.statistical_evidence_fingerprint,
            "stability_evidence_fingerprint": self.stability_evidence_fingerprint,
        }

    def validate(self) -> None:
        if not self.run_id or not self.run_fingerprint:
            raise ResearchEvidenceBundleError("evidence bundle identity is incomplete")
        if not self.statistical_evidence_fingerprint or not self.stability_evidence_fingerprint:
            raise ResearchEvidenceBundleError("evidence bundle evidence identity is incomplete")
        expected = hashlib.sha256(self._payload(self._fingerprint_payload())).hexdigest()
        if self.fingerprint != expected:
            raise ResearchEvidenceBundleError("evidence bundle fingerprint mismatch")

    def as_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        self.validate()
        data = self._fingerprint_payload()
        if include_fingerprint:
            data["fingerprint"] = self.fingerprint
        return data


def bind_research_evidence_bundle(
    record: ResearchRecord,
    statistical_evidence: StatisticalEvidence,
    stability_evidence: StabilityEvidence,
    *,
    bundle_revision: str = "RESEARCH-EVIDENCE-BUNDLE-1",
) -> ResearchEvidenceBundle:
    """Bind statistical and stability evidence to the exact same research record."""
    record.validate()
    validate_statistical_evidence_binding(statistical_evidence, record)
    validate_stability_evidence_binding(stability_evidence, record)

    if statistical_evidence.dataset_role != stability_evidence.dataset_role:
        raise ResearchEvidenceBundleError("evidence dataset roles do not match")
    if statistical_evidence.fingerprint == stability_evidence.fingerprint:
        raise ResearchEvidenceBundleError("statistical and stability evidence fingerprints must be distinct")

    bundle = ResearchEvidenceBundle(
        bundle_revision=bundle_revision,
        run_id=record.run_id,
        run_fingerprint=record.run_fingerprint,
        research_record_fingerprint=record.fingerprint,
        dataset_id=record.dataset_id,
        dataset_role=record.dataset_role,
        strategy_id=record.strategy_id,
        strategy_revision=record.strategy_revision,
        statistical_evidence_fingerprint=statistical_evidence.fingerprint,
        stability_evidence_fingerprint=stability_evidence.fingerprint,
        fingerprint="",
    )
    fingerprint = hashlib.sha256(bundle._payload(bundle._fingerprint_payload())).hexdigest()
    return replace(bundle, fingerprint=fingerprint)


def validate_research_evidence_bundle(
    bundle: ResearchEvidenceBundle,
    record: ResearchRecord,
    statistical_evidence: StatisticalEvidence,
    stability_evidence: StabilityEvidence,
) -> None:
    bundle.validate()
    validate_statistical_evidence_binding(statistical_evidence, record)
    validate_stability_evidence_binding(stability_evidence, record)

    if bundle.run_id != record.run_id:
        raise ResearchEvidenceBundleError("evidence bundle run_id does not match research record")
    if bundle.run_fingerprint != record.run_fingerprint:
        raise ResearchEvidenceBundleError("evidence bundle run fingerprint does not match research record")
    if bundle.research_record_fingerprint != record.fingerprint:
        raise ResearchEvidenceBundleError("evidence bundle is not bound to research record")
    if bundle.dataset_id != record.dataset_id or bundle.dataset_role != record.dataset_role:
        raise ResearchEvidenceBundleError("evidence bundle dataset identity does not match research record")
    if bundle.strategy_id != record.strategy_id or bundle.strategy_revision != record.strategy_revision:
        raise ResearchEvidenceBundleError("evidence bundle strategy identity does not match research record")
    if bundle.statistical_evidence_fingerprint != statistical_evidence.fingerprint:
        raise ResearchEvidenceBundleError("evidence bundle statistical evidence does not match")
    if bundle.stability_evidence_fingerprint != stability_evidence.fingerprint:
        raise ResearchEvidenceBundleError("evidence bundle stability evidence does not match")
