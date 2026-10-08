import pytest

from strategy_factory.external_strategy import ExternalStrategyReference
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.strategy_comparison import (
    ComparisonMetrics,
    StrategyComparisonError,
    StrategyComparisonParticipant,
    build_one_vs_one_comparison,
)
from strategy_factory.test_contract import DatasetRole, ExecutionSemantics, TestDataset


def make_dataset():
    return TestDataset(
        dataset_id="COMMON-DATASET-001",
        role=DatasetRole.DEVELOPMENT,
        data_revision="XAU-M1-FIXTURE-1",
        start="2026-01-01T00:00:00Z",
        end="2026-01-02T00:00:00Z",
        source="synthetic://xauusd/common",
    )


def make_metrics(wins=3, losses=1, ambiguous=0):
    return ResearchMetrics(
        trades=wins + losses + ambiguous,
        decisive_trades=wins + losses,
        wins=wins,
        losses=losses,
        ambiguous=ambiguous,
        win_rate=0.0 if wins + losses == 0 else wins / (wins + losses),
        net_r=0.0,
        profit_factor=None if losses == 0 else wins / losses,
        max_drawdown_r=0.0,
        gross_profit_r=float(wins),
        gross_loss_r=-float(losses),
    )


def make_participants():
    baseline = StrategyComparisonParticipant(
        strategy_id="SP2L_V3_RR2_TRAIL4",
        strategy_revision="REV-20261008",
        metrics=ComparisonMetrics.from_research_metrics(make_metrics(3, 1)),
    )
    external = ExternalStrategyReference(
        strategy_id="ALIREZA_SP2L",
        upstream_repository="AlirezaSadabadi/PythonTraderBot",
        upstream_path="code/SP2L/SP2L_Advanced_Bot_Optimized.py",
        upstream_ref="main",
        upstream_blob_sha="602c6b79d86189e044b9520689d963b746d74b5c",
    )
    challenger = StrategyComparisonParticipant(
        strategy_id="ALIREZA_SP2L",
        strategy_revision="UPSTREAM-602c6b79",
        metrics=ComparisonMetrics.from_research_metrics(make_metrics(2, 2)),
        external_reference=external,
    )
    return baseline, challenger


def test_1v1_requires_distinct_strategy_ids():
    baseline, challenger = make_participants()
    same = StrategyComparisonParticipant(
        strategy_id=baseline.strategy_id,
        strategy_revision="OTHER",
        metrics=challenger.metrics,
    )
    with pytest.raises(StrategyComparisonError):
        build_one_vs_one_comparison(
            dataset=make_dataset(),
            execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
            baseline=baseline,
            challenger=same,
        )


def test_1v1_uses_common_dataset_and_never_declares_winner():
    baseline, challenger = make_participants()
    comparison = build_one_vs_one_comparison(
        dataset=make_dataset(),
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        baseline=baseline,
        challenger=challenger,
    )
    payload = comparison.as_dict()
    assert payload["decision"] == "DESCRIPTIVE_ONLY"
    assert payload["winner"] is None
    assert payload["production_eligible"] is False
    assert payload["metric_deltas"]["win_rate"] == pytest.approx(-0.25)


def test_external_reference_is_immutable_and_traceable():
    _, challenger = make_participants()
    reference = challenger.external_reference
    assert reference is not None
    assert reference.fingerprint
    assert reference.upstream_blob_sha == "602c6b79d86189e044b9520689d963b746d74b5c"


def test_invalid_external_role_cannot_pass():
    with pytest.raises(StrategyComparisonError):
        participant = StrategyComparisonParticipant(
            strategy_id="ALIREZA_SP2L",
            strategy_revision="UPSTREAM-1",
            metrics=ComparisonMetrics.from_research_metrics(make_metrics()),
            external_reference=ExternalStrategyReference(
                strategy_id="ALIREZA_SP2L",
                upstream_repository="AlirezaSadabadi/PythonTraderBot",
                upstream_path="code/SP2L/SP2L_Advanced_Bot_Optimized.py",
                upstream_ref="main",
                upstream_blob_sha="602c6b79d86189e044b9520689d963b746d74b5c",
                implementation_role="CANONICAL",
            ),
        )
        participant.validate()
