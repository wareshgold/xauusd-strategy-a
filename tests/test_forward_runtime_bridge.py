from __future__ import annotations

import hashlib

from strategy_factory.forward_gate_factory import ForwardGateResult
from strategy_factory.forward_runtime_bridge import (
    ForwardRuntimeBridgeError,
    run_bound_forward,
)
from strategy_factory.forward_session_factory import DemoForwardSessionFactory
from strategy_factory.models import GateResult, GateStatus


class SyntheticHoldoutRecord:
    strategy_id = "SP2L-A"
    strategy_revision = "REV-SYNTH-RUNTIME-1"
    manifest_revision = "MANIFEST-SYNTH-RUNTIME-1"
    execution_semantics = "BAR_CLOSE_RESEARCH"
    dataset_id = "HOLDOUT-RUNTIME-1"

    def validate(self):
        return None


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _session():
    record = SyntheticHoldoutRecord()
    gate = ForwardGateResult(
        gate=GateResult(
            name="FRESH_HOLDOUT_TO_FORWARD",
            status=GateStatus.PASS,
            evidence="synthetic-runtime-evidence",
            details={
                "strategy_revision": record.strategy_revision,
                "manifest_revision": record.manifest_revision,
                "holdout_dataset_id": record.dataset_id,
                "holdout_dataset_sha256": _sha(b"holdout-runtime"),
                "holdout_artifact_id": "HOLDOUT-RUNTIME-ART-1",
                "handoff_fingerprint": _sha(b"synthetic-runtime-handoff"),
                "production_decision": False,
            },
        )
    )
    return DemoForwardSessionFactory().prepare(
        gate=gate,
        source_record=record,
        session_id="FORWARD-RUNTIME-SESSION-1",
        forward_dataset_id="FORWARD-RUNTIME-DATA-1",
        forward_dataset_artifact_id="FORWARD-RUNTIME-ART-1",
        forward_dataset_content_sha256=_sha(b"forward-runtime"),
    ).session


def test_bound_forward_runs_injected_runner_and_binds_observed_reconciliation():
    calls = []

    def run_forward():
        calls.append("run")
        return {"observed": 2}

    def reconcile(result):
        assert result == {"observed": 2}
        return {
            "reconciliation_id": "RECON-RUNTIME-1",
            "broker_server": "SYNTHETIC-MT5",
            "symbol": "XAUUSD.ecn",
            "observed_positions": 2,
            "matched_positions": 2,
            "mismatched_positions": 0,
        }

    result = run_bound_forward(
        session=_session(),
        run_forward=run_forward,
        reconcile=reconcile,
        started_utc="2026-10-07T01:00:00Z",
        running_utc="2026-10-07T01:01:00Z",
        completed_utc="2026-10-07T01:02:00Z",
    )

    assert calls == ["run"]
    assert result.session_id == "FORWARD-RUNTIME-SESSION-1"
    assert [event.state.value for event in result.lifecycle_events] == [
        "STARTED",
        "RUNNING",
        "COMPLETED",
    ]
    assert result.reconciliation.reconciled is True
    assert result.reconciliation.matched_positions == 2


def test_bound_forward_rejects_incomplete_reconciliation_without_execution_retry():
    def run_forward():
        return {"observed": 0}

    def reconcile(_result):
        return {
            "reconciliation_id": "RECON-RUNTIME-2",
            "broker_server": "SYNTHETIC-MT5",
            "symbol": "XAUUSD.ecn",
            "observed_positions": 0,
            "matched_positions": 0,
        }

    try:
        run_bound_forward(
            session=_session(),
            run_forward=run_forward,
            reconcile=reconcile,
            started_utc="2026-10-07T02:00:00Z",
            running_utc="2026-10-07T02:01:00Z",
            completed_utc="2026-10-07T02:02:00Z",
        )
    except ForwardRuntimeBridgeError as exc:
        assert "mismatched_positions" in str(exc)
    else:
        raise AssertionError("expected incomplete reconciliation to fail closed")
