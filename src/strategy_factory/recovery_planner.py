"""Explicit planning for safe reconstruction of queued Factory jobs.

Planning is read-only: it does not mutate an orchestrator queue or execute work.
Only QUEUED-only jobs can be proposed, and every proposal must be explicitly
approved and matched to a caller-supplied, fingerprint-verified Job Spec.
Interrupted DISPATCHED jobs require manual reconciliation and are never planned.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping

from .job_events import FactoryJobEventLedger
from .jobs import ResearchJobSpec
from .recovery_report import FactoryRecoveryReport, validate_recovery_report


def _canonical(value: dict[str, object]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


@dataclass(frozen=True)
class QueueReconstructionItem:
    job_id: str
    job_fingerprint: str
    original_queue_sequence: int
    job: ResearchJobSpec


@dataclass(frozen=True)
class QueueReconstructionPlan:
    plan_id: str
    recovery_report_id: str
    approved_job_ids: tuple[str, ...]
    items: tuple[QueueReconstructionItem, ...]
    automatic_requeue_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "plan_id": self.plan_id,
            "recovery_report_id": self.recovery_report_id,
            "approved_job_ids": list(self.approved_job_ids),
            "items": [
                {
                    "job_id": item.job_id,
                    "job_fingerprint": item.job_fingerprint,
                    "original_queue_sequence": item.original_queue_sequence,
                    "job": item.job.as_dict(),
                }
                for item in self.items
            ],
            "automatic_requeue_performed": self.automatic_requeue_performed,
        }


def plan_queue_reconstruction(
    *,
    ledger: FactoryJobEventLedger,
    report: FactoryRecoveryReport,
    job_specs: Mapping[str, ResearchJobSpec],
    approved_job_ids: tuple[str, ...] | list[str],
) -> QueueReconstructionPlan:
    """Build an explicit, deterministic plan; never queue or execute jobs."""
    validate_recovery_report(report)
    current_report_id = _report_id_from_ledger(ledger)
    if current_report_id != report.report_id:
        raise ValueError("recovery report does not match the current journal")

    approved = tuple(sorted(set(approved_job_ids)))
    if len(approved) != len(approved_job_ids):
        raise ValueError("approved_job_ids must not contain duplicates")

    summaries = {item["job_id"]: item for item in report.jobs}
    unknown = set(approved) - set(summaries)
    if unknown:
        raise ValueError(f"approved job id is absent from recovery report: {sorted(unknown)[0]}")

    items: list[QueueReconstructionItem] = []
    for job_id in approved:
        summary = summaries[job_id]
        if summary["status"] != "QUEUED_REVIEW_REQUIRED":
            raise ValueError(
                f"job {job_id} is not safe for queue reconstruction: {summary['status']}"
            )
        job = job_specs.get(job_id)
        if job is None:
            raise ValueError(f"verified Job Spec is required for queued job {job_id}")
        job.validate()
        if job.job_id != job_id:
            raise ValueError(f"Job Spec identity mismatch for {job_id}")

        events = ledger.for_job(job_id)
        lifecycle = [
            event for event in events
            if event.event_type in {"QUEUED", "DISPATCHED", "COMPLETED", "FAILED"}
        ]
        if len(lifecycle) != 1 or lifecycle[0].event_type != "QUEUED":
            raise ValueError(f"job {job_id} no longer has a QUEUED-only journal history")
        queued = lifecycle[0]
        if queued.job_fingerprint != job.fingerprint:
            raise ValueError(f"Job Spec fingerprint mismatch for {job_id}")
        if queued.sequence != summary["last_sequence"]:
            raise ValueError(f"queued event sequence mismatch for {job_id}")
        items.append(
            QueueReconstructionItem(
                job_id=job_id,
                job_fingerprint=job.fingerprint,
                original_queue_sequence=queued.sequence,
                job=job,
            )
        )

    identity = {
        "recovery_report_id": report.report_id,
        "approved_job_ids": list(approved),
        "items": [
            {
                "job_id": item.job_id,
                "job_fingerprint": item.job_fingerprint,
                "original_queue_sequence": item.original_queue_sequence,
            }
            for item in items
        ],
        "automatic_requeue_performed": False,
    }
    plan = QueueReconstructionPlan(
        plan_id=hashlib.sha256(_canonical(identity).encode("utf-8")).hexdigest(),
        recovery_report_id=report.report_id,
        approved_job_ids=approved,
        items=tuple(items),
        automatic_requeue_performed=False,
    )
    validate_queue_reconstruction_plan(plan)
    return plan


def _report_id_from_ledger(ledger: FactoryJobEventLedger) -> str:
    from .recovery_report import inspect_factory_recovery
    return inspect_factory_recovery(ledger).report_id


def validate_queue_reconstruction_plan(plan: QueueReconstructionPlan) -> None:
    if len(plan.plan_id) != 64 or any(c not in "0123456789abcdef" for c in plan.plan_id):
        raise ValueError("queue reconstruction plan id must be a lowercase SHA-256 digest")
    if plan.automatic_requeue_performed:
        raise ValueError("queue reconstruction planning must never perform automatic requeue")
    if tuple(item.job_id for item in plan.items) != plan.approved_job_ids:
        raise ValueError("plan items must exactly match sorted approved job ids")
    for item in plan.items:
        item.job.validate()
        if item.job.job_id != item.job_id or item.job.fingerprint != item.job_fingerprint:
            raise ValueError("reconstruction plan contains a mismatched Job Spec")
        if item.original_queue_sequence < 1:
            raise ValueError("original queue sequence must be positive")
    identity = {
        "recovery_report_id": plan.recovery_report_id,
        "approved_job_ids": list(plan.approved_job_ids),
        "items": [
            {
                "job_id": item.job_id,
                "job_fingerprint": item.job_fingerprint,
                "original_queue_sequence": item.original_queue_sequence,
            }
            for item in plan.items
        ],
        "automatic_requeue_performed": False,
    }
    expected_id = hashlib.sha256(_canonical(identity).encode("utf-8")).hexdigest()
    if plan.plan_id != expected_id:
        raise ValueError("queue reconstruction plan fingerprint mismatch")
