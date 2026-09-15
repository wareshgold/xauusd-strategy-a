import pytest

from research.evidence.sp2l_evidence_candidate_intake import (
    CandidateDisposition,
    EvidenceCandidate,
    EvidenceProvenance,
    EvidenceTier,
    intake_candidate,
)
from research.fixtures.sp2l_synthetic_fixture_contract import GeometryDimension


def candidate(disposition=CandidateDisposition.REPEAT_ONLY):
    return EvidenceCandidate(
        candidate_id="candidate-001",
        dimensions=(GeometryDimension.P_GAP,),
        provenance=EvidenceProvenance(
            artifact_ref="source-video-7HEC5mO3d3U",
            tier=EvidenceTier.TIER_1,
            timestamp="00:36:30",
            frame_ref="65700",
        ),
        discriminator_claim="Evidence changes the stated hypothesis only for review; no geometry is promoted.",
        before_hypothesis="exact executable P-Gap boundary unresolved",
        after_hypothesis="candidate evidence narrows the boundary interpretation",
        disposition=disposition,
    )


def test_repeat_candidate_is_validated_without_promotion():
    result = intake_candidate(candidate())
    assert result.disposition is CandidateDisposition.REPEAT_ONLY


def test_manual_adjudication_candidate_requires_hypothesis_change():
    result = intake_candidate(candidate(CandidateDisposition.READY_FOR_MANUAL_ADJUDICATION))
    assert result.provenance.tier is EvidenceTier.TIER_1


def test_provenance_requires_source_pointer():
    with pytest.raises(ValueError, match="frame_ref or transcript_ref"):
        EvidenceProvenance(
            artifact_ref="video",
            tier=EvidenceTier.TIER_1,
            timestamp="00:36:30",
        ).validate()


def test_manual_candidate_cannot_have_identical_hypotheses():
    item = candidate(CandidateDisposition.READY_FOR_MANUAL_ADJUDICATION)
    invalid = EvidenceCandidate(
        item.candidate_id,
        item.dimensions,
        item.provenance,
        item.discriminator_claim,
        "same",
        "same",
        item.disposition,
    )
    with pytest.raises(ValueError, match="change the hypothesis"):
        intake_candidate(invalid)


def test_candidate_does_not_expose_execution_signal():
    assert not hasattr(candidate(), "buy")
    assert not hasattr(candidate(), "sell")
