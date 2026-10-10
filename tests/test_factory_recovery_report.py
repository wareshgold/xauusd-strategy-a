from __future__ import annotations

from dataclasses import replace

import pytest

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.recovery_report import (
    FactoryRecoveryReport,
    inspect_factory_recovery,
    validate_recovery_report,
)
from strategy_factory.test_contract import ExecutionSemantics


def make_job(job_id: str) -> ResearchJobSpec:
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


def append(ledger, job, event_type, worker_id=None):
    ledger.append(
        event_type=event_type,
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
        worker_id=worker_id,
        station="DEV",
        phase="DEV",
    )


def test_recovery_report_classifies_jobs_without_requeueing(tmp_path):
    ledger = FactoryJobEventLedger(tmp_path / "events.jsonl")
    queued = make_job("JOB-QUEUED")
    interrupted = make_job("JOB-INTERRUPTED")
    completed = make_job("JOB-COMPLETED")
    failed = make_job("JOB-FAILED")

    append(ledger, queued, "QUEUED")
    for job in (interrupted, completed, failed):
        append(ledger, job, "QUEUED")
        append(ledger, job, "DISPATCHED", worker_id="W01")
    append(ledger, completed, "COMPLETED", worker_id="W01")
    append(ledger, failed, "FAILED", worker_id="W01")

    report = inspect_factory_recovery(FactoryJobEventLedger(ledger.path))

    by_id = {item["job_id"]: item for item in report.jobs}
    assert by_id[queued.job_id]["status"] == "QUEUED_REVIEW_REQUIRED"
    assert by_id[interrupted.job_id]["status"] == "INTERRUPTED_REVIEW_REQUIRED"
    assert by_id[completed.job_id]["status"] == "TERMINAL_COMPLETED"
    assert by_id[failed.job_id]["status"] == "TERMINAL_FAILED"
    assert report.journal_event_count == len(ledger.entries())
    assert report.status_counts == {
        "QUEUED_REVIEW_REQUIRED": 1,
        "INTERRUPTED_REVIEW_REQUIRED": 1,
        "TERMINAL_COMPLETED": 1,
        "TERMINAL_FAILED": 1,
    }
    assert report.automatic_requeue_performed is False


def test_recovery_report_identity_is_stable_for_same_journal(tmp_path):
    path = tmp_path / "events.jsonl"
    ledger = FactoryJobEventLedger(path)
    job = make_job("JOB-STABLE")
    append(ledger, job, "QUEUED")

    first = inspect_factory_recovery(FactoryJobEventLedger(path))
    second = inspect_factory_recovery(FactoryJobEventLedger(path))

    assert first.report_id == second.report_id
    assert first.to_dict() == second.to_dict()


def test_recovery_report_rejects_inconsistent_counts():
    report = FactoryRecoveryReport(
        report_id="a" * 64,
        journal_event_count=0,
        jobs=({"job_id": "JOB-1", "status": "QUEUED_REVIEW_REQUIRED"},),
        status_counts={},
        automatic_requeue_performed=False,
    )

    with pytest.raises(ValueError, match="status counts"):
        validate_recovery_report(report)


def test_recovery_report_rejects_claim_of_automatic_requeue():
    report = FactoryRecoveryReport(
        report_id="a" * 64,
        journal_event_count=0,
        jobs=(),
        status_counts={},
        automatic_requeue_performed=True,
    )

    with pytest.raises(ValueError, match="automatic requeue"):
        validate_recovery_report(report)
