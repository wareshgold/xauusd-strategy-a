from .reporting_boundary import ResearchReportContext, canonical_claim_allowed


def test_research_context_does_not_authorize_canonical_claims():
    context = ResearchReportContext(geometry_frozen=False, strategy_validation_unlocked=False)
    assert canonical_claim_allowed(context) is False


def test_canonical_claim_requires_both_gates():
    assert canonical_claim_allowed(ResearchReportContext(True, False)) is False
    assert canonical_claim_allowed(ResearchReportContext(False, True)) is False
    assert canonical_claim_allowed(ResearchReportContext(True, True)) is True
