"""Read-only consistency audit between Factory worker snapshots and job journal.

This module reports orchestration discrepancies only. It never mutates worker
state, the queue, the journal, or research/strategy decisions.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .job_events import (
    DEFAULT_JOB_EVENTS_FILE,
    FactoryJobEventLedger,
    inspect_job_journal_snapshot,
)


_ACTIVE_STATES = {"RUNNING", "HEARTBEAT"}
_TERMINAL_STATES = {"COMPLETED", "FAILED"}
_LIFECYCLE_TYPES = {"QUEUED", "DISPATCHED", "COMPLETED", "FAILED"}


def _worker_value(worker: Any, name: str) -> Any:
    if isinstance(worker, Mapping):
        return worker.get(name)
    return getattr(worker, name, None)


def inspect_worker_journal_consistency(
    ledger: FactoryJobEventLedger,
    workers: Sequence[Any],
) -> dict[str, Any]:
    """Return deterministic findings for mismatched worker/journal lifecycle.

    A worker can be supplied as a FactoryWorker instance or a serialized
    telemetry mapping. Findings are diagnostic and never authorize retry.
    """
    events = ledger.entries()
    by_job: dict[str, list[Any]] = {}
    for event in events:
        if event.event_type in _LIFECYCLE_TYPES:
            by_job.setdefault(event.job_id, []).append(event)

    # Recovery status is derived from the same durable lifecycle journal. Join
    # it with the worker snapshot to surface contradictions across all three
    # operator-facing views; this is diagnostic only and never repairs state.
    recovery_rows = ledger.recovery_summary()
    recovery_by_job = {row["job_id"]: row for row in recovery_rows}
    recovery_status_counts: dict[str, int] = {}
    for recovery_row in recovery_rows:
        status = recovery_row["status"]
        recovery_status_counts[status] = recovery_status_counts.get(status, 0) + 1

    worker_rows: list[dict[str, Any]] = []
    seen_worker_ids: set[str] = set()
    findings: list[dict[str, str]] = []
    workers_by_job: dict[str, list[dict[str, Any]]] = {}

    for worker in workers:
        worker_id = str(_worker_value(worker, "worker_id") or "")
        job_id_value = _worker_value(worker, "job_id")
        job_id = str(job_id_value) if job_id_value else None
        state = str(_worker_value(worker, "state") or "UNKNOWN")
        row = {"worker_id": worker_id, "job_id": job_id, "state": state}
        worker_rows.append(row)
        if worker_id in seen_worker_ids:
            findings.append({
                "code": "DUPLICATE_WORKER_ID",
                "worker_id": worker_id,
                "job_id": job_id or "",
                "detail": "Worker snapshot contains a duplicate worker_id",
            })
        seen_worker_ids.add(worker_id)
        if job_id:
            workers_by_job.setdefault(job_id, []).append(row)
            recovery = recovery_by_job.get(job_id)
            recovery_status = recovery["status"] if recovery else None
            contradictory = (
                (recovery_status == "QUEUED_REVIEW_REQUIRED"
                 and state in _ACTIVE_STATES | _TERMINAL_STATES)
                or (recovery_status == "INTERRUPTED_REVIEW_REQUIRED"
                    and state in _TERMINAL_STATES)
                or (recovery_status == "TERMINAL_COMPLETED" and state == "FAILED")
                or (recovery_status == "TERMINAL_FAILED" and state == "COMPLETED")
            )
            if contradictory:
                findings.append({
                    "code": "RECOVERY_WORKER_STATE_CONFLICT",
                    "worker_id": worker_id,
                    "job_id": job_id,
                    "detail": (
                        f"Recovery summary status {recovery_status} conflicts "
                        f"with worker state {state}"
                    ),
                })

        if state in _ACTIVE_STATES:
            history = by_job.get(job_id or "", [])
            latest = history[-1] if history else None
            if latest is None or latest.event_type != "DISPATCHED" or latest.worker_id != worker_id:
                findings.append({
                    "code": "ACTIVE_WORKER_JOURNAL_MISMATCH",
                    "worker_id": worker_id,
                    "job_id": job_id or "",
                    "detail": "Active worker has no matching latest DISPATCHED event",
                })
        elif state in _TERMINAL_STATES and job_id:
            history = by_job.get(job_id, [])
            latest = history[-1] if history else None
            if (
                latest is None
                or latest.event_type != state
                or latest.worker_id != worker_id
            ):
                findings.append({
                    "code": "TERMINAL_WORKER_JOURNAL_MISMATCH",
                    "worker_id": worker_id,
                    "job_id": job_id,
                    "detail": "Terminal worker state lacks a matching latest terminal journal event",
                })

    for job_id, history in by_job.items():
        latest = history[-1]
        if latest.event_type != "DISPATCHED":
            continue
        matching = [
            row for row in workers_by_job.get(job_id, [])
            if row["worker_id"] == latest.worker_id and row["state"] in _ACTIVE_STATES
        ]
        if not matching:
            findings.append({
                "code": "DISPATCHED_JOB_NOT_ACTIVE_ON_WORKER",
                "worker_id": latest.worker_id or "",
                "job_id": job_id,
                "detail": "Journal ends at DISPATCHED but no matching worker is active; manual reconciliation may be required",
            })

    findings.sort(key=lambda item: (
        item["code"], item["job_id"], item["worker_id"], item["detail"]
    ))
    worker_rows.sort(key=lambda item: (item["worker_id"], item["job_id"] or "", item["state"]))
    return {
        "status": "CONSISTENT" if not findings else "REVIEW_REQUIRED",
        "worker_count": len(worker_rows),
        "journal_event_count": len(events),
        "recovery_job_count": len(recovery_rows),
        "recovery_status_counts": dict(sorted(recovery_status_counts.items())),
        "finding_count": len(findings),
        "findings": findings,
        "automatic_action_performed": False,
    }



def inspect_worker_journal_file_consistency(
    workers: Sequence[Any],
    path: Path = DEFAULT_JOB_EVENTS_FILE,
) -> dict[str, Any]:
    """Audit worker state against one validated on-disk journal snapshot.

    Invalid, missing, or unreadable journals produce REVIEW_REQUIRED without
    constructing a partial ledger. The parsed ledger and integrity digest come
    from the same byte snapshot; no repair, replay, retry, or write is performed.
    """
    integrity, events = inspect_job_journal_snapshot(path)
    if integrity["status"] != "VALID" or events is None:
        finding = {
            "code": "JOURNAL_INTEGRITY_REVIEW_REQUIRED",
            "worker_id": "",
            "job_id": "",
            "detail": str(integrity.get("error") or integrity["status"]),
        }
        return {
            "status": "REVIEW_REQUIRED",
            "worker_count": len(workers),
            "journal_event_count": None,
            "recovery_job_count": None,
            "recovery_status_counts": {},
            "finding_count": 1,
            "findings": [finding],
            "journal_integrity": integrity,
            "automatic_action_performed": False,
        }

    ledger = FactoryJobEventLedger.from_snapshot(events)
    report = inspect_worker_journal_consistency(ledger, workers)
    report["journal_integrity"] = integrity
    report["status"] = (
        "CONSISTENT"
        if report["status"] == "CONSISTENT" and integrity["status"] == "VALID"
        else "REVIEW_REQUIRED"
    )
    report["automatic_action_performed"] = False
    return report
