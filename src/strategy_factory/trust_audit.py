from __future__ import annotations

"""Append-only hash-chained audit for trusted Fresh Holdout evidence.

The hash chain detects accidental edits/reordering but is not a remote trust
anchor: privileged filesystem users can rewrite the entire file. Deployment
must restrict write access and preserve independent backups/attestations.
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .job_events import _journal_write_lock
from .trust_anchor import TrustAnchorError


class TrustAuditError(RuntimeError):
    """Raised when the trust audit cannot be validated or durably appended."""


def _default_audit_path() -> Path:
    if os.name == "nt":
        return Path("C:/ProgramData/SP2L/trust/verification-audit.jsonl")
    return Path("/var/lib/sp2l/trust/verification-audit.jsonl")


def _canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _read_valid_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise TrustAuditError("trust verification audit is unreadable") from exc
    entries: list[dict[str, Any]] = []
    previous = "0" * 64
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line:
            raise TrustAuditError(f"trust verification audit has an empty line at {line_number}")
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TrustAuditError(
                f"trust verification audit JSON invalid at line {line_number}"
            ) from exc
        if not isinstance(entry, dict):
            raise TrustAuditError(f"trust verification audit entry {line_number} is not an object")
        digest = entry.get("entry_sha256")
        body = {key: value for key, value in entry.items() if key != "entry_sha256"}
        expected = hashlib.sha256(_canonical(body)).hexdigest()
        if (
            entry.get("sequence") != len(entries) + 1
            or entry.get("previous_entry_sha256") != previous
            or digest != expected
        ):
            raise TrustAuditError(
                f"trust verification audit hash chain invalid at line {line_number}"
            )
        entries.append(entry)
        previous = digest
    return entries


def append_verification_audit(
    *,
    phase: str,
    session_id: str,
    envelope_path: Path,
    artifact_path: Path,
    verification: dict[str, Any],
    consume_holdout_once: bool = False,
    audit_path: Path | None = None,
) -> dict[str, Any]:
    """Validate and durably append one successful verification record.

    Holdout-to-Forward consumes a signed envelope once globally. Runtime phases
    are repeatable for the same bound session, so preflight and dispatch can
    both be audited without being mistaken for a replay.
    """
    if phase not in {"holdout_to_forward", "runtime_preflight", "runtime_dispatch"}:
        raise TrustAuditError("unsupported trust verification audit phase")
    if not session_id:
        raise TrustAuditError("trust audit requires a forward session ID")
    if verification.get("verified") is not True:
        raise TrustAuditError("only successfully verified evidence may be audited")
    path = Path(audit_path) if audit_path is not None else _default_audit_path()
    try:
        envelope_sha = hashlib.sha256(Path(envelope_path).read_bytes()).hexdigest()
        artifact_sha = hashlib.sha256(Path(artifact_path).read_bytes()).hexdigest()
    except OSError as exc:
        raise TrustAuditError("verified evidence or artifact became unreadable before audit") from exc
    now = datetime.now(timezone.utc).isoformat()

    try:
        with _journal_write_lock(path):
            entries = _read_valid_entries(path)
            if consume_holdout_once:
                if phase != "holdout_to_forward":
                    raise TrustAuditError("one-time Holdout consumption is valid only at Holdout-to-Forward")
                if any(
                    item.get("phase") == "holdout_to_forward"
                    and item.get("envelope_sha256") == envelope_sha
                    for item in entries
                ):
                    raise TrustAuditError("signed Holdout evidence has already been consumed")
            body = {
                "sequence": len(entries) + 1,
                "phase": phase,
                "session_id": session_id,
                "envelope_sha256": envelope_sha,
                "key_id": verification.get("key_id"),
                "artifact_sha256": artifact_sha,
                "issued_at_utc": verification.get("issued_at_utc"),
                "expires_at_utc": verification.get("expires_at_utc"),
                "recorded_at_utc": now,
                "previous_entry_sha256": entries[-1]["entry_sha256"] if entries else "0" * 64,
            }
            entry = {**body, "entry_sha256": hashlib.sha256(_canonical(body)).hexdigest()}
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("ab") as handle:
                handle.write(_canonical(entry) + b"\n")
                handle.flush()
                os.fsync(handle.fileno())
            return entry
    except TrustAuditError:
        raise
    except (OSError, ValueError, TypeError) as exc:
        raise TrustAuditError("trust verification audit could not be durably appended") from exc
