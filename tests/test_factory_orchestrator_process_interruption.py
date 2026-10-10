from __future__ import annotations

from pathlib import Path

import pytest

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.orchestrator import FactoryOrchestrator
from strategy_factory.recovery_report import inspect_factory_recovery
from strategy_factory.test_contract import ExecutionSemantics
from strategy_factory.worker import FactoryWorker, FactoryWorkerFleet


def _job() -> ResearchJobSpec:
    return ResearchJobSpec(
        job_id="JOB-PROCESS-INTERRUPTION",
        strategy_id="SP2L-RESEARCH",
        strategy_revision="revision-frozen-for-test",
        manifest_revision="manifest-test-1",
        test_id="SYNTHETIC-PROCESS-INTERRUPTION",
        dataset_id="synthetic-fixture-only",
        data_revision="fixture-v1",
        dataset_fingerprint="a" * 64,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"fixture": "process-interruption"},
    )


def test_process_interruption_after_dispatch_is_reviewed_not_retried(
    tmp_path: Path,
) -> None:
    journal_path = tmp_path / "factory-job-events.jsonl"
    ledger = FactoryJobEventLedger(path=journal_path)
    worker = FactoryWorker(worker_id="W01")
    orchestrator = FactoryOrchestrator(
        fleet=FactoryWorkerFleet(workers=[worker]),
        events=ledger,
    )
    orchestrator.submit(_job(), station="DEV", phase="DEV")

    execution_calls: list[str] = []

    def interrupted_execution(job: ResearchJobSpec, current_worker: FactoryWorker):
        execution_calls.append(job.job_id)
        # BaseException models process-level interruption: run_next's normal
        # Exception handler must not fabricate a FAILED terminal event.
        raise SystemExit("synthetic process interruption")

    with pytest.raises(SystemExit, match="synthetic process interruption"):
        orchestrator.run_next(
            worker_id="W01",
            execute=interrupted_execution,
        )

    assert execution_calls == ["JOB-PROCESS-INTERRUPTION"]
    assert worker.state == "RUNNING"
    assert orchestrator.pending() == ()
    assert [event.event_type for event in ledger.entries()] == [
        "QUEUED",
        "DISPATCHED",
    ]

    # Re-load only the durable journal, as a restarted process would. Recovery
    # inspection must report an interrupted job and must not queue or execute it.
    before_bytes = journal_path.read_bytes()
    restarted_ledger = FactoryJobEventLedger(path=journal_path)
    report = inspect_factory_recovery(restarted_ledger)

    assert report.status_counts == {"INTERRUPTED_REVIEW_REQUIRED": 1}
    assert report.jobs[0]["job_id"] == "JOB-PROCESS-INTERRUPTION"
    assert report.jobs[0]["status"] == "INTERRUPTED_REVIEW_REQUIRED"
    assert report.automatic_requeue_performed is False
    assert journal_path.read_bytes() == before_bytes
    assert [event.event_type for event in restarted_ledger.entries()] == [
        "QUEUED",
        "DISPATCHED",
    ]
