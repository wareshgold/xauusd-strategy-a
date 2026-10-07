from __future__ import annotations

"""Research-only Factory orchestration.

This module owns queue/lifecycle telemetry. It does not define Strategy A
geometry, choose candidates, optimize parameters, or authorize production.
Execution is injected through a callable so the Factory cannot silently
invent research semantics.
"""

from dataclasses import dataclass, field
from typing import Callable, Any

from .jobs import ResearchJobSpec
from .worker import FactoryWorker, FactoryWorkerFleet


@dataclass(frozen=True)
class QueuedResearchJob:
    job: ResearchJobSpec
    station: str
    phase: str
    detail: str = "Queued for research execution"


@dataclass
class FactoryOrchestrator:
    """Deterministic FIFO queue around the existing Factory worker layer."""

    fleet: FactoryWorkerFleet
    queue: list[QueuedResearchJob] = field(default_factory=list)

    def submit(
        self,
        job: ResearchJobSpec,
        *,
        station: str,
        phase: str,
        detail: str = "Queued for research execution",
    ) -> None:
        job.validate()
        self.queue.append(
            QueuedResearchJob(
                job=job,
                station=station,
                phase=phase,
                detail=detail,
            )
        )
        self.fleet.publish()

    def pending(self) -> tuple[QueuedResearchJob, ...]:
        return tuple(self.queue)

    def run_next(
        self,
        *,
        worker_id: str,
        execute: Callable[[ResearchJobSpec, FactoryWorker], Any],
    ) -> Any:
        """Dispatch exactly one queued job to an idle worker.

        The executor owns actual research execution and must return its own
        result/artifact. This orchestrator never interprets strategy rules.
        """
        if not self.queue:
            raise RuntimeError("factory queue is empty")

        worker = self.fleet.get(worker_id)
        if worker.state not in {"IDLE", "COMPLETED", "FAILED"}:
            raise RuntimeError(
                f"worker {worker_id!r} is not available: {worker.state}"
            )

        queued = self.queue.pop(0)
        worker.start(
            job_id=queued.job.job_id,
            job_type=queued.job.test_id,
            station=queued.station,
            phase=queued.phase,
            detail=queued.detail,
        )
        self.fleet.publish()

        try:
            result = execute(queued.job, worker)
        except Exception as exc:
            worker.fail(str(exc))
            self.fleet.publish()
            raise

        artifact = None
        detail = "Research job completed"
        if isinstance(result, dict):
            artifact = result.get("output_artifact")
            detail = str(result.get("detail") or detail)
        elif isinstance(result, str):
            artifact = result

        worker.complete(output_artifact=artifact, detail=detail)
        self.fleet.publish()
        return result
