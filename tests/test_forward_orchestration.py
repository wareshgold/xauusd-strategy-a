from __future__ import annotations

import hashlib

import pytest

from strategy_factory.forward_gate_factory import ForwardGateResult
from strategy_factory.forward_runtime_bridge import ForwardRuntimeBridgeError
from strategy_factory.forward_session_factory import DemoForwardSessionFactory
from strategy_factory.forward_orchestration import (
    ForwardOrchestrationError,
    run_factory_bound_forward,
)
from strategy_factory.models import GateResult, GateStatus


class SyntheticHoldoutRecord:
    strategy_id = "SP2L-A"
    strategy_revision = "REV-SYNTH-ORCH-1"
    manifest_revision = "MANIFEST-SYNTH-ORCH-1"
    execution_semantics = "BAR_CLOSE_RESEARCH"
    dataset_id = "HOLDOUT-ORCH-1"

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
            evidence="synthetic-orchestration-evidence",
            details={
                "source_station": "holdout",
                "destination_station": "forward",
                "forward_session_id": "FORWARD-ORCH-SESSION-1",
                "forward_dataset_id": "FORWARD-ORCH-DATA-1",
                "forward_artifact_id": "FORWARD-ORCH-ART-1",
                "forward_dataset_sha256": _sha(b"forward-orchestration"),
                "strategy_revision": record.strategy_revision,
                "manifest_revision": record.manifest_revision,
                "holdout_dataset_id": record.dataset_id,
                "holdout_dataset_sha256": _sha(b"holdout-orchestration"),
                "holdout_artifact_id": "HOLDOUT-ORCH-ART-1",
                "handoff_fingerprint": _sha(b"synthetic-orchestration-handoff"),
                "production_decision": False,
            },
        )
    )
    return DemoForwardSessionFactory().prepare(
        gate=gate,
        source_record=record,
        session_id="FORWARD-ORCH-SESSION-1",
        forward_dataset_id="FORWARD-ORCH-DATA-1",
        forward_dataset_artifact_id="FORWARD-ORCH-ART-1",
        forward_dataset_content_sha256=_sha(b"forward-orchestration"),
    ).session


def _reconciliation(observed=3, mismatched=0):
    return {
        "reconciliation_id": "RECON-ORCH-1",
        "broker_server": "SYNTHETIC-MT5",
        "symbol": "XAUUSD.ecn",
        "observed_positions": observed,
        "matched_positions": observed - mismatched,
        "mismatched_positions": mismatched,
    }


def test_factory_bound_forward_composes_frozen_runtime_and_reconciliation():
    calls = []

    def runner():
        calls.append("runner")
        return {"runner": "ok"}

    def reconcile(result):
        assert result == {"runner": "ok"}
        calls.append("reconcile")
        return _reconciliation()

    result = run_factory_bound_forward(
        session=_session(),
        run_forward=runner,
        reconcile=reconcile,
        started_utc="2026-10-07T03:00:00Z",
        running_utc="2026-10-07T03:01:00Z",
        completed_utc="2026-10-07T03:02:00Z",
    )

    assert calls == ["runner", "reconcile"]
    assert result.session_id == "FORWARD-ORCH-SESSION-1"
    assert result.reconciled is True
    assert result.production_decision is False
    assert [event.state.value for event in result.runtime.lifecycle_events] == [
        "STARTED",
        "RUNNING",
        "COMPLETED",
    ]


def test_factory_bound_forward_fail_closes_runner_failure():
    def runner():
        raise RuntimeError("synthetic runner failure")

    with pytest.raises(ForwardOrchestrationError, match="runner failed"):
        run_factory_bound_forward(
            session=_session(),
            run_forward=runner,
            reconcile=lambda _: _reconciliation(),
            started_utc="2026-10-07T04:00:00Z",
            running_utc="2026-10-07T04:01:00Z",
            completed_utc="2026-10-07T04:02:00Z",
        )


def test_factory_bound_forward_fail_closes_reconciliation_failure():
    def reconcile(_):
        raise RuntimeError("synthetic reconciliation failure")

    with pytest.raises(ForwardOrchestrationError, match="reconciliation failed"):
        run_factory_bound_forward(
            session=_session(),
            run_forward=lambda: {"runner": "ok"},
            reconcile=reconcile,
            started_utc="2026-10-07T05:00:00Z",
            running_utc="2026-10-07T05:01:00Z",
            completed_utc="2026-10-07T05:02:00Z",
        )


def test_factory_bound_forward_preserves_observed_reconciliation_mismatch():
    result = run_factory_bound_forward(
        session=_session(),
        run_forward=lambda: {"runner": "ok"},
        reconcile=lambda _: _reconciliation(observed=3, mismatched=1),
        started_utc="2026-10-07T06:00:00Z",
        running_utc="2026-10-07T06:01:00Z",
        completed_utc="2026-10-07T06:02:00Z",
    )

    assert result.reconciled is False
    assert result.runtime.reconciliation.mismatched_positions == 1
    assert result.production_decision is False
