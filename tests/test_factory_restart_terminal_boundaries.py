from __future__ import annotations

from pathlib import Path

import pytest

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.orchestrator import FactoryOrchestrator
from strategy_factory.recovery_report import inspect_factory_recovery
from strategy_factory.test_contract import ExecutionSemantics
from strategy_factory.worker import FactoryWorker, FactoryWorkerFleet


def make_job() -> ResearchJobSpec:
    return ResearchJobSpec(
        job_id="JOB-RESTART-BOUNDARY",
        strategy_id="SP2L-RESEARCH",
        strategy_revision="frozen-fixture",
        manifest_revision="manifest-fixture",
        test_id="SYNTHETIC-RESTART-BOUNDARY",
        dataset_id="synthetic-only",
        data_revision="fixture-v1",
        dataset_fingerprint="a" * 64,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"fixture": "restart-boundary"},
    )


def make_orchestrator(path: Path):
    ledger = FactoryJobEventLedger(path=path)
    worker = FactoryWorker(worker_id="W01")
    return ledger, worker, FactoryOrchestrator(
        fleet=FactoryWorkerFleet(workers=[worker]), events=ledger
    )


def test_restart_after_executor_return_but_before_terminal_journal_is_review_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    path = tmp_path / "events.jsonl"
    ledger, worker, orchestrator = make_orchestrator(path)
    orchestrator.submit(make_job(), station="DEV", phase="DEV")
    calls = []
    original_append = ledger.append

    def interrupt_completion(**kwargs):
        if kwargs.get("event_type") == "COMPLETED":
            raise SystemExit("interrupted before durable terminal event")
        return original_append(**kwargs)

    monkeypatch.setattr(ledger, "append", interrupt_completion)
    with pytest.raises(SystemExit, match="before durable terminal"):
        orchestrator.run_next(
            worker_id="W01",
            execute=lambda job, current_worker: calls.append(job.job_id)
            or {"output_artifact": "synthetic-output"},
        )

    assert calls == ["JOB-RESTART-BOUNDARY"]
    assert worker.state == "COMPLETED"
    assert [e.event_type for e in ledger.entries()] == ["QUEUED", "DISPATCHED"]
    before = path.read_bytes()

    report = inspect_factory_recovery(FactoryJobEventLedger(path=path))
    assert report.status_counts == {"INTERRUPTED_REVIEW_REQUIRED": 1}
    assert report.automatic_requeue_performed is False
    assert path.read_bytes() == before


def test_restart_after_durable_terminal_event_does_not_mark_job_interrupted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    path = tmp_path / "events.jsonl"
    ledger, worker, orchestrator = make_orchestrator(path)
    orchestrator.submit(make_job(), station="DEV", phase="DEV")
    calls = []

    def interrupt_after_completion(**kwargs):
        if kwargs.get("operation") == "publish_after_completion":
            raise SystemExit("interrupted after durable terminal event")

    monkeypatch.setattr(orchestrator, "_publish_telemetry_safely", interrupt_after_completion)
    with pytest.raises(SystemExit, match="after durable terminal"):
        orchestrator.run_next(
            worker_id="W01",
            execute=lambda job, current_worker: calls.append(job.job_id)
            or {"output_artifact": "synthetic-output"},
        )

    assert calls == ["JOB-RESTART-BOUNDARY"]
    assert worker.state == "COMPLETED"
    assert [e.event_type for e in ledger.entries()] == [
        "QUEUED", "DISPATCHED", "COMPLETED"
    ]
    before = path.read_bytes()

    report = inspect_factory_recovery(FactoryJobEventLedger(path=path))
    assert report.status_counts == {"TERMINAL_COMPLETED": 1}
    assert report.automatic_requeue_performed is False
    assert path.read_bytes() == before
