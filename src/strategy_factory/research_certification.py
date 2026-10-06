from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .comparison_validation_gate import ComparisonValidationGateResult, ComparisonValidationGateStatus
from .research_acceptance import ResearchAcceptance
from .research_evidence_bundle import ResearchEvidenceBundle, validate_research_evidence_bundle
from .research_evidence_ledger import ResearchEvidenceLedger
from .research_record import ResearchRecord
from .statistical_evidence import StatisticalEvidence
from .stability_evidence import StabilityEvidence
from .unified_research_quality import UnifiedResearchQuality


class ResearchCertificationError(ValueError):
    """Raised when the immutable research certification chain is invalid."""


@dataclass(frozen=True)
class ResearchCertification:
    """Immutable certification that one research result has a complete evidence chain.

    Certification is descriptive/provenance-only. It does not select winners,
    promote canonical rules, or authorize production.
    """

    certification_revision: str
    run_id: str
    research_record_fingerprint: str
    statistical_evidence_fingerprint: str
    stability_evidence_fingerprint: str
    bundle_fingerprint: str
    acceptance_fingerprint: str
    comparison_gate_fingerprint: str
    quality_fingerprint: str
    source_snapshot_fingerprint: str
    certified: bool
    production_eligible: bool
    fingerprint: str

    def _payload(self) -> dict[str, object]:
        return {
            "certification_revision": self.certification_revision,
            "run_id": self.run_id,
            "research_record_fingerprint": self.research_record_fingerprint,
            "statistical_evidence_fingerprint": self.statistical_evidence_fingerprint,
            "stability_evidence_fingerprint": self.stability_evidence_fingerprint,
            "bundle_fingerprint": self.bundle_fingerprint,
            "acceptance_fingerprint": self.acceptance_fingerprint,
            "comparison_gate_fingerprint": self.comparison_gate_fingerprint,
            "quality_fingerprint": self.quality_fingerprint,
            "source_snapshot_fingerprint": self.source_snapshot_fingerprint,
            "certified": self.certified,
            "production_eligible": self.production_eligible,
        }

    def validate(self) -> None:
        if not self.run_id:
            raise ResearchCertificationError("research certification run identity is incomplete")
        if not self.certified:
            raise ResearchCertificationError("research certification is not certified")
        if self.production_eligible:
            raise ResearchCertificationError("research certification cannot authorize production")
        expected = hashlib.sha256(
            json.dumps(self._payload(), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if self.fingerprint != expected:
            raise ResearchCertificationError("research certification fingerprint mismatch")


def certify_research_result(
    record: ResearchRecord,
    statistical: StatisticalEvidence,
    stability: StabilityEvidence,
    bundle: ResearchEvidenceBundle,
    research_ledger: ResearchEvidenceLedger,
    acceptance: ResearchAcceptance,
    comparison_gate: ComparisonValidationGateResult,
    quality: UnifiedResearchQuality,
    *,
    certification_revision: str = "RESEARCH-CERTIFICATION-1",
) -> ResearchCertification:
    try:
        record.validate()
        statistical.validate()
        stability.validate()
        bundle.validate()
        acceptance.validate()
        quality.validate()
        comparison_gate.validate()
        validate_research_evidence_bundle(bundle, record, statistical, stability)
    except Exception as exc:
        raise ResearchCertificationError(str(exc)) from exc

    if acceptance.run_id != record.run_id:
        raise ResearchCertificationError("research acceptance run_id does not match record")
    if acceptance.research_record_fingerprint != record.fingerprint:
        raise ResearchCertificationError("research acceptance record fingerprint does not match record")
    if acceptance.statistical_evidence_fingerprint != statistical.fingerprint:
        raise ResearchCertificationError("research acceptance statistical evidence does not match")
    if acceptance.stability_evidence_fingerprint != stability.fingerprint:
        raise ResearchCertificationError("research acceptance stability evidence does not match")
    if acceptance.bundle_fingerprint != bundle.fingerprint:
        raise ResearchCertificationError("research acceptance bundle does not match")
    if not acceptance.ledger_registered:
        raise ResearchCertificationError("research acceptance ledger registration is not confirmed")

    if quality.run_id != record.run_id:
        raise ResearchCertificationError("unified research quality run_id does not match record")
    if quality.research_acceptance_fingerprint != acceptance.fingerprint:
        raise ResearchCertificationError("unified research quality acceptance does not match")
    if quality.comparison_gate_fingerprint != comparison_gate.fingerprint:
        raise ResearchCertificationError("unified research quality comparison gate does not match")
    if not quality.accepted or not quality.comparison_validated:
        raise ResearchCertificationError("unified research quality is not accepted")

    if comparison_gate.status is not ComparisonValidationGateStatus.PASS:
        raise ResearchCertificationError("comparison validation gate is not PASS")

    if not any(
        entry.bundle_fingerprint == bundle.fingerprint and entry.run_id == record.run_id
        for entry in research_ledger.entries()
    ):
        raise ResearchCertificationError("research evidence bundle is not registered in ledger")

    source_snapshot_fingerprint = record.snapshot_fingerprint
    result = ResearchCertification(
        certification_revision=certification_revision,
        run_id=record.run_id,
        research_record_fingerprint=record.fingerprint,
        statistical_evidence_fingerprint=statistical.fingerprint,
        stability_evidence_fingerprint=stability.fingerprint,
        bundle_fingerprint=bundle.fingerprint,
        acceptance_fingerprint=acceptance.fingerprint,
        comparison_gate_fingerprint=comparison_gate.fingerprint,
        quality_fingerprint=quality.fingerprint,
        source_snapshot_fingerprint=source_snapshot_fingerprint,
        certified=True,
        production_eligible=False,
        fingerprint="",
    )
    fingerprint = hashlib.sha256(
        json.dumps(result._payload(), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    final = ResearchCertification(**{**result.__dict__, "fingerprint": fingerprint})
    final.validate()
    return final
