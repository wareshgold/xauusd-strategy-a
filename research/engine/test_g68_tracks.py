from .reporting_boundary import ResearchReportContext, canonical_claim_allowed


def test_unfrozen_geometry_cannot_make_canonical_claim():
    context = ResearchReportContext(geometry_frozen=False, strategy_validation_unlocked=False)
    assert canonical_claim_allowed(context) is False
