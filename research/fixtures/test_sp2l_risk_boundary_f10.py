from sp2l_risk_boundary_f10 import CandidateTrade, evaluate, f10_cases


def test_risk_budget_changes_size_not_geometry():
    candidate = f10_cases()["base_structural_stop"]
    low = evaluate(candidate, 10000.0, 0.01, 1.0)
    high = evaluate(candidate, 10000.0, 0.02, 1.0)

    assert low.entry == high.entry == candidate.entry
    assert low.stop == high.stop == candidate.structural_anchor
    assert high.position_size == 2 * low.position_size


def test_candidate_stop_anchors_are_not_silently_aliased():
    cases = f10_cases()
    assert cases["wick_candidate"].structural_anchor != cases["body_candidate"].structural_anchor
    assert cases["base_structural_stop"].structural_anchor != cases["relevant_swing_candidate"].structural_anchor


def test_risk_engine_does_not_rewrite_strategy_geometry():
    candidate = CandidateTrade(entry=103.0, structural_anchor=99.0)
    result = evaluate(candidate, 25000.0, 0.005, 2.0)
    assert result.entry == 103.0
    assert result.stop == 99.0
