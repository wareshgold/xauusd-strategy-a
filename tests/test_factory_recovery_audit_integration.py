from __future__ import annotations

import hashlib
from pathlib import Path

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
