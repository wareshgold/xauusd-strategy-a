from __future__ import annotations

import pytest

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.orchestrator import FactoryOrchestrator
from strategy_factory.recovery_report import inspect_factory_recovery
from strategy_factory.test_contract import ExecutionSemantics
from strategy_factory.worker import FactoryWorker, FactoryWorkerFleet


def _job() -> ResearchJobSpec:
    return ResearchJobSpec(
        job_id="JOB-WORKER-START-FAULT",
        strategy_id="SP2L-RESEARCH",
        strategy_revision="revision-frozen-for-test",
        manifest_revision="manifest-test-1",
        test_id="SYNTHETIC-WORKER-START-FAULT",
        dataset_id="synthetic-fixture-only",
        data_revision="fixture-v1",
        dataset_fingerprint="a" * 64,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"fixture": "worker-start-fault"},
    )


def test_worker_start_failure_after_dispatch_cannot_redispatch_queued_job(
    monkeypatch,
) -> None:
    ledger = FactoryJobEventLedger(path=None)
    worker = FactoryWorker(worker_id="W01")
    orchestrator = FactoryOrchestrator(
        fleet=FactoryWorkerFleet(workers=[worker]),
        events=ledger,
    )
    orchestrator.submit(_job(), station="DEV", phase="DEV")
    execute_calls: list[str] = []

    def fail_start(**kwargs) -> None:
        raise OSError("injected worker start failure")

    monkeypatch.setattr(worker, "start", fail_start)

    with pytest.raises(OSError, match="injected worker start failure"):
        orchestrator.run_next(
            worker_id="W01",
            execute=lambda job, current_worker: execute_calls.append(job.job_id),
        )

    assert execute_calls == []
    assert worker.state == "IDLE"
    assert orchestrator.pending() == ()
    assert [event.event_type for event in ledger.entries()] == [
        "QUEUED",
        "DISPATCHED",
    ]

    # A subsequent explicit call in this process cannot dispatch the same job
    # again; the durable DISPATCHED-only history is left for manual review.
    with pytest.raises(RuntimeError, match="queue is empty"):
        orchestrator.run_next(
            worker_id="W01",
            execute=lambda job, current_worker: execute_calls.append(job.job_id),
        )

    report = inspect_factory_recovery(ledger)
    assert report.status_counts == {"INTERRUPTED_REVIEW_REQUIRED": 1}
    assert report.jobs[0]["job_id"] == "JOB-WORKER-START-FAULT"
    assert report.automatic_requeue_performed is False
    assert execute_calls == []
    assert [event.event_type for event in ledger.entries()] == [
        "QUEUED",
        "DISPATCHED",
    ]
