from __future__ import annotations

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.recovery_report import inspect_factory_recovery
from strategy_factory.worker_journal_audit import inspect_worker_journal_consistency


def append(ledger, event_type, job_id, fingerprint, worker_id=None):
    return ledger.append(
        event_type=event_type,
        job_id=job_id,
        job_fingerprint=fingerprint,
        worker_id=worker_id,
        station="DEV",
        phase="DEV",
    )


def test_recovery_report_identity_changes_when_journal_evidence_changes(tmp_path):
    path = tmp_path / "events.jsonl"
    ledger = FactoryJobEventLedger(path)
    fingerprint = "a" * 64
    append(ledger, "QUEUED", "JOB-PROVENANCE", fingerprint)
    first = inspect_factory_recovery(FactoryJobEventLedger(path))

    append(ledger, "DISPATCHED", "JOB-PROVENANCE", fingerprint, worker_id="W01")
    second = inspect_factory_recovery(FactoryJobEventLedger(path))

    assert first.report_id != second.report_id
    assert first.journal_event_count == 1
    assert second.journal_event_count == 2
    assert first.automatic_requeue_performed is False
    assert second.automatic_requeue_performed is False


def test_worker_audit_accepts_serialized_telemetry_and_is_order_independent():
    ledger = FactoryJobEventLedger(path=None)
    fingerprint = "b" * 64
    append(ledger, "QUEUED", "JOB-A", fingerprint)
    append(ledger, "DISPATCHED", "JOB-A", fingerprint, worker_id="W01")
    append(ledger, "QUEUED", "JOB-B", fingerprint)
    append(ledger, "DISPATCHED", "JOB-B", fingerprint, worker_id="W02")
    workers = [
        {"worker_id": "W01", "job_id": "JOB-A", "state": "RUNNING"},
        {"worker_id": "W02", "job_id": "JOB-B", "state": "HEARTBEAT"},
    ]

    forward = inspect_worker_journal_consistency(ledger, workers)
    reversed_order = inspect_worker_journal_consistency(ledger, list(reversed(workers)))

    assert forward == reversed_order
    assert forward["status"] == "CONSISTENT"
    assert forward["finding_count"] == 0
    assert forward["automatic_action_performed"] is False


def test_duplicate_worker_identity_is_a_review_finding():
    ledger = FactoryJobEventLedger(path=None)
    fingerprint = "c" * 64
    append(ledger, "QUEUED", "JOB-DUP", fingerprint)
    append(ledger, "DISPATCHED", "JOB-DUP", fingerprint, worker_id="W01")
    worker = {"worker_id": "W01", "job_id": "JOB-DUP", "state": "RUNNING"}

    report = inspect_worker_journal_consistency(ledger, [worker, dict(worker)])

    assert report["status"] == "REVIEW_REQUIRED"
    assert report["finding_count"] == 1
    assert report["findings"][0]["code"] == "DUPLICATE_WORKER_ID"
    assert report["automatic_action_performed"] is False


def test_report_identity_is_reproducible_after_persisted_restart(tmp_path):
    path = tmp_path / "restart-events.jsonl"
    first_process = FactoryJobEventLedger(path)
    fingerprint = "d" * 64
    append(first_process, "QUEUED", "JOB-RESTART", fingerprint)
    append(first_process, "DISPATCHED", "JOB-RESTART", fingerprint, worker_id="W01")

    before_restart = inspect_factory_recovery(first_process)
    after_restart = inspect_factory_recovery(FactoryJobEventLedger(path))

    assert before_restart.to_dict() == after_restart.to_dict()
    assert before_restart.report_id == after_restart.report_id
