"""Auditable, read-only Factory restart inspection reports.

Recovery inspection summarizes the append-only orchestration journal. It never
reconstructs missing job specs, requeues work, retries execution, or promotes
research artifacts.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .job_events import FactoryJobEventLedger


def _canonical(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


@dataclass(frozen=True)
class FactoryRecoveryReport:
    report_id: str
    journal_event_count: int
    jobs: tuple[dict[str, Any], ...]
    status_counts: dict[str, int]
    automatic_requeue_performed: bool = False
    journal_event_fingerprints: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "journal_event_count": self.journal_event_count,
            "jobs": [dict(job) for job in self.jobs],
            "status_counts": dict(self.status_counts),
            "journal_event_fingerprints": list(self.journal_event_fingerprints),
            "automatic_requeue_performed": self.automatic_requeue_performed,
        }


def _identity_payload(
    *,
    journal_event_fingerprints: tuple[str, ...] | list[str],
    jobs: tuple[dict[str, Any], ...] | list[dict[str, Any]],
    status_counts: dict[str, int],
    automatic_requeue_performed: bool,
) -> dict[str, Any]:
    return {
        "journal_event_fingerprints": list(journal_event_fingerprints),
        "jobs": [dict(job) for job in jobs],
        "status_counts": dict(status_counts),
        "automatic_requeue_performed": automatic_requeue_performed,
    }


def inspect_factory_recovery(ledger: FactoryJobEventLedger) -> FactoryRecoveryReport:
    """Return a deterministic read-only recovery summary for a loaded journal."""
    events = ledger.entries()
    summaries = ledger.recovery_summary()
    status_counts: dict[str, int] = {}
    for item in summaries:
        status = str(item["status"])
        status_counts[status] = status_counts.get(status, 0) + 1

    event_fingerprints = tuple(event.event_fingerprint for event in events)
    identity_payload = _identity_payload(
        journal_event_fingerprints=event_fingerprints,
        jobs=summaries,
        status_counts=status_counts,
        automatic_requeue_performed=False,
    )
    report_id = hashlib.sha256(_canonical(identity_payload).encode("utf-8")).hexdigest()
    report = FactoryRecoveryReport(
        report_id=report_id,
        journal_event_count=len(events),
        jobs=tuple(dict(item) for item in summaries),
        status_counts=status_counts,
        journal_event_fingerprints=event_fingerprints,
        automatic_requeue_performed=False,
    )
    validate_recovery_report(report)
    return report


def validate_recovery_report(report: FactoryRecoveryReport) -> None:
    """Fail closed if report provenance, summaries, or side-effect claims drift."""
    if len(report.report_id) != 64 or any(
        char not in "0123456789abcdef" for char in report.report_id
    ):
        raise ValueError("recovery report id must be a lowercase SHA-256 digest")
    if report.journal_event_count < 0:
        raise ValueError("journal_event_count cannot be negative")
    if report.journal_event_count != len(report.journal_event_fingerprints):
        raise ValueError("journal event count does not match journal fingerprints")
    if any(
        len(value) != 64 or any(char not in "0123456789abcdef" for char in value)
        for value in report.journal_event_fingerprints
    ):
        raise ValueError("journal event fingerprints must be lowercase SHA-256 digests")
    if report.automatic_requeue_performed:
        raise ValueError("recovery inspection must never perform automatic requeue")

    expected_counts: dict[str, int] = {}
    for job in report.jobs:
        status = job.get("status")
        if not isinstance(status, str) or not status:
            raise ValueError("every recovery job summary must have a status")
        expected_counts[status] = expected_counts.get(status, 0) + 1
    if report.status_counts != expected_counts:
        raise ValueError("recovery report status counts do not match job summaries")

    identity_payload = _identity_payload(
        journal_event_fingerprints=report.journal_event_fingerprints,
        jobs=report.jobs,
        status_counts=report.status_counts,
        automatic_requeue_performed=report.automatic_requeue_performed,
    )
    expected_report_id = hashlib.sha256(
        _canonical(identity_payload).encode("utf-8")
    ).hexdigest()
    if report.report_id != expected_report_id:
        raise ValueError("recovery report id does not match report provenance and content")
