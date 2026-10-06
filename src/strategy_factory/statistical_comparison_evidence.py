from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .multiple_comparison import MultipleComparisonResult
from .research_comparison import ResearchComparison


class StatisticalComparisonEvidenceError(ValueError):
    """Raised when statistical comparison evidence is invalid."""


@dataclass(frozen=True)
class StatisticalComparisonEvidence:
    """Immutable provenance binding for a comparison and its p-value adjustment."""

    evidence_revision: str
    comparison_fingerprint: str
    adjustment_fingerprint: str
    method: str
    family_size: int
    raw_p_values: tuple[float, ...]
    adjusted_p_values: tuple[float, ...]
    fingerprint: str

    def _payload(self) -> dict[str, object]:
        return {
            "evidence_revision": self.evidence_revision,
            "comparison_fingerprint": self.comparison_fingerprint,
            "adjustment_fingerprint": self.adjustment_fingerprint,
            "method": self.method,
            "family_size": self.family_size,
            "raw_p_values": list(self.raw_p_values),
            "adjusted_p_values": list(self.adjusted_p_values),
        }

    def validate(self) -> None:
        if not self.evidence_revision or not self.comparison_fingerprint or not self.adjustment_fingerprint:
            raise StatisticalComparisonEvidenceError("statistical comparison evidence identity is incomplete")
        if self.family_size < 1:
            raise StatisticalComparisonEvidenceError("family_size must be positive")
        if len(self.raw_p_values) != self.family_size or len(self.adjusted_p_values) != self.family_size:
            raise StatisticalComparisonEvidenceError("p-value counts do not match family_size")
        expected = hashlib.sha256(json.dumps(self._payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if self.fingerprint != expected:
            raise StatisticalComparisonEvidenceError("statistical comparison evidence fingerprint mismatch")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {**self._payload(), "fingerprint": self.fingerprint}


def bind_statistical_comparison_evidence(
    comparison: ResearchComparison,
    adjustment: MultipleComparisonResult,
    *,
    evidence_revision: str = "STATISTICAL-COMPARISON-EVIDENCE-1",
) -> StatisticalComparisonEvidence:
    comparison.validate()
    adjustment.validate()
    if adjustment.family_size != comparison.comparison_count:
        raise StatisticalComparisonEvidenceError("adjustment family_size does not match comparison_count")
    evidence = StatisticalComparisonEvidence(
        evidence_revision=evidence_revision,
        comparison_fingerprint=comparison.fingerprint,
        adjustment_fingerprint=adjustment.fingerprint,
        method=adjustment.method,
        family_size=adjustment.family_size,
        raw_p_values=adjustment.raw_p_values,
        adjusted_p_values=adjustment.adjusted_p_values,
        fingerprint="",
    )
    fingerprint = hashlib.sha256(json.dumps(evidence._payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return StatisticalComparisonEvidence(**{**evidence.__dict__, "fingerprint": fingerprint})


def validate_statistical_comparison_evidence(
    evidence: StatisticalComparisonEvidence,
    comparison: ResearchComparison,
    adjustment: MultipleComparisonResult,
) -> None:
    evidence.validate()
    comparison.validate()
    adjustment.validate()
    if evidence.comparison_fingerprint != comparison.fingerprint:
        raise StatisticalComparisonEvidenceError("comparison fingerprint does not match evidence")
    if evidence.adjustment_fingerprint != adjustment.fingerprint:
        raise StatisticalComparisonEvidenceError("adjustment fingerprint does not match evidence")
    if evidence.method != adjustment.method or evidence.family_size != adjustment.family_size:
        raise StatisticalComparisonEvidenceError("adjustment identity does not match evidence")
    if evidence.raw_p_values != adjustment.raw_p_values or evidence.adjusted_p_values != adjustment.adjusted_p_values:
        raise StatisticalComparisonEvidenceError("adjustment p-values do not match evidence")
