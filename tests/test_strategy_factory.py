from strategy_factory.factory import StrategyResearchFactory
from strategy_factory.models import GateStatus, StrategyPassport


def make_passport() -> StrategyPassport:
    return StrategyPassport(
        strategy_id="SP2L-A-FACTORY-0001",
        source_revision="SOURCE-PENDING",
        geometry_revision="GEOMETRY-PENDING",
        code_revision="CODE-PENDING",
        data_revision="DATA-PENDING",
        execution_model="TICK_FEASIBLE_RESEARCH_ONLY",
        parameter_set={"canonical": False},
    )


def test_factory_is_blocked_until_all_gates_pass():
    factory = StrategyResearchFactory(make_passport())
    factory.evaluate_source(source_resolved=True, unresolved_items=[])
    factory.evaluate_code(fixtures_passed=10, fixtures_total=10)
    factory.evaluate_validation(development_pass=True, untouched_validation_pass=True, robustness_pass=True, fresh_holdout_pass=False)
    factory.evaluate_forward(python_mt5_reconciled=True, forward_pass=True)
    assert factory.run.production_eligible is False
    assert any(gate.status is GateStatus.BLOCKED for gate in factory.run.gates)


def test_factory_becomes_eligible_only_after_all_gates_pass():
    factory = StrategyResearchFactory(make_passport())
    factory.evaluate_source(source_resolved=True, unresolved_items=[])
    factory.evaluate_code(fixtures_passed=10, fixtures_total=10)
    factory.evaluate_validation(development_pass=True, untouched_validation_pass=True, robustness_pass=True, fresh_holdout_pass=True)
    factory.evaluate_forward(python_mt5_reconciled=True, forward_pass=True)
    assert factory.run.production_eligible is True


def test_failed_source_is_blocking():
    factory = StrategyResearchFactory(make_passport())
    result = factory.evaluate_source(source_resolved=False, unresolved_items=["SL anchor", "fill semantics"])
    assert result.status is GateStatus.BLOCKED
    assert factory.run.production_eligible is False
