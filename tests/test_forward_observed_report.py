from dataclasses import replace

import pytest

from strategy_factory.forward_observed_evidence import ForwardTradeObservation, build_forward_observed_evidence
from strategy_factory.forward_observed_report import ForwardObservedReportError, build_forward_observed_report
from strategy_factory.forward_observed_statistics import build_forward_observed_statistics


def evidence():
    trades = (
        ForwardTradeObservation(1, 11, 21, "S1", 100.0, 101.0, 10.0, -1.0, 0.0, 0.0, 9.0, 10.0),
        ForwardTradeObservation(2, 12, 22, "S2", 100.0, 99.0, -8.0, -1.0, 0.0, 0.0, -9.0, -5.0),
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
        observed_positions=2,
        matched_positions=2,
        mismatched_positions=0,
        trades=trades,
    )


def test_report_is_deterministic_and_research_only():
    ev = evidence()
    a = build_forward_observed_report(ev)
    b = build_forward_observed_report(ev)
    assert a == b
    assert a.status == "OBSERVED_FORWARD_RESEARCH"
    assert a.canonical_eligible is False
    assert a.production_eligible is False
    assert a.evidence_fingerprint == ev.fingerprint
    assert a.statistics["observation_count"] == 2
    assert a.fingerprint


def test_report_rejects_evidence_drift():
    ev = evidence()
    report = build_forward_observed_report(ev)
    stats = build_forward_observed_statistics(ev)
    with pytest.raises(ForwardObservedReportError, match="identity drift"):
        replace(report, symbol="OTHER").validate(ev, stats)


def test_report_rejects_statistics_drift():
    ev = evidence()
    report = build_forward_observed_report(ev)
    stats = build_forward_observed_statistics(ev)
    drifted = replace(report, statistics={**report.statistics, "observation_count": 3})
    with pytest.raises(ForwardObservedReportError, match="statistics payload drift"):
        drifted.validate(ev, stats)


def test_report_rejects_fingerprint_tampering():
    ev = evidence()
    report = build_forward_observed_report(ev)
    stats = build_forward_observed_statistics(ev)
    with pytest.raises(ForwardObservedReportError, match="fingerprint"):
        replace(report, fingerprint="f" * 64).validate(ev, stats)
