from __future__ import annotations

from pathlib import Path

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.worker import FactoryWorker
from strategy_factory.worker_journal_audit import (
    inspect_worker_journal_consistency,
    inspect_worker_journal_file_consistency,
)


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



def test_recovery_summary_and_worker_snapshot_conflicts_are_reported_without_repair():
    cases = [
        (
            ("QUEUED",),
            "RUNNING",
            "RECOVERY_WORKER_STATE_CONFLICT",
        ),
        (
            ("QUEUED", "DISPATCHED"),
            "COMPLETED",
            "RECOVERY_WORKER_STATE_CONFLICT",
        ),
        (
            ("QUEUED", "DISPATCHED", "COMPLETED"),
            "FAILED",
            "RECOVERY_WORKER_STATE_CONFLICT",
        ),
    ]

    for index, (history, worker_state, expected_code) in enumerate(cases):
        ledger = FactoryJobEventLedger(path=None)
        job_id = f"JOB-RECOVERY-JOIN-{index}"
        for event_type in history:
            append(
                ledger,
                event_type,
                job_id=job_id,
                worker_id="W01" if event_type != "QUEUED" else None,
            )
        worker = FactoryWorker(
            worker_id="W01",
            job_id=job_id,
            state=worker_state,
            station="DEV",
            phase="DEV",
        )
        before_events = ledger.entries()
        before_worker = worker.__dict__.copy()

        report = inspect_worker_journal_consistency(ledger, [worker])
        repeated = inspect_worker_journal_consistency(ledger, [worker])

        assert report == repeated
        assert report["status"] == "REVIEW_REQUIRED"
        assert expected_code in {finding["code"] for finding in report["findings"]}
        assert report["recovery_job_count"] == 1
        assert report["recovery_status_counts"]
        assert report["automatic_action_performed"] is False
        assert ledger.entries() == before_events
        assert worker.__dict__ == before_worker



def test_file_audit_includes_integrity_from_same_validated_snapshot(tmp_path: Path):
    path = tmp_path / "valid-factory-journal.jsonl"
    ledger = FactoryJobEventLedger(path)
    append(ledger, "QUEUED")
    before = path.read_bytes()
    worker = FactoryWorker(worker_id="W01", state="IDLE")

    report = inspect_worker_journal_file_consistency([worker], path)

    assert report["journal_integrity"]["status"] == "VALID"
    assert report["journal_integrity"]["sha256"]
    assert report["journal_event_count"] == 1
    assert report["status"] == "CONSISTENT"
    assert report["automatic_action_performed"] is False
    assert path.read_bytes() == before


def test_file_audit_fails_closed_on_corrupt_journal_without_repair_or_replay(
    tmp_path: Path,
):
    path = tmp_path / "corrupt-factory-journal.jsonl"
    path.write_bytes(b'{"sequence":')
    before = path.read_bytes()
    workers = [FactoryWorker(worker_id="W01", state="IDLE")]

    report = inspect_worker_journal_file_consistency(workers, path)

    assert report["status"] == "REVIEW_REQUIRED"
    assert report["journal_integrity"]["status"] == "INVALID_REVIEW_REQUIRED"
    assert report["journal_event_count"] is None
    assert report["finding_count"] == 1
    assert report["findings"][0]["code"] == "JOURNAL_INTEGRITY_REVIEW_REQUIRED"
    assert report["automatic_action_performed"] is False
    assert path.read_bytes() == before


def test_file_audit_requires_review_for_missing_journal(tmp_path: Path):
    path = tmp_path / "missing-factory-journal.jsonl"

    report = inspect_worker_journal_file_consistency([], path)

    assert report["status"] == "REVIEW_REQUIRED"
    assert report["journal_integrity"]["status"] == "MISSING_REVIEW_REQUIRED"
    assert report["journal_integrity"]["exists"] is False
    assert report["automatic_action_performed"] is False


def test_file_audit_fails_closed_on_unreadable_journal(
    tmp_path: Path, monkeypatch
):
    path = tmp_path / "unreadable-factory-journal.jsonl"
    path.write_bytes(b"do not mutate")
    before = path.read_bytes()
    original_read_bytes = Path.read_bytes

    def deny_read(self: Path) -> bytes:
        if self == path:
            raise PermissionError("synthetic access denied")
        return original_read_bytes(self)

    monkeypatch.setattr(Path, "read_bytes", deny_read)

    report = inspect_worker_journal_file_consistency(
        [FactoryWorker(worker_id="W01", state="IDLE")], path
    )

    assert report["status"] == "REVIEW_REQUIRED"
    assert report["journal_integrity"]["status"] == "UNREADABLE_REVIEW_REQUIRED"
    assert report["journal_event_count"] is None
    assert report["finding_count"] == 1
    assert report["findings"][0]["code"] == "JOURNAL_INTEGRITY_REVIEW_REQUIRED"
    assert report["automatic_action_performed"] is False
    assert original_read_bytes(path) == before
