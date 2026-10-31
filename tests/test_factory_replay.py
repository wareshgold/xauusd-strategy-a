from __future__ import annotations

import pytest

from strategy_factory.replay import ReplayRequest
from strategy_factory.worker_state import WorkerLifecycle, WorkerStatus


INPUT_SHA = "a" * 64


def failed_worker(worker_id: str = "worker-01", job_id: str = "JOB-REPLAY-01"):
    worker = WorkerLifecycle(worker_id=worker_id, job_id=job_id)
    worker.transition(WorkerStatus.CLAIMED)
    worker.transition(WorkerStatus.FAILED, reason="worker process exited")
    return worker


def test_replay_request_preserves_input_sha_and_is_deterministic():
    first = ReplayRequest.from_failed_job(failed_worker(), input_sha256=INPUT_SHA)
    second = ReplayRequest.from_failed_job(
        failed_worker(worker_id="worker-99"), input_sha256=INPUT_SHA
    )

    assert first.input_sha256 == INPUT_SHA
    assert first.job_id == "JOB-REPLAY-01"
    assert first.replay_id == second.replay_id
    assert first.failed_worker_id == "worker-01"
    assert first.failure_reason == "worker process exited"


def test_replay_identity_changes_when_job_or_input_changes():
    original = ReplayRequest.from_failed_job(failed_worker(), input_sha256=INPUT_SHA)
    changed_input = ReplayRequest.from_failed_job(
        failed_worker(), input_sha256="b" * 64
    )
    changed_job = ReplayRequest.from_failed_job(
        failed_worker(job_id="JOB-OTHER"), input_sha256=INPUT_SHA
    )

    assert original.replay_id != changed_input.replay_id
    assert original.replay_id != changed_job.replay_id


@pytest.mark.parametrize("bad_sha", ["", "abc", "G" * 64, "a" * 63])
def test_replay_rejects_invalid_input_hash(bad_sha):
    with pytest.raises(ValueError, match="input_sha256"):
        ReplayRequest.from_failed_job(failed_worker(), input_sha256=bad_sha)


def test_replay_requires_failed_worker_with_reason():
    worker = WorkerLifecycle(worker_id="worker-02", job_id="JOB-02")
    with pytest.raises(ValueError, match="FAILED or REPLAY_READY"):
        ReplayRequest.from_failed_job(worker, input_sha256=INPUT_SHA)

    worker.transition(WorkerStatus.CLAIMED)
    worker.transition(WorkerStatus.FAILED, reason="retryable failure")
    request = ReplayRequest.from_failed_job(worker, input_sha256=INPUT_SHA)
    assert request.to_dict()["failure_reason"] == "retryable failure"
