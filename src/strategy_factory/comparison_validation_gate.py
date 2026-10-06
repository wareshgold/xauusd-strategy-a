from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json

from .multiple_comparison import MultipleComparisonResult
from .research_comparison import ResearchComparison
from .statistical_comparison_evidence import (
    StatisticalComparisonEvidence,
    StatisticalComparisonEvidenceError,
    validate_statistical_comparison_evidence,
)
from .statistical_comparison_evidence_ledger import StatisticalComparisonEvidenceLedger
from .statistical_comparison_governance import (
    StatisticalComparisonUsageLedger,
    StatisticalComparisonUsageError,
)


class ComparisonValidationGateStatus(str, Enum):
    PASS = "PASS"
    BLOCKED = "BLOCKED"
    FAIL = "FAIL"


class ComparisonValidationGateError(ValueError):
    """Raised when unified comparison validation cannot be evaluated."""


@dataclass(frozen=True)
class ComparisonValidationGateResult:
    status: ComparisonValidationGateStatus
    comparison_fingerprint: str
    adjustment_fingerprint: str
    evidence_fingerprint: str
    registered: bool
    governed: bool
    blocking_reasons: tuple[str, ...]
    fingerprint: str

    def _payload(self) -> dict[str, object]:
        return {
            "status": self.status.value,
            "comparison_fingerprint": self.comparison_fingerprint,
            "adjustment_fingerprint": self.adjustment_fingerprint,
            "evidence_fingerprint": self.evidence_fingerprint,
            "registered": self.registered,
            "governed": self.governed,
            "blocking_reasons": list(self.blocking_reasons),
        }

    def validate(self) -> None:
        if not self.comparison_fingerprint or not self.adjustment_fingerprint or not self.evidence_fingerprint:
            raise ComparisonValidationGateError("comparison validation gate identity is incomplete")
        expected = hashlib.sha256(
            json.dumps(self._payload(), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if self.fingerprint != expected:
            raise ComparisonValidationGateError("comparison validation gate fingerprint mismatch")
        if self.status is ComparisonValidationGateStatus.PASS and (
            not self.registered or not self.governed or self.blocking_reasons
        ):
            raise ComparisonValidationGateError("PASS comparison gate has unresolved controls")
        if self.status is ComparisonValidationGateStatus.BLOCKED and not self.blocking_reasons:
            raise ComparisonValidationGateError("BLOCKED comparison gate requires a reason")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {**self._payload(), "fingerprint": self.fingerprint}


def evaluate_comparison_validation_gate(
    comparison: ResearchComparison,
    adjustment: MultipleComparisonResult,
    evidence: StatisticalComparisonEvidence,
    evidence_ledger: StatisticalComparisonEvidenceLedger,
    governance_ledger: StatisticalComparisonUsageLedger,
    *,
    purpose: str = "FINAL_EVIDENCE",
) -> ComparisonValidationGateResult:
    reasons: list[str] = []
    try:
        comparison.validate()
        adjustment.validate()
        validate_statistical_comparison_evidence(evidence, comparison, adjustment)
    except Exception as exc:
        result = _result(
            ComparisonValidationGateStatus.FAIL,
            comparison,
            adjustment,
            evidence,
            registered=False,
            governed=False,
            reasons=(str(exc),),
        )
        return result

    registered = evidence_ledger.contains(evidence)
    if not registered:
        reasons.append("STATISTICAL_COMPARISON_EVIDENCE_NOT_REGISTERED")

    governed = False
    if registered:
        try:
            governance_ledger.record(
                evidence,
                ledger=evidence_ledger,
                purpose=purpose,
            )
            governed = True
        except StatisticalComparisonUsageError as exc:
            reasons.append(str(exc))

    status = ComparisonValidationGateStatus.PASS if not reasons else ComparisonValidationGateStatus.BLOCKED
    return _result(
        status,
        comparison,
        adjustment,
        evidence,
        registered=registered,
        governed=governed,
        reasons=tuple(reasons),
    )


def _result(
    status: ComparisonValidationGateStatus,
    comparison: ResearchComparison,
    adjustment: MultipleComparisonResult,
    evidence: StatisticalComparisonEvidence,
    *,
    registered: bool,
    governed: bool,
    reasons: tuple[str, ...],
) -> ComparisonValidationGateResult:
    result = ComparisonValidationGateResult(
        status=status,
        comparison_fingerprint=comparison.fingerprint,
        adjustment_fingerprint=adjustment.fingerprint,
        evidence_fingerprint=evidence.fingerprint,
        registered=registered,
        governed=governed,
        blocking_reasons=reasons,
        fingerprint="",
    )
    fingerprint = hashlib.sha256(
        json.dumps(result._payload(), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return ComparisonValidationGateResult(**{**result.__dict__, "fingerprint": fingerprint})
