from __future__ import annotations

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.test_contract import ExecutionSemantics
from strategy_factory.worker_journal_audit import inspect_worker_journal_consistency


def _job() -> ResearchJobSpec:
    return ResearchJobSpec(
        job_id="JOB-DUPLICATE-COMPLETION",
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


def test_lifecycle_conflict_is_reported_without_current_worker_snapshot():
    ledger = FactoryJobEventLedger(path=None)
    job = _job()
    for event_type in ("QUEUED", "DISPATCHED", "COMPLETED", "COMPLETED"):
        ledger.append(
            event_type=event_type,
            job_id=job.job_id,
            job_fingerprint=job.fingerprint,
            worker_id="worker-1",
            station="discovery",
            phase="DISCOVERY",
            detail=f"synthetic {event_type.lower()} event",
            output_artifact="SYNTHETIC-ONLY",
        )

    report = inspect_worker_journal_consistency(ledger, workers=[])

    assert report["status"] == "REVIEW_REQUIRED"
    assert report["finding_count"] == 1
    assert report["findings"] == [{
        "code": "JOB_LIFECYCLE_CONFLICT",
        "worker_id": "worker-1",
        "job_id": job.job_id,
        "detail": (
            "Journal lifecycle history is invalid "
            "(LIFECYCLE_CONFLICT_REVIEW_REQUIRED); "
            "manual reconciliation required; no automatic retry"
        ),
    }]
    assert report["automatic_action_performed"] is False


def test_valid_completed_lifecycle_remains_consistent_without_worker_snapshot():
    ledger = FactoryJobEventLedger(path=None)
    job = _job()
    for event_type in ("QUEUED", "DISPATCHED", "COMPLETED"):
        ledger.append(
            event_type=event_type,
            job_id=job.job_id,
            job_fingerprint=job.fingerprint,
            worker_id="worker-1",
            station="discovery",
            phase="DISCOVERY",
            detail=f"synthetic {event_type.lower()} event",
            output_artifact="SYNTHETIC-ONLY",
        )

    report = inspect_worker_journal_consistency(ledger, workers=[])

    assert report["status"] == "CONSISTENT"
    assert report["finding_count"] == 0
    assert report["automatic_action_performed"] is False
