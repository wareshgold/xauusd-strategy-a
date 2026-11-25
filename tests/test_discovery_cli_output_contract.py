from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "run_sp2l_v3_xauusd_discovery_matrix.py"
)


def test_discovery_cli_writes_completion_artifacts_to_requested_output_dir(
    tmp_path, monkeypatch, capsys
):
    start = "2026-10-05T00:00:00+00:00"
    end = "2026-10-05T00:09:00+00:00"
    artifact_path = tmp_path / "synthetic_m1.json"
    output_dir = tmp_path / "requested-discovery-output"
    bars = [
        {
            "time": 1791158400 + index * 60,
            "open": 4000,
            "high": 4001,
            "low": 3999,
            "close": 4000,
            "tick_volume": 1,
            "spread": 0,
            "real_volume": 0,
        }
        for index in range(10)
    ]
    artifact_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "research_only": True,
                "symbol": "XAUUSD.ecn",
                "timeframe": "M1",
                "window_utc": {"start": start, "end": end},
                "bars": bars,
            }
        ),
        encoding="utf-8",
    )

    mt5_calls = []
    mt5_stub = ModuleType("MetaTrader5")
    mt5_stub.initialize = lambda **kwargs: mt5_calls.append(("initialize", kwargs)) or True
    mt5_stub.symbol_info = lambda symbol: (
        mt5_calls.append(("symbol_info", symbol))
        or SimpleNamespace(point=0.01, trade_contract_size=100.0)
    )
    mt5_stub.symbol_select = lambda symbol, enabled: (
        mt5_calls.append(("symbol_select", symbol, enabled)) or True
    )
    mt5_stub.shutdown = lambda: mt5_calls.append(("shutdown",))
    monkeypatch.setitem(sys.modules, "MetaTrader5", mt5_stub)

    spec = importlib.util.spec_from_file_location(
        "_sp2l_discovery_cli_output_contract", SCRIPT_PATH
    )
    assert spec is not None and spec.loader is not None
    discovery = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(discovery)

    # Keep this test focused on the CLI/output contract, not SP2L geometry or
    # the size of the discovery grid.
    monkeypatch.setattr(discovery, "build_population", lambda bars, symbol: [])
    monkeypatch.setattr(
        discovery,
        "make_variants",
        lambda: [
            {
                "name": "RR2_NO_TRAIL",
                "rr": 2.0,
                "activation_points": None,
                "distance_points": None,
            }
        ],
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(SCRIPT_PATH),
            "--mt5-path",
            "MOCK_MT5",
            "--symbol",
            "XAUUSD.ecn",
            "--start",
            start,
            "--end",
            end,
            "--bars-artifact",
            str(artifact_path),
            "--output-dir",
            str(output_dir),
        ],
    )

    discovery.main()

    completion = json.loads(capsys.readouterr().out)
    assert completion["status"] == "COMPLETE"
    json_path = Path(completion["json"])
    assert json_path.is_file()
    assert json_path.parent == output_dir.resolve()

    raw_json = json_path.read_bytes()
    import hashlib

    assert hashlib.sha256(raw_json).hexdigest() == completion["sha256"]
    result = json.loads(raw_json.decode("utf-8"))
    assert result["research_only"] is True
    assert result["dataset_provenance"]["source"] == "M1_ARTIFACT"
    assert result["dataset_provenance"]["content_sha256"] is not None

    generated_files = list(output_dir.iterdir())
    assert len(generated_files) == 4
    assert all(path.is_file() for path in generated_files)
    assert all(path.parent == output_dir.resolve() for path in generated_files)
    assert any(path.suffix == ".json" for path in generated_files)
    assert any(path.name.endswith("_SUMMARY.csv") for path in generated_files)
    assert any(path.name.endswith("_TRADES.csv") for path in generated_files)
    assert any(path.name.endswith("_SNAPSHOT.md") for path in generated_files)

    assert mt5_calls == [
        ("initialize", {"path": "MOCK_MT5"}),
        ("symbol_info", "XAUUSD.ecn"),
        ("symbol_select", "XAUUSD.ecn", True),
        ("shutdown",),
    ]
