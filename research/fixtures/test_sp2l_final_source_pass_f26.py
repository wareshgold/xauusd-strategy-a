from sp2l_final_source_pass_f26 import (
    Resolution,
    final_source_decisions,
    generic_fvg_is_source_equivalent_to_pgap,
    market_close_reclaim_can_replace_pending_limit,
    production_freeze_is_allowed,
    risk_budget_can_define_structural_stop,
)


def test_all_core_semantics_are_classified():
    decisions = {d.item: d for d in final_source_decisions()}
    for item in ("P-Gap", "Pending Limit", "Structural invalidation", "Trigger family", "AB=CD", "Leg 1 / Leg 2"):
        assert decisions[item].semantic is Resolution.CONFIRMED


def test_unresolved_geometry_is_not_promoted():
    decisions = {d.item: d for d in final_source_decisions()}
    assert decisions["P-Gap"].executable_geometry is Resolution.UNRESOLVED
    assert decisions["Structural invalidation"].executable_geometry is Resolution.UNRESOLVED
    assert decisions["AB=CD"].executable_geometry is Resolution.UNRESOLVED
    assert decisions["Leg 1 / Leg 2"].executable_geometry is Resolution.UNRESOLVED


def test_forbidden_substitutions_remain_false():
    assert generic_fvg_is_source_equivalent_to_pgap() is False
    assert market_close_reclaim_can_replace_pending_limit() is False
    assert risk_budget_can_define_structural_stop() is False


def test_production_freeze_remains_locked():
    assert production_freeze_is_allowed() is False
