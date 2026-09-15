"""Manual adjudication record for SP2L evidence candidates.

Research-governance infrastructure only. This module records a human review
outcome without promoting Strategy A geometry or generating execution signals.
"""

from dataclasses import dataclass
from enum import Enum

from research.evidence.sp2l_evidence_candidate_intake import EvidenceCandidate, EvidenceTier


class AdjudicationOutcome(str, Enum):
    SOURCE_DISCRIMINATED = "source_discriminated"
    REMAINS_BLOCKED = "remains_blocked"


@dataclass(frozen=True)
class ManualAdjudication:
    candidate_id: str
    adjudicator_ref: str
    outcome: AdjudicationOutcome
    source_discriminator_confirmed: bool
    reproducibility_confirmed: bool
    invention_required: bool
    rationale: str
    remaining_hypotheses: str = ""

    def validate_against(self, candidate: EvidenceCandidate) -> None:
        if not self.candidate_id.strip() or self.candidate_id != candidate.candidate_id:
            raise ValueError("candidate_id must match the evidence candidate")
        if not self.adjudicator_ref.strip():
            raise ValueError("adjudicator_ref must be non-empty")
        if not self.rationale.strip():
            raise ValueError("rationale must be non-empty")
        if candidate.provenance.tier not in (EvidenceTier.TIER_1, EvidenceTier.TIER_2):
            raise ValueError("manual adjudication requires Tier-1 or Tier-2 provenance")
        if self.outcome is AdjudicationOutcome.SOURCE_DISCRIMINATED:
            if not self.source_discriminator_confirmed:
                raise ValueError("source discriminator must be confirmed")
            if not self.reproducibility_confirmed:
                raise ValueError("reproducibility must be confirmed")
            if self.invention_required:
                raise ValueError("source-discriminated outcome cannot require invention")
        if self.outcome is AdjudicationOutcome.REMAINS_BLOCKED and not self.remaining_hypotheses.strip():
            raise ValueError("blocked outcome must record remaining hypotheses")


def record_adjudication(candidate: EvidenceCandidate, adjudication: ManualAdjudication) -> ManualAdjudication:
    """Validate a human adjudication record; never promotes geometry."""
    candidate.validate()
    adjudication.validate_against(candidate)
    return adjudication
