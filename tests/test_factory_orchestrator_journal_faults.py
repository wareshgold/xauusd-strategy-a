from __future__ import annotations

import pytest

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.orchestrator import FactoryOrchestrator
from strategy_factory.test_contract import ExecutionSemantics
from strategy_factory.worker import FactoryWorker, FactoryWorkerFleet
from strategy_factory.worker_journal_audit import inspect_worker_journal_consistency


def _job() -> ResearchJobSpec:
    return ResearchJobSpec(
        job_id="JOB-COMPLETION-JOURNAL-FAULT",
        strategy_id="SP2L-RESEARCH",
        strategy_revision="revision-frozen-for-test",
        manifest_revision="manifest-test-1",
        test_id="SYNTHETIC-FAULT-INJECTION",
        dataset_id="synthetic-fixture-only",
        data_revision="fixture-v1",
        dataset_fingerprint="a" * 64,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"fixture": "journal-completion-failure"},
    )


def test_completed_event_append_failure_is_detectable_without_auto_repair(monkeypatch):
    ledger = FactoryJobEventLedger(path=None)
    worker = FactoryWorker(worker_id="W01")
    orchestrator = FactoryOrchestrator(
        fleet=FactoryWorkerFleet(workers=[worker]),
        events=ledger,
    )
    orchestrator.submit(_job(), station="DEV", phase="DEV")
    original_append = ledger.append
    execution_calls = []

    def fail_only_completion_append(**kwargs):
        if kwargs.get("event_type") == "COMPLETED":
            raise OSError("injected completion journal failure")
        return original_append(**kwargs)

    monkeypatch.setattr(ledger, "append", fail_only_completion_append)

    with pytest.raises(OSError, match="injected completion journal failure"):
        orchestrator.run_next(
            worker_id="W01",
            execute=lambda job, current_worker: execution_calls.append(job.job_id)
            or {"output_artifact": "synthetic-result"},
        )

    assert execution_calls == ["JOB-COMPLETION-JOURNAL-FAULT"]
    assert worker.state == "COMPLETED"
    assert orchestrator.pending() == ()
    assert [event.event_type for event in ledger.entries()] == [
        "QUEUED",
        "DISPATCHED",
    ]

    before_events = ledger.entries()
    before_worker = worker.__dict__.copy()
    report = inspect_worker_journal_consistency(ledger, [worker])
    codes = {finding["code"] for finding in report["findings"]}

    assert report["status"] == "REVIEW_REQUIRED"
    assert "TERMINAL_WORKER_JOURNAL_MISMATCH" in codes
    assert "DISPATCHED_JOB_NOT_ACTIVE_ON_WORKER" in codes
    assert report["automatic_action_performed"] is False
    assert ledger.entries() == before_events
    assert worker.__dict__.copy() == before_worker


def test_failed_event_append_failure_preserves_original_execution_error(monkeypatch):
    ledger = FactoryJobEventLedger(path=None)
    worker = FactoryWorker(worker_id="W01")
    orchestrator = FactoryOrchestrator(
        fleet=FactoryWorkerFleet(workers=[worker]),
        events=ledger,
    )
    orchestrator.submit(
        _job(),
        station="DEV",
        phase="DEV",
        detail="failure-journal-fault",
    )
    original_append = ledger.append

    def fail_only_failure_append(**kwargs):
        if kwargs.get("event_type") == "FAILED":
            raise OSError("injected FAILED journal failure")
        return original_append(**kwargs)

    def fail_execution(job, current_worker):
        raise ValueError("original research executor failure")

    monkeypatch.setattr(ledger, "append", fail_only_failure_append)

    with pytest.raises(ValueError, match="original research executor failure") as caught:
        orchestrator.run_next(
            worker_id="W01",
            execute=fail_execution,
        )

    assert any(
        "injected FAILED journal failure" in note
        for note in getattr(caught.value, "__notes__", [])
    )
    assert worker.state == "FAILED"
    assert worker.error == "original research executor failure"
    assert orchestrator.pending() == ()
    assert [event.event_type for event in ledger.entries()] == [
        "QUEUED",
        "DISPATCHED",
    ]

    before_events = ledger.entries()
    before_worker = worker.__dict__.copy()
    report = inspect_worker_journal_consistency(ledger, [worker])
    codes = {finding["code"] for finding in report["findings"]}

    assert report["status"] == "REVIEW_REQUIRED"
    assert "TERMINAL_WORKER_JOURNAL_MISMATCH" in codes
    assert "DISPATCHED_JOB_NOT_ACTIVE_ON_WORKER" in codes
    assert report["automatic_action_performed"] is False
    assert ledger.entries() == before_events
    assert worker.__dict__.copy() == before_worker


def test_failure_telemetry_publish_failure_preserves_original_execution_error(monkeypatch):
    ledger = FactoryJobEventLedger(path=None)
    worker = FactoryWorker(worker_id="W01")
    fleet = FactoryWorkerFleet(workers=[worker])
    orchestrator = FactoryOrchestrator(fleet=fleet, events=ledger)
    orchestrator.submit(
        _job(),
        station="DEV",
        phase="DEV",
        detail="failure-telemetry-fault",
    )

    def fail_publish():
        raise OSError("injected worker telemetry publish failure")

    def fail_execution(job, current_worker):
        # Let run_next's initial worker-state publication succeed. Inject the
        # telemetry fault only after execution has started, so the exception
        # handler's secondary publish is the operation under test.
        monkeypatch.setattr(fleet, "publish", fail_publish)
        raise ValueError("original research executor failure")

    with pytest.raises(ValueError, match="original research executor failure") as caught:
        orchestrator.run_next(worker_id="W01", execute=fail_execution)

    assert any(
        "injected worker telemetry publish failure" in note
        for note in getattr(caught.value, "__notes__", [])
    )
    assert worker.state == "FAILED"
    assert worker.error == "original research executor failure"
    assert orchestrator.pending() == ()
    assert [event.event_type for event in ledger.entries()] == [
        "QUEUED",
        "DISPATCHED",
        "FAILED",
    ]
    report = inspect_worker_journal_consistency(ledger, [worker])
    assert report["status"] == "CONSISTENT"
    assert report["automatic_action_performed"] is False
