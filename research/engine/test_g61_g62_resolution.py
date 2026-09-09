from .g61_g62_resolution import CASES, Verdict, canonical_cases, frozen_geometry_allowed, unresolved_critical_blockers


def test_only_explicitly_rejected_candidate_is_generic_fvg():
    rejected = [case.case_id for case in CASES if case.verdict is Verdict.REJECTED]
    assert rejected == ["B1-GENERIC-FVG"]


def test_critical_geometry_remains_unresolved():
    assert unresolved_critical_blockers() == ("B1", "B2", "B3", "B4", "B5", "B6")
    assert canonical_cases() == ()


def test_frozen_geometry_stays_blocked():
    assert not frozen_geometry_allowed()
