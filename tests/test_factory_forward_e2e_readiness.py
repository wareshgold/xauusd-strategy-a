from __future__ import annotations

import hashlib

from strategy_factory.forward_gate_factory import ForwardGateResult
from strategy_factory.forward_session_factory import DemoForwardSessionFactory
from strategy_factory.forward_session_lifecycle import (
    DemoForwardSessionLifecycle,
    ForwardSessionState,
    bind_mt5_reconciliation,
)
from strategy_factory.models import GateResult, GateStatus


class SyntheticHoldoutRecord:
    strategy_id = "SP2L-A"
    strategy_revision = "REV-SYNTH-FWD-1"
    manifest_revision = "MANIFEST-SYNTH-FWD-1"
    execution_semantics = "BAR_CLOSE_RESEARCH"
    dataset_id = "HOLDOUT-SYNTH-1"

    def validate(self):
        return None


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _gate(session_id: str, dataset_id: str, artifact_id: str, dataset_sha256: str) -> ForwardGateResult:
    return ForwardGateResult(
        gate=GateResult(
            name="FRESH_HOLDOUT_TO_FORWARD",
            status=GateStatus.PASS,
            evidence="synthetic-holdout-forward-evidence",
            details={
                "source_station": "holdout",
                "destination_station": "forward",
                "forward_session_id": session_id,
                "forward_dataset_id": dataset_id,
                "forward_artifact_id": artifact_id,
                "forward_dataset_sha256": dataset_sha256,
                "strategy_revision": "REV-SYNTH-FWD-1",
                "manifest_revision": "MANIFEST-SYNTH-FWD-1",
                "holdout_dataset_id": "HOLDOUT-SYNTH-1",
                "holdout_dataset_sha256": _sha(b"holdout"),
                "holdout_artifact_id": "HOLDOUT-ART-SYNTH-1",
                "handoff_fingerprint": _sha(b"synthetic-handoff"),
                "production_decision": False,
            },
        )
    )


def test_factory_forward_readiness_composes_gate_session_lifecycle_and_reconciliation():
    record = SyntheticHoldoutRecord()

    forward_sha = _sha(b"forward")
    gate = _gate(
        "FORWARD-SESSION-SYNTH-1",
        "FORWARD-DATA-SYNTH-1",
        "FORWARD-ART-SYNTH-1",
        forward_sha,
    )
    session = DemoForwardSessionFactory().prepare(
        gate=gate,
        source_record=record,
        session_id="FORWARD-SESSION-SYNTH-1",
        forward_dataset_id="FORWARD-DATA-SYNTH-1",
        forward_dataset_artifact_id="FORWARD-ART-SYNTH-1",
        forward_dataset_content_sha256=forward_sha,
    ).session

    assert session.strategy_revision == record.strategy_revision
    assert session.manifest_revision == record.manifest_revision
    assert session.holdout_dataset_id == record.dataset_id
    assert session.forward_dataset_id != session.holdout_dataset_id
    assert session.production_decision is False
    assert session.post_holdout_tuning is False

    lifecycle = DemoForwardSessionLifecycle(session)
    assert lifecycle.state is ForwardSessionState.PREPARED

    lifecycle.start(occurred_utc="2026-10-07T00:00:00Z")
    lifecycle.assert_frozen_identity(
        strategy_revision=record.strategy_revision,
        manifest_revision=record.manifest_revision,
        execution_semantics=record.execution_semantics,
    )
    lifecycle.run(occurred_utc="2026-10-07T00:01:00Z")
    lifecycle.complete(occurred_utc="2026-10-07T00:02:00Z")

    assert lifecycle.state is ForwardSessionState.COMPLETED
    assert len(lifecycle.entries()) == 3
    assert all(
        event.session_fingerprint == session.fingerprint
        and event.strategy_revision == session.strategy_revision
        and event.manifest_revision == session.manifest_revision
        and event.execution_semantics == session.execution_semantics
        and event.production_decision is False
        and event.post_holdout_tuning is False
        for event in lifecycle.entries()
    )

    receipt = bind_mt5_reconciliation(
        session=session,
        lifecycle=lifecycle,
        reconciliation_id="RECON-SYNTH-1",
        broker_server="SYNTHETIC-MT5",
        symbol="XAUUSD.ecn",
        observed_positions=4,
        matched_positions=4,
        mismatched_positions=0,
    )

    assert receipt.reconciled is True
    assert receipt.session_id == session.session_id
    assert receipt.session_fingerprint == session.fingerprint
    assert receipt.observed_positions == 4
    assert receipt.matched_positions == 4
    assert receipt.mismatched_positions == 0
    receipt.validate()


def test_factory_forward_readiness_preserves_frozen_identity_fingerprints():
    record = SyntheticHoldoutRecord()
    forward_sha = _sha(b"forward-2")
    gate = _gate(
        "FORWARD-SESSION-SYNTH-2",
        "FORWARD-DATA-SYNTH-2",
        "FORWARD-ART-SYNTH-2",
        forward_sha,
    )
    kwargs = dict(
        gate=gate,
        source_record=record,
        session_id="FORWARD-SESSION-SYNTH-2",
        forward_dataset_id="FORWARD-DATA-SYNTH-2",
        forward_dataset_artifact_id="FORWARD-ART-SYNTH-2",
        forward_dataset_content_sha256=forward_sha,
    )

    a = DemoForwardSessionFactory().prepare(**kwargs).session
    b = DemoForwardSessionFactory().prepare(**kwargs).session

    assert a.fingerprint == b.fingerprint
    assert a.gate_fingerprint == b.gate_fingerprint

    lifecycle_a = DemoForwardSessionLifecycle(a)
    lifecycle_b = DemoForwardSessionLifecycle(b)

    for lifecycle in (lifecycle_a, lifecycle_b):
        lifecycle.start(occurred_utc="2026-10-07T00:00:00Z")
        lifecycle.run(occurred_utc="2026-10-07T00:01:00Z")
        lifecycle.complete(occurred_utc="2026-10-07T00:02:00Z")

    assert [e.event_fingerprint for e in lifecycle_a.entries()] == [
        e.event_fingerprint for e in lifecycle_b.entries()
    ]
