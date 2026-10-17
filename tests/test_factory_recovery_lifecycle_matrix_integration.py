from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.recovery_report import inspect_factory_recovery
from strategy_factory.worker import FactoryWorker
from strategy_factory.worker_journal_audit import inspect_worker_journal_file_consistency


def _append_queued(ledger: FactoryJobEventLedger) -> None:
    ledger.append(
        event_type="QUEUED",
        job_id="JOB-RECOVERY-INTEGRATION",
        job_fingerprint="a" * 64,
        station="DEV",
        phase="DEV",
        detail="synthetic integration fixture",
    )


def test_recovery_report_and_worker_audit_agree_without_side_effects(tmp_path: Path):
    path = tmp_path / "factory-job-events.jsonl"
    ledger = FactoryJobEventLedger(path)
    _append_queued(ledger)
    before_bytes = path.read_bytes()
    before_digest = hashlib.sha256(before_bytes).hexdigest()
    worker = FactoryWorker(worker_id="W01")
    before_worker = worker.__dict__.copy()

    audit = inspect_worker_journal_file_consistency([worker], path)
    first_report = inspect_factory_recovery(FactoryJobEventLedger(path))
    second_report = inspect_factory_recovery(FactoryJobEventLedger(path))

    assert audit["status"] == "CONSISTENT"
    assert audit["journal_integrity"]["status"] == "VALID"
    assert audit["journal_integrity"]["sha256"] == before_digest
    assert audit["journal_event_count"] == first_report.journal_event_count == 1
    assert first_report.to_dict() == second_report.to_dict()
    assert first_report.report_id == second_report.report_id
    assert first_report.status_counts == {"QUEUED_REVIEW_REQUIRED": 1}
    assert first_report.automatic_requeue_performed is False
    assert audit["automatic_action_performed"] is False
    assert path.read_bytes() == before_bytes
    assert worker.__dict__ == before_worker


@pytest.mark.parametrize(
    ("history", "expected_status", "worker_state"),
    [
        (("QUEUED",), "QUEUED_REVIEW_REQUIRED", "IDLE"),
        (("QUEUED", "DISPATCHED"), "INTERRUPTED_REVIEW_REQUIRED", "IDLE"),
        (("QUEUED", "DISPATCHED", "COMPLETED"), "TERMINAL_COMPLETED", "IDLE"),
        (("QUEUED", "DISPATCHED", "FAILED"), "TERMINAL_FAILED", "IDLE"),
        (
            ("QUEUED", "DISPATCHED", "COMPLETED", "FAILED"),
            "TERMINAL_CONFLICT_REVIEW_REQUIRED",
            "IDLE",
        ),
    ],
)
def test_lifecycle_matrix_is_deterministic_and_never_repairs(
    tmp_path: Path,
    history: tuple[str, ...],
    expected_status: str,
    worker_state: str,
):
    path = tmp_path / "factory-job-events.jsonl"
    ledger = FactoryJobEventLedger(path)
    for event_type in history:
        ledger.append(
            event_type=event_type,
            job_id="JOB-LIFECYCLE-MATRIX",
            job_fingerprint="b" * 64,
            worker_id="W01" if event_type != "QUEUED" else None,
            station="DEV",
            phase="DEV",
            detail="synthetic lifecycle matrix",
        )

    before_bytes = path.read_bytes()
    before_digest = hashlib.sha256(before_bytes).hexdigest()
    worker = FactoryWorker(worker_id="W01", state=worker_state)
    before_worker = worker.__dict__.copy()

    audit_first = inspect_worker_journal_file_consistency([worker], path)
    report_first = inspect_factory_recovery(FactoryJobEventLedger(path))
    audit_second = inspect_worker_journal_file_consistency([worker], path)
    report_second = inspect_factory_recovery(FactoryJobEventLedger(path))

    assert report_first.to_dict() == report_second.to_dict()
    assert report_first.report_id == report_second.report_id
    assert report_first.status_counts == {expected_status: 1}
    assert report_first.jobs[0]["status"] == expected_status
    assert report_first.automatic_requeue_performed is False

    assert audit_first == audit_second
    assert audit_first["journal_integrity"]["status"] == "VALID"
    assert audit_first["journal_integrity"]["sha256"] == before_digest
    assert audit_first["automatic_action_performed"] is False
    assert path.read_bytes() == before_bytes
    assert worker.__dict__ == before_worker
