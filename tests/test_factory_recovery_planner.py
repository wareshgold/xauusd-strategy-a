from __future__ import annotations

from dataclasses import replace

import pytest

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.recovery_planner import (
    plan_queue_reconstruction,
    validate_queue_reconstruction_plan,
)
from strategy_factory.recovery_report import inspect_factory_recovery
from strategy_factory.test_contract import ExecutionSemantics


def make_job(job_id: str, fingerprint_char: str = "a") -> ResearchJobSpec:
    return ResearchJobSpec(
        job_id=job_id,
        strategy_id="SP2L-A",
        strategy_revision="REV-1",
        manifest_revision="MANIFEST-1",
        test_id="TEST-1",
        dataset_id="DATA-1",
        data_revision="DATA-REV-1",
        dataset_fingerprint=fingerprint_char * 64,
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


def setup_ledger(tmp_path):
    ledger = FactoryJobEventLedger(tmp_path / "events.jsonl")
    queued = make_job("JOB-QUEUED")
    interrupted = make_job("JOB-INTERRUPTED")
    completed = make_job("JOB-COMPLETED")
    failed = make_job("JOB-FAILED")
    append(ledger, queued, "QUEUED")
    for job in (interrupted, completed, failed):
        append(ledger, job, "QUEUED")
        append(ledger, job, "DISPATCHED", "W01")
    append(ledger, completed, "COMPLETED", "W01")
    append(ledger, failed, "FAILED", "W01")
    return ledger, queued, interrupted, completed, failed


def test_plan_requires_explicit_approval_and_matching_job_spec(tmp_path):
    ledger, queued, *_ = setup_ledger(tmp_path)
    report = inspect_factory_recovery(FactoryJobEventLedger(ledger.path))

    plan = plan_queue_reconstruction(
        ledger=FactoryJobEventLedger(ledger.path),
        report=report,
        job_specs={queued.job_id: queued},
        approved_job_ids=[queued.job_id],
    )

    assert plan.approved_job_ids == (queued.job_id,)
    assert len(plan.items) == 1
    assert plan.items[0].job == queued
    assert plan.items[0].job_fingerprint == queued.fingerprint
    assert plan.automatic_requeue_performed is False
    validate_queue_reconstruction_plan(plan)


def test_plan_is_deterministic_for_same_journal_and_approval(tmp_path):
    ledger, queued, *_ = setup_ledger(tmp_path)
    path = ledger.path
    first_ledger = FactoryJobEventLedger(path)
    report = inspect_factory_recovery(first_ledger)
    first = plan_queue_reconstruction(
        ledger=first_ledger, report=report,
        job_specs={queued.job_id: queued}, approved_job_ids=[queued.job_id],
    )
    second_ledger = FactoryJobEventLedger(path)
    second = plan_queue_reconstruction(
        ledger=second_ledger,
        report=inspect_factory_recovery(second_ledger),
        job_specs={queued.job_id: queued}, approved_job_ids=[queued.job_id],
    )

    assert first.plan_id == second.plan_id
    assert first.to_dict() == second.to_dict()


def test_plan_rejects_interrupted_job_even_when_explicitly_approved(tmp_path):
    ledger, _, interrupted, *_ = setup_ledger(tmp_path)
    report = inspect_factory_recovery(ledger)

    with pytest.raises(ValueError, match="not safe for queue reconstruction"):
        plan_queue_reconstruction(
            ledger=ledger, report=report,
            job_specs={interrupted.job_id: interrupted},
            approved_job_ids=[interrupted.job_id],
        )


def test_plan_rejects_missing_job_spec(tmp_path):
    ledger, queued, *_ = setup_ledger(tmp_path)
    report = inspect_factory_recovery(ledger)

    with pytest.raises(ValueError, match="Job Spec is required"):
        plan_queue_reconstruction(
            ledger=ledger, report=report, job_specs={},
            approved_job_ids=[queued.job_id],
        )


def test_plan_rejects_fingerprint_mismatch(tmp_path):
    ledger, queued, *_ = setup_ledger(tmp_path)
    report = inspect_factory_recovery(ledger)
    wrong_spec = make_job(queued.job_id, fingerprint_char="b")

    with pytest.raises(ValueError, match="fingerprint mismatch"):
        plan_queue_reconstruction(
            ledger=ledger, report=report,
            job_specs={queued.job_id: wrong_spec},
            approved_job_ids=[queued.job_id],
        )


def test_plan_rejects_stale_recovery_report(tmp_path):
    ledger, queued, *_ = setup_ledger(tmp_path)
    report = inspect_factory_recovery(ledger)
    append(ledger, queued, "HANDOFF_ACCEPTED")

    with pytest.raises(ValueError, match="does not match the current journal"):
        plan_queue_reconstruction(
            ledger=ledger, report=report,
            job_specs={queued.job_id: queued},
            approved_job_ids=[queued.job_id],
        )


def test_plan_rejects_duplicate_or_unknown_approvals(tmp_path):
    ledger, queued, *_ = setup_ledger(tmp_path)
    report = inspect_factory_recovery(ledger)

    with pytest.raises(ValueError, match="must not contain duplicates"):
        plan_queue_reconstruction(
            ledger=ledger, report=report,
            job_specs={queued.job_id: queued},
            approved_job_ids=[queued.job_id, queued.job_id],
        )
    with pytest.raises(ValueError, match="absent from recovery report"):
        plan_queue_reconstruction(
            ledger=ledger, report=report, job_specs={},
            approved_job_ids=["JOB-UNKNOWN"],
        )


def test_plan_validator_rejects_mutated_job_spec():
    job = make_job("JOB-VALIDATE")
    # Build a valid minimal plan from a correctly fingerprinted item.
    from strategy_factory.recovery_planner import QueueReconstructionItem, QueueReconstructionPlan
    plan = QueueReconstructionPlan(
        plan_id="a" * 64,
        recovery_report_id="b" * 64,
        approved_job_ids=(job.job_id,),
        items=(QueueReconstructionItem(
            job_id=job.job_id, job_fingerprint="c" * 64,
            original_queue_sequence=1, job=job,
        ),),
    )

    with pytest.raises(ValueError, match="mismatched Job Spec"):
        validate_queue_reconstruction_plan(plan)



def test_restart_keeps_dispatched_without_terminal_event_manual_only(tmp_path):
    path = tmp_path / "events.jsonl"
    original = FactoryJobEventLedger(path)
    interrupted = make_job("JOB-EXECUTION-OUTCOME-UNKNOWN")
    append(original, interrupted, "QUEUED")
    append(original, interrupted, "DISPATCHED", "W01")

    # Model the critical uncertainty window: the executor may have run, but
    # its terminal COMPLETED/FAILED event was not persisted before process loss.
    restarted = FactoryJobEventLedger(path)
    report = inspect_factory_recovery(restarted)
    item = next(entry for entry in report.jobs if entry["job_id"] == interrupted.job_id)
    assert item["status"] == "INTERRUPTED_REVIEW_REQUIRED"
    assert item["action"] == "MANUAL_RECONCILIATION_REQUIRED"

    with pytest.raises(ValueError, match="not safe for queue reconstruction"):
        plan_queue_reconstruction(
            ledger=restarted,
            report=report,
            job_specs={interrupted.job_id: interrupted},
            approved_job_ids=[interrupted.job_id],
        )
