from sp2l_blocker_b1_b6_f16 import CandidateStatus, F16_BLOCKERS, blocker_by_id, production_safe

def test_all_b1_b6_blockers_are_explicit():
    assert [b.id for b in F16_BLOCKERS] == ["B1_PGAP", "B2_ENTRY", "B3_SL", "B4_TRIGGER", "B5_ABCD", "B6_LEG2_TP1"]

def test_critical_geometry_is_not_promoted():
    for blocker_id in ("B1_PGAP", "B3_SL", "B5_ABCD", "B6_LEG2_TP1"):
        assert production_safe(blocker_by_id(blocker_id)) is False

def test_entry_and_trigger_remain_candidate_families():
    assert blocker_by_id("B2_ENTRY").status is CandidateStatus.CANDIDATE
    assert blocker_by_id("B4_TRIGGER").status is CandidateStatus.CANDIDATE

def test_forbidden_shortcuts_remain_unresolved():
    assert "generic_three_candle_imbalance" in blocker_by_id("B1_PGAP").candidates
    assert "fixed_ratio_projection" in blocker_by_id("B6_LEG2_TP1").candidates
    assert not production_safe(blocker_by_id("B1_PGAP"))
    assert not production_safe(blocker_by_id("B6_LEG2_TP1"))
