from __future__ import annotations

import pytest

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.orchestrator import FactoryOrchestrator
from strategy_factory.recovery_apply import apply_queue_reconstruction
from strategy_factory.recovery_planner import plan_queue_reconstruction
from strategy_factory.recovery_report import inspect_factory_recovery
from strategy_factory.test_contract import ExecutionSemantics
from strategy_factory.worker import FactoryWorker, FactoryWorkerFleet


def make_job(job_id: str = "JOB-QUEUED") -> ResearchJobSpec:
    return ResearchJobSpec(
        job_id=job_id,
        strategy_id="SP2L-A",
        strategy_revision="REV-1",
        manifest_revision="MANIFEST-1",
        test_id="TEST-1",
        dataset_id="DATA-1",
        data_revision="DATA-REV-1",
        dataset_fingerprint="a" * 64,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"canonical": False},
    )


def make_orchestrator(ledger: FactoryJobEventLedger) -> FactoryOrchestrator:
    return FactoryOrchestrator(
        fleet=FactoryWorkerFleet(workers=[FactoryWorker(worker_id="W01")]),
        events=ledger,
    )


def make_plan(ledger: FactoryJobEventLedger, job: ResearchJobSpec):
    return plan_queue_reconstruction(
        ledger=ledger,
        report=inspect_factory_recovery(ledger),
        job_specs={job.job_id: job},
        approved_job_ids=[job.job_id],
    )


def journal_queued(ledger: FactoryJobEventLedger, job: ResearchJobSpec) -> None:
    ledger.append(
        event_type="QUEUED",
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
        station="DEV",
        phase="DEV",
    )


def test_apply_reconstruction_is_explicit_and_does_not_dispatch(tmp_path):
    ledger = FactoryJobEventLedger(tmp_path / "events.jsonl")
    job = make_job()
    journal_queued(ledger, job)
    plan = make_plan(ledger, job)
    orchestrator = make_orchestrator(ledger)

    assert apply_queue_reconstruction(
        orchestrator, plan, station="DEV", phase="RECOVERY"
    ) is True
    assert len(orchestrator.pending()) == 1
    assert orchestrator.pending()[0].job == job
    assert not any(
        event.event_type == "DISPATCHED"
        for event in ledger.for_job(job.job_id)
    )
    assert sum(
        event.event_type == "QUEUE_RECONSTRUCTION_APPLIED"
        for event in ledger.entries()
    ) == 1


def test_apply_same_plan_is_idempotent(tmp_path):
    ledger = FactoryJobEventLedger(tmp_path / "events.jsonl")
    job = make_job()
    journal_queued(ledger, job)
    plan = make_plan(ledger, job)
    orchestrator = make_orchestrator(ledger)

    assert apply_queue_reconstruction(
        orchestrator, plan, station="DEV", phase="RECOVERY"
    ) is True
    count = len(ledger.entries())

    assert apply_queue_reconstruction(
        orchestrator, plan, station="DEV", phase="RECOVERY"
    ) is False
    assert len(orchestrator.pending()) == 1
    assert len(ledger.entries()) == count


def test_same_plan_can_restore_memory_queue_after_restart(tmp_path):
    path = tmp_path / "events.jsonl"
    ledger = FactoryJobEventLedger(path)
    job = make_job()
    journal_queued(ledger, job)
    plan = make_plan(ledger, job)
    first = make_orchestrator(ledger)

    assert apply_queue_reconstruction(
        first, plan, station="DEV", phase="RECOVERY"
    ) is True

    restarted_ledger = FactoryJobEventLedger(path)
    restarted = make_orchestrator(restarted_ledger)
    assert restarted.pending() == ()
    assert apply_queue_reconstruction(
        restarted, plan, station="DEV", phase="RECOVERY"
    ) is True
    assert [item.job.job_id for item in restarted.pending()] == [job.job_id]
    assert sum(
        event.event_type == "QUEUE_RECONSTRUCTION_APPLIED"
        for event in restarted_ledger.entries()
    ) == 1


def test_apply_rejects_stale_plan(tmp_path):
    ledger = FactoryJobEventLedger(tmp_path / "events.jsonl")
    job = make_job()
    journal_queued(ledger, job)
    plan = make_plan(ledger, job)
    ledger.append(
        event_type="OPERATOR_NOTE",
        job_id="NOTE-1",
        job_fingerprint="b" * 64,
        station="FACTORY",
        phase="RECOVERY",
        detail="journal changed after planning",
    )
    orchestrator = make_orchestrator(ledger)

    with pytest.raises(ValueError, match="stale"):
        apply_queue_reconstruction(
            orchestrator, plan, station="DEV", phase="RECOVERY"
        )
    assert orchestrator.pending() == ()
    assert not any(
        event.event_type == "QUEUE_RECONSTRUCTION_APPLIED"
        for event in ledger.entries()
    )


def test_apply_rejects_queue_conflict_before_writing_marker(tmp_path):
    ledger = FactoryJobEventLedger(tmp_path / "events.jsonl")
    job = make_job()
    journal_queued(ledger, job)
    plan = make_plan(ledger, job)
    orchestrator = make_orchestrator(ledger)
    conflicting = make_job("JOB-QUEUED")
    from strategy_factory.orchestrator import QueuedResearchJob
    orchestrator.queue.append(
        QueuedResearchJob(
            job=conflicting,
            station="OTHER",
            phase="OTHER",
            detail="conflicting pre-existing entry",
        )
    )

    with pytest.raises(ValueError, match="conflicts"):
        apply_queue_reconstruction(
            orchestrator, plan, station="DEV", phase="RECOVERY"
        )
    assert len(ledger.entries()) == 1
    assert not any(
        event.event_type == "QUEUE_RECONSTRUCTION_APPLIED"
        for event in ledger.entries()
    )


def test_reconstruction_marker_does_not_appear_as_a_recoverable_job(tmp_path):
    ledger = FactoryJobEventLedger(tmp_path / "events.jsonl")
    job = make_job()
    journal_queued(ledger, job)
    plan = make_plan(ledger, job)
    orchestrator = make_orchestrator(ledger)

    apply_queue_reconstruction(orchestrator, plan, station="DEV", phase="RECOVERY")
    report = inspect_factory_recovery(ledger)

    assert [item["job_id"] for item in report.jobs] == [job.job_id]
    assert report.status_counts == {"QUEUED_REVIEW_REQUIRED": 1}



def test_publish_failure_rolls_back_memory_and_retry_restores_queue(tmp_path, monkeypatch):
    path = tmp_path / "events.jsonl"
    ledger = FactoryJobEventLedger(path)
    job = make_job()
    journal_queued(ledger, job)
    plan = make_plan(ledger, job)
    orchestrator = make_orchestrator(ledger)

    original_publish = orchestrator.fleet.publish
    calls = {"count": 0}

    def fail_once():
        calls["count"] += 1
        if calls["count"] == 1:
            raise OSError("simulated telemetry publish failure")
        return original_publish()

    monkeypatch.setattr(orchestrator.fleet, "publish", fail_once)
    with pytest.raises(OSError, match="simulated telemetry"):
        apply_queue_reconstruction(
            orchestrator, plan, station="DEV", phase="RECOVERY"
        )

    assert orchestrator.pending() == ()
    assert sum(
        event.event_type == "QUEUE_RECONSTRUCTION_APPLIED"
        for event in ledger.entries()
    ) == 1

    assert apply_queue_reconstruction(
        orchestrator, plan, station="DEV", phase="RECOVERY"
    ) is True
    assert [item.job.job_id for item in orchestrator.pending()] == [job.job_id]
    assert sum(
        event.event_type == "QUEUE_RECONSTRUCTION_APPLIED"
        for event in ledger.entries()
    ) == 1


def test_applied_job_runs_only_after_explicit_run_next(tmp_path):
    ledger = FactoryJobEventLedger(tmp_path / "events.jsonl")
    job = make_job()
    journal_queued(ledger, job)
    plan = make_plan(ledger, job)
    orchestrator = make_orchestrator(ledger)
    executions = []

    apply_queue_reconstruction(
        orchestrator, plan, station="DEV", phase="RECOVERY"
    )
    assert executions == []
    assert not any(
        event.event_type == "DISPATCHED"
        for event in ledger.for_job(job.job_id)
    )

    result = orchestrator.run_next(
        worker_id="W01",
        execute=lambda spec, worker: executions.append(spec.job_id) or {"detail": "fixture"},
    )

    assert result == {"detail": "fixture"}
    assert executions == [job.job_id]
    assert [event.event_type for event in ledger.for_job(job.job_id)] == [
        "QUEUED", "DISPATCHED", "COMPLETED"
    ]



def test_restart_after_durable_marker_restores_queue_without_dispatch(tmp_path, monkeypatch):
    path = tmp_path / "events.jsonl"
    ledger = FactoryJobEventLedger(path)
    job = make_job()
    journal_queued(ledger, job)
    plan = make_plan(ledger, job)
    first_process = make_orchestrator(ledger)

    def crash_after_marker():
        raise OSError("simulated crash after durable marker")

    monkeypatch.setattr(first_process.fleet, "publish", crash_after_marker)
    with pytest.raises(OSError, match="after durable marker"):
        apply_queue_reconstruction(
            first_process, plan, station="DEV", phase="RECOVERY"
        )

    # The marker is durable, but the failed process has no in-memory queue entry.
    assert first_process.pending() == ()
    assert sum(
        event.event_type == "QUEUE_RECONSTRUCTION_APPLIED"
        for event in ledger.entries()
    ) == 1

    # A fresh process loads only the journal; replaying the same approved plan
    # restores the missing queue entry without creating another marker or dispatch.
    restarted_ledger = FactoryJobEventLedger(path)
    restarted = make_orchestrator(restarted_ledger)
    assert restarted.pending() == ()
    assert apply_queue_reconstruction(
        restarted, plan, station="DEV", phase="RECOVERY"
    ) is True

    assert [item.job.job_id for item in restarted.pending()] == [job.job_id]
    assert sum(
        event.event_type == "QUEUE_RECONSTRUCTION_APPLIED"
        for event in restarted_ledger.entries()
    ) == 1
    assert not any(
        event.event_type == "DISPATCHED"
        for event in restarted_ledger.for_job(job.job_id)
    )
    report = inspect_factory_recovery(restarted_ledger)
    assert report.status_counts == {"QUEUED_REVIEW_REQUIRED": 1}
    assert report.automatic_requeue_performed is False
