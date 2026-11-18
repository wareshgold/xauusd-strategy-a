"""Research-only runner and position provenance primitives.

This module records identity and configuration evidence. It does not connect to
MT5, submit/modify/cancel orders, interpret strategy geometry, or make signals.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = 1


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _validate_json_value(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"non-finite number at {path}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_value(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise TypeError(f"non-string object key at {path}")
        for key, item in value.items():
            _validate_json_value(item, f"{path}.{key}")
        return
    raise TypeError(f"unsupported JSON value at {path}: {type(value).__name__}")


def canonical_json(value: Any) -> str:
    """Stable JSON representation used for hashes and event-chain payloads."""
    _validate_json_value(value)
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def make_run_identity(
    *,
    runner_id: str,
    runner_version: str,
    git_commit: str,
    config: Mapping[str, Any],
    started_at_utc: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Create an immutable identity snapshot for one process execution."""
    for field, value in (
        ("runner_id", runner_id),
        ("runner_version", runner_version),
        ("git_commit", git_commit),
    ):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", git_commit):
        raise ValueError("git_commit must be a 7-40 character hexadecimal commit")
    snapshot = dict(config)
    _validate_json_value(snapshot)
    config_hash = sha256_json(snapshot)
    identity = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id or uuid.uuid4().hex,
        "runner_id": runner_id,
        "runner_version": runner_version,
        "git_commit": git_commit.lower(),
        "started_at_utc": started_at_utc or _utc_now(),
        "config_id": f"CFG_{config_hash[:12].upper()}",
        "config_hash_sha256": config_hash,
        "config_snapshot": snapshot,
    }
    if not re.fullmatch(r"[0-9a-f]{32}", identity["run_id"]):
        raise ValueError("run_id must be a 32-character lowercase hex UUID")
    return identity


def mt5_comment_token(identity: Mapping[str, Any]) -> str:
    """Compact correlation hint only; never treat broker comment as authority."""
    run_short = str(identity["run_id"])[:8]
    cfg_short = str(identity["config_hash_sha256"])[:8]
    token = f"S2L:{run_short}:{cfg_short}"
    if len(token) > 31:
        raise AssertionError("MT5 correlation token exceeds 31 characters")
    return token


def write_run_manifest(path: str | Path, identity: Mapping[str, Any]) -> None:
    """Create once; never overwrite an existing run manifest."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_json(dict(identity)) + "\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(str(target), flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        try:
            target.unlink()
        except OSError:
            pass
        raise


class ProvenanceEventLog:
    """Append-only, SHA-256 hash-chained JSONL evidence log.

    A malformed/truncated existing tail is a hard error. This class is intended
    for one writer process per log; external multi-process locking is required
    if a future integration ever permits concurrent writers.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _last_chain_state(self) -> tuple[int, str]:
        if not self.path.exists():
            return 0, "0" * 64
        sequence = 0
        previous = "0" * 64
        with self.path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.endswith("\n"):
                    raise ValueError(f"truncated provenance log at line {line_number}")
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid provenance JSON at line {line_number}") from exc
                event_hash = record.pop("event_hash_sha256", None)
                if record.get("sequence") != sequence + 1:
                    raise ValueError(f"invalid provenance sequence at line {line_number}")
                if record.get("previous_event_hash_sha256") != previous:
                    raise ValueError(f"broken provenance chain at line {line_number}")
                expected = sha256_json(record)
                if event_hash != expected:
                    raise ValueError(f"provenance hash mismatch at line {line_number}")
                sequence += 1
                previous = event_hash
        return sequence, previous

    def append(self, event_type: str, fields: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("event_type must be non-empty")
        sequence, previous = self._last_chain_state()
        record = {
            "schema_version": SCHEMA_VERSION,
            "sequence": sequence + 1,
            "event_ts_utc": _utc_now(),
            "event_type": event_type,
            "previous_event_hash_sha256": previous,
            "fields": dict(fields),
        }
        _validate_json_value(record)
        event_hash = sha256_json(record)
        complete = {**record, "event_hash_sha256": event_hash}
        line = canonical_json(complete) + "\n"
        fd = os.open(str(self.path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, "a", encoding="utf-8", newline="\\n") as stream:
            stream.write(line)
            stream.flush()
            os.fsync(stream.fileno())
        return complete


def run_started(log: ProvenanceEventLog, identity: Mapping[str, Any]) -> dict[str, Any]:
    return log.append("RUNNER_STARTED", {"identity": dict(identity)})


def position_linked(
    log: ProvenanceEventLog,
    identity: Mapping[str, Any],
    *,
    position_id: int,
    symbol: str,
    magic: int,
    order_ticket: int | None = None,
    deal_ticket: int | None = None,
    broker_comment: str | None = None,
) -> dict[str, Any]:
    """Link observed broker identifiers to the immutable run/config identity."""
    if int(position_id) <= 0 or int(magic) < 0 or not symbol:
        raise ValueError("invalid position_id, magic, or symbol")
    return log.append("POSITION_LINKED", {
        "run_id": identity["run_id"],
        "runner_id": identity["runner_id"],
        "runner_version": identity["runner_version"],
        "git_commit": identity["git_commit"],
        "config_id": identity["config_id"],
        "config_hash_sha256": identity["config_hash_sha256"],
        "position_id": int(position_id),
        "symbol": str(symbol),
        "magic": int(magic),
        "order_ticket": int(order_ticket) if order_ticket is not None else None,
        "deal_ticket": int(deal_ticket) if deal_ticket is not None else None,
        # Retained as an untrusted hint, not used to establish provenance.
        "broker_comment": broker_comment,
    })


def verify_event_log(path: str | Path) -> dict[str, Any]:
    """Verify the complete hash chain and return a compact integrity summary."""
    log = ProvenanceEventLog(path)
    count, final_hash = log._last_chain_state()
    return {"valid": True, "event_count": count, "final_event_hash_sha256": final_hash}
