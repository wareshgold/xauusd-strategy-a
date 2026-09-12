from research.fixtures.sp2l_target_mapping_candidates_g319 import Candidate, assert_fixture_invariants, build_candidate


def test_target_mapping_candidates_are_distinct_and_ordered():
    assert_fixture_invariants()
    levels = {candidate: build_candidate(candidate) for candidate in Candidate}
    assert len({(v.sl, v.entry, v.tp1, v.tp2) for v in levels.values()}) == 3


def test_c1_is_only_a_hypothesis_fixture_not_a_selector():
    c1 = build_candidate(Candidate.C1)
    assert (c1.sl, c1.entry, c1.tp1, c1.tp2) == (-400.0, 100.0, 350.0, 600.0)
    # The fixture intentionally exposes candidate geometry; it does not
    # provide a function that selects C1 as canonical Strategy A.
