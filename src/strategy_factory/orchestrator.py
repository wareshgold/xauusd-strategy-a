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
from .job_events import FactoryJobEventLedger
from .handoff import ResearchHandoff, build_research_handoff
from .worker import FactoryWorker, FactoryWorkerFleet
from .research_record import ResearchRecord


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
    events: FactoryJobEventLedger = field(default_factory=FactoryJobEventLedger)

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
        self.events.append(
            event_type="QUEUED",
            job_id=job.job_id,
            job_fingerprint=job.fingerprint,
            station=station,
            phase=phase,
            detail=detail,
        )
        self.fleet.publish()

    def pending(self) -> tuple[QueuedResearchJob, ...]:
        return tuple(self.queue)

    def handoff(
        self,
        *,
        record: ResearchRecord,
        source_station: str,
        destination_station: str,
        detail: str = "Validated research artifact handoff",
    ) -> ResearchHandoff:
        """Explicitly hand one PASS research record to the next declared station.

        Completion alone never implies promotion. The caller must supply an
        immutable PASS ResearchRecord, and the handoff is journaled separately.
        """
        record.validate()
        handoff = build_research_handoff(
            events=self.events,
            job_id=record.run_id,
            source_station=source_station,
            destination_station=destination_station,
            detail=detail,
            record=record,
        )
        self.events.append(
            event_type="HANDOFF_ACCEPTED",
            job_id=record.run_id,
            job_fingerprint=record.run_fingerprint,
            station=destination_station,
            phase=destination_station.upper(),
            detail=detail,
            output_artifact=record.evidence_id,
        )
        self.fleet.publish()
        return handoff

    def run_next(
        self,
        *,
        worker_id: str,
        execute: Callable[[ResearchJobSpec, FactoryWorker], Any],
        heartbeat_every: Callable[[FactoryWorker], None] | None = None,
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
        self.events.append(
            event_type="DISPATCHED",
            job_id=queued.job.job_id,
            job_fingerprint=queued.job.fingerprint,
            worker_id=worker.worker_id,
            station=queued.station,
            phase=queued.phase,
            detail=queued.detail,
        )
        self.fleet.publish()

        try:
            if heartbeat_every is not None:
                heartbeat_every(worker)
                self.fleet.publish()
            result = execute(queued.job, worker)
            if heartbeat_every is not None:
                heartbeat_every(worker)
                self.fleet.publish()
        except Exception as exc:
            worker.fail(str(exc))
            self.events.append(
                event_type="FAILED",
                job_id=queued.job.job_id,
                job_fingerprint=queued.job.fingerprint,
                worker_id=worker.worker_id,
                station=queued.station,
                phase=queued.phase,
                detail=str(exc),
            )
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
        self.events.append(
            event_type="COMPLETED",
            job_id=queued.job.job_id,
            job_fingerprint=queued.job.fingerprint,
            worker_id=worker.worker_id,
            station=queued.station,
            phase=queued.phase,
            detail=detail,
            output_artifact=artifact,
            research_run_fingerprint=(result.get("run_fingerprint") if isinstance(result, dict) else None),
        )
        self.fleet.publish()
        return result


@dataclass(frozen=True)
class RunnerExecutionContext:
    """Immutable dependency bundle for one already-declared research job.

    The caller supplies the test specification, adapter, readiness snapshot,
    and observed dataset hash. The Factory never constructs strategy geometry,
    datasets, optimization ranges, or production decisions.
    """

    spec: Any
    adapter: Any
    snapshot: Any
    observed_content_sha256: str
    evidence_id: str | None = None
    result_revision: str = "RECEIPT_METRICS_V1"
    purpose: str = "HISTORICAL_TEST"


def build_runner_executor(runner: Any, context: RunnerExecutionContext):
    """Build an executor that delegates one queued job to ResearchJobRunner."""

    def execute(job: ResearchJobSpec, worker: FactoryWorker) -> dict[str, Any]:
        result = runner.run(
            job=job,
            spec=context.spec,
            adapter=context.adapter,
            snapshot=context.snapshot,
            observed_content_sha256=context.observed_content_sha256,
            evidence_id=context.evidence_id,
            result_revision=context.result_revision,
            purpose=context.purpose,
        )
        return {
            "output_artifact": result.evidence.evidence_id,
            "detail": (
                "Research run accepted"
                if result.accepted
                else "Research run completed with non-pass gate"
            ),
            "accepted": result.accepted,
            "run_id": result.run.run_id,
            "evidence_id": result.evidence.evidence_id,
            "run_fingerprint": result.run.fingerprint,
        }
    return execute
