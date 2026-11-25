from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace
import json

import pytest

import strategy_factory.stability_adapter as module
from strategy_factory.stability_adapter import StabilityAdapterError, StabilityMatrixAdapter
from strategy_factory.test_contract import (
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
)


def _spec():
    return HistoricalTestSpec(
        test_id="STABILITY-SECONDARY-ARTIFACT",
        strategy_id="SP2L-A",
        strategy_revision="REV-TEST",
        dataset=TestDataset(
            dataset_id="M1-DATASET",
            role=DatasetRole.DEVELOPMENT,
            data_revision="M1-REV",
            start="2026-10-05T00:00:00Z",
            end="2026-10-07T05:30:00Z",
            source="FIXTURE",
        ),
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"research_only": True},
    )


def test_stability_adapter_rejects_discovery_json_mutation_during_execution(tmp_path, monkeypatch):
    dataset_path = tmp_path / "m1.json"
    dataset_path.write_bytes(b'{"bars":[]}')
    dataset_sha = hashlib.sha256(dataset_path.read_bytes()).hexdigest()

    discovery_path = tmp_path / "discovery.json"
    discovery_path.write_text(
        json.dumps({
            "research_only": True,
            "dataset_provenance": {
                "content_sha256": dataset_sha,
                "artifact_id": "M1-ARTIFACT",
            },
            "trades": [],
        }),
        encoding="utf-8",
    )
    discovery_raw = discovery_path.read_bytes()
    discovery_sha = hashlib.sha256(discovery_raw).hexdigest()

    script_path = tmp_path / "stability.py"
    script_path.write_text("# fixture", encoding="utf-8")

    adapter = StabilityMatrixAdapter(
        script_path=script_path,
        discovery_json_path=discovery_path,
        dataset_artifact_path=dataset_path,
        expected_dataset_content_sha256=dataset_sha,
        expected_dataset_artifact_id="M1-ARTIFACT",
        expected_discovery_artifact_id="DISCOVERY-MATRIX-STABILITY-SECONDARY-ARTIFACT-RR2_ACT10_D2",
        expected_discovery_content_sha256=discovery_sha,
        expected_discovery_byte_size=len(discovery_raw),
    )

    def mutate_during_execution(*args, **kwargs):
        discovery_path.write_bytes(discovery_raw + b" ")
        return SimpleNamespace(returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(module.subprocess, "run", mutate_during_execution)

    with pytest.raises(StabilityAdapterError, match="Discovery JSON changed while Stability was running"):
        adapter.execute(_spec())
