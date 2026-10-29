from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from strategy_factory import trust_anchor
from strategy_factory.forward_preparation import prepare_holdout_to_forward
from strategy_factory.forward_runtime_bridge import run_bound_forward
from strategy_factory.holdout_factory import HoldoutFactory
from strategy_factory.job_events import FactoryJobEventLedger

from test_forward_preparation import _kwargs
from test_holdout_factory import _context


def _signed_kwargs(holdout, context, events, tmp_path, monkeypatch):
    kwargs = _kwargs(holdout, context, events, tmp_path)
    artifact_path = Path(context.holdout_dataset_artifact_path)
    actual_sha = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    record = holdout.result.record
    snapshot = holdout.result.snapshot

    private_key = Ed25519PrivateKey.generate()
    public_key_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    keyring_path = tmp_path / "runtime-test-keyring.json"
    keyring_path.write_text(
        json.dumps({"keys": {"e2e-test-key": base64.b64encode(public_key_bytes).decode("ascii")}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(trust_anchor, "_default_keyring_path", lambda: keyring_path)

    envelope = {
        "schema_version": "SP2L-SIGNED-EVIDENCE-1",
        "key_id": "e2e-test-key",
        "issued_at_utc": "2026-10-01T00:00:00Z",
        "expires_at_utc": "2030-01-01T00:00:00Z",
        "payload": {
            "strategy_id": record.strategy_id,
            "strategy_revision": record.strategy_revision,
            "manifest_revision": record.manifest_revision,
            "execution_semantics": record.execution_semantics,
            "readiness_snapshot_fingerprint": snapshot.fingerprint,
            "holdout_dataset_id": record.dataset_id,
            "holdout_artifact_id": holdout.result.run.artifact_id,
            "holdout_dataset_role": "FRESH_HOLDOUT",
            "forward_session_id": kwargs["forward_session_id"],
            "holdout_run_id": holdout.result.run.run_id,
            "holdout_run_fingerprint": record.run_fingerprint,
            "holdout_evidence_id": record.evidence_id,
            "holdout_evidence_fingerprint": record.evidence_fingerprint,
            "holdout_audit_fingerprint": record.audit_fingerprint,
            "holdout_record_fingerprint": record.fingerprint,
            "holdout_dataset_fingerprint": holdout.result.run.dataset_fingerprint,
            "holdout_artifact_byte_size": artifact_path.stat().st_size,
            "holdout_artifact_sha256": actual_sha,
        },
    }
    signed_bytes = json.dumps(
        envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")
    envelope["signature_b64"] = base64.b64encode(private_key.sign(signed_bytes)).decode("ascii")
    envelope_path = tmp_path / "signed-holdout-evidence.json"
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    kwargs["trust_envelope_path"] = str(envelope_path)
    kwargs["holdout_artifact_path"] = str(artifact_path)
    return kwargs


def test_factory_fresh_holdout_to_forward_e2e_preserves_research_lock(tmp_path, monkeypatch):
    runner, context = _context(tmp_path / "holdout")

    holdout = HoldoutFactory(runner).prepare_and_run(context)
    assert holdout.result.accepted is True
    assert holdout.result.record.dataset_role == "FRESH_HOLDOUT"
    assert holdout.result.record.strategy_revision == context.spec.strategy_revision

    events = FactoryJobEventLedger(path=None)
    result = prepare_holdout_to_forward(
        **_signed_kwargs(holdout, context, events, tmp_path, monkeypatch)
    )

    assert result.ready is True
    assert result.gate.passed is True
    assert result.session.production_decision is False
    assert result.session.handoff_fingerprint == result.handoff.fingerprint
    assert result.session.lifecycle_state == "PREPARED"

    assert result.handoff.source_station == "holdout"
    assert result.handoff.destination_station == "forward"
    assert result.handoff.dataset_content_sha256 == context.holdout_dataset_content_sha256
    assert result.handoff.dataset_artifact_id == context.holdout_dataset_artifact_id

    assert [event.event_type for event in events.entries()] == [
        "COMPLETED",
        "HANDOFF_ACCEPTED",
    ]



def test_persisted_journal_forward_e2e_binds_gate_prefix_to_reconciliation(tmp_path, monkeypatch):
    import hashlib

    runner, context = _context(tmp_path / "persisted-journal-e2e")
    holdout = HoldoutFactory(runner).prepare_and_run(context)
    journal_path = tmp_path / "persisted-journal-e2e" / "factory_job_events.jsonl"
    events = FactoryJobEventLedger(path=journal_path)
    prepared = prepare_holdout_to_forward(**_signed_kwargs(holdout, context, events, tmp_path, monkeypatch))

    gate_details = prepared.gate.gate.details
    before_forward = journal_path.read_bytes()
    audited_size = gate_details["source_event_ledger_byte_size"]
    audited_prefix = before_forward[:audited_size]
    assert hashlib.sha256(audited_prefix).hexdigest() == gate_details[
        "source_event_ledger_sha256"
    ]
    assert gate_details["source_event_ledger_source"] == "persisted_jsonl"
    assert gate_details["production_decision"] is False

    observed = {"observed_positions": 2}

    def reconcile(result):
        assert result is observed
        return {
            "reconciliation_id": "RECON-PERSISTED-E2E",
            "broker_server": "SYNTHETIC-MT5",
            "symbol": "XAUUSD.ecn",
            "observed_positions": 2,
            "matched_positions": 2,
            "mismatched_positions": 0,
        }

    runtime = run_bound_forward(
        session=prepared.session,
        run_forward=lambda: observed,
        reconcile=reconcile,
        started_utc="2026-10-28T01:00:00Z",
        running_utc="2026-10-28T01:01:00Z",
        completed_utc="2026-10-28T01:02:00Z",
    )

    final_bytes = journal_path.read_bytes()
    assert final_bytes.startswith(audited_prefix)
    assert runtime.reconciliation.reconciled is True
    assert runtime.reconciliation.mismatched_positions == 0
    assert runtime.session_fingerprint == prepared.session.fingerprint
    assert runtime.handoff_fingerprint == prepared.handoff.fingerprint
    assert prepared.session.production_decision is False
    assert [event.event_type for event in events.entries()] == [
        "COMPLETED",
        "HANDOFF_ACCEPTED",
    ]

def test_factory_full_provenance_chain_reaches_reconciliation(tmp_path, monkeypatch):
    runner, context = _context(tmp_path / "full-chain")

    holdout = HoldoutFactory(runner).prepare_and_run(context)
    events = FactoryJobEventLedger(path=None)
    prepared = prepare_holdout_to_forward(
        **_signed_kwargs(holdout, context, events, tmp_path, monkeypatch)
    )

    observed_runner_result = {"observed_positions": 3}

    def run_forward():
        return observed_runner_result

    def reconcile(result):
        assert result is observed_runner_result
        return {
            "reconciliation_id": "RECON-FULL-CHAIN-1",
            "broker_server": "SYNTHETIC-MT5",
            "symbol": "XAUUSD.ecn",
            "observed_positions": result["observed_positions"],
            "matched_positions": 3,
            "mismatched_positions": 0,
        }

    runtime = run_bound_forward(
        session=prepared.session,
        run_forward=run_forward,
        reconcile=reconcile,
        started_utc="2026-10-08T01:00:00Z",
        running_utc="2026-10-08T01:01:00Z",
        completed_utc="2026-10-08T01:02:00Z",
    )

    handoff_fp = prepared.handoff.fingerprint
    session_fp = prepared.session.fingerprint

    assert prepared.gate.gate.details["handoff_fingerprint"] == handoff_fp
    assert prepared.session.handoff_fingerprint == handoff_fp

    assert runtime.session_id == prepared.session.session_id
    assert runtime.session_fingerprint == session_fp
    assert runtime.handoff_fingerprint == handoff_fp

    assert [event.state.value for event in runtime.lifecycle_events] == [
        "STARTED",
        "RUNNING",
        "COMPLETED",
    ]
    assert all(event.session_fingerprint == session_fp for event in runtime.lifecycle_events)
    assert all(event.handoff_fingerprint == handoff_fp for event in runtime.lifecycle_events)
    assert all(event.strategy_revision == prepared.session.strategy_revision for event in runtime.lifecycle_events)
    assert all(event.manifest_revision == prepared.session.manifest_revision for event in runtime.lifecycle_events)
    assert all(event.execution_semantics == prepared.session.execution_semantics for event in runtime.lifecycle_events)
    assert all(event.post_holdout_tuning is False for event in runtime.lifecycle_events)
    assert all(event.production_decision is False for event in runtime.lifecycle_events)

    receipt = runtime.reconciliation
    assert receipt.session_id == prepared.session.session_id
    assert receipt.session_fingerprint == session_fp
    assert receipt.handoff_fingerprint == handoff_fp
    assert receipt.observed_positions == 3
    assert receipt.matched_positions == 3
    assert receipt.mismatched_positions == 0
    assert receipt.reconciled is True

    assert runtime.runner_result is observed_runner_result


def test_factory_forward_runtime_stops_before_reconciliation_when_runner_fails(tmp_path, monkeypatch):
    import pytest
    from strategy_factory.forward_runtime_bridge import ForwardRuntimeBridgeError

    runner, context = _context(tmp_path / "runner-failure")
    holdout = HoldoutFactory(runner).prepare_and_run(context)
    events = FactoryJobEventLedger(path=None)
    prepared = prepare_holdout_to_forward(**_signed_kwargs(holdout, context, events, tmp_path, monkeypatch))

    reconciled = False

    def run_forward():
        raise RuntimeError("synthetic runner failure")

    def reconcile(_result):
        nonlocal reconciled
        reconciled = True
        return {}

    with pytest.raises(ForwardRuntimeBridgeError, match="bound forward runner failed"):
        run_bound_forward(
            session=prepared.session,
            run_forward=run_forward,
            reconcile=reconcile,
            started_utc="2026-10-08T02:00:00Z",
            running_utc="2026-10-08T02:01:00Z",
            completed_utc="2026-10-08T02:02:00Z",
        )

    assert reconciled is False


def test_factory_forward_runtime_rejects_incomplete_reconciliation_without_fabrication(
    tmp_path, monkeypatch,
):
    import pytest
    from strategy_factory.forward_runtime_bridge import ForwardRuntimeBridgeError

    runner, context = _context(tmp_path / "reconciliation-failure")
    holdout = HoldoutFactory(runner).prepare_and_run(context)
    events = FactoryJobEventLedger(path=None)
    prepared = prepare_holdout_to_forward(**_signed_kwargs(holdout, context, events, tmp_path, monkeypatch))

    observed_runner_result = {"observed_positions": 2}

    def run_forward():
        return observed_runner_result

    def reconcile(_result):
        return {
            "reconciliation_id": "RECON-INCOMPLETE-1",
            "broker_server": "SYNTHETIC-MT5",
            "symbol": "XAUUSD.ecn",
            "observed_positions": 2,
        }

    with pytest.raises(
        ForwardRuntimeBridgeError,
        match="omitted required observed fields",
    ):
        run_bound_forward(
            session=prepared.session,
            run_forward=run_forward,
            reconcile=reconcile,
            started_utc="2026-10-08T03:00:00Z",
            running_utc="2026-10-08T03:01:00Z",
            completed_utc="2026-10-08T03:02:00Z",
        )
