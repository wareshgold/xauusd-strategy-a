from __future__ import annotations

"""Telemetry-backed Factory worker lifecycle.

Workers observe and report research execution; they do not define strategy
geometry, choose candidates, or authorize production decisions.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Any

from .telemetry import publish_workers, utc_now


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class FactoryWorker:
    worker_id: str
    job_id: str | None = None
    job_type: str | None = None
    station: str | None = None
    phase: str | None = None
    state: str = "IDLE"
    progress: float = 0.0
    detail: str | None = None
    started_utc: str | None = None
    heartbeat_utc: str | None = None
    output_artifact: str | None = None
    error: str | None = None

    def _touch(self) -> None:
        self.heartbeat_utc = _now()

    def start(self, *, job_id: str, job_type: str, station: str, phase: str | None = None, detail: str | None = None) -> None:
        self.job_id = job_id
        self.job_type = job_type
        self.station = station
        self.phase = phase
        self.state = "RUNNING"
        self.progress = 0.0
        self.detail = detail
        self.started_utc = _now()
        self.output_artifact = None
        self.error = None
        self._touch()

    def heartbeat(self, *, progress: float | None = None, detail: str | None = None) -> None:
        self.state = "HEARTBEAT"
        if progress is not None:
            self.progress = max(0.0, min(100.0, float(progress)))
        if detail is not None:
            self.detail = detail
        self._touch()

    def complete(self, *, output_artifact: str | None = None, detail: str | None = None) -> None:
        self.state = "COMPLETED"
        self.progress = 100.0
        self.output_artifact = output_artifact
        if detail is not None:
            self.detail = detail
        self._touch()

    def fail(self, error: str, *, detail: str | None = None) -> None:
        self.state = "FAILED"
        self.error = str(error)
        if detail is not None:
            self.detail = detail
        self._touch()

    def idle(self) -> None:
        self.state = "IDLE"
        self.job_id = None
        self.job_type = None
        self.station = None
        self.phase = None
        self.progress = 0.0
        self.detail = None
        self.started_utc = None
        self.output_artifact = None
        self.error = None
        self._touch()

    def as_dict(self) -> dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "job_id": self.job_id,
            "job_type": self.job_type,
            "station": self.station,
            "phase": self.phase,
            "state": self.state,
            "started_utc": self.started_utc,
            "heartbeat_utc": self.heartbeat_utc or utc_now(),
            "progress": self.progress,
            "detail": self.detail,
            "output_artifact": self.output_artifact,
            "error": self.error,
        }


@dataclass
class FactoryWorkerFleet:
    workers: list[FactoryWorker] = field(default_factory=list)

    def publish(self) -> None:
        publish_workers([worker.as_dict() for worker in self.workers])

    def get(self, worker_id: str) -> FactoryWorker:
        for worker in self.workers:
            if worker.worker_id == worker_id:
                return worker
        raise KeyError(f"unknown factory worker: {worker_id}")

    def run_one(
        self,
        worker_id: str,
        *,
        job_id: str,
        job_type: str,
        station: str,
        execute: Callable[[], Any],
        phase: str | None = None,
        detail: str | None = None,
    ) -> Any:
        worker = self.get(worker_id)
        worker.start(job_id=job_id, job_type=job_type, station=station, phase=phase, detail=detail)
        self.publish()
        try:
            result = execute()
        except Exception as exc:
            worker.fail(str(exc))
            self.publish()
            raise
        worker.complete(detail="Research job completed")
        self.publish()
        return result
