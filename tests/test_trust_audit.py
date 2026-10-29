from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from strategy_factory.trust_audit import (
    TrustAuditError,
    append_verification_audit,
    classify_holdout_recovery_state,
)


def _fixture(tmp_path: Path):
    envelope = tmp_path / "signed-envelope.json"
    envelope.write_text('{"synthetic":"envelope"}', encoding="utf-8")
    artifact = tmp_path / "holdout.bin"
    artifact.write_bytes(b"synthetic holdout artifact")
    verification = {
        "verified": True,
        "key_id": "synthetic-test-key",
        "issued_at_utc": "2026-10-29T09:00:00+00:00",
        "expires_at_utc": "2030-01-01T00:00:00+00:00",
    }
    audit = tmp_path / "verification-audit.jsonl"
    return envelope, artifact, verification, audit


def _append(envelope, artifact, verification, audit, *, phase="holdout_to_forward", session="session-1", consume=False, resume=False, boundary=None):
    return append_verification_audit(
        phase=phase,
        session_id=session,
        envelope_path=envelope,
        artifact_path=artifact,
        verification=verification,
        consume_holdout_once=consume,
        resume_holdout_once=resume,
        source_event_ledger_boundary=boundary or ({
            "source_event_ledger_prefix_sha256": hashlib.sha256(b"").hexdigest(),
            "source_event_ledger_prefix_byte_size": 0,
            "source_event_ledger_sequence_boundary": 0,
            "source_event_ledger_prefix_source": "in_memory",
            "source_event_ledger_path": None,
        } if consume else None),
        audit_path=audit,
    )


def test_trust_audit_appends_hash_chained_records_and_allows_runtime_rechecks(tmp_path):
    envelope, artifact, verification, audit = _fixture(tmp_path)
    first = _append(envelope, artifact, verification, audit, consume=True)
    preflight = _append(
        envelope, artifact, verification, audit, phase="runtime_preflight", consume=False
    )
    dispatch = _append(
        envelope, artifact, verification, audit, phase="runtime_dispatch", consume=False
    )

    assert [first["sequence"], preflight["sequence"], dispatch["sequence"]] == [1, 2, 3]
    assert preflight["previous_entry_sha256"] == first["entry_sha256"]
    assert dispatch["previous_entry_sha256"] == preflight["entry_sha256"]
    assert len(audit.read_text(encoding="utf-8").splitlines()) == 3


def test_trust_audit_rejects_reconsumption_of_same_holdout_envelope(tmp_path):
    envelope, artifact, verification, audit = _fixture(tmp_path)
    _append(envelope, artifact, verification, audit, consume=True)
    with pytest.raises(TrustAuditError, match="already been consumed"):
        _append(envelope, artifact, verification, audit, consume=True, session="session-2")



def test_trust_audit_allows_recovery_only_for_same_session_and_boundary(tmp_path):
    envelope, artifact, verification, audit = _fixture(tmp_path)
    boundary = {
        "source_event_ledger_prefix_sha256": hashlib.sha256(b"").hexdigest(),
        "source_event_ledger_prefix_byte_size": 0,
        "source_event_ledger_sequence_boundary": 0,
        "source_event_ledger_prefix_source": "in_memory",
        "source_event_ledger_path": None,
    }
    first = _append(
        envelope, artifact, verification, audit, consume=True, boundary=boundary
    )

    # Reject mismatched recovery attempts before a valid recovery record exists.
    with pytest.raises(TrustAuditError, match="same session and unchanged signed journal boundary"):
        _append(
            envelope, artifact, verification, audit,
            phase="holdout_to_forward_recovery",
            session="different-session",
            consume=True, resume=True, boundary=boundary,
        )

    changed_boundary = dict(boundary, source_event_ledger_prefix_sha256="a" * 64)
    with pytest.raises(TrustAuditError, match="same session and unchanged signed journal boundary"):
        _append(
            envelope, artifact, verification, audit,
            phase="holdout_to_forward_recovery",
            consume=True, resume=True, boundary=changed_boundary,
        )

    recovered = _append(
        envelope, artifact, verification, audit,
        phase="holdout_to_forward_recovery",
        consume=True, resume=True, boundary=boundary,
    )
    assert first["phase"] == "holdout_to_forward"
    assert recovered["phase"] == "holdout_to_forward_recovery"
    assert recovered["session_id"] == first["session_id"]
    assert recovered["source_event_ledger_prefix_sha256"] == boundary["source_event_ledger_prefix_sha256"]

    # A recovery record is itself a one-time reconciliation action. A repeated
    # call must not keep extending the audit chain as if each retry were new.
    with pytest.raises(TrustAuditError, match="recovery has already been recorded"):
        _append(
            envelope, artifact, verification, audit,
            phase="holdout_to_forward_recovery",
            consume=True, resume=True, boundary=boundary,
        )



def test_trust_audit_fails_closed_when_existing_chain_is_tampered(tmp_path):
    envelope, artifact, verification, audit = _fixture(tmp_path)
    _append(envelope, artifact, verification, audit, consume=True)
    entry = json.loads(audit.read_text(encoding="utf-8"))
    entry["session_id"] = "altered"
    audit.write_text(json.dumps(entry, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")

    with pytest.raises(TrustAuditError, match="hash chain invalid"):
        _append(envelope, artifact, verification, audit, phase="runtime_preflight")


def test_trust_audit_rejects_unverified_evidence(tmp_path):
    envelope, artifact, verification, audit = _fixture(tmp_path)
    verification["verified"] = False
    with pytest.raises(TrustAuditError, match="only successfully verified"):
        _append(envelope, artifact, verification, audit, consume=True)


def test_trust_audit_rejects_unsupported_phase(tmp_path):
    envelope, artifact, verification, audit = _fixture(tmp_path)
    with pytest.raises(TrustAuditError, match="unsupported"):
        _append(envelope, artifact, verification, audit, phase="unknown")


def test_recovery_classifier_is_read_only_and_distinguishes_recovery_states(tmp_path):
    envelope, artifact, verification, audit = _fixture(tmp_path)
    boundary = {
        "source_event_ledger_prefix_sha256": hashlib.sha256(b"").hexdigest(),
        "source_event_ledger_prefix_byte_size": 0,
        "source_event_ledger_sequence_boundary": 0,
        "source_event_ledger_prefix_source": "in_memory",
        "source_event_ledger_path": None,
    }
    before = classify_holdout_recovery_state(
        envelope_path=envelope, session_id="session-1",
        source_event_ledger_boundary=boundary, audit_path=audit,
    )
    assert before["status"] == "NOT_CONSUMED"
    assert not audit.exists()

    _append(envelope, artifact, verification, audit, consume=True, boundary=boundary)
    unchanged = classify_holdout_recovery_state(
        envelope_path=envelope, session_id="session-1",
        source_event_ledger_boundary=boundary, audit_path=audit,
    )
    assert unchanged["status"] == "RECOVERY_CANDIDATE_UNCHANGED_BOUNDARY"
    assert unchanged["automatic_recovery_allowed"] is False

    changed = dict(boundary, source_event_ledger_prefix_sha256="a" * 64)
    drift = classify_holdout_recovery_state(
        envelope_path=envelope, session_id="session-1",
        source_event_ledger_boundary=changed, audit_path=audit,
    )
    assert drift["status"] == "JOURNAL_BOUNDARY_CHANGED_REVIEW_REQUIRED"
    assert drift["manual_reconciliation_required"] is True

    wrong_session = classify_holdout_recovery_state(
        envelope_path=envelope, session_id="session-2",
        source_event_ledger_boundary=boundary, audit_path=audit,
    )
    assert wrong_session["status"] == "SESSION_MISMATCH_REVIEW_REQUIRED"
    assert len(audit.read_text(encoding="utf-8").splitlines()) == 1

    _append(
        envelope, artifact, verification, audit,
        phase="holdout_to_forward_recovery",
        consume=True, resume=True, boundary=boundary,
    )
    repeated = classify_holdout_recovery_state(
        envelope_path=envelope, session_id="session-1",
        source_event_ledger_boundary=boundary, audit_path=audit,
    )
    assert repeated["status"] == "RECOVERY_ALREADY_RECORDED_REVIEW_REQUIRED"
    assert len(audit.read_text(encoding="utf-8").splitlines()) == 2


def test_recovery_classifier_fails_closed_on_corrupt_audit_without_mutation(tmp_path):
    envelope, _artifact, _verification, audit = _fixture(tmp_path)
    audit.write_text('{"sequence":1}\\n', encoding="utf-8")
    before = audit.read_bytes()
    boundary = {
        "source_event_ledger_prefix_sha256": hashlib.sha256(b"").hexdigest(),
        "source_event_ledger_prefix_byte_size": 0,
        "source_event_ledger_sequence_boundary": 0,
        "source_event_ledger_prefix_source": "in_memory",
        "source_event_ledger_path": None,
    }
    result = classify_holdout_recovery_state(
        envelope_path=envelope, session_id="session-1",
        source_event_ledger_boundary=boundary, audit_path=audit,
    )
    assert result["status"] == "AUDIT_INVALID_REVIEW_REQUIRED"
    assert result["automatic_recovery_allowed"] is False
    assert audit.read_bytes() == before




def test_trust_audit_rejects_incomplete_final_record_without_mutation(tmp_path):
    envelope, artifact, verification, audit = _fixture(tmp_path)
    _append(envelope, artifact, verification, audit, consume=True)
    audit.write_bytes(audit.read_bytes()[:-1])
    before = audit.read_bytes()

    with pytest.raises(TrustAuditError, match="incomplete final record"):
        _append(envelope, artifact, verification, audit, phase="runtime_preflight")

    assert audit.read_bytes() == before



def test_trust_audit_rejects_duplicate_json_keys_without_mutation(tmp_path):
    envelope, artifact, verification, audit = _fixture(tmp_path)
    _append(envelope, artifact, verification, audit, consume=True)
    audit.write_bytes(b'{"sequence":1,"sequence":1}' + bytes([10]))
    before = audit.read_bytes()

    with pytest.raises(TrustAuditError, match="duplicate JSON key"):
        _append(envelope, artifact, verification, audit, phase="runtime_preflight")

    assert audit.read_bytes() == before


def test_trust_audit_rejects_noncanonical_record_without_mutation(tmp_path):
    envelope, artifact, verification, audit = _fixture(tmp_path)
    entry = _append(envelope, artifact, verification, audit, consume=True)
    # Whitespace makes the record valid JSON but not the canonical encoding
    # required by the audit writer. Keep a complete LF-terminated record.
    audit.write_bytes(json.dumps(entry).encode("utf-8") + bytes([10]))
    before = audit.read_bytes()

    with pytest.raises(TrustAuditError, match="not canonical"):
        _append(envelope, artifact, verification, audit, phase="runtime_preflight")

    assert audit.read_bytes() == before


def test_trust_audit_rejects_boolean_sequence_without_mutation(tmp_path):
    envelope, artifact, verification, audit = _fixture(tmp_path)
    entry = _append(envelope, artifact, verification, audit, consume=True)
    entry["sequence"] = True
    body = {key: value for key, value in entry.items() if key != "entry_sha256"}
    entry["entry_sha256"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")
    ).hexdigest()
    audit.write_bytes(
        json.dumps(entry, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")
        + bytes([10])
    )
    before = audit.read_bytes()

    with pytest.raises(TrustAuditError, match="hash chain invalid"):
        _append(envelope, artifact, verification, audit, phase="runtime_preflight")

    assert audit.read_bytes() == before



def test_trust_audit_serializes_concurrent_appends_without_lost_records(tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    envelope, artifact, verification, audit = _fixture(tmp_path)
    workers = 6

    def append_one(_index):
        return _append(
            envelope, artifact, verification, audit,
            phase="runtime_preflight", session="concurrent-session",
        )

    with ThreadPoolExecutor(max_workers=workers) as pool:
        returned = list(pool.map(append_one, range(workers)))

    entries = [
        json.loads(line)
        for line in audit.read_text(encoding="utf-8").splitlines()
    ]
    assert len(entries) == workers
    assert sorted(entry["sequence"] for entry in returned) == list(range(1, workers + 1))
    previous = "0" * 64
    for sequence, entry in enumerate(entries, start=1):
        assert entry["sequence"] == sequence
        assert entry["previous_entry_sha256"] == previous
        body = {key: value for key, value in entry.items() if key != "entry_sha256"}
        expected = hashlib.sha256(
            json.dumps(
                body, sort_keys=True, separators=(",", ":"),
                ensure_ascii=True, allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        assert entry["entry_sha256"] == expected
        previous = entry["entry_sha256"]



def test_trust_audit_rolls_back_append_when_fsync_fails(tmp_path, monkeypatch):
    import strategy_factory.trust_audit as trust_audit

    envelope, artifact, verification, audit = _fixture(tmp_path)
    _append(envelope, artifact, verification, audit, phase="runtime_preflight")
    original = audit.read_bytes()
    real_fsync = trust_audit.os.fsync
    calls = 0

    def fail_first_fsync(fd):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("injected append fsync failure")
        return real_fsync(fd)

    monkeypatch.setattr(trust_audit.os, "fsync", fail_first_fsync)
    with pytest.raises(TrustAuditError, match="rolled back to its previous byte size"):
        _append(envelope, artifact, verification, audit, phase="runtime_dispatch")

    assert calls == 2
    assert audit.read_bytes() == original


def test_trust_audit_reports_manual_reconciliation_when_rollback_fails(tmp_path, monkeypatch):
    import strategy_factory.trust_audit as trust_audit

    envelope, artifact, verification, audit = _fixture(tmp_path)
    _append(envelope, artifact, verification, audit, phase="runtime_preflight")
    original = audit.read_bytes()
    calls = 0

    def fail_both_fsyncs(_fd):
        nonlocal calls
        calls += 1
        raise OSError(f"injected fsync failure {calls}")

    monkeypatch.setattr(trust_audit.os, "fsync", fail_both_fsyncs)
    with pytest.raises(TrustAuditError, match="manual reconciliation required"):
        _append(envelope, artifact, verification, audit, phase="runtime_dispatch")

    assert calls == 2
    # truncate may have restored the visible bytes even though its durability
    # could not be confirmed; the caller must still treat this as uncertain.
    assert audit.read_bytes() == original
