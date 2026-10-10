from __future__ import annotations

from dataclasses import replace

import pytest

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.orchestrator import FactoryOrchestrator
from strategy_factory.replay_planner import plan_failed_job_replay
from strategy_factory.test_contract import (
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
)
from strategy_factory.worker import FactoryWorker, FactoryWorkerFleet
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
        spec, manifest_revision="MANIFEST-R1",
        dataset_fingerprint="a" * 64, job_id="JOB-1",
    )


def make_orchestrator() -> FactoryOrchestrator:
    return FactoryOrchestrator(
        fleet=FactoryWorkerFleet(workers=[FactoryWorker(worker_id="worker-1")]),
        events=FactoryJobEventLedger(path=None),
    )


def make_plan(job: ResearchJobSpec):
    lifecycle = WorkerLifecycle(worker_id="worker-1", job_id=job.job_id)
    lifecycle.transition(WorkerStatus.CLAIMED)
    lifecycle.transition(WorkerStatus.FAILED, reason="process exited")
    return plan_failed_job_replay(job, lifecycle, input_sha256=job.fingerprint)


def journal_failed(orchestrator: FactoryOrchestrator, job: ResearchJobSpec):
    orchestrator.events.append(
        event_type="QUEUED", job_id=job.job_id,
        job_fingerprint=job.fingerprint, station="DEV", phase="DEV",
    )
    orchestrator.events.append(
        event_type="DISPATCHED", job_id=job.job_id,
        job_fingerprint=job.fingerprint, worker_id="worker-1",
        station="DEV", phase="DEV",
    )
    orchestrator.events.append(
        event_type="FAILED", job_id=job.job_id,
        job_fingerprint=job.fingerprint, worker_id="worker-1",
        station="DEV", phase="DEV", detail="process exited",
    )


def test_submit_replay_queues_only_after_matching_failure_is_journaled():
    job = make_job()
    orchestrator = make_orchestrator()
    journal_failed(orchestrator, job)
    plan = make_plan(job)

    orchestrator.submit_replay(plan, station="DEV", phase="REPLAY")

    assert len(orchestrator.pending()) == 1
    queued = orchestrator.pending()[0]
    assert queued.job.job_id == plan.replay_job.job_id
    assert queued.job.fingerprint == plan.replay_job.fingerprint
    assert orchestrator.events.for_job(queued.job.job_id)[0].event_type == "QUEUED"
    assert not any(e.event_type == "DISPATCHED" for e in orchestrator.events.for_job(queued.job.job_id))


def test_submit_replay_rejects_unjournaled_failure():
    job = make_job()
    orchestrator = make_orchestrator()

    with pytest.raises(ValueError, match="journaled FAILED"):
        orchestrator.submit_replay(
            make_plan(job), station="DEV", phase="REPLAY"
        )

    assert orchestrator.pending() == ()


def test_submit_replay_rejects_original_fingerprint_mismatch():
    job = make_job()
    orchestrator = make_orchestrator()
    journal_failed(orchestrator, job)
    plan = replace(make_plan(job), original_job_fingerprint="b" * 64)

    with pytest.raises(ValueError, match="fingerprint"):
        orchestrator.submit_replay(plan, station="DEV", phase="REPLAY")

    assert orchestrator.pending() == ()


def test_submit_replay_rejects_failure_from_different_worker():
    job = make_job()
    orchestrator = make_orchestrator()
    journal_failed(orchestrator, job)
    plan = make_plan(job)
    wrong_worker_request = replace(plan.request, failed_worker_id="worker-other")
    plan = replace(plan, request=wrong_worker_request)

    with pytest.raises(ValueError, match="failed worker"):
        orchestrator.submit_replay(plan, station="DEV", phase="REPLAY")

    assert orchestrator.pending() == ()
