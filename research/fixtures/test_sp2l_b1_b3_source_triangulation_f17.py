from sp2l_b1_b3_source_triangulation_f17 import Candidate, f17_evidence, frozen_candidates


def test_generic_three_candle_gap_is_not_authorized():
    evidence = {e.candidate: e for e in f17_evidence()}
    assert not evidence[Candidate.PGAP_GENERIC_THREE_CANDLE].source_supported


def test_source_marked_pgap_remains_candidate_not_frozen():
    evidence = {e.candidate: e for e in f17_evidence()}
    assert evidence[Candidate.PGAP_SOURCE_MARKED_STRUCTURE].source_supported
    assert not evidence[Candidate.PGAP_SOURCE_MARKED_STRUCTURE].source_uniquely_determined


def test_entry_candidates_remain_unresolved_between_relevant_and_latest_structure():
    evidence = {e.candidate: e for e in f17_evidence()}
    assert evidence[Candidate.ENTRY_FIRST_RELEVANT_LOW_HIGH].source_supported
    assert evidence[Candidate.ENTRY_LATEST_COMPLETED_HL_LH].source_supported
    assert Candidate.ENTRY_FIRST_RELEVANT_LOW_HIGH not in frozen_candidates()
    assert Candidate.ENTRY_LATEST_COMPLETED_HL_LH not in frozen_candidates()


def test_leg2_start_is_not_entry_candidate():
    evidence = {e.candidate: e for e in f17_evidence()}
    assert not evidence[Candidate.ENTRY_LEG2_START].source_supported


def test_sl_ohlc_models_are_not_uniquely_frozen():
    evidence = {e.candidate: e for e in f17_evidence()}
    for candidate in (
        Candidate.SL_WICK_EXTREME,
        Candidate.SL_BODY_EDGE,
        Candidate.SL_STRUCTURAL_PIVOT,
    ):
        assert evidence[candidate].source_supported
        assert not evidence[candidate].source_uniquely_determined
