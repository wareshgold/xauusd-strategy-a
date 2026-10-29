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
    resume_holdout_once: bool = False,
    source_event_ledger_boundary: dict[str, Any] | None = None,
    audit_path: Path | None = None,
) -> dict[str, Any]:
    """Validate and durably append one successful verification record.

    Holdout-to-Forward consumes a signed envelope once globally. A recovery
    record is allowed only for the same envelope, session, and exact signed
    source-journal boundary; callers must independently verify that the journal
    still equals that boundary before requesting recovery. Runtime phases are
    repeatable for the same bound session.
    """
    if phase not in {"holdout_to_forward", "holdout_to_forward_recovery", "runtime_preflight", "runtime_dispatch"}:
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
            if resume_holdout_once and not consume_holdout_once:
                raise TrustAuditError("Holdout recovery requires one-time consumption mode")
            if consume_holdout_once:
                if phase not in {"holdout_to_forward", "holdout_to_forward_recovery"}:
                    raise TrustAuditError("one-time Holdout consumption is valid only at Holdout-to-Forward")
                if source_event_ledger_boundary is None:
                    raise TrustAuditError("Holdout consumption requires a signed source-journal boundary")
                boundary_fields = {
                    "source_event_ledger_prefix_sha256",
                    "source_event_ledger_prefix_byte_size",
                    "source_event_ledger_sequence_boundary",
                    "source_event_ledger_prefix_source",
                    "source_event_ledger_path",
                }
                if set(source_event_ledger_boundary) != boundary_fields:
                    raise TrustAuditError("Holdout source-journal recovery boundary fields are invalid")
                boundary_sha = source_event_ledger_boundary.get("source_event_ledger_prefix_sha256")
                boundary_size = source_event_ledger_boundary.get("source_event_ledger_prefix_byte_size")
                boundary_count = source_event_ledger_boundary.get("source_event_ledger_sequence_boundary")
                boundary_source = source_event_ledger_boundary.get("source_event_ledger_prefix_source")
                boundary_path = source_event_ledger_boundary.get("source_event_ledger_path")
                if (
                    not isinstance(boundary_sha, str)
                    or len(boundary_sha) != 64
                    or any(char not in "0123456789abcdef" for char in boundary_sha)
                    or not isinstance(boundary_size, int)
                    or isinstance(boundary_size, bool)
                    or boundary_size < 0
                    or not isinstance(boundary_count, int)
                    or isinstance(boundary_count, bool)
                    or boundary_count < 0
                    or boundary_source not in {"persisted_jsonl", "in_memory"}
                    or (boundary_source == "persisted_jsonl" and not isinstance(boundary_path, str))
                    or (boundary_source == "in_memory" and boundary_path is not None)
                ):
                    raise TrustAuditError("Holdout source-journal recovery boundary values are invalid")
                prior_consumption = next((
                    item for item in entries
                    if item.get("phase") == "holdout_to_forward"
                    and item.get("envelope_sha256") == envelope_sha
                ), None)
                if prior_consumption is not None:
                    if not resume_holdout_once:
                        raise TrustAuditError("signed Holdout evidence has already been consumed")
                    prior_boundary = {
                        key: prior_consumption.get(key) for key in boundary_fields
                    }
                    prior_recovery = next((
                        item for item in entries
                        if item.get("phase") == "holdout_to_forward_recovery"
                        and item.get("envelope_sha256") == envelope_sha
                    ), None)
                    if prior_recovery is not None:
                        raise TrustAuditError(
                            "Holdout recovery has already been recorded; manual reconciliation required"
                        )
                    if (
                        prior_consumption.get("session_id") != session_id
                        or prior_boundary != source_event_ledger_boundary
                        or phase != "holdout_to_forward_recovery"
                    ):
                        raise TrustAuditError(
                            "Holdout recovery requires the same session and unchanged signed journal boundary"
                        )
                elif resume_holdout_once or phase == "holdout_to_forward_recovery":
                    raise TrustAuditError("Holdout recovery has no matching prior consumption record")
            elif resume_holdout_once or phase == "holdout_to_forward_recovery":
                raise TrustAuditError("Holdout recovery requires one-time consumption mode")
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
                **(source_event_ledger_boundary or {}),
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
        raise TrustAuditError(f"trust verification audit could not be durably appended: {exc!r}") from exc


def classify_holdout_recovery_state(
    *,
    envelope_path: Path,
    session_id: str,
    source_event_ledger_boundary: dict[str, Any],
    audit_path: Path | None = None,
) -> dict[str, Any]:
    """Return a read-only recovery classification; never appends or repairs.

    The caller must independently verify that the supplied boundary describes
    the current journal snapshot. A recovery candidate is not permission to
    execute a transition: the caller must still perform signed-evidence
    verification and journal-prefix validation before any mutation.
    """
    if not session_id:
        raise TrustAuditError("recovery classification requires a forward session ID")
    boundary_fields = {
        "source_event_ledger_prefix_sha256",
        "source_event_ledger_prefix_byte_size",
        "source_event_ledger_sequence_boundary",
        "source_event_ledger_prefix_source",
        "source_event_ledger_path",
    }
    if set(source_event_ledger_boundary) != boundary_fields:
        raise TrustAuditError("Holdout source-journal recovery boundary fields are invalid")
    path = Path(audit_path) if audit_path is not None else _default_audit_path()
    try:
        envelope_sha = hashlib.sha256(Path(envelope_path).read_bytes()).hexdigest()
        entries = _read_valid_entries(path)
    except TrustAuditError:
        return {
            "status": "AUDIT_INVALID_REVIEW_REQUIRED",
            "automatic_recovery_allowed": False,
            "manual_reconciliation_required": True,
        }
    except OSError as exc:
        raise TrustAuditError("recovery classification evidence is unreadable") from exc

    consumption = next((
        item for item in entries
        if item.get("phase") == "holdout_to_forward"
        and item.get("envelope_sha256") == envelope_sha
    ), None)
    if consumption is None:
        return {
            "status": "NOT_CONSUMED",
            "automatic_recovery_allowed": False,
            "manual_reconciliation_required": False,
        }
    if consumption.get("session_id") != session_id:
        status = "SESSION_MISMATCH_REVIEW_REQUIRED"
    elif any(
        item.get("phase") == "holdout_to_forward_recovery"
        and item.get("envelope_sha256") == envelope_sha
        for item in entries
    ):
        status = "RECOVERY_ALREADY_RECORDED_REVIEW_REQUIRED"
    elif {
        key: consumption.get(key) for key in boundary_fields
    } != source_event_ledger_boundary:
        status = "JOURNAL_BOUNDARY_CHANGED_REVIEW_REQUIRED"
    else:
        status = "RECOVERY_CANDIDATE_UNCHANGED_BOUNDARY"

    candidate = status == "RECOVERY_CANDIDATE_UNCHANGED_BOUNDARY"
    return {
        "status": status,
        "automatic_recovery_allowed": False,
        "manual_reconciliation_required": not candidate,
        "envelope_sha256": envelope_sha,
        "session_id": session_id,
        "consumption_sequence": consumption.get("sequence"),
        "recovery_candidate_requires_fresh_signature_and_journal_verification": candidate,
    }
