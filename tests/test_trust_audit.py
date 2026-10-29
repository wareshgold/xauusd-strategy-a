from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from strategy_factory.trust_audit import (
    TrustAuditError,
    append_verification_audit,
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


def test_trust_audit_fails_closed_when_existing_chain_is_tampered(tmp_path):
    envelope, artifact, verification, audit = _fixture(tmp_path)
    _append(envelope, artifact, verification, audit, consume=True)
    entry = json.loads(audit.read_text(encoding="utf-8"))
    entry["session_id"] = "altered"
    audit.write_text(json.dumps(entry) + "\n", encoding="utf-8")

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
