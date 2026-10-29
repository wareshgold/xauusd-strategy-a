from __future__ import annotations

import hashlib

from strategy_factory.forward_gate_factory import ForwardGateResult
from strategy_factory.forward_runtime_bridge import (
    ForwardRuntimeBridgeError,
    run_bound_forward,
)
from strategy_factory.forward_session_factory import DemoForwardSessionFactory
from strategy_factory.models import GateResult, GateStatus, StrategyPassport
from strategy_factory.manifest import EvidenceStatus, RuleAuthority, StrategyManifest, StrategyRule
from strategy_factory.snapshot import build_readiness_snapshot
from strategy_factory.source_ledger import SourceResolutionLedger


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


def _readiness_bundle(record):
    manifest = StrategyManifest(
        strategy_id=record.strategy_id,
        revision=record.manifest_revision,
        rules=[
            StrategyRule(
                rule_id="SYNTHETIC-RUNTIME-RULE",
                name="Synthetic test-only rule",
                authority=RuleAuthority.CANONICAL,
                evidence_status=EvidenceStatus.SOURCE_CONFIRMED,
            )
        ],
    )
    passport = StrategyPassport(
        strategy_id=record.strategy_id,
        source_revision=record.manifest_revision,
        geometry_revision="SYNTHETIC-TEST-GEOMETRY",
        code_revision="SYNTHETIC-TEST-CODE",
        data_revision="SYNTHETIC-TEST-DATA",
        execution_model="BAR_CLOSE_RESEARCH_ONLY",
        parameter_set={"synthetic_test_only": True},
        canonical=True,
    )
    ledger = SourceResolutionLedger()
    snapshot = build_readiness_snapshot(manifest, passport, ledger)
    return snapshot, manifest, passport, ledger


def _session():
    record = SyntheticHoldoutRecord()
    readiness_snapshot, readiness_manifest, readiness_passport, readiness_ledger = _readiness_bundle(record)
    gate = ForwardGateResult(
        readiness_snapshot=readiness_snapshot,
        readiness_manifest=readiness_manifest,
        readiness_passport=readiness_passport,
        readiness_ledger=readiness_ledger,
        gate=GateResult(
            name="FRESH_HOLDOUT_TO_FORWARD",
            status=GateStatus.PASS,
            evidence="synthetic-runtime-evidence",
            details={
                "source_station": "holdout",
                "destination_station": "forward",
                "forward_session_id": "FORWARD-RUNTIME-SESSION-1",
                "forward_dataset_id": "FORWARD-RUNTIME-DATA-1",
                "forward_artifact_id": "FORWARD-RUNTIME-ART-1",
                "forward_dataset_sha256": _sha(b"forward-runtime"),
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

def test_bound_forward_rejects_session_without_source_inputs_before_runner():
    from dataclasses import replace

    calls = []
    session = replace(
        _session(),
        readiness_snapshot=None,
        readiness_manifest=None,
        readiness_passport=None,
        readiness_ledger=None,
    )

    try:
        run_bound_forward(
            session=session,
            run_forward=lambda: calls.append("run"),
            reconcile=lambda _result: {},
            started_utc="2026-10-07T03:00:00Z",
            running_utc="2026-10-07T03:01:00Z",
            completed_utc="2026-10-07T03:02:00Z",
        )
    except Exception as exc:
        assert "requires authoritative readiness snapshot" in str(exc)
    else:
        raise AssertionError("forward runtime must reject sessions without source inputs")

    assert calls == []

