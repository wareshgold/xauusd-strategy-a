import pytest

from strategy_factory.forward_observed_evidence import (
    ForwardTradeObservation,
    build_forward_observed_evidence,
)
from strategy_factory.forward_statistical_boundary import (
    ForwardStatisticalBoundaryError,
    require_explicit_r_mapping,
)
from strategy_factory.statistics import evaluate_statistical_validation
from strategy_factory.test_contract import DatasetRole


def observed():
    trade = ForwardTradeObservation(
        deal_id=11,
        order_id=22,
        position_id=33,
        signal_id="X:1:BUY",
        entry_price=4120.0,
        exit_price=4121.0,
        profit=10.0,
        commission=-1.0,
        swap=0.0,
        fee=0.0,
        net=9.0,
        pips_result=10.0,
    )
    return build_forward_observed_evidence(
        session_id="SESSION-1",
        session_fingerprint="a" * 64,
        handoff_fingerprint="b" * 64,
        strategy_revision="STRAT-1",
        manifest_revision="MANIFEST-1",
        execution_semantics="TICK_FEASIBLE",
        broker_server="OtetGroup-MT5",
        symbol="XAUUSD.ecn",
        runner_completed=True,
        reconciliation_id="REC-1",
        observed_positions=1,
        matched_positions=1,
        mismatched_positions=0,
        trades=(trade,),
    )


def statistical():
    from strategy_factory.metrics import ResearchMetrics

    metrics = ResearchMetrics(
        trades=1,
        decisive_trades=1,
        ambiguous_trades=0,
        wins=1,
        losses=0,
        win_rate=1.0,
        net_r=1.0,
        profit_factor=2.0,
        max_drawdown_r=0.0,
    )
    return evaluate_statistical_validation(
        metrics,
        role=DatasetRole.FRESH_HOLDOUT,
        trade_returns_r=(1.0,),
    )


def test_forward_statistical_boundary_requires_explicit_r_mapping():
    with pytest.raises(ForwardStatisticalBoundaryError, match="explicit trade-return mapping"):
        require_explicit_r_mapping(observed())


def test_forward_statistical_boundary_binds_explicit_mapping():
    result = require_explicit_r_mapping(
        observed(),
        statistical_result=statistical(),
        trade_returns_r=(1.0,),
        mapping_revision="EXPLICIT-R-MAPPING-1",
        mapping_source="source-confirmed-contract-placeholder",
    )
    result.validate(observed())
    assert result.evidence_fingerprint == observed().fingerprint


def test_forward_statistical_boundary_rejects_count_drift():
    with pytest.raises(ForwardStatisticalBoundaryError, match="count"):
        require_explicit_r_mapping(
            observed(),
            statistical_result=statistical(),
            trade_returns_r=(1.0, 2.0),
            mapping_revision="EXPLICIT-R-MAPPING-1",
            mapping_source="source-confirmed-contract-placeholder",
        )
