from .source_discrimination_g56 import CASES, Resolution, production_allowed, unresolved_blockers


def test_g56_has_explicit_cases_for_b1_to_b6():
    assert {case.blocker for case in CASES} == {"B1", "B2", "B3", "B4", "B5", "B6"}


def test_source_consistent_candidates_are_not_promoted_to_canonical_geometry():
    assert all(case.resolution in {Resolution.SUPPORTED, Resolution.UNRESOLVED} for case in CASES)
    assert unresolved_blockers() == ("B1", "B2", "B4", "B6")


def test_production_remains_blocked():
    assert production_allowed() is False
