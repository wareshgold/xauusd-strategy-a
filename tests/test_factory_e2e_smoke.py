import hashlib

import pytest

from strategy_factory.adapter import build_execution_receipt
from strategy_factory.datasets import DatasetRegistry, fingerprint_dataset
from strategy_factory.evidence import EvidenceLedger
from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.orchestrator import (
    FactoryOrchestrator,
    RunnerExecutionContext,
    build_runner_executor,
)
from strategy_factory.research_provenance import ResearchProvenanceStatus
from strategy_factory.research_record import ResearchRecordLedger
from strategy_factory.runs import ResearchRunLedger
from strategy_factory.snapshot import ReadinessSnapshot
from strategy_factory.starnet_adapter import build_world_state
from strategy_factory.test_contract import (
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
)
from strategy_factory.usage import DatasetUsageLedger
from strategy_factory.worker import FactoryWorker, FactoryWorkerFleet
from strategy_factory.metrics import ResearchMetrics


class DeterministicSyntheticAdapter:
    """Synthetic execution engine used only to prove Factory wiring.

    It returns a fixed receipt and never defines Strategy A geometry.
    """

    engine_revision = "SYNTHETIC-ENGINE-1"

    def __init__(self, input_fingerprint: str) -> None:
        self.input_fingerprint = input_fingerprint

    def execute(self, spec: HistoricalTestSpec):
        return build_execution_receipt(
            execution_id=f"EXEC-{spec.test_id}",
            spec=spec,
            engine_revision=self.engine_revision,
            input_fingerprint=self.input_fingerprint,
            metrics=ResearchMetrics(
                trades=4,
                decisive_trades=4,
                wins=3,
                losses=1,
                ambiguous=0,
                win_rate=0.75,
                net_r=2.0,
                profit_factor=3.0,
                max_drawdown_r=1.0,
                gross_profit_r=3.0,
                gross_loss_r=-1.0,
            ),
        )


def make_spec_and_job():
    payload = b"SP2L-FACTORY-SYNTHETIC-FIXTURE-V1\\n"
    content_sha256 = hashlib.sha256(payload).hexdigest()
    dataset = TestDataset(
        dataset_id="SYNTHETIC-FIXTURE-001",
        role=DatasetRole.DEVELOPMENT,
        data_revision="FIXTURE-1",
        start="2026-01-01T00:00:00Z",
        end="2026-01-02T00:00:00Z",
        source="synthetic://sp2l/factory-e2e-v1",
    )
    spec = HistoricalTestSpec(
        test_id="SYNTHETIC_FACTORY_E2E_V1",
        strategy_id="SP2L-A",
        strategy_revision="REV-SYNTH-1",
        dataset=dataset,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"research_only": True},
    )
    dataset_fingerprint = fingerprint_dataset(dataset, content_sha256)
    job = ResearchJobSpec.from_test_spec(
        spec,
        manifest_revision="MANIFEST-SYNTH-1",
        dataset_fingerprint=dataset_fingerprint,
        job_id="E2E-SYNTH-001",
    )
    return payload, content_sha256, spec, job


def make_snapshot(spec: HistoricalTestSpec) -> ReadinessSnapshot:
    source_ledger = {"entries": [], "resolution_state": "SYNTHETIC_ONLY"}
    source_readiness = {"status": "SYNTHETIC_ONLY"}
    passport_eligibility = {"status": "SYNTHETIC_ONLY"}
    manifest_fingerprint = "1" * 64
    passport_fingerprint = "2" * 64
    payload = ReadinessSnapshot._fingerprint_payload(
        snapshot_revision="READINESS-SNAPSHOT-SYNTH-1",
        strategy_id=spec.strategy_id,
        manifest_revision="MANIFEST-SYNTH-1",
        manifest_fingerprint=manifest_fingerprint,
        passport_fingerprint=passport_fingerprint,
        source_ledger=source_ledger,
        source_readiness=source_readiness,
        passport_eligibility=passport_eligibility,
    )
    return ReadinessSnapshot(
        snapshot_revision="READINESS-SNAPSHOT-SYNTH-1",
        strategy_id=spec.strategy_id,
        manifest_revision="MANIFEST-SYNTH-1",
        manifest_fingerprint=manifest_fingerprint,
        passport_fingerprint=passport_fingerprint,
        source_ledger=source_ledger,
        source_readiness=source_readiness,
        passport_eligibility=passport_eligibility,
        fingerprint=hashlib.sha256(payload).hexdigest(),
    )


def build_runner(spec, content_sha256):
    registry = DatasetRegistry()
    registry.register(spec.dataset, content_sha256)
    usage = DatasetUsageLedger(registry)
    runs = ResearchRunLedger(registry, usage)
    evidence = EvidenceLedger(runs)
    records = ResearchRecordLedger()
    from strategy_factory.runner import ResearchJobRunner

    runner = ResearchJobRunner(runs=runs, evidence=evidence, records=records)
    adapter = DeterministicSyntheticAdapter(content_sha256)
    return runner, adapter, make_snapshot(spec), records


def test_synthetic_factory_brain_runs_adapter_to_evidence_record_and_handoff():
    payload, content_sha256, spec, job = make_spec_and_job()
    assert hashlib.sha256(payload).hexdigest() == content_sha256

    runner, adapter, snapshot, records = build_runner(spec, content_sha256)
    events = FactoryJobEventLedger(path=None)
    fleet = FactoryWorkerFleet([FactoryWorker("W01")])
    orchestrator = FactoryOrchestrator(fleet=fleet, events=events)

    orchestrator.submit(job, station="discovery", phase="DISCOVERY")
    context = RunnerExecutionContext(
        spec=spec,
        adapter=adapter,
        snapshot=snapshot,
        observed_content_sha256=content_sha256,
        evidence_id="SYNTH-EVIDENCE-001",
    )
    result = orchestrator.run_next(
        worker_id="W01",
        execute=build_runner_executor(runner, context),
    )

    assert result["accepted"] is True
    assert result["run_id"] == job.job_id
    assert result["evidence_id"] == "SYNTH-EVIDENCE-001"
    assert result["output_artifact"] == "SYNTH-EVIDENCE-001"

    record = records.get(job.job_id)
    assert record.provenance_status is ResearchProvenanceStatus.PASS
    assert record.evidence_id == "SYNTH-EVIDENCE-001"
    record.validate()

    handoff = orchestrator.handoff(
        record=record,
        source_station="discovery",
        destination_station="stability",
        detail="Synthetic evidence-bound handoff",
    )
    handoff.validate()

    world = build_world_state(
        [
            {
                "worker_id": "W01",
                "station": "discovery",
                "state": "COMPLETED",
                "progress": 100,
                "job_id": job.job_id,
                "job_type": spec.test_id,
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
    assert handoff.output_artifact == record.evidence_id
    assert handoff.source_event_fingerprint == events.entries()[2].event_fingerprint
    assert len(world.handoffs) == 1
    assert world.handoffs[0].source_station == "discovery"
    assert world.handoffs[0].destination_station == "stability"
    assert world.handoffs[0].output_artifact == record.evidence_id
    assert world.production_locked is True
    assert world.buy_sell_generation == 0


def test_synthetic_factory_brain_rejects_adapter_semantics_drift():
    _payload, content_sha256, spec, job = make_spec_and_job()

    class DriftedAdapter(DeterministicSyntheticAdapter):
        def execute(self, declared_spec):
            receipt = super().execute(declared_spec)
            return type(receipt)(
                execution_id=receipt.execution_id,
                test_id=receipt.test_id,
                strategy_revision=receipt.strategy_revision,
                execution_semantics=ExecutionSemantics.TICK_FEASIBLE,
                engine_revision=receipt.engine_revision,
                input_fingerprint=receipt.input_fingerprint,
                completed=receipt.completed,
                metrics=receipt.metrics,
            )

    runner, _adapter, snapshot, _records = build_runner(spec, content_sha256)
    events = FactoryJobEventLedger(path=None)
    fleet = FactoryWorkerFleet([FactoryWorker("W01")])
    orchestrator = FactoryOrchestrator(fleet=fleet, events=events)
    orchestrator.submit(job, station="discovery", phase="DISCOVERY")

    context = RunnerExecutionContext(
        spec=spec,
        adapter=DriftedAdapter(content_sha256),
        snapshot=snapshot,
        observed_content_sha256=content_sha256,
        evidence_id="SYNTH-EVIDENCE-DRIFT",
    )

    with pytest.raises(Exception, match="execution adapter failed"):
        orchestrator.run_next(
            worker_id="W01",
            execute=build_runner_executor(runner, context),
        )

    assert [e.event_type for e in events.entries()] == [
        "QUEUED",
        "DISPATCHED",
        "FAILED",
    ]
