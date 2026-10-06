import pytest

from strategy_factory.metrics import MetricsContractError, ResearchMetrics


def metrics(**overrides):
    values = dict(
        trades=10,
        decisive_trades=10,
        wins=6,
        losses=4,
        ambiguous=0,
        win_rate=0.6,
        net_r=2.5,
        profit_factor=1.4,
        max_drawdown_r=1.2,
        gross_profit_r=6.0,
        gross_loss_r=-3.5,
    )
    values.update(overrides)
    return ResearchMetrics(**values)


def test_metrics_contract_is_valid_and_serializable():
    m = metrics()
    m.validate()
    assert m.as_dict()["win_rate"] == 0.6


def test_decisive_count_must_match_wins_and_losses():
    with pytest.raises(MetricsContractError):
        metrics(decisive_trades=9).validate()


def test_total_trades_must_include_ambiguous():
    with pytest.raises(MetricsContractError):
        metrics(trades=11).validate()


def test_win_rate_must_match_counts():
    with pytest.raises(MetricsContractError):
        metrics(win_rate=0.7).validate()


def test_zero_decisive_trades_have_zero_win_rate():
    m = metrics(
        trades=2, decisive_trades=0, wins=0, losses=0, ambiguous=2, win_rate=0.0
    )
    m.validate()


def test_invalid_drawdown_or_gross_signs_are_rejected():
    with pytest.raises(MetricsContractError):
        metrics(max_drawdown_r=-1).validate()
    with pytest.raises(MetricsContractError):
        metrics(gross_profit_r=-1).validate()
    with pytest.raises(MetricsContractError):
        metrics(gross_loss_r=1).validate()
