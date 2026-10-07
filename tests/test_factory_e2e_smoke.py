import hashlib
import json

from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.orchestrator import FactoryOrchestrator
from strategy_factory.research_provenance import ResearchProvenanceStatus
from strategy_factory.research_record import ResearchRecord
from strategy_factory.starnet_adapter import build_world_state
from strategy_factory.test_contract import ExecutionSemantics
from strategy_factory.worker import FactoryWorker, FactoryWorkerFleet


def make_job():
    return ResearchJobSpec(
        job_id="E2E-SYNTH-001",
        strategy_id="SP2L-A",
        strategy_revision="REV-SYNTH-1",
        manifest_revision="MANIFEST-SYNTH-1",
        test_id="SYNTHETIC_RESEARCH_ONLY",
        dataset_id="SYNTHETIC-FIXTURE",
        data_revision="FIXTURE-1",
        dataset_fingerprint="1" * 64,
        execution_semantics=ExecutionSemantics.NEXT_BAR,
        parameters={"research_only": True},
    )


def make_pass_record(job, evidence_id):
    base = ResearchRecord(
        record_revision="RESEARCH-RECORD-1",
        run_id=job.job_id,
        run_fingerprint=job.fingerprint,
        evidence_id=evidence_id,
        evidence_fingerprint="2" * 64,
        snapshot_fingerprint="3" * 64,
        audit_fingerprint="4" * 64,
        strategy_id=job.strategy_id,
        strategy_revision=job.strategy_revision,
        manifest_revision=job.manifest_revision,
        dataset_id=job.dataset_id,
        dataset_role="DEVELOPMENT",
        data_revision=job.data_revision,
        dataset_fingerprint=job.dataset_fingerprint,
        execution_semantics=job.execution_semantics.value,
        provenance_status=ResearchProvenanceStatus.PASS,
        provenance_reasons=(),
        fingerprint="",
    )
    payload = json.dumps(
        base.as_dict(include_fingerprint=False),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return ResearchRecord(
        **base.as_dict(include_fingerprint=False),
        fingerprint=hashlib.sha256(payload).hexdigest(),
    )


def test_synthetic_factory_brain_runs_queue_to_world_handoff():
    events = FactoryJobEventLedger(path=None)
    fleet = FactoryWorkerFleet([FactoryWorker("W01")])
    orchestrator = FactoryOrchestrator(fleet=fleet, events=events)
    job = make_job()

    orchestrator.submit(job, station="discovery", phase="DISCOVERY")
    result = orchestrator.run_next(
        worker_id="W01",
        execute=lambda _job, _worker: {
            "output_artifact": "SYNTH-EVIDENCE-001",
            "detail": "Synthetic research smoke test completed",
        },
    )

    record = make_pass_record(job, result["output_artifact"])
    handoff = orchestrator.handoff(
        record=record,
        source_station="discovery",
        destination_station="stability",
        detail="Synthetic evidence-bound handoff",
    )

    world = build_world_state(
        [
            {
                "worker_id": "W01",
                "station": "discovery",
                "state": "COMPLETED",
                "progress": 100,
                "job_id": job.job_id,
                "job_type": job.test_id,
                "phase": "DISCOVERY",
                "output_artifact": result["output_artifact"],
            }
        ],
        events=events.entries(),
    )

    assert [e.event_type for e in events.entries()] == [
        "QUEUED",
        "DISPATCHED",
        "COMPLETED",
        "HANDOFF_ACCEPTED",
    ]
    assert handoff.output_artifact == "SYNTH-EVIDENCE-001"
    assert len(world.handoffs) == 1
    assert world.handoffs[0].source_station == "discovery"
    assert world.handoffs[0].destination_station == "stability"
    assert world.production_locked is True
    assert world.buy_sell_generation == 0
