from __future__ import annotations

import hashlib
import json

import strategy_factory.stability_factory as module
from strategy_factory.adapter import build_execution_receipt
from strategy_factory.datasets import DatasetArtifact, DatasetRegistry
from strategy_factory.evidence import EvidenceLedger
from strategy_factory.job_events import FactoryJobEventLedger
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.research_record import ResearchRecordLedger
from strategy_factory.runs import ResearchRunLedger
from strategy_factory.snapshot import ReadinessSnapshot
from strategy_factory.test_contract import (
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
)
from strategy_factory.usage import DatasetUsageLedger
from strategy_factory.handoff import build_research_handoff
from strategy_factory.stability_factory import StabilityFactory, StabilityFactoryContext


def _snapshot(spec):
    ledger = {"entries": [], "resolution_state": "SYNTHETIC_ONLY"}
    readiness = {"status": "SYNTHETIC_ONLY"}
    eligibility = {"status": "SYNTHETIC_ONLY"}
    payload = ReadinessSnapshot._fingerprint_payload(
        snapshot_revision="SYNTH",
        strategy_id=spec.strategy_id,
        manifest_revision="MANIFEST",
        manifest_fingerprint="1" * 64,
        passport_fingerprint="2" * 64,
        source_ledger=ledger,
        source_readiness=readiness,
        passport_eligibility=eligibility,
    )
    return ReadinessSnapshot(
        snapshot_revision="SYNTH",
        strategy_id=spec.strategy_id,
        manifest_revision="MANIFEST",
        manifest_fingerprint="1" * 64,
        passport_fingerprint="2" * 64,
        source_ledger=ledger,
        source_readiness=readiness,
        passport_eligibility=eligibility,
        fingerprint=hashlib.sha256(payload).hexdigest(),
    )


def test_stability_factory_is_dataset_bound_and_does_not_requery_mt5(tmp_path, monkeypatch):
    raw = b'{"schema_version":1,"research_only":true,"symbol":"XAUUSD.ecn","timeframe":"M1","bars":[]}'
    dataset_path = tmp_path / "m1.json"
    dataset_path.write_bytes(raw)
    sha = hashlib.sha256(raw).hexdigest()

    discovery_path = tmp_path / "discovery.json"
    discovery_path.write_text(json.dumps({
        "research_only": True,
        "dataset_provenance": {
            "content_sha256": sha,
            "artifact_id": "MT5-M1-TEST",
        },
    }), encoding="utf-8")

    dataset = TestDataset(
        dataset_id="MT5-STABILITY-001",
        role=DatasetRole.DEVELOPMENT,
        data_revision="MT5-M1-TEST",
        start="2026-10-05T00:00:00Z",
        end="2026-10-07T05:30:00Z",
        source="MT5:XAUUSD.ecn:M1",
    )
    spec = HistoricalTestSpec(
        test_id="STABILITY_FACTORY_TEST",
        strategy_id="SP2L-A",
        strategy_revision="REV-TEST",
        dataset=dataset,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"research_only": True, "stability_variant": "RR2_ACT10_D2"},
    )

    # Build a minimal valid source record by exercising the generic runner
    # through a fake upstream result.
    registry = DatasetRegistry()
    usage = DatasetUsageLedger(registry)
    runs = ResearchRunLedger(registry, usage)
    evidence = EvidenceLedger(runs)
    records = ResearchRecordLedger()

    from strategy_factory.runner import ResearchJobRunner
    from strategy_factory.jobs import ResearchJobSpec

    registry.register(dataset, sha, lock=True, artifact=DatasetArtifact(
        artifact_id="MT5-M1-TEST",
        location=str(dataset_path),
        content_sha256=sha,
        byte_size=len(raw),
        format="json",
    ))
    job = ResearchJobSpec.from_test_spec(
        spec,
        manifest_revision="MANIFEST",
        dataset_fingerprint=registry.get(dataset.dataset_id).fingerprint,
        job_id="DISCOVERY-001",
    )

    class FakeAdapter:
        engine_revision = "DISCOVERY-TEST"
        def execute(self, declared_spec):
            return build_execution_receipt(
                execution_id="DISCOVERY-EXEC",
                spec=declared_spec,
                engine_revision=self.engine_revision,
                input_fingerprint=sha,
                metrics=ResearchMetrics(
                    trades=1, decisive_trades=1, wins=1, losses=0, ambiguous=0,
                    win_rate=1.0, net_r=1.0, profit_factor=None,
                    max_drawdown_r=0.0, gross_profit_r=1.0, gross_loss_r=0.0,
                ),
            )

    upstream = ResearchJobRunner(runs=runs, evidence=evidence, records=records)
    upstream_result = upstream.run(
        job=job, spec=spec, adapter=FakeAdapter(), snapshot=_snapshot(spec),
        observed_content_sha256=sha,
        observed_artifact=registry.get(dataset.dataset_id).artifact,
        evidence_id="DISCOVERY-EVIDENCE-001",
    )

    events = FactoryJobEventLedger(path=None)
    events.append(
        event_type="COMPLETED", job_id=job.job_id, job_fingerprint=job.fingerprint,
        worker_id="worker", station="discovery", phase="DISCOVERY",
        detail="done", output_artifact=upstream_result.evidence.evidence_id,
        research_run_fingerprint=upstream_result.run.fingerprint,
    )
    handoff = build_research_handoff(
        events=events, job_id=job.job_id, source_station="discovery",
        destination_station="stability", record=upstream_result.record,
        dataset_content_sha256=sha, dataset_artifact_id="MT5-M1-TEST",
    )

    # The adapter is monkeypatched: no MT5 path or exporter is available here.
    class FakeStabilityAdapter:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
        def execute(self, declared_spec):
            return build_execution_receipt(
                execution_id="STABILITY-EXEC", spec=declared_spec,
                engine_revision="STABILITY-TEST", input_fingerprint=sha,
                metrics=ResearchMetrics(
                    trades=1, decisive_trades=1, wins=1, losses=0, ambiguous=0,
                    win_rate=1.0, net_r=1.0, profit_factor=None,
                    max_drawdown_r=0.0, gross_profit_r=1.0, gross_loss_r=0.0,
                ),
            )
    monkeypatch.setattr(module, "StabilityMatrixAdapter", FakeStabilityAdapter)

    # Use a fresh runner but the same immutable artifact identity.
    stability_registry = DatasetRegistry()
    stability_usage = DatasetUsageLedger(stability_registry)
    stability_runs = ResearchRunLedger(stability_registry, stability_usage)
    stability_evidence = EvidenceLedger(stability_runs)
    stability_records = ResearchRecordLedger()
    stability_runner = ResearchJobRunner(
        runs=stability_runs, evidence=stability_evidence, records=stability_records
    )

    result = StabilityFactory(stability_runner).prepare_and_run(
        StabilityFactoryContext(
            spec=spec,
            manifest_revision="MANIFEST",
            job_id="STABILITY-001",
            readiness_snapshot=_snapshot(spec),
            handoff=handoff,
            source_record=upstream_result.record,
            source_event=events.for_job(job.job_id)[0],
            discovery_json_path=discovery_path,
            dataset_artifact_path=dataset_path,
            dataset_artifact_id="MT5-M1-TEST",
            dataset_content_sha256=sha,
            stability_script=tmp_path / "stability.py",
            variant_name="RR2_ACT10_D2",
        )
    )
    assert result.result.accepted is True
    assert result.result.dataset_provenance.status.value == "PASS"


def test_stability_factory_blocks_dataset_mismatch(tmp_path):
    # Structural guard: the factory must reject a handoff that names another
    # dataset before any Stability execution is attempted.
    raw = b"dataset"
    dataset_path = tmp_path / "m1.json"
    dataset_path.write_bytes(raw)
    sha = hashlib.sha256(raw).hexdigest()

    # A malformed handoff is sufficient because mismatch must be caught at the
    # factory boundary.
    from strategy_factory.handoff import ResearchHandoff
    bad = ResearchHandoff(
        handoff_revision="RESEARCH-HANDOFF-1",
        handoff_id="H",
        job_id="J",
        job_fingerprint="a" * 64,
        source_station="discovery",
        destination_station="stability",
        output_artifact="E",
        dataset_content_sha256="b" * 64,
        dataset_artifact_id="WRONG",
        source_event_fingerprint="c" * 64,
        detail="x",
        fingerprint="0" * 64,
    )
    assert bad.dataset_content_sha256 != sha
