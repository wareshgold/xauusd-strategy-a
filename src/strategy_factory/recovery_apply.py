"""Explicit, journaled application of a reviewed queue reconstruction plan.

This restores pending in-memory queue entries only. It never dispatches or
executes jobs. A single durable plan marker is written before queue mutation,
so the same plan can safely restore the queue after a process interruption.
"""
from __future__ import annotations

import json
from typing import Any

from .recovery_planner import (
    QueueReconstructionPlan,
    validate_queue_reconstruction_plan,
)
from .recovery_report import inspect_factory_recovery
from .orchestrator import QueuedResearchJob


EVENT_TYPE = "QUEUE_RECONSTRUCTION_APPLIED"
MARKER_PREFIX = "__QUEUE_RECONSTRUCTION__::"


def _canonical(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _marker_payload(plan: QueueReconstructionPlan, *, station: str, phase: str) -> dict[str, Any]:
    return {
        "schema": "FACTORY_QUEUE_RECONSTRUCTION_APPLY_V1",
        "plan_id": plan.plan_id,
        "recovery_report_id": plan.recovery_report_id,
        "station": station,
        "phase": phase,
        "items": [
            {
                "job_id": item.job_id,
                "job_fingerprint": item.job_fingerprint,
                "original_queue_sequence": item.original_queue_sequence,
            }
            for item in plan.items
        ],
    }


def _read_markers(orchestrator: Any) -> list[dict[str, Any]]:
    markers: list[dict[str, Any]] = []
    for event in orchestrator.events.entries():
        if event.event_type != EVENT_TYPE:
            continue
        try:
            payload = json.loads(event.detail or "")
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("queue reconstruction marker is malformed") from exc
        if (
            payload.get("schema") != "FACTORY_QUEUE_RECONSTRUCTION_APPLY_V1"
            or event.job_id != f"{MARKER_PREFIX}{payload.get('plan_id', '')}"
            or event.job_fingerprint != payload.get("plan_id")
        ):
            raise ValueError("queue reconstruction marker identity is invalid")
        markers.append(payload)
    return markers


def apply_queue_reconstruction(
    orchestrator: Any,
    plan: QueueReconstructionPlan,
    *,
    station: str,
    phase: str,
    detail: str = "Explicitly approved queue reconstruction applied; execution not started",
) -> bool:
    """Apply a reviewed plan to the in-memory queue, without dispatching it.

    Returns True if one or more entries were restored; False if already applied
    and present. Journal marker persistence happens before queue mutation.
    """
    validate_queue_reconstruction_plan(plan)
    if not plan.items:
        raise ValueError("empty queue reconstruction plans cannot be applied")
    if not station.strip() or not phase.strip():
        raise ValueError("station and phase are required")

    payload = _marker_payload(plan, station=station, phase=phase)
    markers = _read_markers(orchestrator)

    # Validate the in-memory queue before writing any durable apply marker.
    existing: dict[str, QueuedResearchJob] = {}
    for queued in orchestrator.queue:
        prior = existing.get(queued.job.job_id)
        if prior is not None:
            raise ValueError(f"duplicate job already exists in queue: {queued.job.job_id}")
        existing[queued.job.job_id] = queued

    additions: list[QueuedResearchJob] = []
    for item in plan.items:
        current = existing.get(item.job_id)
        if current is not None:
            if (
                current.job.fingerprint != item.job_fingerprint
                or current.station != station
                or current.phase != phase
            ):
                raise ValueError(f"queued job conflicts with reconstruction plan: {item.job_id}")
            continue
        additions.append(
            QueuedResearchJob(
                job=item.job,
                station=station,
                phase=phase,
                detail=detail,
            )
        )

    same_plan = [item for item in markers if item.get("plan_id") == plan.plan_id]
    if same_plan:
        if len(same_plan) != 1 or same_plan[0] != payload:
            raise ValueError("existing application marker does not match this plan")
    else:
        current_report = inspect_factory_recovery(orchestrator.events)
        if current_report.report_id != plan.recovery_report_id:
            raise ValueError("queue reconstruction plan is stale for the current journal")

        approved_ids = set(plan.approved_job_ids)
        for marker in markers:
            overlap = approved_ids.intersection(
                item.get("job_id") for item in marker.get("items", [])
            )
            if overlap:
                raise ValueError(
                    f"job already belongs to an applied reconstruction plan: {sorted(overlap)[0]}"
                )

        for item in plan.items:
            lifecycle = [
                event for event in orchestrator.events.for_job(item.job_id)
                if event.event_type in {"QUEUED", "DISPATCHED", "COMPLETED", "FAILED"}
            ]
            if (
                len(lifecycle) != 1
                or lifecycle[0].event_type != "QUEUED"
                or lifecycle[0].job_fingerprint != item.job_fingerprint
                or lifecycle[0].sequence != item.original_queue_sequence
            ):
                raise ValueError(
                    f"job {item.job_id} no longer has the planned QUEUED-only journal history"
                )

        marker_job_id = f"{MARKER_PREFIX}{plan.plan_id}"
        orchestrator.events.append(
            event_type=EVENT_TYPE,
            job_id=marker_job_id,
            job_fingerprint=plan.plan_id,
            station=station,
            phase=phase,
            detail=_canonical(payload),
        )

    # The durable marker precedes this single list replacement. If the process
    # stops after journaling, retrying the same plan restores missing entries.
    prior_queue = list(orchestrator.queue)
    orchestrator.queue = [*prior_queue, *additions]
    try:
        orchestrator.fleet.publish()
    except Exception:
        # The marker intentionally remains durable. A retry can safely rebuild
        # the queue from it; do not leave an in-memory partial apply on error.
        orchestrator.queue = prior_queue
        raise
    return bool(additions)
