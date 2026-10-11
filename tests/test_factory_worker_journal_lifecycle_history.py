from __future__ import annotations

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.worker_journal_audit import inspect_worker_journal_consistency


def append(ledger, event_type: str, *, job_id: str = "DISCOVERY-1", worker_id: str | None = "W01"):
    return ledger.append(
        event_type=event_type,
        job_id=job_id,
        job_fingerprint="a" * 64,
        worker_id=worker_id,
        station="stability",
        phase="STABILITY",
        detail="Stability completed" if event_type == "COMPLETED" else event_type,
        output_artifact="EVIDENCE-DISCOVERY-1" if event_type == "COMPLETED" else None,
        research_run_fingerprint="b" * 64 if event_type == "COMPLETED" else None,
    )


def test_audit_surfaces_repeated_terminal_lifecycle_even_without_worker_snapshot():
    ledger = FactoryJobEventLedger(path=None)
    append(ledger, "COMPLETED")
    append(ledger, "COMPLETED")
    append(ledger, "COMPLETED")
    before = ledger.entries()

    report = inspect_worker_journal_consistency(ledger, [])

    assert report["status"] == "REVIEW_REQUIRED"
    assert report["recovery_status_counts"] == {"LIFECYCLE_CONFLICT_REVIEW_REQUIRED": 1}
    assert report["findings"] == [{
        "code": "LIFECYCLE_CONFLICT_REVIEW_REQUIRED",
        "worker_id": "W01",
        "job_id": "DISCOVERY-1",
        "detail": (
            "Journal lifecycle history is not a valid single-job "
            "transition sequence: ['COMPLETED', 'COMPLETED', 'COMPLETED']"
        ),
    }]
    assert report["automatic_action_performed"] is False
    assert ledger.entries() == before


def test_audit_surfaces_completed_and_failed_terminal_conflict():
    ledger = FactoryJobEventLedger(path=None)
    append(ledger, "QUEUED", worker_id=None)
    append(ledger, "DISPATCHED")
    append(ledger, "COMPLETED")
    append(ledger, "FAILED")
    before = ledger.entries()

    report = inspect_worker_journal_consistency(ledger, [])

    assert report["status"] == "REVIEW_REQUIRED"
    assert report["recovery_status_counts"] == {"TERMINAL_CONFLICT_REVIEW_REQUIRED": 1}
    assert report["finding_count"] == 1
    assert report["findings"][0]["code"] == "TERMINAL_CONFLICT_REVIEW_REQUIRED"
    assert report["findings"][0]["job_id"] == "DISCOVERY-1"
    assert report["automatic_action_performed"] is False
    assert ledger.entries() == before


def test_valid_single_completion_history_is_not_flagged():
    ledger = FactoryJobEventLedger(path=None)
    append(ledger, "QUEUED", worker_id=None)
    append(ledger, "DISPATCHED")
    append(ledger, "COMPLETED")

    report = inspect_worker_journal_consistency(ledger, [])

    assert report["status"] == "CONSISTENT"
    assert report["finding_count"] == 0
    assert report["recovery_status_counts"] == {"TERMINAL_COMPLETED": 1}
