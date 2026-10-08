from __future__ import annotations

import hashlib
import json
from types import SimpleNamespace

import pytest

from src.strategy_factory.forward_gate_factory import ForwardGateResult
from src.strategy_factory.forward_session_factory import DemoForwardSessionFactory
from src.strategy_factory.forward_session_lifecycle import (
    DemoForwardSessionLifecycle,
    ForwardSessionLifecycleError,
    ForwardSessionState,
    bind_mt5_reconciliation,
)
from src.strategy_factory.models import GateResult, GateStatus


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _session():
    gate = ForwardGateResult(
        gate=GateResult(
            name="FRESH_HOLDOUT_TO_FORWARD",
            status=GateStatus.PASS,
            evidence="holdout-pass",
            details={
                "production_decision": False,
                "handoff_fingerprint": _sha("handoff"),
                "strategy_revision": "STRAT-1",
                "manifest_revision": "MAN-1",
                "holdout_dataset_id": "HOLDOUT-1",
                "holdout_artifact_id": "ART-H",
                "holdout_dataset_sha256": _sha("holdout"),
            },
        )
    )
    record = SimpleNamespace(
        strategy_id="SP2L",
        strategy_revision="STRAT-1",
        manifest_revision="MAN-1",
        dataset_id="HOLDOUT-1",
        execution_semantics="CLOSE_ON_TARGET",
        validate=lambda: None,
    )
    return DemoForwardSessionFactory().prepare(
        gate=gate,
        source_record=record,
        session_id="SESSION-1",
        forward_dataset_id="FORWARD-1",
        forward_dataset_artifact_id="ART-F",
        forward_dataset_content_sha256=_sha("forward"),
    ).session


def test_lifecycle_is_monotonic_and_frozen():
    session = _session()
    lifecycle = DemoForwardSessionLifecycle(session)
    assert lifecycle.state is ForwardSessionState.PREPARED
    lifecycle.start(occurred_utc="2026-10-07T10:00:00+00:00")
    lifecycle.run(occurred_utc="2026-10-07T10:01:00+00:00")
    lifecycle.complete(occurred_utc="2026-10-07T10:02:00+00:00")
    assert lifecycle.state is ForwardSessionState.COMPLETED
    assert [e.sequence for e in lifecycle.entries()] == [1, 2, 3]
    assert all(e.handoff_fingerprint == _sha("handoff") for e in lifecycle.entries())
    lifecycle.assert_frozen_identity(
        strategy_revision="STRAT-1",
        manifest_revision="MAN-1",
        execution_semantics="CLOSE_ON_TARGET",
    )


def test_invalid_transition_is_rejected():
    lifecycle = DemoForwardSessionLifecycle(_session())
    with pytest.raises(ForwardSessionLifecycleError):
        lifecycle.complete(occurred_utc="2026-10-07T10:00:00+00:00")


def test_identity_drift_and_tuning_are_rejected():
    lifecycle = DemoForwardSessionLifecycle(_session())
    lifecycle.start(occurred_utc="2026-10-07T10:00:00+00:00")
    with pytest.raises(ForwardSessionLifecycleError):
        lifecycle.assert_frozen_identity(
            strategy_revision="STRAT-2",
            manifest_revision="MAN-1",
            execution_semantics="CLOSE_ON_TARGET",
        )
    with pytest.raises(ForwardSessionLifecycleError):
        lifecycle.assert_frozen_identity(
            strategy_revision="STRAT-1",
            manifest_revision="MAN-1",
            execution_semantics="CLOSE_ON_TARGET",
            post_holdout_tuning=True,
        )


def test_event_fingerprints_are_deterministic():
    a = DemoForwardSessionLifecycle(_session())
    b = DemoForwardSessionLifecycle(_session())
    ea = a.start(occurred_utc="2026-10-07T10:00:00+00:00")
    eb = b.start(occurred_utc="2026-10-07T10:00:00+00:00")
    assert ea.event_fingerprint == eb.event_fingerprint


def test_reconciliation_requires_completed_session():
    lifecycle = DemoForwardSessionLifecycle(_session())
    with pytest.raises(ForwardSessionLifecycleError):
        bind_mt5_reconciliation(
            session=lifecycle.session,
            lifecycle=lifecycle,
            reconciliation_id="REC-1",
            broker_server="OtetGroup-MT5",
            symbol="XAUUSD.ecn",
            observed_positions=2,
            matched_positions=2,
            mismatched_positions=0,
        )


def test_reconciliation_binds_to_completed_session():
    lifecycle = DemoForwardSessionLifecycle(_session())
    lifecycle.start(occurred_utc="2026-10-07T10:00:00+00:00")
    lifecycle.run(occurred_utc="2026-10-07T10:01:00+00:00")
    lifecycle.complete(occurred_utc="2026-10-07T10:02:00+00:00")
    receipt = bind_mt5_reconciliation(
        session=lifecycle.session,
        lifecycle=lifecycle,
        reconciliation_id="REC-1",
        broker_server="OtetGroup-MT5",
        symbol="XAUUSD.ecn",
        observed_positions=2,
        matched_positions=2,
        mismatched_positions=0,
    )
    assert receipt.reconciled is True
    assert receipt.handoff_fingerprint == lifecycle.session.handoff_fingerprint
    receipt.validate()


def test_reconciliation_count_mismatch_is_rejected():
    lifecycle = DemoForwardSessionLifecycle(_session())
    lifecycle.start(occurred_utc="2026-10-07T10:00:00+00:00")
    lifecycle.run(occurred_utc="2026-10-07T10:01:00+00:00")
    lifecycle.complete(occurred_utc="2026-10-07T10:02:00+00:00")
    with pytest.raises(ForwardSessionLifecycleError):
        bind_mt5_reconciliation(
            session=lifecycle.session,
            lifecycle=lifecycle,
            reconciliation_id="REC-1",
            broker_server="OtetGroup-MT5",
            symbol="XAUUSD.ecn",
            observed_positions=2,
            matched_positions=1,
            mismatched_positions=0,
        )


def test_event_validation_rejects_handoff_fingerprint_drift():
    from dataclasses import replace

    lifecycle = DemoForwardSessionLifecycle(_session())
    event = lifecycle.start(occurred_utc="2026-10-07T10:00:00+00:00")
    forged = replace(event, handoff_fingerprint=_sha("different-handoff"))
    with pytest.raises(ForwardSessionLifecycleError):
        forged.validate()


def test_reconciliation_binding_rejects_handoff_drift_in_lifecycle():
    from dataclasses import replace

    lifecycle = DemoForwardSessionLifecycle(_session())
    lifecycle.start(occurred_utc="2026-10-07T10:00:00+00:00")
    lifecycle.run(occurred_utc="2026-10-07T10:01:00+00:00")
    lifecycle.complete(occurred_utc="2026-10-07T10:02:00+00:00")

    forged = replace(
        lifecycle.entries()[1],
        handoff_fingerprint=_sha("different-handoff"),
    )
    lifecycle._events[1] = forged

    with pytest.raises(ForwardSessionLifecycleError):
        bind_mt5_reconciliation(
            session=lifecycle.session,
            lifecycle=lifecycle,
            reconciliation_id="REC-DRIFT-HANDOFF",
            broker_server="OtetGroup-MT5",
            symbol="XAUUSD.ecn",
            observed_positions=1,
            matched_positions=1,
            mismatched_positions=0,
        )


def test_reconciliation_binding_rejects_session_fingerprint_drift_in_lifecycle():
    from dataclasses import replace

    lifecycle = DemoForwardSessionLifecycle(_session())
    lifecycle.start(occurred_utc="2026-10-07T10:00:00+00:00")
    lifecycle.run(occurred_utc="2026-10-07T10:01:00+00:00")
    lifecycle.complete(occurred_utc="2026-10-07T10:02:00+00:00")

    forged = replace(
        lifecycle.entries()[0],
        session_fingerprint=_sha("different-session"),
    )
    lifecycle._events[0] = forged

    with pytest.raises(ForwardSessionLifecycleError):
        bind_mt5_reconciliation(
            session=lifecycle.session,
            lifecycle=lifecycle,
            reconciliation_id="REC-DRIFT-SESSION",
            broker_server="OtetGroup-MT5",
            symbol="XAUUSD.ecn",
            observed_positions=1,
            matched_positions=1,
            mismatched_positions=0,
        )


def test_reconciliation_binding_rejects_strategy_manifest_or_execution_drift():
    from dataclasses import replace

    lifecycle = DemoForwardSessionLifecycle(_session())
    lifecycle.start(occurred_utc="2026-10-07T10:00:00+00:00")
    lifecycle.run(occurred_utc="2026-10-07T10:01:00+00:00")
    lifecycle.complete(occurred_utc="2026-10-07T10:02:00+00:00")

    for field, value in (
        ("strategy_revision", "STRAT-DRIFT"),
        ("manifest_revision", "MAN-DRIFT"),
        ("execution_semantics", "DRIFTED_SEMANTICS"),
    ):
        forged = replace(lifecycle.entries()[0], **{field: value})
        lifecycle._events[0] = forged
        with pytest.raises(ForwardSessionLifecycleError):
            bind_mt5_reconciliation(
                session=lifecycle.session,
                lifecycle=lifecycle,
                reconciliation_id=f"REC-DRIFT-{field}",
                broker_server="OtetGroup-MT5",
                symbol="XAUUSD.ecn",
                observed_positions=1,
                matched_positions=1,
                mismatched_positions=0,
            )
        lifecycle._events[0] = replace(
            lifecycle.entries()[0],
            **{field: getattr(lifecycle.session, field)},
        )


def test_reconciliation_receipt_validation_rejects_fingerprint_tampering():
    from dataclasses import replace

    lifecycle = DemoForwardSessionLifecycle(_session())
    lifecycle.start(occurred_utc="2026-10-07T10:00:00+00:00")
    lifecycle.run(occurred_utc="2026-10-07T10:01:00+00:00")
    lifecycle.complete(occurred_utc="2026-10-07T10:02:00+00:00")
    receipt = bind_mt5_reconciliation(
        session=lifecycle.session,
        lifecycle=lifecycle,
        reconciliation_id="REC-TAMPER",
        broker_server="OtetGroup-MT5",
        symbol="XAUUSD.ecn",
        observed_positions=1,
        matched_positions=1,
        mismatched_positions=0,
    )

    forged = replace(receipt, handoff_fingerprint=_sha("different-handoff"))
    with pytest.raises(ForwardSessionLifecycleError):
        forged.validate()
