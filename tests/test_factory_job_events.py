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
