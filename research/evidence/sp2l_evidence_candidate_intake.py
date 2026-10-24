"""Source-first SP2L evidence candidate intake contract.

Research-only infrastructure. This module records whether new evidence
actually discriminates an unresolved executable geometry dimension. It never
promotes geometry and contains no Strategy A execution rules.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final

from research.fixtures.sp2l_synthetic_fixture_contract import GeometryDimension


class EvidenceTier(str, Enum):
    TIER_1 = "tier-1"
    TIER_2 = "tier-2"


class CandidateDisposition(str, Enum):
    REPEAT_ONLY = "repeat_only"
    NARROWS_NOT_UNIQUE = "narrows_not_unique"
    READY_FOR_MANUAL_ADJUDICATION = "ready_for_manual_adjudication"


@dataclass(frozen=True)
class EvidenceProvenance:
    artifact_ref: str
    tier: EvidenceTier
    timestamp: str
    frame_ref: str | None = None
    transcript_ref: str | None = None

    def validate(self) -> None:
        if not self.artifact_ref.strip():
            raise ValueError("artifact_ref must be non-empty")
        if not self.timestamp.strip():
            raise ValueError("timestamp must be non-empty")
        if self.frame_ref is None and self.transcript_ref is None:
            raise ValueError("provenance must include frame_ref or transcript_ref")


@dataclass(frozen=True)
class EvidenceCandidate:
    candidate_id: str
    dimensions: tuple[GeometryDimension, ...]
    provenance: EvidenceProvenance
    discriminator_claim: str
    before_hypothesis: str
    after_hypothesis: str
    disposition: CandidateDisposition
    notes: str = ""

    def validate(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("candidate_id must be non-empty")
        if not self.dimensions:
            raise ValueError("at least one geometry dimension is required")
        if len(set(self.dimensions)) != len(self.dimensions):
            raise ValueError("geometry dimensions must be unique")
        self.provenance.validate()
        if not self.discriminator_claim.strip():
            raise ValueError("discriminator_claim must be non-empty")
        if not self.before_hypothesis.strip() or not self.after_hypothesis.strip():
            raise ValueError("before_hypothesis and after_hypothesis must be non-empty")
        if self.disposition is CandidateDisposition.READY_FOR_MANUAL_ADJUDICATION:
            if self.provenance.tier not in (EvidenceTier.TIER_1, EvidenceTier.TIER_2):
                raise ValueError("manual-adjudication candidates require Tier-1 or Tier-2 provenance")
            if self.before_hypothesis == self.after_hypothesis:
                raise ValueError("manual-adjudication candidate must change the hypothesis state")


BLOCKED_BY_DEFAULT: Final[bool] = True


def intake_candidate(candidate: EvidenceCandidate) -> EvidenceCandidate:
    """Validate an evidence record without promoting any geometry."""
    candidate.validate()
    return candidate
