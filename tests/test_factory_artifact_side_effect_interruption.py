from __future__ import annotations

from pathlib import Path

import pytest

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.orchestrator import FactoryOrchestrator
from strategy_factory.recovery_planner import plan_queue_reconstruction
from strategy_factory.recovery_report import inspect_factory_recovery
from strategy_factory.test_contract import ExecutionSemantics
from strategy_factory.worker import FactoryWorker, FactoryWorkerFleet


def _job() -> ResearchJobSpec:
    return ResearchJobSpec(
        job_id="JOB-ARTIFACT-SIDE-EFFECT",
        strategy_id="SP2L-RESEARCH",
        strategy_revision="frozen-synthetic-fixture",
        manifest_revision="manifest-synthetic-fixture",
        test_id="SYNTHETIC-ARTIFACT-INTERRUPTION",
        dataset_id="synthetic-only",
        data_revision="fixture-v1",
        dataset_fingerprint="c" * 64,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"fixture": "artifact-written-before-process-interruption"},
    )


def test_existing_artifact_with_dispatched_only_journal_is_never_requeued(
    tmp_path: Path,
) -> None:
    journal_path = tmp_path / "events.jsonl"
    artifact_path = tmp_path / "synthetic-result.json"
    job = _job()
    ledger = FactoryJobEventLedger(path=journal_path)
    worker = FactoryWorker(worker_id="W01")
    orchestrator = FactoryOrchestrator(
        fleet=FactoryWorkerFleet(workers=[worker]), events=ledger
    )
    orchestrator.submit(job, station="DEV", phase="DEV")
    calls: list[str] = []

    def executor_writes_artifact_then_process_stops(spec, current_worker):
        calls.append(spec.job_id)
        artifact_path.write_text(
            '{"fixture":"synthetic","job_id":"JOB-ARTIFACT-SIDE-EFFECT"}',
            encoding="utf-8",
        )
        # Model a process interruption after an external side effect but before
        # the executor returns a receipt that could be journaled as COMPLETED.
        raise SystemExit("synthetic stop after artifact persistence")

    with pytest.raises(SystemExit, match="after artifact persistence"):
        orchestrator.run_next(
            worker_id="W01", execute=executor_writes_artifact_then_process_stops
        )

    assert calls == ["JOB-ARTIFACT-SIDE-EFFECT"]
    assert artifact_path.is_file()
    artifact_bytes = artifact_path.read_bytes()
    assert [event.event_type for event in ledger.entries()] == ["QUEUED", "DISPATCHED"]

    # Restart using only the durable journal. The artifact's existence does
    # not establish a valid completion receipt; the interrupted job remains
    # ambiguous and must be reconciled, not replayed.
    restarted_ledger = FactoryJobEventLedger(path=journal_path)
    report = inspect_factory_recovery(restarted_ledger)
    assert report.status_counts == {"INTERRUPTED_REVIEW_REQUIRED": 1}
    assert report.jobs[0]["status"] == "INTERRUPTED_REVIEW_REQUIRED"
    assert report.automatic_requeue_performed is False

    with pytest.raises(ValueError, match="not safe for queue reconstruction"):
        plan_queue_reconstruction(
            ledger=restarted_ledger,
            report=report,
            job_specs={job.job_id: job},
            approved_job_ids=[job.job_id],
        )

    assert artifact_path.read_bytes() == artifact_bytes
    assert [event.event_type for event in restarted_ledger.entries()] == [
        "QUEUED", "DISPATCHED"
    ]
    assert calls == ["JOB-ARTIFACT-SIDE-EFFECT"]
