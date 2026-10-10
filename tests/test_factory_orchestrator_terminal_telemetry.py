from __future__ import annotations

import pytest

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.orchestrator import FactoryOrchestrator
from strategy_factory.test_contract import ExecutionSemantics
from strategy_factory.worker import FactoryWorker, FactoryWorkerFleet


def _job(job_id: str) -> ResearchJobSpec:
    return ResearchJobSpec(
        job_id=job_id,
        strategy_id="SP2L-RESEARCH",
        strategy_revision="revision-frozen-for-test",
        manifest_revision="manifest-test-1",
        test_id="SYNTHETIC-TERMINAL-TELEMETRY",
        dataset_id="synthetic-fixture-only",
        data_revision="fixture-v1",
        dataset_fingerprint="a" * 64,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"fixture": "terminal-telemetry"},
    )


def _orchestrator_with_second_publish_failure(monkeypatch):
    ledger = FactoryJobEventLedger(path=None)
    worker = FactoryWorker(worker_id="W01")
    fleet = FactoryWorkerFleet(workers=[worker])
    orchestrator = FactoryOrchestrator(fleet=fleet, events=ledger)
    publish_calls = 0

    def publish():
        nonlocal publish_calls
        publish_calls += 1
        if publish_calls == 2:
            raise OSError("injected terminal telemetry failure")

    monkeypatch.setattr(fleet, "publish", publish)
    return orchestrator, worker, ledger, lambda: publish_calls


def test_completion_telemetry_failure_does_not_hide_completed_job(monkeypatch):
    orchestrator, worker, ledger, publish_calls = (
        _orchestrator_with_second_publish_failure(monkeypatch)
    )

    result = orchestrator.run_next(
        worker_id="W01",
        execute=lambda job, current_worker: {"output_artifact": "ARTIFACT-1"},
    ) if orchestrator.submit(_job("JOB-COMPLETION-TELEMETRY"), station="DEV", phase="DEV") is None else None

    assert result == {"output_artifact": "ARTIFACT-1"}
    assert publish_calls() == 2
    assert worker.state == "COMPLETED"
    assert [event.event_type for event in ledger.entries()] == [
        "QUEUED",
        "DISPATCHED",
        "COMPLETED",
    ]
    assert orchestrator.telemetry_errors == [
        {
            "job_id": "JOB-COMPLETION-TELEMETRY",
            "worker_id": "W01",
            "operation": "publish_after_completion",
            "error_type": "OSError",
            "error": "injected terminal telemetry failure",
        }
    ]


def test_failure_telemetry_fault_is_recorded_without_replacing_execution_error(
    monkeypatch,
):
    orchestrator, worker, ledger, publish_calls = (
        _orchestrator_with_second_publish_failure(monkeypatch)
    )
    orchestrator.submit(_job("JOB-FAILURE-TELEMETRY"), station="DEV", phase="DEV")

    def fail_execution(job, current_worker):
        raise ValueError("original research execution failure")

    with pytest.raises(ValueError, match="original research execution failure") as caught:
        orchestrator.run_next(worker_id="W01", execute=fail_execution)

    assert publish_calls() == 2
    assert worker.state == "FAILED"
    assert [event.event_type for event in ledger.entries()] == [
        "QUEUED",
        "DISPATCHED",
        "FAILED",
    ]
    assert orchestrator.telemetry_errors == [
        {
            "job_id": "JOB-FAILURE-TELEMETRY",
            "worker_id": "W01",
            "operation": "publish_after_failure",
            "error_type": "OSError",
            "error": "injected terminal telemetry failure",
        }
    ]
    assert any(
        "injected terminal telemetry failure" in note
        for note in getattr(caught.value, "__notes__", [])
    )
