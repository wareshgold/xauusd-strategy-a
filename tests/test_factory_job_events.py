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


def test_completion_journal_failure_requires_manual_reconciliation(monkeypatch):
    job = make_job("JOB-COMPLETION-PERSISTENCE-FAILURE")
    events = FactoryJobEventLedger(path=None)
    fleet = FactoryWorkerFleet([FactoryWorker("W01")])
    orchestrator = FactoryOrchestrator(fleet=fleet, events=events)
    orchestrator.submit(job, station="discovery", phase="DISCOVERY")

    original_append = events.append

    def fail_completion(**kwargs):
        if kwargs.get("event_type") == "COMPLETED":
            raise OSError("synthetic completion journal failure")
        return original_append(**kwargs)

    monkeypatch.setattr(events, "append", fail_completion)
    with pytest.raises(OSError, match="synthetic completion journal failure"):
        orchestrator.run_next(
            worker_id="W01",
            execute=lambda _job, _worker: {"output_artifact": "EVIDENCE-EXECUTED"},
        )

    # Execution happened, but its terminal event was not durable. The remaining
    # DISPATCHED journal history must require human reconciliation, never retry.
    assert orchestrator.pending() == ()
    assert fleet.get("W01").state == "COMPLETED"
    assert [event.event_type for event in events.entries()] == ["QUEUED", "DISPATCHED"]
    summary = events.recovery_summary()
    assert summary[0]["status"] == "INTERRUPTED_REVIEW_REQUIRED"
    assert summary[0]["action"] == "MANUAL_RECONCILIATION_REQUIRED"


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


def test_submit_journal_failure_does_not_create_phantom_pending_job(monkeypatch):
    job = make_job("JOB-SUBMIT-PERSISTENCE-FAILURE")
    events = FactoryJobEventLedger(path=None)
    fleet = FactoryWorkerFleet([FactoryWorker("W01")])
    orchestrator = FactoryOrchestrator(fleet=fleet, events=events)

    def fail_append(**_kwargs):
        raise OSError("synthetic journal failure")

    monkeypatch.setattr(events, "append", fail_append)
    with pytest.raises(OSError, match="synthetic journal failure"):
        orchestrator.submit(job, station="discovery", phase="DISCOVERY")

    assert orchestrator.pending() == ()
    assert events.entries() == ()
    assert fleet.get("W01").state == "IDLE"


def test_dispatch_journal_failure_preserves_queue_and_idle_worker(monkeypatch):
    job = make_job("JOB-DISPATCH-PERSISTENCE-FAILURE")
    events = FactoryJobEventLedger(path=None)
    fleet = FactoryWorkerFleet([FactoryWorker("W01")])
    orchestrator = FactoryOrchestrator(fleet=fleet, events=events)
    orchestrator.submit(job, station="discovery", phase="DISCOVERY")

    original_append = events.append

    def fail_dispatch(**kwargs):
        if kwargs.get("event_type") == "DISPATCHED":
            raise OSError("synthetic dispatch journal failure")
        return original_append(**kwargs)

    monkeypatch.setattr(events, "append", fail_dispatch)
    with pytest.raises(OSError, match="synthetic dispatch journal failure"):
        orchestrator.run_next(
            worker_id="W01",
            execute=lambda _job, _worker: {"output_artifact": "MUST-NOT-RUN"},
        )

    assert [item.job.job_id for item in orchestrator.pending()] == [job.job_id]
    assert fleet.get("W01").state == "IDLE"
    assert [event.event_type for event in events.entries()] == ["QUEUED"]


def test_failed_persistence_does_not_advance_in_memory_sequence(tmp_path: Path, monkeypatch):
    path = tmp_path / "blocked-events.jsonl"
    ledger = FactoryJobEventLedger(path)
    job = make_job("JOB-PERSISTENCE-FAILURE")
    original_open = Path.open

    def fail_append(self, *args, **kwargs):
        mode = args[0] if args else kwargs.get("mode", "r")
        if self == path and "a" in mode:
            raise OSError("synthetic disk write failure")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail_append)

    with pytest.raises(OSError, match="synthetic disk write failure"):
        ledger.append(
            event_type="QUEUED",
            job_id=job.job_id,
            job_fingerprint=job.fingerprint,
        )

    assert ledger.entries() == ()
    assert not path.exists()


def test_restart_reports_persisted_jobs_without_automatic_queue_replay(tmp_path: Path):
    path = tmp_path / "restart-recovery.jsonl"
    queued_job = make_job("JOB-RESTART-QUEUED")
    interrupted_job = make_job("JOB-RESTART-DISPATCHED")

    original = FactoryJobEventLedger(path)
    for job in (queued_job, interrupted_job):
        original.append(
            event_type="QUEUED",
            job_id=job.job_id,
            job_fingerprint=job.fingerprint,
            station="discovery",
            phase="DISCOVERY",
        )
    original.append(
        event_type="DISPATCHED",
        job_id=interrupted_job.job_id,
        job_fingerprint=interrupted_job.fingerprint,
        worker_id="W01",
        station="discovery",
        phase="DISCOVERY",
    )

    # Restart loads evidence only. It must not reconstruct or dispatch jobs
    # without an explicit, reviewed queue-reconstruction step.
    recovered_events = FactoryJobEventLedger(path)
    orchestrator = FactoryOrchestrator(
        fleet=FactoryWorkerFleet([FactoryWorker("W01")]),
        events=recovered_events,
    )

    assert orchestrator.pending() == ()
    summary = {item["job_id"]: item for item in recovered_events.recovery_summary()}
    assert summary[queued_job.job_id]["status"] == "QUEUED_REVIEW_REQUIRED"
    assert summary[queued_job.job_id]["action"] == "JOB_SPEC_AND_QUEUE_RECONSTRUCTION_REQUIRED"
    assert summary[interrupted_job.job_id]["status"] == "INTERRUPTED_REVIEW_REQUIRED"
    assert summary[interrupted_job.job_id]["action"] == "MANUAL_RECONCILIATION_REQUIRED"
    assert orchestrator.pending() == ()


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
    with pytest.raises(ValueError, match=r"invalid JSON at line 2.*automatic repair refused"):
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


@pytest.mark.parametrize(
    "history",
    [
        ("COMPLETED", "DISPATCHED", "QUEUED"),
        ("QUEUED", "QUEUED"),
        ("QUEUED", "DISPATCHED", "DISPATCHED"),
    ],
)
def test_recovery_summary_requires_manual_review_for_invalid_lifecycle_order(history):
    ledger = FactoryJobEventLedger(path=None)
    job = make_job("JOB-RECOVERY-INVALID-ORDER")

    for event_type in history:
        ledger.append(
            event_type=event_type,
            job_id=job.job_id,
            job_fingerprint=job.fingerprint,
            worker_id="W01" if event_type == "DISPATCHED" else None,
        )

    summary = ledger.recovery_summary()
    assert len(summary) == 1
    assert summary[0]["status"] == "LIFECYCLE_CONFLICT_REVIEW_REQUIRED"
    assert summary[0]["action"] == "MANUAL_RECONCILIATION_REQUIRED"


def test_recovery_summary_ignores_non_lifecycle_handoff_fingerprint():
    ledger = FactoryJobEventLedger(path=None)
    job = make_job("JOB-HANDOFF-001")
    for event_type in ("QUEUED", "DISPATCHED", "COMPLETED"):
        ledger.append(
            event_type=event_type,
            job_id=job.job_id,
            job_fingerprint=job.fingerprint,
            worker_id="W01" if event_type != "QUEUED" else None,
            station="discovery",
            phase="DISCOVERY",
            output_artifact="EVIDENCE-1" if event_type == "COMPLETED" else None,
        )

    # Handoff metadata is a separate provenance event, not a job lifecycle
    # transition; it must not corrupt the source job's recovery identity.
    ledger.append(
        event_type="HANDOFF_ACCEPTED",
        job_id=job.job_id,
        job_fingerprint="b" * 64,
        station="stability",
        phase="STABILITY",
        output_artifact="EVIDENCE-1",
    )

    summary = ledger.recovery_summary()
    assert len(summary) == 1
    assert summary[0]["job_id"] == job.job_id
    assert summary[0]["job_fingerprint"] == job.fingerprint
    assert summary[0]["status"] == "TERMINAL_COMPLETED"
    assert summary[0]["action"] == "NO_RETRY"


def test_job_event_ledger_rejects_non_hex_job_fingerprint():
    ledger = FactoryJobEventLedger(path=None)
    with pytest.raises(ValueError, match="lowercase hexadecimal SHA-256"):
        ledger.append(
            event_type="QUEUED",
            job_id="JOB-BAD-FINGERPRINT",
            job_fingerprint="g" * 64,
            station="discovery",
            phase="DISCOVERY",
        )

    assert ledger.entries() == ()


def test_persisted_journal_rejects_non_string_fingerprint_without_mutation(tmp_path: Path):
    path = tmp_path / "invalid-fingerprint-events.jsonl"
    job = make_job("JOB-INVALID-FINGERPRINT-TYPE")
    ledger = FactoryJobEventLedger(path)
    ledger.append(
        event_type="QUEUED",
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
        station="discovery",
        phase="DISCOVERY",
    )
    payload = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    payload["job_fingerprint"] = None
    path.write_text(json.dumps(payload) + "\\n", encoding="utf-8")
    original_bytes = path.read_bytes()

    with pytest.raises(ValueError, match="job_fingerprint must be lowercase hexadecimal SHA-256"):
        FactoryJobEventLedger(path)

    assert path.read_bytes() == original_bytes


def test_persisted_journal_rejects_non_integer_sequence_without_mutation(tmp_path: Path):
    path = tmp_path / "invalid-sequence-events.jsonl"
    job = make_job("JOB-INVALID-SEQUENCE-TYPE")
    ledger = FactoryJobEventLedger(path)
    ledger.append(
        event_type="QUEUED",
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
        station="discovery",
        phase="DISCOVERY",
    )
    payload = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    payload["sequence"] = "1"
    path.write_text(json.dumps(payload) + "\\n", encoding="utf-8")
    original_bytes = path.read_bytes()

    with pytest.raises(ValueError, match="factory job event identity is incomplete"):
        FactoryJobEventLedger(path)

    assert path.read_bytes() == original_bytes


def test_persisted_journal_rejects_truncated_tail_without_repair(tmp_path: Path):
    path = tmp_path / "truncated-events.jsonl"
    job = make_job("JOB-TRUNCATED-TAIL")
    ledger = FactoryJobEventLedger(path)
    ledger.append(
        event_type="QUEUED",
        job_id=job.job_id,
        job_fingerprint=job.fingerprint,
        station="discovery",
        phase="DISCOVERY",
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write('{"sequence":2,"event_type":"DISPATCHED"')

    original_bytes = path.read_bytes()
    with pytest.raises(ValueError, match=r"invalid JSON at line 2.*automatic repair refused"):
        FactoryJobEventLedger(path)

    # A suspicious tail is preserved for explicit/manual reconciliation.
    assert path.read_bytes() == original_bytes
