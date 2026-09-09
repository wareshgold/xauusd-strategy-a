from sp2l_source_geometry_candidates_g36 import CANDIDATES, Resolution


def test_no_critical_geometry_is_promoted_by_default():
    critical = {"B1", "B2", "B3", "B4", "B5", "B6"}
    assert {candidate.blocker for candidate in CANDIDATES} == critical
    assert not any(candidate.resolution is Resolution.CONFIRMED for candidate in CANDIDATES)


def test_research_registry_is_not_a_production_spec():
    for candidate in CANDIDATES:
        assert candidate.forbidden_assumption
