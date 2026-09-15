import pytest

from research.evidence.sp2l_evidence_candidate_intake import (
    CandidateDisposition,
    EvidenceCandidate,
    EvidenceProvenance,
    EvidenceTier,
)
from research.evidence.sp2l_manual_adjudication import (
    AdjudicationOutcome,
    ManualAdjudication,
    record_adjudication,
)
from research.fixtures.sp2l_synthetic_fixture_contract import GeometryDimension


def candidate():
    return EvidenceCandidate(
        candidate_id="candidate-001",
        dimensions=(GeometryDimension.P_GAP,),
        provenance=EvidenceProvenance(
            artifact_ref="source-video-7HEC5mO3d3U",
            tier=EvidenceTier.TIER_1,
            timestamp="00:36:30",
            frame_ref="65700",
        ),
        discriminator_claim="Candidate evidence is presented for human review only.",
        before_hypothesis="exact executable P-Gap boundary unresolved",
        after_hypothesis="candidate boundary interpretation is reviewable",
        disposition=CandidateDisposition.READY_FOR_MANUAL_ADJUDICATION,
    )


def test_blocked_adjudication_records_remaining_hypotheses():
    result = record_adjudication(
        candidate(),
        ManualAdjudication(
            "candidate-001", "human-review-001", AdjudicationOutcome.REMAINS_BLOCKED,
            False, False, True, "Source does not uniquely discriminate the boundary.",
            "Multiple candle-boundary interpretations remain viable.",
        ),
    )
    assert result.outcome is AdjudicationOutcome.REMAINS_BLOCKED


def test_source_discriminated_requires_all_safety_conditions():
    result = record_adjudication(
        candidate(),
        ManualAdjudication(
            "candidate-001", "human-review-001", AdjudicationOutcome.SOURCE_DISCRIMINATED,
            True, True, False, "Human review confirms the cited source discriminator.",
        ),
    )
    assert result.outcome is AdjudicationOutcome.SOURCE_DISCRIMINATED


def test_source_discriminated_cannot_require_invention():
    with pytest.raises(ValueError, match="require invention"):
        record_adjudication(
            candidate(),
            ManualAdjudication(
                "candidate-001", "human-review-001", AdjudicationOutcome.SOURCE_DISCRIMINATED,
                True, True, True, "Would require an inferred threshold.",
            ),
        )


def test_blocked_outcome_requires_remaining_hypotheses():
    with pytest.raises(ValueError, match="remaining hypotheses"):
        record_adjudication(
            candidate(),
            ManualAdjudication(
                "candidate-001", "human-review-001", AdjudicationOutcome.REMAINS_BLOCKED,
                False, False, False, "Insufficient discrimination.",
            ),
        )
