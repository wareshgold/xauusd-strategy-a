from sp2l_source_geometry_candidates_g36 import CANDIDATES, Resolution, unresolved_blockers


def test_all_current_critical_geometry_candidates_remain_unresolved():
    assert {candidate.blocker for candidate in CANDIDATES} == {"B1", "B2", "B3", "B4", "B5", "B6"}
    assert all(candidate.resolution is Resolution.UNRESOLVED for candidate in CANDIDATES)


def test_unresolved_blockers_are_explicit():
    assert unresolved_blockers() == ("B1", "B2", "B3", "B4", "B5", "B6")
