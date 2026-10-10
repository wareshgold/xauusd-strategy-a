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
