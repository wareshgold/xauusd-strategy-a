from __future__ import annotations

from pathlib import Path

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.recovery_report import inspect_factory_recovery
from strategy_factory.test_contract import ExecutionSemantics


def _job() -> ResearchJobSpec:
    return ResearchJobSpec(
        job_id="JOB-RECEIPT-RECONCILIATION",
        strategy_id="SP2L-RESEARCH",
        strategy_revision="frozen-synthetic-fixture",
        manifest_revision="manifest-synthetic-fixture",
        test_id="SYNTHETIC-RECEIPT-RECONCILIATION",
        dataset_id="synthetic-only",
        data_revision="fixture-v1",
        dataset_fingerprint="d" * 64,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"fixture": "non-lifecycle-artifact-marker"},
    )


def test_non_lifecycle_artifact_marker_cannot_promote_interrupted_job(
    tmp_path: Path,
) -> None:
    path = tmp_path / "events.jsonl"
    ledger = FactoryJobEventLedger(path=path)
    job = _job()
    ledger.append(
        event_type="QUEUED",
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
        station="DEV",
        phase="DEV",
    )
    ledger.append(
        event_type="DISPATCHED",
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
        worker_id="W01",
        station="DEV",
        phase="DEV",
    )
    # A marker that mentions an artifact is deliberately not a lifecycle
    # terminal receipt. Recovery must not infer COMPLETED from it.
    ledger.append(
        event_type="HANDOFF_ACCEPTED",
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
        station="VALIDATION",
        phase="VALIDATION",
        output_artifact="synthetic-artifact-id",
        research_run_fingerprint="e" * 64,
    )
    before = path.read_bytes()

    restarted = FactoryJobEventLedger(path=path)
    report = inspect_factory_recovery(restarted)

    assert report.jobs[0]["status"] == "INTERRUPTED_REVIEW_REQUIRED"
    assert report.jobs[0]["action"] == "MANUAL_RECONCILIATION_REQUIRED"
    assert report.automatic_requeue_performed is False
    assert path.read_bytes() == before
    assert [event.event_type for event in restarted.entries()] == [
        "QUEUED", "DISPATCHED", "HANDOFF_ACCEPTED"
    ]
