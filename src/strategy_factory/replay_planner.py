"""Explicit replay planning for failed research jobs.

Planning is deliberately separate from queue submission and execution. A caller
must review and submit the returned replay job explicitly; this module never
runs or automatically retries work.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .jobs import ResearchJobSpec
from .replay import ReplayRequest
from .worker_state import WorkerLifecycle, WorkerStatus


@dataclass(frozen=True)
class FailedJobReplayPlan:
    request: ReplayRequest
    original_job_fingerprint: str
    replay_job: ResearchJobSpec

    def to_dict(self) -> dict[str, object]:
        return {
            "request": self.request.to_dict(),
            "original_job_fingerprint": self.original_job_fingerprint,
            "replay_job": self.replay_job.as_dict(),
            "replay_job_fingerprint": self.replay_job.fingerprint,
            "automatic_execution": False,
        }


def plan_failed_job_replay(
    job: ResearchJobSpec,
    worker: WorkerLifecycle,
    *,
    input_sha256: str,
) -> FailedJobReplayPlan:
    """Create a replay plan only when failed worker and original job agree.

    The input hash is caller-supplied and must identify the exact immutable
    input being replayed. The planner does not infer or regenerate inputs.
    """
    job.validate()
    if worker.job_id != job.job_id:
        raise ValueError("failed worker job_id does not match the supplied original job")
    if worker.status not in {WorkerStatus.FAILED, WorkerStatus.REPLAY_READY}:
        raise ValueError("replay planning requires a failed or replay-ready worker")

    request = ReplayRequest.from_failed_job(worker, input_sha256=input_sha256)
    replay_job_id = f"{job.job_id}::replay::{request.replay_id[:16]}"
    replay_job = replace(job, job_id=replay_job_id)
    replay_job.validate()

    if replay_job.fingerprint == job.fingerprint:
        raise ValueError("replay job must have a distinct job fingerprint")

    return FailedJobReplayPlan(
        request=request,
        original_job_fingerprint=job.fingerprint,
        replay_job=replay_job,
    )
