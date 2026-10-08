import pytest

from strategy_factory.forward_observed_evidence import ForwardTradeObservation, build_forward_observed_evidence
from strategy_factory.forward_observed_statistics import (
    ForwardObservedStatisticsError,
    build_forward_observed_statistics,
)


def evidence():
    trades = (
        ForwardTradeObservation(1, 11, 21, "S1", 100, 101, 10, -1, 0, 0, 9, 10),
        ForwardTradeObservation(2, 12, 22, "S2", 100, 99, -8, -1, 0, 0, -9, -5),
        ForwardTradeObservation(3, 13, 23, "S3", 100, 100, 0, -1, 0, 0, -1, 0),
        ForwardTradeObservation(4, 14, 24, "S4", 100, 100.5, 5, -1, 0, 0, 4, None),
    )
    return build_forward_observed_evidence(
        session_id="SESSION",
        session_fingerprint="a" * 64,
        handoff_fingerprint="b" * 64,
        strategy_revision="STRAT",
        manifest_revision="MANIFEST",
        execution_semantics="TICK_FEASIBLE",
        broker_server="BROKER",
        symbol="XAUUSD.ecn",
        runner_completed=True,
        reconciliation_id="REC",
        observed_positions=4,
        matched_positions=4,
        mismatched_positions=0,
        trades=trades,
    )


def test_observed_statistics_is_deterministic_and_excludes_missing_pips():
    a = build_forward_observed_statistics(evidence())
    b = build_forward_observed_statistics(evidence())
    assert a == b
    assert a.observation_count == 4
    assert a.pips_measured_count == 3
    assert a.pips_missing_count == 1
    assert a.positive_pips_count == 1
    assert a.negative_pips_count == 1
    assert a.zero_pips_count == 1
    assert a.net_measured_count == 4
    assert a.mean_pips is not None
    assert a.mean_net is not None
    assert a.canonical_eligible is False
    assert a.production_eligible is False


def test_observed_statistics_rejects_evidence_binding_tamper():
    stats = build_forward_observed_statistics(evidence())
    other = build_forward_observed_statistics(evidence())
    assert stats.evidence_fingerprint == other.evidence_fingerprint
    with pytest.raises(ForwardObservedStatisticsError, match="not bound"):
        from dataclasses import replace
        replace(stats, evidence_fingerprint="f" * 64).validate(evidence())


def test_observed_statistics_rejects_invalid_confidence_level():
    with pytest.raises(ForwardObservedStatisticsError, match="confidence level"):
        build_forward_observed_statistics(evidence(), confidence_level=1.0)
