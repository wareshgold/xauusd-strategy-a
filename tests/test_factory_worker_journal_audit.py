from __future__ import annotations

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.worker import FactoryWorker
from strategy_factory.worker_journal_audit import inspect_worker_journal_consistency


def append(ledger, event_type, job_id="JOB-1", worker_id=None):
    ledger.append(
        event_type=event_type,
        job_id=job_id,
        job_fingerprint="a" * 64,
        worker_id=worker_id,
        station="DEV",
        phase="DEV",
    )


def test_matching_active_worker_and_dispatched_journal_is_consistent():
    ledger = FactoryJobEventLedger(path=None)
    append(ledger, "QUEUED")
    append(ledger, "DISPATCHED", worker_id="W01")
    worker = FactoryWorker(
        worker_id="W01", job_id="JOB-1", state="RUNNING", station="DEV", phase="DEV"
    )

    report = inspect_worker_journal_consistency(ledger, [worker])

    assert report["status"] == "CONSISTENT"
    assert report["finding_count"] == 0
    assert report["automatic_action_performed"] is False


def test_completed_worker_without_terminal_journal_event_requires_review():
    ledger = FactoryJobEventLedger(path=None)
    append(ledger, "QUEUED")
    append(ledger, "DISPATCHED", worker_id="W01")
    worker = FactoryWorker(
        worker_id="W01", job_id="JOB-1", state="COMPLETED", station="DEV", phase="DEV"
    )

    report = inspect_worker_journal_consistency(ledger, [worker])

    assert report["status"] == "REVIEW_REQUIRED"
    assert "TERMINAL_WORKER_JOURNAL_MISMATCH" in {
        finding["code"] for finding in report["findings"]
    }
    assert report["automatic_action_performed"] is False


def test_restart_idle_worker_does_not_hide_interrupted_dispatch():
    ledger = FactoryJobEventLedger(path=None)
    append(ledger, "QUEUED")
    append(ledger, "DISPATCHED", worker_id="W01")
    restarted_worker = FactoryWorker(worker_id="W01", state="IDLE")

    report = inspect_worker_journal_consistency(ledger, [restarted_worker])

    assert report["status"] == "REVIEW_REQUIRED"
    assert report["findings"] == [{
        "code": "DISPATCHED_JOB_NOT_ACTIVE_ON_WORKER",
        "worker_id": "W01",
        "job_id": "JOB-1",
        "detail": "Journal ends at DISPATCHED but no matching worker is active; manual reconciliation may be required",
    }]
    assert report["automatic_action_performed"] is False


def test_active_worker_with_wrong_worker_id_is_reported_deterministically():
    ledger = FactoryJobEventLedger(path=None)
    append(ledger, "QUEUED")
    append(ledger, "DISPATCHED", worker_id="W01")
    worker = FactoryWorker(
        worker_id="W02", job_id="JOB-1", state="HEARTBEAT", station="DEV", phase="DEV"
    )

    first = inspect_worker_journal_consistency(ledger, [worker])
    second = inspect_worker_journal_consistency(ledger, [worker])

    assert first == second
    assert {finding["code"] for finding in first["findings"]} == {
        "ACTIVE_WORKER_JOURNAL_MISMATCH",
        "DISPATCHED_JOB_NOT_ACTIVE_ON_WORKER",
    }


def test_duplicate_worker_ids_are_reported_deterministically_without_mutation():
    ledger = FactoryJobEventLedger(path=None)
    append(ledger, "QUEUED")
    append(ledger, "DISPATCHED", worker_id="W01")
    workers = [
        FactoryWorker(
            worker_id="W01", job_id="JOB-1", state="RUNNING", station="DEV", phase="DEV"
        ),
        FactoryWorker(worker_id="W01", state="IDLE"),
    ]
    before_events = ledger.entries()
    before_workers = [worker.__dict__.copy() for worker in workers]

    first = inspect_worker_journal_consistency(ledger, workers)
    second = inspect_worker_journal_consistency(ledger, workers)

    assert first == second
    assert first["status"] == "REVIEW_REQUIRED"
    assert first["finding_count"] == 1
    assert first["findings"] == [{
        "code": "DUPLICATE_WORKER_ID",
        "worker_id": "W01",
        "job_id": "",
        "detail": "Worker snapshot contains a duplicate worker_id",
    }]
    assert first["automatic_action_performed"] is False
    assert ledger.entries() == before_events
    assert [worker.__dict__.copy() for worker in workers] == before_workers
