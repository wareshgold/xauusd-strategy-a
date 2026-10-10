import json
from pathlib import Path

import pytest

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.orchestrator import FactoryOrchestrator
from strategy_factory.test_contract import ExecutionSemantics
from strategy_factory.worker import FactoryWorker, FactoryWorkerFleet


def make_job(job_id: str = "JOB-EVENT-001") -> ResearchJobSpec:
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


def test_job_event_ledger_fingerprints_and_filters(tmp_path: Path):
    ledger = FactoryJobEventLedger(tmp_path / "events.jsonl")
    job = make_job()
    queued = ledger.append(
        event_type="QUEUED",
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
        station="discovery",
        phase="DISCOVERY",
    )
    dispatched = ledger.append(
        event_type="DISPATCHED",
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
        worker_id="W01",
        station="discovery",
        phase="DISCOVERY",
    )

    queued.validate()
    dispatched.validate()
    assert [e.event_type for e in ledger.for_job(job.job_id)] == ["QUEUED", "DISPATCHED"]
    assert ledger.entries()[0].sequence == 1
    assert ledger.entries()[1].sequence == 2
    assert len((tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()) == 2


def test_orchestrator_records_real_queue_lifecycle():
    job = make_job()
    # These tests assert one invocation's lifecycle, not the persistent runtime journal.
    events = FactoryJobEventLedger(path=None)
    fleet = FactoryWorkerFleet([FactoryWorker("W01")])
    orchestrator = FactoryOrchestrator(fleet=fleet, events=events)

    orchestrator.submit(job, station="discovery", phase="DISCOVERY")
    assert [e.event_type for e in events.entries()] == ["QUEUED"]

    result = orchestrator.run_next(
        worker_id="W01",
        execute=lambda _job, _worker: {
            "output_artifact": "EVIDENCE-JOB-EVENT-001",
            "detail": "Research run accepted",
        },
    )

    assert result["output_artifact"] == "EVIDENCE-JOB-EVENT-001"
    assert [e.event_type for e in events.entries()] == ["QUEUED", "DISPATCHED", "COMPLETED"]
    completed = events.entries()[-1]
    assert completed.worker_id == "W01"
    assert completed.station == "discovery"
    assert completed.output_artifact == "EVIDENCE-JOB-EVENT-001"


def test_orchestrator_records_failed_execution():
    job = make_job()
    # Keep this assertion independent of previously persisted runtime events.
    events = FactoryJobEventLedger(path=None)
    fleet = FactoryWorkerFleet([FactoryWorker("W01")])
    orchestrator = FactoryOrchestrator(fleet=fleet, events=events)
    orchestrator.submit(job, station="stability", phase="STABILITY")

    try:
        orchestrator.run_next(
            worker_id="W01",
            execute=lambda _job, _worker: (_ for _ in ()).throw(RuntimeError("adapter failed")),
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("expected execution failure")

    assert [e.event_type for e in events.entries()] == ["QUEUED", "DISPATCHED", "FAILED"]
    assert fleet.get("W01").state == "FAILED"



def test_orchestrator_rejects_duplicate_job_ids_before_and_after_execution():
    job = make_job()
    events = FactoryJobEventLedger(path=None)
    fleet = FactoryWorkerFleet([FactoryWorker("W01")])
    orchestrator = FactoryOrchestrator(fleet=fleet, events=events)

    orchestrator.submit(job, station="discovery", phase="DISCOVERY")
    with pytest.raises(ValueError, match="already been submitted"):
        orchestrator.submit(job, station="stability", phase="STABILITY")

    assert len(orchestrator.pending()) == 1
    assert [event.event_type for event in events.entries()] == ["QUEUED"]

    orchestrator.run_next(
        worker_id="W01",
        execute=lambda _job, _worker: {"output_artifact": "EVIDENCE-1"},
    )
    prior_events = events.entries()

    with pytest.raises(ValueError, match="already been submitted"):
        orchestrator.submit(job, station="stability", phase="STABILITY")

    assert orchestrator.pending() == ()
    assert events.entries() == prior_events


def test_worker_fleet_does_not_publish_to_shared_status_by_default(monkeypatch):
    def unexpected_publish(*_args, **_kwargs):
        raise AssertionError("default worker fleet must not publish shared telemetry")

    monkeypatch.setattr("strategy_factory.worker.publish_workers", unexpected_publish)
    fleet = FactoryWorkerFleet([FactoryWorker("W01")])

    assert fleet.status_path is None
    fleet.publish()


def test_worker_fleet_publishes_only_to_explicit_status_path(tmp_path: Path):
    status_path = tmp_path / "isolated-worker-status.json"
    fleet = FactoryWorkerFleet(
        [FactoryWorker("W01")],
        status_path=status_path,
    )

    fleet.publish()

    payload = json.loads(status_path.read_text(encoding="utf-8"))
    assert [worker["worker_id"] for worker in payload["workers"]] == ["W01"]


def test_failed_job_is_terminal_and_does_not_block_next_queued_job():
    failed_job = make_job("JOB-FAIL-001")
    next_job = make_job("JOB-NEXT-002")
    events = FactoryJobEventLedger(path=None)
    fleet = FactoryWorkerFleet([FactoryWorker("W01")])
    orchestrator = FactoryOrchestrator(fleet=fleet, events=events)

    orchestrator.submit(failed_job, station="discovery", phase="DISCOVERY")
    orchestrator.submit(next_job, station="discovery", phase="DISCOVERY")

    with pytest.raises(RuntimeError, match="synthetic adapter failure"):
        orchestrator.run_next(
            worker_id="W01",
            execute=lambda _job, _worker: (_ for _ in ()).throw(
                RuntimeError("synthetic adapter failure")
            ),
        )

    assert [item.job.job_id for item in orchestrator.pending()] == [next_job.job_id]
    assert fleet.get("W01").state == "FAILED"
    assert [event.event_type for event in events.entries()] == [
        "QUEUED",
        "QUEUED",
        "DISPATCHED",
        "FAILED",
    ]

    with pytest.raises(ValueError, match="already been submitted"):
        orchestrator.submit(failed_job, station="discovery", phase="DISCOVERY")

    result = orchestrator.run_next(
        worker_id="W01",
        execute=lambda job, _worker: {"output_artifact": f"EVIDENCE-{job.job_id}"},
    )
    assert result["output_artifact"] == "EVIDENCE-JOB-NEXT-002"
    assert orchestrator.pending() == ()
    assert [event.event_type for event in events.entries()] == [
        "QUEUED",
        "QUEUED",
        "DISPATCHED",
        "FAILED",
        "DISPATCHED",
        "COMPLETED",
    ]


def test_persisted_ledger_restores_sequence_and_rejects_replayed_job(tmp_path: Path):
    path = tmp_path / "persistent-events.jsonl"
    job = make_job()

    first_process = FactoryJobEventLedger(path)
    first_process.append(
        event_type="QUEUED",
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
        station="discovery",
        phase="DISCOVERY",
    )

    # Simulate a process restart: the next ledger must recover the journal.
    restarted_ledger = FactoryJobEventLedger(path)
    assert len(restarted_ledger.entries()) == 1
    assert restarted_ledger.entries()[0].sequence == 1
    second_event = restarted_ledger.append(
        event_type="DISPATCHED",
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
        worker_id="W01",
        station="discovery",
        phase="DISCOVERY",
    )
    assert second_event.sequence == 2

    orchestrator = FactoryOrchestrator(
        fleet=FactoryWorkerFleet([FactoryWorker("W01")]),
        events=FactoryJobEventLedger(path),
    )
    with pytest.raises(ValueError, match="already been submitted"):
        orchestrator.submit(job, station="stability", phase="STABILITY")


def test_persisted_ledger_fails_closed_on_truncated_jsonl_record(tmp_path: Path):
    path = tmp_path / "corrupt-events.jsonl"
    job = make_job()
    ledger = FactoryJobEventLedger(path)
    ledger.append(
        event_type="QUEUED",
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
        station="discovery",
        phase="DISCOVERY",
    )

    with path.open("a", encoding="utf-8") as handle:
        handle.write('{"sequence":')

    # Do not silently discard a partial tail or continue with incomplete history.
    with pytest.raises(json.JSONDecodeError):
        FactoryJobEventLedger(path)

def test_recovery_summary_requires_review_and_never_requests_auto_retry(tmp_path: Path):
    ledger = FactoryJobEventLedger(tmp_path / "recovery-events.jsonl")
    queued_job = make_job("JOB-RECOVERY-QUEUED")
    interrupted_job = make_job("JOB-RECOVERY-DISPATCHED")
    completed_job = make_job("JOB-RECOVERY-COMPLETED")
    failed_job = make_job("JOB-RECOVERY-FAILED")

    for job in (queued_job, interrupted_job, completed_job, failed_job):
        ledger.append(
            event_type="QUEUED",
            job_id=job.job_id,
            job_fingerprint=job.fingerprint,
        )
    for job in (interrupted_job, completed_job, failed_job):
        ledger.append(
            event_type="DISPATCHED",
            job_id=job.job_id,
            job_fingerprint=job.fingerprint,
            worker_id="W01",
        )
    ledger.append(
        event_type="COMPLETED",
        job_id=completed_job.job_id,
        job_fingerprint=completed_job.fingerprint,
        worker_id="W01",
    )
    ledger.append(
        event_type="FAILED",
        job_id=failed_job.job_id,
        job_fingerprint=failed_job.fingerprint,
        worker_id="W01",
    )

    summary = {item["job_id"]: item for item in ledger.recovery_summary()}
    assert summary[queued_job.job_id]["status"] == "QUEUED_REVIEW_REQUIRED"
    assert summary[queued_job.job_id]["action"] == "JOB_SPEC_AND_QUEUE_RECONSTRUCTION_REQUIRED"
    assert summary[interrupted_job.job_id]["status"] == "INTERRUPTED_REVIEW_REQUIRED"
    assert summary[interrupted_job.job_id]["action"] == "MANUAL_RECONCILIATION_REQUIRED"
    assert summary[completed_job.job_id]["status"] == "TERMINAL_COMPLETED"
    assert summary[completed_job.job_id]["action"] == "NO_RETRY"
    assert summary[failed_job.job_id]["status"] == "TERMINAL_FAILED"
    assert summary[failed_job.job_id]["action"] == "NO_RETRY"


def test_recovery_summary_rejects_job_fingerprint_drift():
    ledger = FactoryJobEventLedger(path=None)
    job = make_job("JOB-RECOVERY-FINGERPRINT")
    ledger.append(
        event_type="QUEUED",
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
    )
    ledger.append(
        event_type="DISPATCHED",
        job_id=job.job_id,
        job_fingerprint="b" * 64,
        worker_id="W01",
    )

    with pytest.raises(ValueError, match="fingerprint changed within ledger"):
        ledger.recovery_summary()



def test_recovery_summary_fails_closed_on_conflicting_terminal_events():
    ledger = FactoryJobEventLedger(path=None)
    job = make_job("JOB-RECOVERY-CONFLICTING-TERMINALS")

    for event_type in ("QUEUED", "DISPATCHED", "COMPLETED", "FAILED"):
        ledger.append(
            event_type=event_type,
            job_id=job.job_id,
            job_fingerprint=job.fingerprint,
            worker_id="W01" if event_type != "QUEUED" else None,
        )

    summary = ledger.recovery_summary()
    assert len(summary) == 1
    assert summary[0]["job_id"] == job.job_id
    assert summary[0]["status"] == "TERMINAL_CONFLICT_REVIEW_REQUIRED"
    assert summary[0]["action"] == "MANUAL_RECONCILIATION_REQUIRED"
    assert summary[0]["action"] != "NO_RETRY"
