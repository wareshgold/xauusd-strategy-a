import hashlib
from pathlib import Path

import strategy_factory.discovery_factory as module
from strategy_factory.adapter import build_execution_receipt
from strategy_factory.datasets import DatasetArtifact, DatasetRegistry, fingerprint_dataset
from strategy_factory.discovery_factory import DiscoveryFactory, DiscoveryFactoryContext
from strategy_factory.evidence import EvidenceLedger
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
from strategy_factory.mt5_dataset import MT5M1Snapshot


def make_snapshot(spec):
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


def test_discovery_factory_binds_mt5_artifact_to_runner(tmp_path, monkeypatch):
    raw = (
        b"time_epoch_seconds,time_utc_iso,open,high,low,close,tick_volume,spread,real_volume\\n"
        b"1791158400,2026-10-05T00:00:00+00:00,4000,4001,3999,4000.5,10,2,0\\n"
    )
    artifact_path = tmp_path / "m1.csv"
    artifact_path.write_bytes(raw)
    sha = hashlib.sha256(raw).hexdigest()
    entry_path = tmp_path / "v3_entries.csv"
    entry_path.write_text(
        "strategy,variant,direction,setup_time_utc,entry_time_utc,entry_proxy,sl_initial,target,risk_price,exit_time_utc,exit_price,exit_reason,status,r_multiple\n"
        "A,A_TRAIL_0.40_ACTIVATED_PROXY_V3,BUY,2026-10-05T00:00:00Z,2026-10-05T00:00:00Z,4000,3999,4002,1,2026-10-05T00:01:00Z,4001,TP,CLOSED,1\n",
        encoding="utf-8",
    )
    entry_sha = hashlib.sha256(entry_path.read_bytes()).hexdigest()
    dataset = TestDataset(
        dataset_id="MT5-FACTORY-001",
        role=DatasetRole.DEVELOPMENT,
        data_revision="MT5-M1-TEST",
        start="2026-10-05T00:00:00Z",
        end="2026-10-07T05:30:00Z",
        source="MT5:XAUUSD.ecn:M1",
    )
    spec = HistoricalTestSpec(
        test_id="DISCOVERY_FACTORY_TEST",
        strategy_id="SP2L-A",
        strategy_revision="REV-TEST",
        dataset=dataset,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"research_only": True, "discovery_variant": "RR2_ACT10_D2"},
    )

    class FakeExporter:
        def __init__(self, **kwargs):
            pass

        def export(self):
            raise AssertionError("existing M1 artifact path must bypass MT5 export")

    class FakeAdapter:
        engine_revision = "DISCOVERY-TEST"

        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def execute(self, declared_spec):
            dataset_sha = hashlib.sha256(
                Path(self.kwargs["bars_artifact_path"]).read_bytes()
            ).hexdigest()
            input_fingerprint = hashlib.sha256(
                f"FAKE-DISCOVERY:{declared_spec.test_id}:{dataset_sha}".encode()
            ).hexdigest()
            return build_execution_receipt(
                execution_id="DISCOVERY-TEST-EXEC",
                spec=declared_spec,
                engine_revision=self.engine_revision,
                input_fingerprint=input_fingerprint,
                metrics=ResearchMetrics(
                    trades=2,
                    decisive_trades=2,
                    wins=1,
                    losses=1,
                    ambiguous=0,
                    win_rate=0.5,
                    net_r=0.0,
                    profit_factor=1.0,
                    max_drawdown_r=1.0,
                    gross_profit_r=1.0,
                    gross_loss_r=-1.0,
                ),
                receipt_schema_version=2,
                dataset_content_sha256=dataset_sha,
            )

    monkeypatch.setattr(module, "MT5M1ArtifactExporter", FakeExporter)
    monkeypatch.setattr(module, "DiscoveryMatrixAdapter", FakeAdapter)

    registry = DatasetRegistry()
    usage = DatasetUsageLedger(registry)
    runs = ResearchRunLedger(registry, usage)
    evidence = EvidenceLedger(runs)
    records = ResearchRecordLedger()
    from strategy_factory.runner import ResearchJobRunner
    runner = ResearchJobRunner(runs=runs, evidence=evidence, records=records)

    output = DiscoveryFactory(runner).prepare_and_run(
        DiscoveryFactoryContext(
            spec=spec,
            manifest_revision="MANIFEST",
            job_id="DISCOVERY-FACTORY-001",
            readiness_snapshot=make_snapshot(spec),
            mt5_path="MT5",
            exporter_script=tmp_path / "export.py",
            artifact_path=artifact_path,
            discovery_script=tmp_path / "discovery.py",
            evidence_id="DISCOVERY-EVIDENCE-001",
            source_artifact_path=artifact_path,
            source_artifact_sha256=sha,
            entry_population_artifact_path=entry_path,
            entry_population_sha256=entry_sha,
        )
    )

    assert output.result.accepted is True
    assert output.result.dataset_provenance.status.value == "PASS"
    assert output.result.run.artifact_id == f"MT5-M1-{sha[:16]}"
    assert output.result.record.provenance_status.value == "PASS"
    assert output.job.dataset_fingerprint == fingerprint_dataset(dataset, sha)
    assert output.result.receipt.input_fingerprint == hashlib.sha256(
        f"FAKE-DISCOVERY:{spec.test_id}:{sha}".encode()
    ).hexdigest()
