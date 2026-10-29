from __future__ import annotations

import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from strategy_factory import trust_anchor
from strategy_factory.trust_anchor import TrustAnchorError, verify_signed_evidence


NOW = datetime(2026, 10, 29, 10, 0, tzinfo=timezone.utc)


def _canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _fixture(tmp_path, monkeypatch, *, expires="2026-10-29T11:00:00Z"):
    private = Ed25519PrivateKey.generate()
    public_bytes = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    artifact = tmp_path / "holdout.bin"
    artifact.write_bytes(b"immutable fresh holdout")
    payload = {
        "strategy_id": "SP2L-A-SYNTHETIC",
        "strategy_revision": "FROZEN-SYNTHETIC-1",
        "holdout_dataset_id": "FRESH-HOLDOUT-SYNTHETIC-1",
        "holdout_artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
    }
    envelope = {
        "schema_version": "SP2L-SIGNED-EVIDENCE-1",
        "key_id": "test-key-1",
        "issued_at_utc": "2026-10-29T09:00:00Z",
        "expires_at_utc": expires,
        "payload": payload,
    }
    envelope["signature_b64"] = base64.b64encode(
        private.sign(_canonical(envelope))
    ).decode("ascii")
    envelope_path = tmp_path / "envelope.json"
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    keyring_path = tmp_path / "trusted-keyring.json"
    keyring_path.write_text(
        json.dumps({"keys": {"test-key-1": base64.b64encode(public_bytes).decode("ascii")}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(trust_anchor, "_default_keyring_path", lambda: keyring_path)
    bindings = {
        "strategy_id": payload["strategy_id"],
        "strategy_revision": payload["strategy_revision"],
        "holdout_dataset_id": payload["holdout_dataset_id"],
    }
    return envelope_path, artifact, keyring_path, bindings, envelope


def test_signed_evidence_verifies_against_external_keyring_and_artifact(tmp_path, monkeypatch):
    envelope, artifact, _, bindings, _ = _fixture(tmp_path, monkeypatch)
    result = verify_signed_evidence(
        envelope, expected_bindings=bindings, artifact_path=artifact, now_utc=NOW
    )
    assert result["verified"] is True
    assert result["key_id"] == "test-key-1"
    assert result["artifact_sha256"] == hashlib.sha256(artifact.read_bytes()).hexdigest()


def test_signed_evidence_rejects_tampered_payload(tmp_path, monkeypatch):
    envelope_path, artifact, _, bindings, envelope = _fixture(tmp_path, monkeypatch)
    envelope["payload"]["strategy_revision"] = "CHANGED"
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(TrustAnchorError, match="binding mismatch|signature is invalid"):
        verify_signed_evidence(
            envelope_path, expected_bindings=bindings, artifact_path=artifact, now_utc=NOW
        )


def test_signed_evidence_rejects_unknown_key(tmp_path, monkeypatch):
    envelope_path, artifact, keyring_path, bindings, _ = _fixture(tmp_path, monkeypatch)
    keyring_path.write_text(json.dumps({"keys": {}}), encoding="utf-8")
    with pytest.raises(TrustAnchorError, match="unknown or not trusted"):
        verify_signed_evidence(
            envelope_path, expected_bindings=bindings, artifact_path=artifact, now_utc=NOW
        )


def test_signed_evidence_rejects_expired_envelope(tmp_path, monkeypatch):
    envelope_path, artifact, _, bindings, _ = _fixture(
        tmp_path, monkeypatch, expires="2026-10-29T09:59:59Z"
    )
    with pytest.raises(TrustAnchorError, match="expired"):
        verify_signed_evidence(
            envelope_path, expected_bindings=bindings, artifact_path=artifact, now_utc=NOW
        )


def test_signed_evidence_rejects_artifact_byte_change(tmp_path, monkeypatch):
    envelope_path, artifact, _, bindings, _ = _fixture(tmp_path, monkeypatch)
    artifact.write_bytes(b"changed bytes")
    with pytest.raises(TrustAnchorError, match="artifact SHA-256 mismatch"):
        verify_signed_evidence(
            envelope_path, expected_bindings=bindings, artifact_path=artifact, now_utc=NOW
        )


def test_signed_evidence_fails_closed_without_trusted_keyring(tmp_path, monkeypatch):
    envelope_path, artifact, _, bindings, _ = _fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(
        trust_anchor, "_default_keyring_path", lambda: tmp_path / "missing-keyring.json"
    )
    with pytest.raises(TrustAnchorError, match="registry is missing or invalid"):
        verify_signed_evidence(
            envelope_path, expected_bindings=bindings, artifact_path=artifact, now_utc=NOW
        )


def test_signed_evidence_rejects_revoked_key(tmp_path, monkeypatch):
    envelope_path, artifact, keyring_path, bindings, _ = _fixture(tmp_path, monkeypatch)
    keyring = json.loads(keyring_path.read_text(encoding="utf-8"))
    keyring["revoked_key_ids"] = ["test-key-1"]
    keyring_path.write_text(json.dumps(keyring), encoding="utf-8")
    with pytest.raises(TrustAnchorError, match="has been revoked"):
        verify_signed_evidence(
            envelope_path, expected_bindings=bindings, artifact_path=artifact, now_utc=NOW
        )
