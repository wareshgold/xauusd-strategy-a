from __future__ import annotations

"""Append-only research job lifecycle journal.

This is orchestration evidence, not strategy evidence. It records declared
Factory transitions so the visual world can later follow real queue movement
without inventing activity.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JOB_EVENTS_FILE = ROOT / "runtime" / "factory_job_events.jsonl"


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
            raise ValueError("occurred_utc must be a non-empty string")
        if not _is_sha256(self.event_fingerprint):
            raise ValueError("event_fingerprint must be lowercase hexadecimal SHA-256")
        expected = hashlib.sha256(
            _canonical(self.as_dict(include_fingerprint=False)).encode("utf-8")
        ).hexdigest()
        if self.event_fingerprint != expected:
            raise ValueError("factory job event fingerprint mismatch")


class FactoryJobEventLedger:
    """Append-only in-memory lifecycle ledger with optional JSONL persistence."""

    def __init__(self, path: Path | None = DEFAULT_JOB_EVENTS_FILE) -> None:
        self.path = path
        self._events: list[FactoryJobEvent] = []
        if self.path is not None and self.path.exists():
            for line_number, line in enumerate(
                self.path.read_text(encoding="utf-8").splitlines(), start=1
            ):
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
                event.validate()
                if event.sequence != len(self._events) + 1:
                    raise ValueError(
                        "factory job event sequence is not contiguous "
                        f"at line {line_number}; journal preserved"
                    )
                self._events.append(event)

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
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event.as_dict(), ensure_ascii=False, separators=(",", ":")) + "\n")
        # Commit to in-memory state only after persistence succeeds. If disk
        # writing fails, callers may safely retry without a phantom sequence.
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
                }
            )
        return summary

    def as_dict(self) -> list[dict[str, Any]]:
        return [event.as_dict() for event in self._events]
