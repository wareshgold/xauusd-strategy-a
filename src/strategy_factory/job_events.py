from __future__ import annotations

"""Append-only research job lifecycle journal.

This is orchestration evidence, not strategy evidence. It records declared
Factory transitions so the visual world can later follow real queue movement
without inventing activity.
"""

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JOB_EVENTS_FILE = ROOT / "runtime" / "factory_job_events.jsonl"


@contextmanager
def _journal_write_lock(path: Path) -> Iterator[None]:
    """Serialize cooperating writers using an OS-backed persistent sidecar lock.

    The sidecar is deliberately not deleted: unlinking a lock file can split
    cooperating writers across different inodes. All writers must use this
    helper; processes that ignore the sidecar are outside the coordination
    contract.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(path.name + ".lock")
    with lock_path.open("a+b") as lock_file:
        if os.name == "nt":
            import msvcrt

            # Windows byte-range locking requires the target byte to exist.
            lock_file.seek(0, os.SEEK_END)
            if lock_file.tell() == 0:
                lock_file.write(b"\0")
                lock_file.flush()
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


@dataclass(frozen=True)
class FactoryJobEvent:
    sequence: int
    event_type: str
    job_id: str
    job_fingerprint: str
    worker_id: str | None
    station: str | None
    phase: str | None
    detail: str | None
    output_artifact: str | None
    occurred_utc: str
    event_fingerprint: str
    research_run_fingerprint: str | None = None

    def as_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        value = {
            "sequence": self.sequence,
            "event_type": self.event_type,
            "job_id": self.job_id,
            "job_fingerprint": self.job_fingerprint,
            "worker_id": self.worker_id,
            "station": self.station,
            "phase": self.phase,
            "detail": self.detail,
            "output_artifact": self.output_artifact,
            "occurred_utc": self.occurred_utc,
            "research_run_fingerprint": self.research_run_fingerprint,
        }
        if include_fingerprint:
            value["event_fingerprint"] = self.event_fingerprint
        return value

    def validate(self) -> None:
        if (
            not isinstance(self.sequence, int)
            or isinstance(self.sequence, bool)
            or self.sequence < 1
            or not isinstance(self.event_type, str)
            or not self.event_type
            or not isinstance(self.job_id, str)
            or not self.job_id
        ):
            raise ValueError("factory job event identity is incomplete")
        if not _is_sha256(self.job_fingerprint):
            raise ValueError("job_fingerprint must be lowercase hexadecimal SHA-256")
        optional_text_fields = (
            ("worker_id", self.worker_id),
            ("station", self.station),
            ("phase", self.phase),
            ("detail", self.detail),
            ("output_artifact", self.output_artifact),
            ("research_run_fingerprint", self.research_run_fingerprint),
        )
        for field_name, value in optional_text_fields:
            if value is not None and not isinstance(value, str):
                raise ValueError(
                    f"{field_name} must be a string or null"
                )
        if not isinstance(self.occurred_utc, str) or not self.occurred_utc:
            raise ValueError("occurred_utc must be a non-empty ISO-8601 UTC timestamp")
        timestamp_text = (
            self.occurred_utc[:-1] + "+00:00"
            if self.occurred_utc.endswith("Z")
            else self.occurred_utc
        )
        try:
            occurred = datetime.fromisoformat(timestamp_text)
        except ValueError as exc:
            raise ValueError(
                "occurred_utc must be an ISO-8601 timestamp with UTC timezone"
            ) from exc
        if occurred.tzinfo is None or occurred.utcoffset() != timezone.utc.utcoffset(occurred):
            raise ValueError(
                "occurred_utc must be an ISO-8601 timestamp with UTC timezone"
            )
        if not _is_sha256(self.event_fingerprint):
            raise ValueError("event_fingerprint must be lowercase hexadecimal SHA-256")
        expected = hashlib.sha256(
            _canonical(self.as_dict(include_fingerprint=False)).encode("utf-8")
        ).hexdigest()
        if self.event_fingerprint != expected:
            raise ValueError("factory job event fingerprint mismatch")


def _parse_journal_text(text: str) -> list[FactoryJobEvent]:
    """Validate one immutable text snapshot of the append-only JSONL journal."""
    events: list[FactoryJobEvent] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "factory job journal contains invalid JSON at line "
                f"{line_number}; journal preserved and automatic repair refused"
            ) from exc
        if not isinstance(payload, dict):
            raise ValueError(
                "factory job journal record at line "
                f"{line_number} is not an object; journal preserved"
            )
        try:
            event = FactoryJobEvent(**payload)
        except TypeError as exc:
            raise ValueError(
                "factory job journal record has an invalid schema at line "
                f"{line_number}; journal preserved"
            ) from exc
        try:
            event.validate()
        except ValueError as exc:
            raise ValueError(
                f"{exc} at line {line_number}; journal preserved"
            ) from exc
        if event.sequence != len(events) + 1:
            raise ValueError(
                "factory job event sequence is not contiguous "
                f"at line {line_number}; journal preserved"
            )
        events.append(event)
    return events


def inspect_job_journal_snapshot(
    path: Path = DEFAULT_JOB_EVENTS_FILE,
) -> tuple[dict[str, Any], tuple[FactoryJobEvent, ...] | None]:
    """Read and validate one immutable journal snapshot without modifying it.

    Returns the public integrity report plus parsed events from the exact same
    byte snapshot, preventing file-level audits from inspecting one version and
    then loading a potentially different version.
    """
    path = Path(path)
    if not path.exists():
        return ({
            "status": "MISSING_REVIEW_REQUIRED",
            "path": str(path),
            "exists": False,
            "byte_size": 0,
            "line_count": 0,
            "sha256": None,
            "error_type": None,
            "error": "journal file does not exist",
            "automatic_repair_performed": False,
        }, None)

    try:
        raw = path.read_bytes()
    except OSError as exc:
        return ({
            "status": "UNREADABLE_REVIEW_REQUIRED",
            "path": str(path),
            "exists": True,
            "byte_size": None,
            "line_count": None,
            "sha256": None,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "automatic_repair_performed": False,
        }, None)

    digest = hashlib.sha256(raw).hexdigest()
    line_count = len(raw.splitlines())
    try:
        text = raw.decode("utf-8")
        events = tuple(_parse_journal_text(text))
    except (UnicodeDecodeError, ValueError) as exc:
        return ({
            "status": "INVALID_REVIEW_REQUIRED",
            "path": str(path),
            "exists": True,
            "byte_size": len(raw),
            "line_count": line_count,
            "sha256": digest,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "automatic_repair_performed": False,
        }, None)

    return ({
        "status": "VALID",
        "path": str(path),
        "exists": True,
        "byte_size": len(raw),
        "line_count": line_count,
        "event_count": len(events),
        "sha256": digest,
        "error_type": None,
        "error": None,
        "automatic_repair_performed": False,
    }, events)



def verify_job_journal_prefix(
    path: Path,
    *,
    expected_sha256: str,
    expected_byte_size: int,
    sequence_boundary: int,
) -> dict[str, Any]:
    """Verify a signed, byte-exact prefix remains present in a valid JSONL journal.

    Later valid events are allowed: only the first sequence_boundary events and
    their exact serialized bytes are compared to the signed pre-transition
    boundary. This detects deletion, rewriting, reordering, and non-canonical
    substitutions without requiring the post-transition journal to stay frozen.
    """
    path = Path(path)
    if (
        not isinstance(expected_sha256, str)
        or len(expected_sha256) != 64
        or any(char not in "0123456789abcdef" for char in expected_sha256)
        or not isinstance(expected_byte_size, int)
        or isinstance(expected_byte_size, bool)
        or expected_byte_size < 0
        or not isinstance(sequence_boundary, int)
        or isinstance(sequence_boundary, bool)
        or sequence_boundary < 0
    ):
        raise ValueError("signed source event-ledger prefix metadata is invalid")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ValueError("persisted source event journal is missing or unreadable") from exc
    try:
        all_events = _parse_journal_text(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError("persisted source event journal is invalid") from exc
    if len(all_events) < sequence_boundary:
        raise ValueError("persisted source event journal is shorter than the signed prefix boundary")
    if len(raw) < expected_byte_size:
        raise ValueError("persisted source event journal is shorter than the signed prefix byte size")
    prefix = raw[:expected_byte_size]
    if hashlib.sha256(prefix).hexdigest() != expected_sha256:
        raise ValueError("persisted source event journal signed prefix SHA-256 mismatch")
    if sequence_boundary > 0 and not prefix.endswith(b"\\n"):
        raise ValueError("persisted source event journal signed prefix does not end on an event boundary")
    try:
        prefix_events = _parse_journal_text(prefix.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError("persisted source event journal signed prefix is invalid") from exc
    if len(prefix_events) != sequence_boundary:
        raise ValueError("persisted source event journal signed prefix event-count boundary mismatch")
    return {
        "verified": True,
        "path": str(path),
        "prefix_sha256": expected_sha256,
        "prefix_byte_size": expected_byte_size,
        "sequence_boundary": sequence_boundary,
        "current_event_count": len(all_events),
        "current_journal_sha256": hashlib.sha256(raw).hexdigest(),
        "later_events_preserved": len(all_events) > sequence_boundary,
    }


def inspect_job_journal_file(path: Path = DEFAULT_JOB_EVENTS_FILE) -> dict[str, Any]:
    """Inspect a journal snapshot without repairing or rewriting the source file."""
    report, _events = inspect_job_journal_snapshot(path)
    return report


class FactoryJobEventLedger:
    """Append-only in-memory lifecycle ledger with optional JSONL persistence."""

    def __init__(self, path: Path | None = DEFAULT_JOB_EVENTS_FILE) -> None:
        self.path = path
        self._events: list[FactoryJobEvent] = []
        if self.path is not None and self.path.exists():
            self._events = _parse_journal_text(
                self.path.read_text(encoding="utf-8")
            )

    @classmethod
    def from_snapshot(
        cls, events: tuple[FactoryJobEvent, ...]
    ) -> "FactoryJobEventLedger":
        """Build an in-memory ledger from already validated snapshot events."""
        ledger = cls(path=None)
        ledger._events = list(events)
        return ledger

    def append(
        self,
        *,
        event_type: str,
        job_id: str,
        job_fingerprint: str,
        worker_id: str | None = None,
        station: str | None = None,
        phase: str | None = None,
        detail: str | None = None,
        output_artifact: str | None = None,
        research_run_fingerprint: str | None = None,
    ) -> FactoryJobEvent:
        event = FactoryJobEvent(
            sequence=len(self._events) + 1,
            event_type=event_type,
            job_id=job_id,
            job_fingerprint=job_fingerprint,
            worker_id=worker_id,
            station=station,
            phase=phase,
            detail=detail,
            output_artifact=output_artifact,
            occurred_utc=_utc_now(),
            event_fingerprint="",
            research_run_fingerprint=research_run_fingerprint,
        )
        fingerprint = hashlib.sha256(
            _canonical(event.as_dict(include_fingerprint=False)).encode("utf-8")
        ).hexdigest()
        event = FactoryJobEvent(**event.as_dict(include_fingerprint=False), event_fingerprint=fingerprint)
        event.validate()
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            # The lock spans both integrity preflight and append/rollback, so
            # cooperating writers cannot race between validation and write.
            with _journal_write_lock(self.path):
                # Fail closed before the first write if the persisted journal
                # has drifted since this ledger was loaded. Never repair it.
                if self.path.exists():
                    journal_report, journal_events = inspect_job_journal_snapshot(self.path)
                    if (
                        journal_report.get("status") != "VALID"
                        or journal_events is None
                        or journal_events != tuple(self._events)
                    ):
                        raise OSError(
                            "factory job journal no longer matches the in-memory ledger; "
                            "append refused and manual reconciliation required"
                        )
                elif self._events:
                    raise OSError(
                        "factory job journal is missing while the in-memory ledger is non-empty; "
                        "append refused and manual reconciliation required"
                    )
                originally_exists = self.path.exists()
                original_size = self.path.stat().st_size if originally_exists else 0
                serialized = (
                    json.dumps(event.as_dict(), ensure_ascii=False, separators=(",", ":"))
                    + "\n"
                )
                try:
                    with self.path.open("a", encoding="utf-8") as handle:
                        handle.write(serialized)
                        handle.flush()
                        os.fsync(handle.fileno())
                except Exception as write_error:
                    # A failed write can leave a partial JSONL tail. Roll back
                    # to the pre-append byte boundary while still holding lock.
                    try:
                        with self.path.open("r+b") as rollback:
                            rollback.truncate(original_size)
                            rollback.flush()
                            os.fsync(rollback.fileno())
                    except OSError as rollback_error:
                        if not originally_exists:
                            try:
                                self.path.unlink(missing_ok=True)
                            except OSError as unlink_error:
                                raise OSError(
                                    "factory job journal append failed and rollback failed; "
                                    "manual reconciliation required"
                                ) from unlink_error
                        else:
                            raise OSError(
                                "factory job journal append failed and rollback failed; "
                                "manual reconciliation required"
                            ) from rollback_error
                    raise write_error
        # Commit to in-memory state only after persistence succeeds.
        self._events.append(event)
        return event

    def entries(self) -> tuple[FactoryJobEvent, ...]:
        return tuple(self._events)

    def for_job(self, job_id: str) -> tuple[FactoryJobEvent, ...]:
        return tuple(event for event in self._events if event.job_id == job_id)

    def recovery_summary(self) -> list[dict[str, Any]]:
        """Classify journaled jobs after restart without requeueing anything.

        A QUEUED-only job is reviewable but its full job spec is not persisted
        here. A DISPATCHED job without a terminal event may have executed
        partially, so it must be reviewed rather than retried automatically.
        COMPLETED/FAILED remain terminal even if later handoff events exist.
        """
        summary: list[dict[str, Any]] = []
        lifecycle_types = {"QUEUED", "DISPATCHED", "COMPLETED", "FAILED"}
        grouped: dict[str, list[FactoryJobEvent]] = {}
        fingerprints: dict[str, str] = {}
        for event in self._events:
            # Recovery reconstructs jobs from lifecycle events only. Plan-level
            # markers and post-completion handoff events remain in the durable
            # journal, but are not job-state transitions and may carry a
            # different provenance fingerprint.
            if event.event_type not in lifecycle_types:
                continue
            prior_fingerprint = fingerprints.setdefault(
                event.job_id, event.job_fingerprint
            )
            if prior_fingerprint != event.job_fingerprint:
                raise ValueError(
                    f"factory job fingerprint changed within ledger: {event.job_id}"
                )
            grouped.setdefault(event.job_id, []).append(event)
        valid_lifecycle_prefixes = {
            ("QUEUED",),
            ("QUEUED", "DISPATCHED"),
            ("QUEUED", "DISPATCHED", "COMPLETED"),
            ("QUEUED", "DISPATCHED", "FAILED"),
        }
        for job_id, job_events in grouped.items():
            event_types = {event.event_type for event in job_events}
            lifecycle_history = tuple(
                event.event_type for event in job_events
                if event.event_type in lifecycle_types
            )
            has_completed = "COMPLETED" in event_types
            has_failed = "FAILED" in event_types
            if has_completed and has_failed:
                status = "TERMINAL_CONFLICT_REVIEW_REQUIRED"
                action = "MANUAL_RECONCILIATION_REQUIRED"
            elif lifecycle_history and lifecycle_history not in valid_lifecycle_prefixes:
                status = "LIFECYCLE_CONFLICT_REVIEW_REQUIRED"
                action = "MANUAL_RECONCILIATION_REQUIRED"
            elif has_completed:
                status = "TERMINAL_COMPLETED"
                action = "NO_RETRY"
            elif has_failed:
                status = "TERMINAL_FAILED"
                action = "NO_RETRY"
            elif "DISPATCHED" in event_types:
                status = "INTERRUPTED_REVIEW_REQUIRED"
                action = "MANUAL_RECONCILIATION_REQUIRED"
            elif "QUEUED" in event_types:
                status = "QUEUED_REVIEW_REQUIRED"
                action = "JOB_SPEC_AND_QUEUE_RECONSTRUCTION_REQUIRED"
            else:
                status = "UNKNOWN_REVIEW_REQUIRED"
                action = "MANUAL_RECONCILIATION_REQUIRED"

            summary.append(
                {
                    "job_id": job_id,
                    "job_fingerprint": fingerprints[job_id],
                    "status": status,
                    "action": action,
                    "last_sequence": job_events[-1].sequence,
                    "last_event_type": job_events[-1].event_type,
                    "last_worker_id": job_events[-1].worker_id,
                    "last_occurred_utc": job_events[-1].occurred_utc,
                    "lifecycle_history": list(lifecycle_history),
                }
            )
        return summary

    def as_dict(self) -> list[dict[str, Any]]:
        return [event.as_dict() for event in self._events]
