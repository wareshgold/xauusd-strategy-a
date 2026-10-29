from __future__ import annotations

import base64
import hashlib
import json
from types import SimpleNamespace
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from strategy_factory.dataset_provenance import DatasetProvenanceStatus

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
from strategy_factory import trust_anchor, trust_audit


class SyntheticHoldoutRecord:
    strategy_id = "SP2L-A"
    strategy_revision = "REV-SYNTH-RUNTIME-1"
    manifest_revision = "MANIFEST-SYNTH-RUNTIME-1"
    execution_semantics = "BAR_CLOSE_RESEARCH"
    dataset_id = "HOLDOUT-RUNTIME-1"
    dataset_role = "FRESH_HOLDOUT"
    run_id = "SYNTHETIC-HOLDOUT-RUN"
    evidence_id = "SYNTHETIC-HOLDOUT-EVIDENCE"
    run_fingerprint = "a" * 64
    evidence_fingerprint = "b" * 64
    audit_fingerprint = "c" * 64
    fingerprint = "d" * 64
    dataset_fingerprint = hashlib.sha256(b"synthetic-holdout-dataset-fingerprint").hexdigest()
    snapshot_fingerprint = ""

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


def _synthetic_holdout_result(record, snapshot, content_sha, artifact_id):
    record.snapshot_fingerprint = snapshot.fingerprint
    dataset_fingerprint = _sha(b"synthetic-holdout-dataset-fingerprint")
    run = SimpleNamespace(
        run_id=record.run_id,
        dataset_role="FRESH_HOLDOUT",
        dataset_id=record.dataset_id,
        artifact_id=artifact_id,
        dataset_fingerprint=dataset_fingerprint,
    )
    provenance = SimpleNamespace(
        status=DatasetProvenanceStatus.PASS,
        observed_artifact_id=artifact_id,
        registered_artifact_id=artifact_id,
        dataset_id=record.dataset_id,
        registered_fingerprint=dataset_fingerprint,
        observed_fingerprint=dataset_fingerprint,
    )
    result = SimpleNamespace(
        accepted=True,
        job_id=record.run_id,
        run=run,
        record=record,
        dataset_provenance=provenance,
    )
    job = SimpleNamespace(job_id=record.run_id)
    return SimpleNamespace(
        job=job,
        result=result,
        holdout_dataset_content_sha256=content_sha,
    )


def _session(tmp_path, monkeypatch):
    record = SyntheticHoldoutRecord()
    readiness_snapshot, readiness_manifest, readiness_passport, readiness_ledger = _readiness_bundle(record)
    artifact_path = tmp_path / "holdout-runtime.bin"
    artifact_path.write_bytes(b"holdout-runtime")
    holdout_sha = _sha(artifact_path.read_bytes())
    holdout_artifact = "HOLDOUT-RUNTIME-ART-1"
    holdout_result = _synthetic_holdout_result(record, readiness_snapshot, holdout_sha, holdout_artifact)

    private_key = Ed25519PrivateKey.generate()
    public_key_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    keyring_path = tmp_path / "test-keyring.json"
    keyring_path.write_text(
        json.dumps({"keys": {"runtime-test-key": base64.b64encode(public_key_bytes).decode("ascii")}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(trust_anchor, "_default_keyring_path", lambda: keyring_path)
    monkeypatch.setattr(trust_audit, "_default_audit_path", lambda: tmp_path / "verification-audit.jsonl")
    boundary_bytes = b""
    boundary_sha = hashlib.sha256(boundary_bytes).hexdigest()
    envelope = {
        "schema_version": "SP2L-SIGNED-EVIDENCE-1",
        "key_id": "runtime-test-key",
        "issued_at_utc": "2026-10-01T00:00:00Z",
        "expires_at_utc": "2030-01-01T00:00:00Z",
        "payload": {
            "source_event_ledger_prefix_sha256": boundary_sha,
            "source_event_ledger_prefix_byte_size": len(boundary_bytes),
            "source_event_ledger_sequence_boundary": 0,
            "source_event_ledger_prefix_source": "in_memory",
            "source_event_ledger_path": None,
            "strategy_id": record.strategy_id,
            "strategy_revision": record.strategy_revision,
            "manifest_revision": record.manifest_revision,
            "execution_semantics": record.execution_semantics,
            "readiness_snapshot_fingerprint": readiness_snapshot.fingerprint,
            "holdout_dataset_id": record.dataset_id,
            "holdout_artifact_id": holdout_artifact,
            "holdout_dataset_role": "FRESH_HOLDOUT",
            "forward_session_id": "FORWARD-RUNTIME-SESSION-1",
            "holdout_run_id": record.run_id,
            "holdout_run_fingerprint": record.run_fingerprint,
            "holdout_evidence_id": record.evidence_id,
            "holdout_evidence_fingerprint": record.evidence_fingerprint,
            "holdout_audit_fingerprint": record.audit_fingerprint,
            "holdout_record_fingerprint": record.fingerprint,
            "holdout_dataset_fingerprint": record.dataset_fingerprint,
            "holdout_artifact_byte_size": artifact_path.stat().st_size,
            "holdout_artifact_sha256": holdout_sha,
        },
    }
    signed_bytes = json.dumps(
        envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")
    envelope["signature_b64"] = base64.b64encode(private_key.sign(signed_bytes)).decode("ascii")
    envelope_path = tmp_path / "signed-evidence.json"
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    gate = ForwardGateResult(
        holdout_result=holdout_result,
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
                "holdout_dataset_sha256": holdout_sha,
                "source_event_ledger_prefix_sha256": boundary_sha,
                "source_event_ledger_prefix_byte_size": len(boundary_bytes),
                "source_event_ledger_sequence_boundary": 0,
                "source_event_ledger_prefix_source": "in_memory",
                "source_event_ledger_path": None,
                "holdout_artifact_id": holdout_artifact,
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
        trust_envelope_path=str(envelope_path),
        holdout_artifact_path=str(artifact_path),
    ).session


def test_bound_forward_runs_injected_runner_and_binds_observed_reconciliation(tmp_path, monkeypatch):
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
        session=_session(tmp_path, monkeypatch),
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


def test_bound_forward_rejects_incomplete_reconciliation_without_execution_retry(tmp_path, monkeypatch):
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
            session=_session(tmp_path, monkeypatch),
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

def test_bound_forward_rejects_session_without_source_inputs_before_runner(tmp_path, monkeypatch):
    from dataclasses import replace

    calls = []
    session = replace(
        _session(tmp_path, monkeypatch),
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


def test_bound_forward_rejects_session_without_holdout_result_before_runner(tmp_path, monkeypatch):
    from dataclasses import replace

    calls = []
    session = replace(_session(tmp_path, monkeypatch), holdout_result=None)
    try:
        run_bound_forward(
            session=session,
            run_forward=lambda: calls.append("run"),
            reconcile=lambda _result: {},
            started_utc="2026-10-07T04:00:00Z",
            running_utc="2026-10-07T04:01:00Z",
            completed_utc="2026-10-07T04:02:00Z",
        )
    except Exception as exc:
        assert "requires the completed HoldoutFactoryResult binding" in str(exc)
    else:
        raise AssertionError("forward runtime must reject sessions without a Holdout result")

    assert calls == []


def test_bound_forward_rejects_tampered_signed_evidence_before_runner(tmp_path, monkeypatch):
    import json
    from dataclasses import replace

    calls = []
    session = _session(tmp_path, monkeypatch)
    envelope_path = Path(session.trust_envelope_path)
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    envelope["payload"]["strategy_revision"] = "TAMPERED-REVISION"
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")

    try:
        run_bound_forward(
            session=session,
            run_forward=lambda: calls.append("run"),
            reconcile=lambda _result: {},
            started_utc="2026-10-07T05:00:00Z",
            running_utc="2026-10-07T05:01:00Z",
            completed_utc="2026-10-07T05:02:00Z",
        )
    except Exception as exc:
        assert "signed evidence verification failed" in str(exc)
    else:
        raise AssertionError("tampered signed evidence must block the forward runner")

    assert calls == []



def test_bound_forward_rejects_artifact_changed_between_preflight_and_dispatch(tmp_path, monkeypatch):
    """A changed Holdout artifact after preflight must block runner dispatch."""
    session = _session(tmp_path, monkeypatch)
    artifact_path = Path(session.holdout_artifact_path)
    original_validate = type(session).validate_for_runtime
    validation_calls = []
    runner_calls = []

    def validate_then_mutate(self, *, audit_phase=None):
        result = original_validate(self, audit_phase=audit_phase)
        validation_calls.append(audit_phase)
        if len(validation_calls) == 1:
            artifact_path.write_bytes(artifact_path.read_bytes() + b"-changed-after-preflight")
        return result

    monkeypatch.setattr(type(session), "validate_for_runtime", validate_then_mutate)

    try:
        run_bound_forward(
            session=session,
            run_forward=lambda: runner_calls.append("run"),
            reconcile=lambda _result: {},
            started_utc="2026-10-29T04:00:00Z",
            running_utc="2026-10-29T04:01:00Z",
            completed_utc="2026-10-29T04:02:00Z",
        )
    except Exception as exc:
        assert "signed evidence verification failed" in str(exc)
    else:
        raise AssertionError("changed Holdout artifact must block runner dispatch")

    assert validation_calls == ["runtime_preflight", "runtime_dispatch"]
    assert runner_calls == []
