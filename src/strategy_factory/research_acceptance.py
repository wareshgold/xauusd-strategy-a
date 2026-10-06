from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .research_evidence_bundle import (
    ResearchEvidenceBundle,
    validate_research_evidence_bundle,
)
from .research_evidence_ledger import ResearchEvidenceLedger
from .research_record import ResearchRecord
from .statistical_evidence import StatisticalEvidence, validate_statistical_evidence_binding
from .stability_evidence import StabilityEvidence, validate_stability_evidence_binding


class ResearchAcceptanceError(ValueError):
    """Raised when the final research evidence chain is invalid."""


@dataclass(frozen=True)
class ResearchAcceptance:
    acceptance_revision: str
    run_id: str
    research_record_fingerprint: str
    statistical_evidence_fingerprint: str
    stability_evidence_fingerprint: str
    bundle_fingerprint: str
    ledger_registered: bool
    accepted: bool
    fingerprint: str

    def _payload(self) -> dict:
        return {
            "acceptance_revision": self.acceptance_revision,
            "run_id": self.run_id,
            "research_record_fingerprint": self.research_record_fingerprint,
            "statistical_evidence_fingerprint": self.statistical_evidence_fingerprint,
            "stability_evidence_fingerprint": self.stability_evidence_fingerprint,
            "bundle_fingerprint": self.bundle_fingerprint,
            "ledger_registered": self.ledger_registered,
            "accepted": self.accepted,
        }

    @staticmethod
    def _fingerprint_payload(payload: dict) -> bytes:
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def validate(self) -> None:
        if not self.run_id:
            raise ResearchAcceptanceError("research acceptance run identity is incomplete")
        if not self.accepted:
            raise ResearchAcceptanceError("research acceptance is not accepted")
        expected = hashlib.sha256(self._fingerprint_payload(self._payload())).hexdigest()
        if self.fingerprint != expected:
            raise ResearchAcceptanceError("research acceptance fingerprint mismatch")


def _ledger_contains_bundle(
    ledger: ResearchEvidenceLedger,
    bundle: ResearchEvidenceBundle,
) -> bool:
    return any(
        entry.bundle_fingerprint == bundle.fingerprint
        and entry.run_id == bundle.run_id
        for entry in ledger.entries()
    )


def evaluate_research_acceptance(
    record: ResearchRecord,
    statistical: StatisticalEvidence,
    stability: StabilityEvidence,
    bundle: ResearchEvidenceBundle,
    ledger: ResearchEvidenceLedger,
    *,
    acceptance_revision: str = "RESEARCH-ACCEPTANCE-1",
) -> ResearchAcceptance:
    try:
        record.validate()
        statistical.validate()
        stability.validate()
        bundle.validate()
        validate_statistical_evidence_binding(statistical, record)
        validate_stability_evidence_binding(stability, record)
        validate_research_evidence_bundle(bundle, record, statistical, stability)
    except Exception as exc:
        raise ResearchAcceptanceError(str(exc)) from exc

    registered = _ledger_contains_bundle(ledger, bundle)
    if not registered:
        raise ResearchAcceptanceError("research evidence bundle is not registered in ledger")

    payload = {
        "acceptance_revision": acceptance_revision,
        "run_id": record.run_id,
        "research_record_fingerprint": record.fingerprint,
        "statistical_evidence_fingerprint": statistical.fingerprint,
        "stability_evidence_fingerprint": stability.fingerprint,
        "bundle_fingerprint": bundle.fingerprint,
        "ledger_registered": registered,
        "accepted": True,
    }
    fingerprint = hashlib.sha256(
        ResearchAcceptance._fingerprint_payload(payload)
    ).hexdigest()
    result = ResearchAcceptance(
        acceptance_revision=acceptance_revision,
        run_id=record.run_id,
        research_record_fingerprint=record.fingerprint,
        statistical_evidence_fingerprint=statistical.fingerprint,
        stability_evidence_fingerprint=stability.fingerprint,
        bundle_fingerprint=bundle.fingerprint,
        ledger_registered=registered,
        accepted=True,
        fingerprint=fingerprint,
    )
    result.validate()
    return result
