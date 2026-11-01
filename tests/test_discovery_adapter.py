import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import strategy_factory.discovery_adapter as module
from strategy_factory.discovery_adapter import DiscoveryMatrixAdapter
from strategy_factory.frozen_entry_population import ENTRY_FIELDS
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
            end="2026-10-07T05:30:00Z",
            source="synthetic://discovery-adapter",
        ),
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={"research_only": True},
    )


def test_discovery_adapter_consumes_declared_variant_without_defining_geometry(tmp_path, monkeypatch):
    script = tmp_path / "run_sp2l_v3_xauusd_discovery_matrix.py"
    script.write_text("# existing Discovery Matrix placeholder\n", encoding="utf-8")

    bars_artifact = tmp_path / "m1.json"
    bars_artifact.write_bytes(b'{"schema_version":1,"bars":[{"time":1791158400,"open":1,"high":1,"low":1,"close":1,"tick_volume":1,"spread":0,"real_volume":1}],"research_only":true,"symbol":"XAUUSD.ecn","timeframe":"M1","window_utc":{"start":"2026-10-05T00:00:00Z","end":"2026-10-07T05:30:00Z"}}')
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

    bars_artifact = tmp_path / "m1.json"
    bars_artifact.write_text(
        json.dumps({
            "schema_version": 1,
            "research_only": True,
            "symbol": "XAUUSD.ecn",
            "timeframe": "M1",
            "window_utc": {
                "start": "2026-10-05T00:00:00Z",
                "end": "2026-10-07T05:30:00Z",
            },
            "bars": [{
                "time": 1791158400,
                "open": 1,
                "high": 1,
                "low": 1,
                "close": 1,
                "tick_volume": 1,
                "spread": 0,
                "real_volume": 1,
            }],
        }),
        encoding="utf-8",
    )

    adapter = DiscoveryMatrixAdapter(
        script_path=script,
        mt5_path="MT5",
        variant_name="RR2_ACT10_D2",
        bars_artifact_path=bars_artifact,
    )

    try:
        adapter.execute(make_spec())
    except Exception as exc:
        assert "output JSON not found" in str(exc)
    else:
        raise AssertionError("expected missing M1 dataset artifact to be rejected")


def test_discovery_adapter_rejects_artifact_mutation_during_run(tmp_path, monkeypatch):
    script = tmp_path / "run_sp2l_v3_xauusd_discovery_matrix.py"
    script.write_text("placeholder\\n", encoding="utf-8")
    bars_artifact = tmp_path / "m1.json"
    bars_artifact.write_text(
        json.dumps({
            "schema_version": 1,
            "research_only": True,
            "symbol": "XAUUSD.ecn",
            "timeframe": "M1",
            "window_utc": {
                "start": "2026-10-05T00:00:00Z",
                "end": "2026-10-07T05:30:00Z",
            },
            "bars": [{
                "time": 1791158400,
                "open": 1,
                "high": 1,
                "low": 1,
                "close": 1,
                "tick_volume": 1,
                "spread": 0,
                "real_volume": 1,
            }],
        }),
        encoding="utf-8",
    )

    def fake_run(*args, **kwargs):
        bars_artifact.write_text(bars_artifact.read_text(encoding="utf-8") + " ", encoding="utf-8")
        return SimpleNamespace(returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    adapter = DiscoveryMatrixAdapter(
        script_path=script,
        mt5_path="MT5",
        variant_name="RR2_ACT10_D2",
        bars_artifact_path=bars_artifact,
    )
    try:
        adapter.execute(make_spec())
    except Exception as exc:
        assert "changed while Discovery was running" in str(exc)
    else:
        raise AssertionError("expected mutated M1 artifact to be rejected")


def test_discovery_adapter_binds_frozen_v3_entry_artifact(tmp_path, monkeypatch):
    script = tmp_path / "run_sp2l_v3_xauusd_discovery_matrix.py"
    script.write_text("placeholder\\n", encoding="utf-8")
    bars_artifact = tmp_path / "m1.csv"
    bars_artifact.write_text(
        "time_epoch_seconds,time_utc_iso,open,high,low,close,tick_volume,spread,real_volume\\n"
        "1791158400,2026-10-05T00:00:00+00:00,4000,4001,3999,4000.5,10,2,0\\n",
        encoding="utf-8",
    )
    entry_artifact = tmp_path / "v3_entries.csv"
    entry_row = [
        "A", "A_TRAIL_0.40_ACTIVATED_PROXY_V3", "BUY",
        "2026-10-04T23:59:00+00:00", "2026-10-05T00:00:00+00:00",
        "4000", "3996", "4008", "4", "2026-10-05T00:04:00+00:00",
        "4004", "OLD_EXIT", "CLOSED", "1",
    ]
    entry_artifact.write_text(
        ",".join(ENTRY_FIELDS) + "\\n" + ",".join(entry_row) + "\\n",
        encoding="utf-8",
    )
    dataset_sha = hashlib.sha256(bars_artifact.read_bytes()).hexdigest()
    entry_sha = hashlib.sha256(entry_artifact.read_bytes()).hexdigest()
    matrix_path = tmp_path / "discovery.json"
    matrix_path.write_text(
        json.dumps({
            "research_only": True,
            "dataset_provenance": {"content_sha256": dataset_sha},
            "frozen_population": {
                "source": "FROZEN_V3_ENTRY_CSV",
                "content_sha256": entry_sha,
                "rows": 1,
            },
            "matrix": [{
                "name": "RR2_ACT10_D2",
                "signals": 1,
                "decisive": 1,
                "wins": 1,
                "losses": 0,
                "ambiguous": 0,
                "net_R": 1.0,
                "profit_factor": 2.0,
                "max_drawdown_R": 0.0,
            }],
            "trades": [{
                "variant": "RR2_ACT10_D2",
                "ambiguous": False,
                "realized_R": 1.0,
            }],
        }),
        encoding="utf-8",
    )

    def fake_run(command, **kwargs):
        assert "--entry-population-artifact" in command
        assert str(entry_artifact) in command
        assert "--entry-population-sha256" in command
        assert entry_sha in command
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({
                "status": "COMPLETE",
                "json": str(matrix_path),
                "sha256": "b" * 64,
            }),
            stderr="",
        )

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    adapter = DiscoveryMatrixAdapter(
        script_path=script,
        mt5_path="MT5",
        start="2026-10-05T00:00:00+00:00",
        end="2026-10-07T05:30:00+00:00",
        variant_name="RR2_ACT10_D2",
        bars_artifact_path=bars_artifact,
        entry_population_artifact_path=entry_artifact,
        entry_population_sha256=entry_sha,
    )
    receipt = adapter.execute(make_spec())
    assert receipt.metrics.trades == 1
    assert receipt.metrics.net_r == 1.0
