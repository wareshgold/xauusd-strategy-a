import json
from pathlib import Path
from types import SimpleNamespace

import strategy_factory.discovery_adapter as module
from strategy_factory.discovery_adapter import DiscoveryMatrixAdapter
from strategy_factory.test_contract import (
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
)


def make_spec() -> HistoricalTestSpec:
    return HistoricalTestSpec(
        test_id="DISCOVERY_ADAPTER_TEST",
        strategy_id="SP2L-A",
        strategy_revision="SP2L-V3",
        dataset=TestDataset(
            dataset_id="DISCOVERY-DATASET",
            role=DatasetRole.DEVELOPMENT,
            data_revision="M1-TEST-1",
            start="2026-10-05T00:00:00Z",
            end="2026-10-07T00:00:00Z",
            source="synthetic://discovery-adapter",
        ),
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"research_only": True},
    )


def test_discovery_adapter_consumes_declared_variant_without_defining_geometry(tmp_path, monkeypatch):
    script = tmp_path / "run_sp2l_v3_xauusd_discovery_matrix.py"
    script.write_text("# existing Discovery Matrix placeholder\n", encoding="utf-8")

    bars_artifact = tmp_path / "m1.json"
    bars_artifact.write_bytes(b'{"schema_version":1,"bars":[{"time":1,"open":1,"high":1,"low":1,"close":1,"tick_volume":1,"spread":0,"real_volume":1}],"research_only":true,"symbol":"XAUUSD.ecn","timeframe":"M1","window_utc":{"start":"2026-10-05T00:00:00Z","end":"2026-10-07T00:00:00Z"}}')
    import hashlib
    dataset_sha = hashlib.sha256(bars_artifact.read_bytes()).hexdigest()

    matrix_path = tmp_path / "discovery.json"
    matrix_path.write_text(
        json.dumps(
            {
                "research_only": True,
                "dataset_provenance": {"content_sha256": dataset_sha},
                "matrix": [
                    {
                        "name": "RR2_ACT10_D2",
                        "signals": 4,
                        "decisive": 3,
                        "wins": 2,
                        "losses": 1,
                        "ambiguous": 1,
                        "net_R": 1.5,
                        "profit_factor": 3.0,
                        "max_drawdown_R": 1.0,
                    }
                ],
                "trades": [
                    {"variant": "RR2_ACT10_D2", "ambiguous": False, "realized_R": 2.0},
                    {"variant": "RR2_ACT10_D2", "ambiguous": False, "realized_R": -0.5},
                    {"variant": "RR2_ACT10_D2", "ambiguous": False, "realized_R": 0.0},
                    {"variant": "RR2_ACT10_D2", "ambiguous": True, "realized_R": None},
                ],
            }
        ),
        encoding="utf-8",
    )

    def fake_run(*args, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps(
                {
                    "status": "COMPLETE",
                    "json": str(matrix_path),
                    "sha256": "a" * 64,
                }
            ),
            stderr="",
        )

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    receipt = DiscoveryMatrixAdapter(
        script_path=script,
        mt5_path=r"C:\Program Files\Otet Group MT5 Terminal\terminal64.exe",
        variant_name="RR2_ACT10_D2",
        bars_artifact_path=bars_artifact,
    ).execute(make_spec())

    assert receipt.test_id == "DISCOVERY_ADAPTER_TEST"
    assert receipt.execution_semantics is ExecutionSemantics.BAR_CLOSE_RESEARCH
    assert receipt.metrics.trades == 4
    assert receipt.metrics.decisive_trades == 3
    assert receipt.metrics.wins == 2
    assert receipt.metrics.losses == 1
    assert receipt.metrics.ambiguous == 1
    assert receipt.metrics.net_r == 1.5
    assert receipt.metrics.gross_profit_r == 2.0
    assert receipt.metrics.gross_loss_r == -0.5
    assert receipt.metrics.profit_factor == 3.0


def test_discovery_adapter_rejects_non_research_output(tmp_path, monkeypatch):
    script = tmp_path / "run_sp2l_v3_xauusd_discovery_matrix.py"
    script.write_text("placeholder\n", encoding="utf-8")

    def fake_run(*args, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"status": "COMPLETE", "json": "unused"}),
            stderr="",
        )

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    adapter = DiscoveryMatrixAdapter(
        script_path=script,
        mt5_path="MT5",
        variant_name="RR2_ACT10_D2",
    )

    try:
        adapter.execute(make_spec())
    except Exception as exc:
        assert "output JSON not found" in str(exc)
    else:
        raise AssertionError("expected missing M1 dataset artifact to be rejected")
