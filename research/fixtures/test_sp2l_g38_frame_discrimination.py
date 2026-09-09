from sp2l_g38_frame_discrimination import (
    Decision,
    abcd_candidates,
    classify_candidates,
    entry_candidates,
    p_gap_candidates,
)


def test_p_gap_rejects_generic_fvg_but_stays_unresolved():
    assert classify_candidates(p_gap_candidates()) is Decision.UNRESOLVED


def test_entry_anchor_stays_unresolved_when_two_source_consistent_candidates_remain():
    assert classify_candidates(entry_candidates()) is Decision.UNRESOLVED


def test_abcd_anchor_stays_unresolved_when_multiple_models_fit():
    assert classify_candidates(abcd_candidates()) is Decision.UNRESOLVED


def test_unique_candidate_can_be_confirmed_without_optimization():
    from sp2l_g38_frame_discrimination import Candidate

    assert classify_candidates([Candidate("source_unique", True)]) is Decision.CONFIRMED
