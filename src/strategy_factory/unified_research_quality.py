from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .comparison_validation_gate import (
    ComparisonValidationGateResult,
    ComparisonValidationGateStatus,
)
from .research_acceptance import ResearchAcceptance, ResearchAcceptanceError
from .research_evidence_bundle import ResearchEvidenceBundle
from .research_evidence_ledger import ResearchEvidenceLedger
from .research_record import ResearchRecord
from .statistical_comparison_evidence import StatisticalComparisonEvidence
from .statistical_comparison_evidence_ledger import StatisticalComparisonEvidenceLedger
from .statistical_comparison_governance import StatisticalComparisonUsageLedger
from .statistical_evidence import StatisticalEvidence
from .stability_evidence import StabilityEvidence


class UnifiedResearchQualityError(ValueError):
    """Raised when the unified research quality chain is invalid."""


@dataclass(frozen=True)
class UnifiedResearchQuality:
    quality_revision: str
    run_id: str
    research_acceptance_fingerprint: str
    comparison_gate_fingerprint: str
    accepted: bool
    comparison_validated: bool
    fingerprint: str

    def _payload(self) -> dict[str, object]:
        return {
            "quality_revision": self.quality_revision,
            "run_id": self.run_id,
            "research_acceptance_fingerprint": self.research_acceptance_fingerprint,
            "comparison_gate_fingerprint": self.comparison_gate_fingerprint,
            "accepted": self.accepted,
            "comparison_validated": self.comparison_validated,
        }

    def validate(self) -> None:
        if not self.run_id:
            raise UnifiedResearchQualityError("unified research quality run identity is incomplete")
        if not self.accepted or not self.comparison_validated:
            raise UnifiedResearchQualityError("unified research quality is not accepted")
        expected = hashlib.sha256(
            json.dumps(self._payload(), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if self.fingerprint != expected:
            raise UnifiedResearchQualityError("unified research quality fingerprint mismatch")


def evaluate_unified_research_quality(
    record: ResearchRecord,
    statistical: StatisticalEvidence,
    stability: StabilityEvidence,
    bundle: ResearchEvidenceBundle,
    research_ledger: ResearchEvidenceLedger,
    acceptance: ResearchAcceptance,
    comparison_gate: ComparisonValidationGateResult,
    *,
    quality_revision: str = "UNIFIED-RESEARCH-QUALITY-1",
) -> UnifiedResearchQuality:
    try:
        record.validate()
        statistical.validate()
        stability.validate()
        acceptance.validate()
        if acceptance.run_id != record.run_id:
            raise UnifiedResearchQualityError("research acceptance run_id does not match record")
        if acceptance.research_record_fingerprint != record.fingerprint:
            raise UnifiedResearchQualityError("research acceptance record fingerprint does not match record")
        if acceptance.bundle_fingerprint != bundle.fingerprint:
            raise UnifiedResearchQualityError("research acceptance bundle fingerprint does not match bundle")
        if acceptance.statistical_evidence_fingerprint != statistical.fingerprint:
            raise UnifiedResearchQualityError("research acceptance statistical evidence does not match")
        if acceptance.stability_evidence_fingerprint != stability.fingerprint:
            raise UnifiedResearchQualityError("research acceptance stability evidence does not match")
        if bundle.statistical_evidence_fingerprint != statistical.fingerprint:
            raise UnifiedResearchQualityError("bundle statistical evidence does not match")
        if bundle.stability_evidence_fingerprint != stability.fingerprint:
            raise UnifiedResearchQualityError("bundle stability evidence does not match")
        if not any(
            entry.bundle_fingerprint == bundle.fingerprint and entry.run_id == record.run_id
            for entry in research_ledger.entries()
        ):
            raise UnifiedResearchQualityError("research evidence bundle is not registered in ledger")
        comparison_gate.validate()
    except Exception as exc:
        raise UnifiedResearchQualityError(str(exc)) from exc

    if comparison_gate.status is not ComparisonValidationGateStatus.PASS:
        raise UnifiedResearchQualityError("comparison validation gate is not PASS")
    if comparison_gate.evidence_fingerprint == "":
        raise UnifiedResearchQualityError("comparison validation evidence identity is incomplete")

    result = UnifiedResearchQuality(
        quality_revision=quality_revision,
        run_id=record.run_id,
        research_acceptance_fingerprint=acceptance.fingerprint,
        comparison_gate_fingerprint=comparison_gate.fingerprint,
        accepted=True,
        comparison_validated=True,
        fingerprint="",
    )
    fingerprint = hashlib.sha256(
        json.dumps(result._payload(), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    result = UnifiedResearchQuality(**{**result.__dict__, "fingerprint": fingerprint})
    result.validate()
    return result
