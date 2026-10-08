from __future__ import annotations

"""Compose two completed research runs into one provenance-locked 1v1 report."""

from dataclasses import dataclass

from .external_strategy import ExternalStrategyReference
from .runner import ResearchJobRunResult
from .strategy_comparison import (
    OneVsOneStrategyComparison,
    StrategyComparisonParticipant,
    build_one_vs_one_comparison,
)
from .test_contract import HistoricalTestSpec


class StrategyComparisonRunnerError(ValueError):
    """Raised when two completed runs cannot be compared fairly."""


@dataclass(frozen=True)
class OneVsOneRunInputs:
    baseline_spec: HistoricalTestSpec
    baseline_result: ResearchJobRunResult
    challenger_spec: HistoricalTestSpec
    challenger_result: ResearchJobRunResult
    challenger_external_reference: ExternalStrategyReference | None = None


def build_one_vs_one_from_runs(
    inputs: OneVsOneRunInputs,
    *,
    comparison_revision: str = "STRATEGY-1V1-RUN-COMPARISON-1",
) -> OneVsOneStrategyComparison:
    """Compare two accepted runs while preserving a common test boundary.

    The Factory never ranks the strategies or promotes one. Both runs must
    consume the exact same dataset identity and execution semantics.
    """

    b_spec = inputs.baseline_spec
    c_spec = inputs.challenger_spec
    b_result = inputs.baseline_result
    c_result = inputs.challenger_result

    b_spec.validate()
    c_spec.validate()

    if not b_result.accepted or not c_result.accepted:
        raise StrategyComparisonRunnerError(
            "1v1 comparison requires two accepted research runs"
        )

    if b_spec.dataset != c_spec.dataset:
        raise StrategyComparisonRunnerError(
            "1v1 comparison requires the exact same dataset contract"
        )

    if b_spec.execution_semantics is not c_spec.execution_semantics:
        raise StrategyComparisonRunnerError(
            "1v1 comparison requires identical execution semantics"
        )

    if b_result.receipt.input_fingerprint != c_result.receipt.input_fingerprint:
        raise StrategyComparisonRunnerError(
            "1v1 comparison requires identical execution input fingerprints"
        )

    if b_result.receipt.execution_semantics is not c_result.receipt.execution_semantics:
        raise StrategyComparisonRunnerError(
            "1v1 comparison requires identical receipt execution semantics"
        )

    baseline = StrategyComparisonParticipant(
        strategy_id=b_spec.strategy_id,
        strategy_revision=b_spec.strategy_revision,
        metrics=__import__(
            "strategy_factory.strategy_comparison",
            fromlist=["ComparisonMetrics"],
        ).ComparisonMetrics.from_research_metrics(b_result.receipt.metrics),
    )
    challenger = StrategyComparisonParticipant(
        strategy_id=c_spec.strategy_id,
        strategy_revision=c_spec.strategy_revision,
        metrics=__import__(
            "strategy_factory.strategy_comparison",
            fromlist=["ComparisonMetrics"],
        ).ComparisonMetrics.from_research_metrics(c_result.receipt.metrics),
        external_reference=inputs.challenger_external_reference,
    )

    return build_one_vs_one_comparison(
        dataset=b_spec.dataset,
        execution_semantics=b_spec.execution_semantics,
        baseline=baseline,
        challenger=challenger,
        comparison_revision=comparison_revision,
    )
