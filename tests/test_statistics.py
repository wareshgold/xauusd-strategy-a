import pytest

from strategy_factory.metrics import ResearchMetrics
from strategy_factory.statistics import (
    StatisticalValidationError,
    evaluate_statistical_validation,
)
from strategy_factory.test_contract import DatasetRole


def metrics() -> ResearchMetrics:
    return ResearchMetrics(
        trades=10,
        decisive_trades=10,
        wins=6,
        losses=4,
        ambiguous=0,
        win_rate=0.6,
        net_r=2.0,
        profit_factor=1.5,
        max_drawdown_r=1.0,
        gross_profit_r=6.0,
        gross_loss_r=-4.0,
    )


def test_wilson_interval_is_deterministic_and_descriptive():
    result = evaluate_statistical_validation(
        metrics(), role=DatasetRole.UNTOUCHED_VALIDATION
    )
    assert result.sample_size == 10
    assert result.win_rate.estimate == 0.6
    assert 0.0 < result.win_rate.lower < 0.6 < result.win_rate.upper < 1.0
    assert result.canonical_eligible is False
    assert result.production_eligible is False


def test_trade_returns_add_mean_interval_and_sign_test():
    result = evaluate_statistical_validation(
        metrics(),
        role=DatasetRole.FRESH_HOLDOUT,
        trade_returns_r=(1, -1, 1, 1, -1, 1, -1, 1, -1, 1),
    )
    assert result.mean_r is not None
    assert result.mean_r.estimate == 0.2
    assert result.sign_test_p_value is not None
    assert 0.0 <= result.sign_test_p_value <= 1.0


def test_multiple_comparison_adjustment_is_bonferroni_descriptive_only():
    result = evaluate_statistical_validation(
        metrics(),
        role=DatasetRole.DEVELOPMENT,
        trade_returns_r=(1, -1, 1, 1, -1, 1, -1, 1, -1, 1),
        comparison_count=4,
    )
    assert result.adjusted_sign_test_p_value == min(
        1.0, result.sign_test_p_value * 4
    )


def test_segment_stability_is_descriptive_range():
    result = evaluate_statistical_validation(
        metrics(),
        role=DatasetRole.UNTOUCHED_VALIDATION,
        segment_mean_r=(0.1, 0.4, -0.2),
    )
    assert result.stability_min_mean_r == -0.2
    assert result.stability_max_mean_r == 0.4
    assert result.stability_range_r == 0.6000000000000001


def test_trade_return_length_must_match_decisive_trades():
    with pytest.raises(StatisticalValidationError, match="decisive_trades"):
        evaluate_statistical_validation(
            metrics(), role=DatasetRole.DEVELOPMENT, trade_returns_r=(1.0,)
        )


def test_invalid_comparison_count_is_rejected():
    with pytest.raises(StatisticalValidationError, match="comparison_count"):
        evaluate_statistical_validation(
            metrics(), role=DatasetRole.DEVELOPMENT, comparison_count=0
        )


def test_zero_decisive_trades_have_explicit_zero_to_one_interval():
    empty = ResearchMetrics(
        trades=0,
        decisive_trades=0,
        wins=0,
        losses=0,
        ambiguous=0,
        win_rate=0.0,
        net_r=0.0,
        profit_factor=None,
        max_drawdown_r=0.0,
        gross_profit_r=0.0,
        gross_loss_r=0.0,
    )
    result = evaluate_statistical_validation(empty, role=DatasetRole.DEVELOPMENT)
    assert result.win_rate.lower == 0.0
    assert result.win_rate.upper == 1.0
