import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from strategy_factory.datasets import DatasetRegistry, fingerprint_dataset
from strategy_factory.mt5_dataset import MT5M1ArtifactExporter
from strategy_factory.test_contract import DatasetRole, TestDataset


def test_mt5_m1_exporter_freezes_artifact_and_registers_it(tmp_path, monkeypatch):
    artifact_path = tmp_path / "m1.json"
    artifact_bytes = b'{"schema_version":1,"research_only":true,"symbol":"XAUUSD.ecn","timeframe":"M1","bars":[]}'
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
