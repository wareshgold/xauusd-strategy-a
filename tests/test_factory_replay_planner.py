from __future__ import annotations

import pytest

from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.replay_planner import plan_failed_job_replay
from strategy_factory.test_contract import (
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
)
from strategy_factory.worker_state import WorkerLifecycle, WorkerStatus


def make_job() -> ResearchJobSpec:
    dataset = TestDataset(
        "D1", DatasetRole.DEVELOPMENT, "DATA-R1",
        "2026-01-01", "2026-02-01", "FIXTURE",
    )
    spec = HistoricalTestSpec(
        "TEST-1", "SP2L-A", "STRAT-R1", dataset,
        ExecutionSemantics.TICK_FEASIBLE,
        parameters={"tp_r": 2, "trail": 2},
    )
    return ResearchJobSpec.from_test_spec(
        spec,
        manifest_revision="MANIFEST-R1",
        dataset_fingerprint="a" * 64,
        job_id="JOB-1",
    )


def failed_worker(job_id: str = "JOB-1") -> WorkerLifecycle:
    worker = WorkerLifecycle(worker_id="worker-1", job_id=job_id)
    worker.transition(WorkerStatus.CLAIMED)
    worker.transition(WorkerStatus.FAILED, reason="process exited")
    return worker


def test_replay_plan_keeps_original_inputs_and_creates_distinct_job_identity():
    job = make_job()
    plan = plan_failed_job_replay(
        job, failed_worker(), input_sha256=job.fingerprint
    )

    assert plan.request.job_id == job.job_id
    assert plan.request.input_sha256 == job.fingerprint
    assert plan.original_job_fingerprint == job.fingerprint
    assert plan.replay_job.job_id.startswith("JOB-1::replay::")
    assert plan.replay_job.fingerprint != job.fingerprint
    assert plan.replay_job.as_dict()["parameters"] == job.as_dict()["parameters"]
    assert plan.to_dict()["automatic_execution"] is False


def test_replay_plan_is_deterministic():
    job = make_job()
    first = plan_failed_job_replay(job, failed_worker(), input_sha256=job.fingerprint)
    second = plan_failed_job_replay(job, failed_worker(), input_sha256=job.fingerprint)

    assert first.request.replay_id == second.request.replay_id
    assert first.replay_job.as_dict() == second.replay_job.as_dict()


def test_replay_plan_rejects_worker_for_different_job():
    with pytest.raises(ValueError, match="does not match"):
        plan_failed_job_replay(
            make_job(), failed_worker("OTHER-JOB"), input_sha256="a" * 64
        )


def test_replay_plan_rejects_non_failed_worker():
    worker = WorkerLifecycle(worker_id="worker-1", job_id="JOB-1")
    with pytest.raises(ValueError, match="failed or replay-ready"):
        plan_failed_job_replay(make_job(), worker, input_sha256="a" * 64)
