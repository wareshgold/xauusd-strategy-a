from dataclasses import replace

import pytest

from strategy_factory.forward_observed_evidence import (
    ForwardObservedEvidenceError,
    ForwardTradeObservation,
    build_forward_observed_evidence,
    observations_from_lifecycle_events,
)


def trade(deal_id=11):
    return ForwardTradeObservation(
        deal_id=deal_id,
        order_id=22,
        position_id=33,
        signal_id="X:1:BUY",
        entry_price=4120.0,
        exit_price=4121.0,
        profit=10.0,
        commission=-1.0,
        swap=-0.5,
        fee=-0.5,
        net=8.0,
        pips_result=10.0,
    )


def evidence():
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
        trades=(trade(),),
    )


def test_forward_observed_evidence_is_deterministic_and_immutable():
    first = evidence()
    second = evidence()
    assert first == second
    assert len(first.fingerprint) == 64
    first.validate()


def test_forward_observed_evidence_rejects_fingerprint_tampering():
    tampered = replace(evidence(), symbol="OTHER")
    with pytest.raises(ForwardObservedEvidenceError, match="fingerprint mismatch"):
        tampered.validate()


def test_forward_observed_evidence_rejects_incomplete_runner():
    with pytest.raises(ForwardObservedEvidenceError, match="incomplete forward runner"):
        build_forward_observed_evidence(
            session_id="SESSION-1",
            session_fingerprint="a" * 64,
            handoff_fingerprint="b" * 64,
            strategy_revision="STRAT-1",
            manifest_revision="MANIFEST-1",
            execution_semantics="TICK_FEASIBLE",
            broker_server="OtetGroup-MT5",
            symbol="XAUUSD.ecn",
            runner_completed=False,
            reconciliation_id="REC-1",
            observed_positions=0,
            matched_positions=0,
            mismatched_positions=0,
            trades=(),
        )


def test_lifecycle_adapter_extracts_only_close_observations():
    events = [
        {
            "event": "TELEGRAM_DEAL_LIFECYCLE",
            "deal": 1,
            "order": 2,
            "position": 3,
            "entry": 0,
            "profit": 0,
            "commission": 0,
            "swap": 0,
            "net": 0,
        },
        {
            "event": "TELEGRAM_DEAL_LIFECYCLE",
            "deal": 4,
            "order": 2,
            "position": 3,
            "entry": 1,
            "signal_id": "X:1:BUY",
            "entry_price": 4120.0,
            "exit_price": 4121.0,
            "profit": 10.0,
            "commission": -1.0,
            "swap": -0.5,
            "fee": -0.5,
            "net": 8.0,
            "pips_result": 10.0,
        },
    ]
    observations = observations_from_lifecycle_events(events)
    assert len(observations) == 1
    assert observations[0].deal_id == 4
    assert observations[0].net == 8.0


def test_lifecycle_adapter_rejects_missing_observed_close_field():
    events = [
        {
            "event": "TELEGRAM_DEAL_LIFECYCLE",
            "deal": 4,
            "order": 2,
            "position": 3,
            "entry": 1,
            "profit": 10.0,
            "commission": -1.0,
            "swap": -0.5,
            "net": 8.0,
        }
    ]
    with pytest.raises(ForwardObservedEvidenceError, match="exit_price"):
        observations_from_lifecycle_events(events)
