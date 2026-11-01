import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from strategy_factory.datasets import DatasetRegistry, fingerprint_dataset
from strategy_factory.mt5_dataset import MT5M1ArtifactExporter, load_existing_m1_snapshot
from strategy_factory.test_contract import DatasetRole, ExecutionSemantics, HistoricalTestSpec, TestDataset


def test_mt5_m1_exporter_freezes_artifact_and_registers_it(tmp_path, monkeypatch):
    artifact_path = tmp_path / "m1.json"
    artifact_bytes = b'{"schema_version":1,"research_only":true,"symbol":"XAUUSD.ecn","timeframe":"M1","window_utc":{"start":"2026-10-05T00:00:00Z","end":"2026-10-07T05:30:00Z"},"bars":[{"time":1791158400,"open":4000.0,"high":4001.0,"low":3999.0,"close":4000.5,"tick_volume":10,"spread":2,"real_volume":0}]}'
    artifact_path.write_bytes(artifact_bytes)
    sha = hashlib.sha256(artifact_bytes).hexdigest()

    def fake_run(*args, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({
                "status": "COMPLETE",
                "artifact": str(artifact_path),
                "symbol": "XAUUSD.ecn",
                "timeframe": "M1",
                "sha256": sha,
            }),
            stderr="",
        )

    import strategy_factory.mt5_dataset as module
    monkeypatch.setattr(module.subprocess, "run", fake_run)

    exporter = MT5M1ArtifactExporter(
        script_path=tmp_path / "export_sp2l_v3_xauusd_m1_artifact.py",
        mt5_path="MT5",
        output_path=artifact_path,
    )
    snapshot = exporter.export()

    dataset = TestDataset(
        dataset_id="MT5-M1-FACTORY-001",
        role=DatasetRole.DEVELOPMENT,
        data_revision="MT5-M1-20261007",
        start="2026-10-05T00:00:00Z",
        end="2026-10-07T05:30:00Z",
        source="MT5:XAUUSD.ecn:M1",
    )
    registry = DatasetRegistry()
    snapshot.register(registry, type("Spec", (), {"dataset": dataset})(), lock=True)

    identity = registry.get(dataset.dataset_id)
    assert identity.artifact == snapshot.artifact
    assert identity.fingerprint == fingerprint_dataset(dataset, sha)
    assert identity.locked is True


def test_existing_m1_csv_snapshot_preserves_source_bytes_and_hash(tmp_path):
    artifact_path = tmp_path / "xauusd_ecn_m1.csv"
    artifact_bytes = (
        "time_epoch_seconds,time_utc_iso,open,high,low,close,tick_volume,spread,real_volume\\n"
        "1791158400,2026-10-05T00:00:00+00:00,4000,4001,3999,4000.5,10,2,0\\n"
        "1791158460,2026-10-05T00:01:00+00:00,4000.5,4002,4000,4001.5,12,2,0\\n"
    ).encode("utf-8")
    artifact_path.write_bytes(artifact_bytes)
    sha = hashlib.sha256(artifact_bytes).hexdigest()
    dataset = TestDataset(
        dataset_id="MT5-M1-CSV-EXISTING",
        role=DatasetRole.DEVELOPMENT,
        data_revision="MT5-M1-CSV-EXISTING",
        start="2026-10-05T00:00:00Z",
        end="2026-10-05T00:01:00Z",
        source="MT5:XAUUSD.ecn:M1",
    )
    spec = HistoricalTestSpec(
        test_id="MT5-M1-CSV-EXISTING-TEST",
        strategy_id="SP2L-A",
        strategy_revision="SP2L-V3",
        dataset=dataset,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
    )

    snapshot = load_existing_m1_snapshot(
        artifact_path,
        expected_sha256=sha,
        spec=spec,
    )
    assert snapshot.artifact.format == "csv"
    assert snapshot.dataset_content_sha256 == sha
    assert snapshot.payload["m1_integrity"]["bars"] == 2
    assert artifact_path.read_bytes() == artifact_bytes
