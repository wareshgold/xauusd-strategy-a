from __future__ import annotations

"""Fail-closed Ed25519 verification for externally signed research evidence.

This module is a verification primitive only. It does not authorize trading or
make Strategy A canonical. The public-key registry must be provisioned outside
the repository and protected from the process/user that supplies the envelope.
"""

import base64
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


class TrustAnchorError(RuntimeError):
    """Raised when signed evidence cannot be authenticated."""


def _default_keyring_path() -> Path:
    # Deliberately not configurable through an environment variable: a caller
    # must not select the trust root alongside the evidence being verified.
    if os.name == "nt":
        root = os.environ.get("PROGRAMDATA")
        if not root:
            raise TrustAnchorError("PROGRAMDATA unavailable; trusted keyring path cannot be resolved")
        return Path(root) / "SP2L" / "trust" / "holdout-ed25519-keyring.json"
    return Path("/etc/sp2l/trust/holdout-ed25519-keyring.json")


def _canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise TrustAnchorError("evidence envelope is not canonical-JSON serializable") from exc


def _utc_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise TrustAnchorError(f"{field} is required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TrustAnchorError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TrustAnchorError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def verify_signed_evidence(
    envelope_path: Path,
    *,
    expected_bindings: dict[str, Any],
    artifact_path: Path,
    now_utc: datetime | None = None,
) -> dict[str, Any]:
    """Verify an Ed25519 envelope against the machine-managed trusted keyring.

    Required envelope fields: schema_version, key_id, issued_at_utc,
    expires_at_utc, payload, signature_b64. The signature covers the canonical
    JSON object containing all fields except signature_b64. Payload must include
    holdout_artifact_sha256 and the caller-supplied expected binding fields.

    This function deliberately has no public-key/verifier injection parameter.
    Tests may monkeypatch the private path resolver; production callers cannot
    choose a trust root through the public API.
    """
    try:
        envelope = json.loads(Path(envelope_path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise TrustAnchorError("signed evidence envelope is missing or unreadable") from exc
    if not isinstance(envelope, dict):
        raise TrustAnchorError("signed evidence envelope must be a JSON object")

    required = {
        "schema_version", "key_id", "issued_at_utc", "expires_at_utc",
        "payload", "signature_b64",
    }
    if set(envelope) != required:
        raise TrustAnchorError("signed evidence envelope fields do not match the required schema")
    if envelope["schema_version"] != "SP2L-SIGNED-EVIDENCE-1":
        raise TrustAnchorError("unsupported signed evidence schema")
    key_id = envelope["key_id"]
    payload = envelope["payload"]
    if not isinstance(key_id, str) or not key_id or not isinstance(payload, dict):
        raise TrustAnchorError("key_id and payload are invalid")

    issued = _utc_timestamp(envelope["issued_at_utc"], "issued_at_utc")
    expires = _utc_timestamp(envelope["expires_at_utc"], "expires_at_utc")
    now = now_utc or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise TrustAnchorError("now_utc must be timezone-aware")
    now = now.astimezone(timezone.utc)
    if expires <= issued:
        raise TrustAnchorError("evidence expiry must be after issuance")
    if issued > now:
        raise TrustAnchorError("signed evidence is not yet valid")
    if now >= expires:
        raise TrustAnchorError("signed evidence has expired")

    for name, expected in expected_bindings.items():
        if name not in payload or payload[name] != expected:
            raise TrustAnchorError(f"signed evidence binding mismatch: {name}")

    artifact = Path(artifact_path)
    try:
        actual_sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
    except OSError as exc:
        raise TrustAnchorError("bound holdout artifact is missing or unreadable") from exc
    if payload.get("holdout_artifact_sha256") != actual_sha:
        raise TrustAnchorError("bound holdout artifact SHA-256 mismatch")

    try:
        keyring_path = _default_keyring_path()
        keyring = json.loads(keyring_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, TrustAnchorError) as exc:
        raise TrustAnchorError("trusted public-key registry is missing or invalid") from exc
    if not isinstance(keyring, dict) or not isinstance(keyring.get("keys"), dict):
        raise TrustAnchorError("trusted public-key registry schema is invalid")
    encoded_key = keyring["keys"].get(key_id)
    if not isinstance(encoded_key, str) or not encoded_key:
        raise TrustAnchorError("signing key is unknown or not trusted")

    try:
        public_key_bytes = base64.b64decode(encoded_key, validate=True)
        signature = base64.b64decode(envelope["signature_b64"], validate=True)
        if len(public_key_bytes) != 32 or len(signature) != 64:
            raise ValueError("invalid Ed25519 key/signature length")
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        signed_fields = {name: value for name, value in envelope.items() if name != "signature_b64"}
        public_key.verify(signature, _canonical_bytes(signed_fields))
    except (ValueError, InvalidSignature) as exc:
        raise TrustAnchorError("signed evidence signature is invalid") from exc

    return {
        "verified": True,
        "schema_version": envelope["schema_version"],
        "key_id": key_id,
        "issued_at_utc": issued.isoformat(),
        "expires_at_utc": expires.isoformat(),
        "payload": payload,
        "artifact_sha256": actual_sha,
    }
