from __future__ import annotations

import base64
import hashlib
import json
import os
import multiprocessing
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest

from strategy_factory.forward_gate_factory import ForwardGateError
from strategy_factory.forward_preparation import (
    ForwardPreparationError,
    prepare_holdout_to_forward,
)
from strategy_factory.job_events import FactoryJobEventLedger, _journal_write_lock
from strategy_factory import trust_anchor, trust_audit

from test_holdout_factory import _context


def _lock_and_signal(path, acquired, release):
    with _journal_write_lock(Path(path)):
        acquired.set()
        release.wait(5)



def _prepared(tmp_path):
    runner, context = _context(tmp_path / "holdout")
    from strategy_factory.holdout_factory import HoldoutFactory

    holdout = HoldoutFactory(runner).prepare_and_run(context)
    events = FactoryJobEventLedger(path=None)
    return holdout, context, events


def _kwargs(holdout, context, events, tmp_path):
    kwargs = {
        "holdout_result": holdout,
        "events": events,
        "manifest_revision": "MANIFEST",
        "forward_session_id": "FORWARD-SESSION-001",
        "forward_dataset_id": "MT5-FORWARD-001",
        "forward_dataset_artifact_id": "MT5-FORWARD-ARTIFACT-001",
        "forward_dataset_content_sha256": "f" * 64,
        "holdout_dataset_content_sha256": context.holdout_dataset_content_sha256,
        "holdout_dataset_artifact_id": context.holdout_dataset_artifact_id,
    }
    artifact_path = Path(context.holdout_dataset_artifact_path)
    actual_sha = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    record = holdout.result.record
    private_key = Ed25519PrivateKey.generate()
    public_key_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    keyring_path = tmp_path / "test-trust-keyring.json"
    keyring_path.write_text(
        json.dumps({"keys": {"preparation-test-key": base64.b64encode(public_key_bytes).decode("ascii")}}),
        encoding="utf-8",
    )
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(trust_anchor, "_default_keyring_path", lambda: keyring_path)
    monkeypatch.setattr(trust_audit, "_default_audit_path", lambda: tmp_path / "verification-audit.jsonl")
    boundary_events = events.entries()
    if events.path is not None and events.path.exists():
        boundary_bytes = events.path.read_bytes()
        boundary_source = "persisted_jsonl"
    else:
        boundary_bytes = "".join(
            json.dumps(event.as_dict(), ensure_ascii=False, separators=(",", ":")) + "\n"
            for event in boundary_events
        ).encode("utf-8")
        boundary_source = "persisted_jsonl" if events.path is not None else "in_memory"
    boundary_sha = hashlib.sha256(boundary_bytes).hexdigest()
    envelope = {
        "schema_version": "SP2L-SIGNED-EVIDENCE-1",
        "key_id": "preparation-test-key",
        "issued_at_utc": "2026-10-01T00:00:00Z",
        "expires_at_utc": "2030-01-01T00:00:00Z",
        "payload": {
            "source_event_ledger_prefix_sha256": boundary_sha,
            "source_event_ledger_prefix_byte_size": len(boundary_bytes),
            "source_event_ledger_sequence_boundary": len(boundary_events),
            "source_event_ledger_prefix_source": boundary_source,
            "strategy_id": record.strategy_id,
            "strategy_revision": record.strategy_revision,
            "manifest_revision": record.manifest_revision,
            "execution_semantics": record.execution_semantics,
            "readiness_snapshot_fingerprint": holdout.result.snapshot.fingerprint,
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
    envelope_path = tmp_path / "test-signed-evidence.json"
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    kwargs["trust_envelope_path"] = str(envelope_path)
    kwargs["holdout_artifact_path"] = str(artifact_path)
    return kwargs



def test_signed_source_journal_boundary_mismatch_blocks_before_transition_append(tmp_path):
    holdout, context, events = _prepared(tmp_path)
    kwargs = _kwargs(holdout, context, events, tmp_path)
    events.append(
        event_type="QUEUED",
        job_id="JOURNAL-CHANGED-AFTER-SIGNING",
        job_fingerprint="a" * 64,
        station="holdout",
        phase="HOLDOUT",
        detail="synthetic boundary mutation",
    )
    before = events.entries()

    with pytest.raises(ForwardPreparationError, match="source_event_ledger_prefix_sha256"):
        prepare_holdout_to_forward(**kwargs)

    assert events.entries() == before
    assert all(event.event_type != "COMPLETED" for event in events.entries())


def test_holdout_to_forward_preparation_passes(tmp_path):
    holdout, context, events = _prepared(tmp_path)
    result = prepare_holdout_to_forward(**_kwargs(holdout, context, events, tmp_path))

    assert result.ready is True
    assert result.gate.passed is True
    assert result.session.production_decision is False
    assert result.handoff.source_station == "holdout"
    assert result.handoff.destination_station == "forward"
    assert result.holdout_event.event_type == "COMPLETED"
    assert result.holdout_event.station == "holdout"


@pytest.mark.parametrize(
    "mutation, message",
    [
        ({"holdout_dataset_content_sha256": "0" * 64}, "does not match"),
        ({"holdout_dataset_artifact_id": "WRONG-ARTIFACT"}, "does not match"),
    ],
)
def test_holdout_to_forward_rejects_invalid_holdout_identity(tmp_path, mutation, message):
    holdout, context, events = _prepared(tmp_path)
    kwargs = _kwargs(holdout, context, events, tmp_path)
    kwargs.update(mutation)

    with pytest.raises(ForwardPreparationError, match=message):
        prepare_holdout_to_forward(**kwargs)



def test_persisted_journal_snapshot_hash_is_bound_to_exact_read_only_bytes(tmp_path):
    holdout, context, _events = _prepared(tmp_path)
    journal_path = tmp_path / "factory_job_events.jsonl"
    events = FactoryJobEventLedger(path=journal_path)

    result = prepare_holdout_to_forward(**_kwargs(holdout, context, events, tmp_path))

    details = result.gate.gate.details
    assert details["source_event_ledger_source"] == "persisted_jsonl"
    assert details["source_event_ledger_path"] == str(journal_path)
    byte_size = details["source_event_ledger_byte_size"]
    final_bytes = journal_path.read_bytes()
    # The forward handoff event is appended after the gate. The exact prefix
    # audited by the gate must still be byte-for-byte present in the journal.
    audited_bytes = final_bytes[:byte_size]
    assert hashlib.sha256(audited_bytes).hexdigest() == details["source_event_ledger_sha256"]
    assert details["source_event_ledger_event_count"] == 1
    assert b"\n" in audited_bytes



def test_external_journal_corruption_is_rejected_before_any_append(tmp_path):
    holdout, context, _unused_events = _prepared(tmp_path)
    journal_path = tmp_path / "factory_job_events.jsonl"
    events = FactoryJobEventLedger(path=journal_path)
    events.append(
        event_type="QUEUED",
        job_id="UNRELATED-JOB",
        job_fingerprint="a" * 64,
        station="holdout",
        phase="HOLDOUT",
        detail="synthetic baseline",
    )
    baseline_events = events.entries()

    # Simulate another process corrupting the file after this ledger was loaded.
    with journal_path.open("ab") as handle:
        handle.write(b"{\n")
    corrupted_bytes = journal_path.read_bytes()

    with pytest.raises(
        ForwardPreparationError,
        match="persisted event journal is not valid",
    ):
        prepare_holdout_to_forward(**_kwargs(holdout, context, events, tmp_path))

    assert journal_path.read_bytes() == corrupted_bytes
    assert events.entries() == baseline_events


def test_valid_but_divergent_journal_snapshot_is_rejected_before_append(tmp_path):
    holdout, context, _unused_events = _prepared(tmp_path)
    journal_path = tmp_path / "factory_job_events.jsonl"
    events = FactoryJobEventLedger(path=journal_path)
    events.append(
        event_type="QUEUED",
        job_id="BASELINE-JOB",
        job_fingerprint="a" * 64,
        station="holdout",
        phase="HOLDOUT",
        detail="original valid journal",
    )
    baseline_events = events.entries()

    replacement_path = tmp_path / "replacement.jsonl"
    replacement = FactoryJobEventLedger(path=replacement_path)
    replacement.append(
        event_type="QUEUED",
        job_id="BASELINE-JOB",
        job_fingerprint="a" * 64,
        station="holdout",
        phase="HOLDOUT",
        detail="different but structurally valid journal",
    )
    journal_path.write_bytes(replacement_path.read_bytes())
    divergent_bytes = journal_path.read_bytes()

    with pytest.raises(
        ForwardPreparationError,
        match="failed pre-append integrity validation",
    ):
        prepare_holdout_to_forward(**_kwargs(holdout, context, events, tmp_path))

    assert journal_path.read_bytes() == divergent_bytes
    assert events.entries() == baseline_events


def test_journal_append_writes_real_jsonl_terminator(tmp_path):
    journal_path = tmp_path / "factory_job_events.jsonl"
    ledger = FactoryJobEventLedger(path=journal_path)
    ledger.append(
        event_type="QUEUED",
        job_id="NEWLINE-JOB",
        job_fingerprint="c" * 64,
    )

    raw = journal_path.read_bytes()
    assert raw.endswith(b"\n")
    report, parsed = __import__(
        "strategy_factory.job_events", fromlist=["inspect_job_journal_snapshot"]
    ).inspect_job_journal_snapshot(journal_path)
    assert report["status"] == "VALID"
    assert parsed is not None and len(parsed) == 1
    lock_path = tmp_path / "factory_job_events.jsonl.lock"
    if os.name == "nt":
        # Windows byte-range locking requires a one-byte lockable file.
        assert lock_path.read_bytes() == b"\0"
    else:
        # POSIX flock can lock an empty persistent sidecar file.
        assert lock_path.read_bytes() == b""



def test_journal_append_fsync_failure_rolls_back_without_memory_commit(tmp_path, monkeypatch):
    journal_path = tmp_path / "factory_job_events.jsonl"
    ledger = FactoryJobEventLedger(path=journal_path)
    ledger.append(
        event_type="QUEUED",
        job_id="BASELINE-JOB",
        job_fingerprint="a" * 64,
    )
    before_bytes = journal_path.read_bytes()
    before_events = ledger.entries()
    real_fsync = os.fsync
    calls = 0

    def fail_first_fsync(fd):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("injected fsync failure")
        return real_fsync(fd)

    monkeypatch.setattr(os, "fsync", fail_first_fsync)
    with pytest.raises(OSError, match="injected fsync failure"):
        ledger.append(
            event_type="QUEUED",
            job_id="ROLLBACK-JOB",
            job_fingerprint="b" * 64,
        )

    assert calls == 2
    assert journal_path.read_bytes() == before_bytes
    assert ledger.entries() == before_events
    report, parsed = __import__(
        "strategy_factory.job_events", fromlist=["inspect_job_journal_snapshot"]
    ).inspect_job_journal_snapshot(journal_path)
    assert report["status"] == "VALID"
    assert parsed == before_events


def test_journal_append_reports_manual_review_if_rollback_fsync_fails(
    tmp_path, monkeypatch
):
    journal_path = tmp_path / "factory_job_events.jsonl"
    ledger = FactoryJobEventLedger(path=journal_path)
    ledger.append(
        event_type="QUEUED",
        job_id="BASELINE-JOB",
        job_fingerprint="a" * 64,
    )
    before_bytes = journal_path.read_bytes()
    before_events = ledger.entries()

    def fail_every_fsync(_fd):
        raise OSError("injected persistent fsync failure")

    monkeypatch.setattr(os, "fsync", fail_every_fsync)
    with pytest.raises(OSError, match="append failed and rollback failed"):
        ledger.append(
            event_type="QUEUED",
            job_id="ROLLBACK-FAILURE-JOB",
            job_fingerprint="c" * 64,
        )

    # Bytes are back at the prior boundary, but failed rollback fsync means
    # durability cannot be asserted; the code must surface manual review.
    assert journal_path.read_bytes() == before_bytes
    assert ledger.entries() == before_events

def test_stale_ledger_writer_fails_closed_after_another_writer_appends(tmp_path):
    journal_path = tmp_path / "factory_job_events.jsonl"
    first = FactoryJobEventLedger(path=journal_path)
    stale = FactoryJobEventLedger(path=journal_path)

    first.append(
        event_type="QUEUED",
        job_id="FIRST-JOB",
        job_fingerprint="a" * 64,
        detail="first cooperative writer",
    )
    before_stale_attempt = journal_path.read_bytes()

    with pytest.raises(OSError, match="no longer matches the in-memory ledger"):
        stale.append(
            event_type="QUEUED",
            job_id="STALE-JOB",
            job_fingerprint="b" * 64,
            detail="stale writer must not append",
        )

    assert journal_path.read_bytes() == before_stale_attempt
    assert len(FactoryJobEventLedger(path=journal_path).entries()) == 1
    assert (tmp_path / "factory_job_events.jsonl.lock").exists()


def test_persisted_journal_lock_serializes_processes(tmp_path):
    journal_path = tmp_path / "factory_job_events.jsonl"
    context = multiprocessing.get_context("spawn")
    first_acquired = context.Event()
    first_release = context.Event()
    second_acquired = context.Event()
    second_release = context.Event()
    first = context.Process(
        target=_lock_and_signal,
        args=(str(journal_path), first_acquired, first_release),
    )
    second = context.Process(
        target=_lock_and_signal,
        args=(str(journal_path), second_acquired, second_release),
    )

    try:
        first.start()
        assert first_acquired.wait(5), "first process failed to acquire journal lock"
        second.start()
        assert not second_acquired.wait(0.25), (
            "second process entered the journal critical section before lock release"
        )
        first_release.set()
        assert second_acquired.wait(5), "second process did not acquire released journal lock"
        second_release.set()
    finally:
        first_release.set()
        second_release.set()
        if first.is_alive():
            first.join(5)
        if second.is_alive():
            second.join(5)
        if first.is_alive():
            first.terminate()
            first.join(2)
        if second.is_alive():
            second.terminate()
            second.join(2)

    assert first.exitcode == 0
    assert second.exitcode == 0

def test_corrupt_persisted_journal_fails_closed_without_repair(tmp_path):
    holdout, context, _events = _prepared(tmp_path)
    journal_path = tmp_path / "factory_job_events.jsonl"

    class ExternallyCorruptedLedger(FactoryJobEventLedger):
        corrupted_bytes = None
        injected = False

        def entries(self):
            if self.path is not None and not self.injected:
                with self.path.open("ab") as handle:
                    handle.write(b"{\n")
                self.injected = True
                self.corrupted_bytes = self.path.read_bytes()
            return super().entries()

    events = ExternallyCorruptedLedger(path=journal_path)
    with pytest.raises(ForwardPreparationError, match="persisted event journal is not valid"):
        prepare_holdout_to_forward(**_kwargs(holdout, context, events, tmp_path))

    assert events.corrupted_bytes is not None
    assert journal_path.read_bytes() == events.corrupted_bytes
    # Boundary validation now rejects corruption before appending the
    # Holdout COMPLETED event; the corrupted journal is left untouched.
    assert [event.event_type for event in events.entries()] == []

def test_holdout_to_forward_rejects_same_forward_dataset(tmp_path):
    holdout, context, events = _prepared(tmp_path)
    kwargs = _kwargs(holdout, context, events, tmp_path)
    kwargs["forward_dataset_id"] = holdout.result.record.dataset_id

    with pytest.raises(ForwardGateError, match="Forward dataset id must differ"):
        prepare_holdout_to_forward(**kwargs)


@pytest.mark.parametrize(
    "field, value, message",
    [
        ("strategy_revision_frozen", False, "frozen"),
        ("post_holdout_tuning", True, "post-holdout"),
    ],
)
def test_holdout_to_forward_rejects_frozen_boundary_breaks(
    tmp_path, field, value, message
):
    holdout, context, events = _prepared(tmp_path)
    kwargs = _kwargs(holdout, context, events, tmp_path)
    kwargs[field] = value

    with pytest.raises(ForwardPreparationError, match=message):
        prepare_holdout_to_forward(**kwargs)


def test_holdout_to_forward_rejects_manifest_drift(tmp_path):
    holdout, context, events = _prepared(tmp_path)
    kwargs = _kwargs(holdout, context, events, tmp_path)
    kwargs["manifest_revision"] = "MANIFEST-DRIFT"

    with pytest.raises(ForwardPreparationError, match="manifest_revision"):
        prepare_holdout_to_forward(**kwargs)


def test_holdout_to_forward_preserves_handoff_identity_into_session(tmp_path):
    holdout, context, events = _prepared(tmp_path)
    result = prepare_holdout_to_forward(**_kwargs(holdout, context, events, tmp_path))

    assert result.session.handoff_fingerprint == result.handoff.fingerprint
    assert result.session.strategy_id == holdout.result.record.strategy_id
    assert result.session.strategy_revision == holdout.result.record.strategy_revision
    assert result.session.manifest_revision == holdout.result.record.manifest_revision
    assert result.session.execution_semantics == holdout.result.record.execution_semantics
    assert result.session.holdout_dataset_id == holdout.result.record.dataset_id
    assert (
        result.session.holdout_dataset_artifact_id
        == result.handoff.dataset_artifact_id
    )
    assert (
        result.session.holdout_dataset_content_sha256
        == result.handoff.dataset_content_sha256
    )
    result.session.validate()


@pytest.mark.parametrize(
    "field, value, message",
    [
        (
            "forward_dataset_content_sha256",
            "a" * 64,
            "Forward dataset identity must differ",
        ),
        (
            "forward_dataset_artifact_id",
            "HOLDOUT-ARTIFACT",
            "Forward dataset artifact id must differ",
        ),
    ],
)
def test_holdout_to_forward_rejects_forward_dataset_reuse(
    tmp_path, field, value, message
):
    holdout, context, events = _prepared(tmp_path)
    kwargs = _kwargs(holdout, context, events, tmp_path)
    if field == "forward_dataset_content_sha256":
        kwargs[field] = context.holdout_dataset_content_sha256
    else:
        kwargs[field] = context.holdout_dataset_artifact_id

    with pytest.raises(ForwardGateError, match=message):
        prepare_holdout_to_forward(**kwargs)


def test_holdout_to_forward_rejects_strategy_revision_drift_in_source_record(
    tmp_path,
):
    from dataclasses import replace

    holdout, context, events = _prepared(tmp_path)
    tampered_record = replace(
        holdout.result.record,
        strategy_revision="REV-DRIFT",
    )
    tampered_result = replace(
        holdout,
        result=replace(holdout.result, record=tampered_record),
    )

    with pytest.raises(ValueError, match="record fingerprint mismatch"):
        prepare_holdout_to_forward(
            **_kwargs(tampered_result, context, events, tmp_path)
        )


def test_holdout_to_forward_never_authorizes_production(tmp_path):
    holdout, context, events = _prepared(tmp_path)
    result = prepare_holdout_to_forward(**_kwargs(holdout, context, events, tmp_path))

    assert result.session.production_decision is False
    assert result.gate.gate.details["production_decision"] is False
    assert all(
        event.station != "production"
        for event in events.entries()
    )


def test_missing_signed_evidence_blocks_holdout_to_forward_before_event_append(tmp_path):
    holdout, context, events = _prepared(tmp_path)
    kwargs = _kwargs(holdout, context, events, tmp_path)
    kwargs.pop("trust_envelope_path")
    before = events.entries()

    with pytest.raises(ForwardPreparationError, match="requires signed evidence"):
        prepare_holdout_to_forward(**kwargs)

    assert events.entries() == before


def test_tampered_signed_evidence_blocks_holdout_to_forward_before_event_append(tmp_path):
    holdout, context, events = _prepared(tmp_path)
    kwargs = _kwargs(holdout, context, events, tmp_path)
    envelope_path = Path(kwargs["trust_envelope_path"])
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    envelope["payload"]["strategy_revision"] = "TAMPERED-REVISION"
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    before = events.entries()

    with pytest.raises(ForwardPreparationError, match="signed evidence verification/audit failed"):
        prepare_holdout_to_forward(**kwargs)

    assert events.entries() == before


def test_signed_holdout_evidence_cannot_be_replayed_for_another_forward_session(tmp_path):
    holdout, context, events = _prepared(tmp_path)
    kwargs = _kwargs(holdout, context, events, tmp_path)
    kwargs["forward_session_id"] = "DIFFERENT-FORWARD-SESSION"
    before = events.entries()

    with pytest.raises(ForwardPreparationError, match="binding mismatch: forward_session_id"):
        prepare_holdout_to_forward(**kwargs)

    assert events.entries() == before
