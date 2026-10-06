from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .comparison_validation_gate import ComparisonValidationGateResult
from .research_acceptance import ResearchAcceptance
from .research_certification import ResearchCertification
from .research_certification_ledger import ResearchCertificationLedger
from .research_evidence_bundle import ResearchEvidenceBundle, validate_research_evidence_bundle
from .research_evidence_ledger import ResearchEvidenceLedger
from .research_record import ResearchRecord
from .snapshot import ReadinessSnapshot
from .statistical_evidence import StatisticalEvidence
from .stability_evidence import StabilityEvidence
from .unified_research_quality import UnifiedResearchQuality


class ResearchAuditPackageError(ValueError):
    """Raised when the final immutable research audit package is invalid."""


@dataclass(frozen=True)
class ResearchAuditPackage:
    """Immutable, deterministic package of one complete research evidence chain.

    This is audit/provenance-only. It does not select winners, promote canonical
    rules, authorize production, or generate trading decisions.
    """

    package_revision: str
    run_id: str
    strategy_id: str
    strategy_revision: str
    manifest_revision: str
    dataset_id: str
    dataset_role: str
    readiness_snapshot_fingerprint: str
    research_record_fingerprint: str
    statistical_evidence_fingerprint: str
    stability_evidence_fingerprint: str
    bundle_fingerprint: str
    acceptance_fingerprint: str
    comparison_gate_fingerprint: str
    quality_fingerprint: str
    certification_fingerprint: str
    certification_ledger_fingerprint: str
    source_readiness_status: str
    frozen_geometry_status: str
    canonical_strategy_status: str
    production_status: str
    certified: bool
    production_eligible: bool
    fingerprint: str

    def _payload(self) -> dict[str, object]:
        return {
            "package_revision": self.package_revision,
            "run_id": self.run_id,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "manifest_revision": self.manifest_revision,
            "dataset_id": self.dataset_id,
            "dataset_role": self.dataset_role,
            "readiness_snapshot_fingerprint": self.readiness_snapshot_fingerprint,
            "research_record_fingerprint": self.research_record_fingerprint,
            "statistical_evidence_fingerprint": self.statistical_evidence_fingerprint,
            "stability_evidence_fingerprint": self.stability_evidence_fingerprint,
            "bundle_fingerprint": self.bundle_fingerprint,
            "acceptance_fingerprint": self.acceptance_fingerprint,
            "comparison_gate_fingerprint": self.comparison_gate_fingerprint,
            "quality_fingerprint": self.quality_fingerprint,
            "certification_fingerprint": self.certification_fingerprint,
            "certification_ledger_fingerprint": self.certification_ledger_fingerprint,
            "source_readiness_status": self.source_readiness_status,
            "frozen_geometry_status": self.frozen_geometry_status,
            "canonical_strategy_status": self.canonical_strategy_status,
            "production_status": self.production_status,
            "certified": self.certified,
            "production_eligible": self.production_eligible,
        }

    def validate(self) -> None:
        if not self.run_id or not self.strategy_id or not self.strategy_revision:
            raise ResearchAuditPackageError("research audit package identity is incomplete")
        if not self.certified:
            raise ResearchAuditPackageError("research audit package is not certified")
        if self.production_eligible:
            raise ResearchAuditPackageError("research audit package cannot authorize production")
        expected = hashlib.sha256(
            json.dumps(self._payload(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        if self.fingerprint != expected:
            raise ResearchAuditPackageError("research audit package fingerprint mismatch")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {**self._payload(), "fingerprint": self.fingerprint}


def build_research_audit_package(
    snapshot: ReadinessSnapshot,
    record: ResearchRecord,
    statistical: StatisticalEvidence,
    stability: StabilityEvidence,
    bundle: ResearchEvidenceBundle,
    research_ledger: ResearchEvidenceLedger,
    acceptance: ResearchAcceptance,
    comparison_gate: ComparisonValidationGateResult,
    quality: UnifiedResearchQuality,
    certification: ResearchCertification,
    certification_ledger: ResearchCertificationLedger,
    *,
    package_revision: str = "RESEARCH-AUDIT-PACKAGE-1",
) -> ResearchAuditPackage:
    try:
        snapshot.validate()
        record.validate()
        statistical.validate()
        stability.validate()
        bundle.validate()
        acceptance.validate()
        comparison_gate.validate()
        quality.validate()
        certification.validate()
        validate_research_evidence_bundle(bundle, record, statistical, stability)
    except Exception as exc:
        raise ResearchAuditPackageError(str(exc)) from exc

    if record.snapshot_fingerprint != snapshot.fingerprint:
        raise ResearchAuditPackageError("research record is not bound to readiness snapshot")
    if record.strategy_id != snapshot.strategy_id or record.manifest_revision != snapshot.manifest_revision:
        raise ResearchAuditPackageError("research record strategy identity does not match readiness snapshot")
    if not any(
        entry.bundle_fingerprint == bundle.fingerprint and entry.run_id == record.run_id
        for entry in research_ledger.entries()
    ):
        raise ResearchAuditPackageError("research evidence bundle is not registered in ledger")
    if acceptance.run_id != record.run_id or not acceptance.ledger_registered:
        raise ResearchAuditPackageError("research acceptance is not bound to registered evidence")
    if quality.run_id != record.run_id or not quality.accepted or not quality.comparison_validated:
        raise ResearchAuditPackageError("unified research quality is not accepted")
    if certification.run_id != record.run_id:
        raise ResearchAuditPackageError("research certification is not bound to record")
    if certification.research_record_fingerprint != record.fingerprint:
        raise ResearchAuditPackageError("research certification record does not match")
    if certification.statistical_evidence_fingerprint != statistical.fingerprint:
        raise ResearchAuditPackageError("research certification statistical evidence does not match")
    if certification.stability_evidence_fingerprint != stability.fingerprint:
        raise ResearchAuditPackageError("research certification stability evidence does not match")
    if certification.bundle_fingerprint != bundle.fingerprint:
        raise ResearchAuditPackageError("research certification bundle does not match")
    if certification.acceptance_fingerprint != acceptance.fingerprint:
        raise ResearchAuditPackageError("research certification acceptance does not match")
    if certification.comparison_gate_fingerprint != comparison_gate.fingerprint:
        raise ResearchAuditPackageError("research certification comparison gate does not match")
    if certification.quality_fingerprint != quality.fingerprint:
        raise ResearchAuditPackageError("research certification quality does not match")

    cert_entries = [
        entry for entry in certification_ledger.entries()
        if entry.run_id == record.run_id and entry.certification_fingerprint == certification.fingerprint
    ]
    if len(cert_entries) != 1:
        raise ResearchAuditPackageError("research certification is not registered exactly once in ledger")
    cert_entry = cert_entries[0]

    readiness = snapshot.source_readiness
    passport = snapshot.passport_eligibility
    source_status = str(readiness.get("gate", readiness.get("status", "UNKNOWN")))
    frozen_geometry = str(passport.get("frozen_geometry", "UNKNOWN"))
    canonical_strategy = str(passport.get("canonical_strategy", "UNKNOWN"))
    production = str(passport.get("production", "UNKNOWN"))

    result = ResearchAuditPackage(
        package_revision=package_revision,
        run_id=record.run_id,
        strategy_id=record.strategy_id,
        strategy_revision=record.strategy_revision,
        manifest_revision=record.manifest_revision,
        dataset_id=record.dataset_id,
        dataset_role=record.dataset_role,
        readiness_snapshot_fingerprint=snapshot.fingerprint,
        research_record_fingerprint=record.fingerprint,
        statistical_evidence_fingerprint=statistical.fingerprint,
        stability_evidence_fingerprint=stability.fingerprint,
        bundle_fingerprint=bundle.fingerprint,
        acceptance_fingerprint=acceptance.fingerprint,
        comparison_gate_fingerprint=comparison_gate.fingerprint,
        quality_fingerprint=quality.fingerprint,
        certification_fingerprint=certification.fingerprint,
        certification_ledger_fingerprint=cert_entry.fingerprint,
        source_readiness_status=source_status,
        frozen_geometry_status=frozen_geometry,
        canonical_strategy_status=canonical_strategy,
        production_status=production,
        certified=True,
        production_eligible=False,
        fingerprint="",
    )
    fingerprint = hashlib.sha256(
        json.dumps(result._payload(), sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    final = ResearchAuditPackage(**{**result.__dict__, "fingerprint": fingerprint})
    final.validate()
    return final
