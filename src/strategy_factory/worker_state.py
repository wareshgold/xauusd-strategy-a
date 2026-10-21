"""Auditable worker lifecycle state machine for Factory orchestration only."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class WorkerStatus(str, Enum):
    IDLE = "IDLE"
    CLAIMED = "CLAIMED"
    RUNNING = "RUNNING"
    VALIDATING = "VALIDATING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    REPLAY_READY = "REPLAY_READY"


_ALLOWED_TRANSITIONS: dict[WorkerStatus, frozenset[WorkerStatus]] = {
    WorkerStatus.IDLE: frozenset({WorkerStatus.CLAIMED}),
    WorkerStatus.CLAIMED: frozenset({WorkerStatus.RUNNING, WorkerStatus.FAILED}),
    WorkerStatus.RUNNING: frozenset({WorkerStatus.VALIDATING, WorkerStatus.FAILED}),
    WorkerStatus.VALIDATING: frozenset({WorkerStatus.PASSED, WorkerStatus.FAILED}),
    WorkerStatus.PASSED: frozenset(),
    WorkerStatus.FAILED: frozenset({WorkerStatus.REPLAY_READY}),
    WorkerStatus.REPLAY_READY: frozenset({WorkerStatus.CLAIMED}),
}


@dataclass(frozen=True)
class WorkerStateEvent:
    worker_id: str
    job_id: str
    previous_status: str
    status: str
    reason: str | None = None


@dataclass
class WorkerLifecycle:
    """Validate lifecycle transitions and retain an append-only in-memory event trail.

    Persistence/JSONL writing is intentionally left to the existing orchestration
    layer; this class does not execute jobs or grant strategy/trading authority.
    """

    worker_id: str
    job_id: str
    status: WorkerStatus = WorkerStatus.IDLE
    events: list[WorkerStateEvent] = field(default_factory=list)

    def transition(
        self, target: WorkerStatus | str, *, reason: str | None = None
    ) -> WorkerStateEvent:
        try:
            next_status = target if isinstance(target, WorkerStatus) else WorkerStatus(target)
        except ValueError as exc:
            raise ValueError(f"Unknown worker status: {target!r}") from exc

        if next_status not in _ALLOWED_TRANSITIONS[self.status]:
            raise ValueError(
                f"Invalid worker transition: {self.status.value} -> {next_status.value}"
            )
        if next_status in {WorkerStatus.FAILED, WorkerStatus.REPLAY_READY} and not reason:
            raise ValueError(f"reason is required for {next_status.value}")

        event = WorkerStateEvent(
            worker_id=self.worker_id,
            job_id=self.job_id,
            previous_status=self.status.value,
            status=next_status.value,
            reason=reason,
        )
        self.status = next_status
        self.events.append(event)
        return event

    def to_dict(self) -> dict[str, object]:
        return {
            "worker_id": self.worker_id,
            "job_id": self.job_id,
            "status": self.status.value,
            "events": [
                {
                    "worker_id": event.worker_id,
                    "job_id": event.job_id,
                    "previous_status": event.previous_status,
                    "status": event.status,
                    "reason": event.reason,
                }
                for event in self.events
            ],
        }
