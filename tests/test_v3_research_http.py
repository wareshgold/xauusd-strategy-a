import csv
import hashlib
import json
from pathlib import Path

import pytest

from strategy_factory.v3_research_http import V3ResearchHTTPApplication, V3ResearchHTTPError


FIELDS = [
    "strategy", "variant", "direction", "setup_time_utc", "entry_time_utc",
    "entry_proxy", "sl_initial", "target", "risk_price", "exit_time_utc",
    "exit_price", "exit_reason", "status", "r_multiple",
]


def write_artifacts(root):
    start = "2027-01-15T08:00:00+00:00"
    end = "2027-01-15T08:02:00+00:00"
    m1 = root / "xauusd_m1.json"
    m1.write_text(json.dumps({
        "schema_version": 1, "research_only": True, "symbol": "XAUUSD.ecn",
        "timeframe": "M1", "window_utc": {"start": start, "end": end},
        "bars": [
            {"time": 1800000000, "open": 100, "high": 100, "low": 100, "close": 100, "tick_volume": 1, "spread": 0, "real_volume": 0},
            {"time": 1800000060, "open": 100, "high": 102, "low": 99, "close": 101.9, "tick_volume": 1, "spread": 0, "real_volume": 0},
            {"time": 1800000120, "open": 101.9, "high": 102, "low": 101.7, "close": 101.8, "tick_volume": 1, "spread": 0, "real_volume": 0},
        ],
    }, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    entries = root / "frozen_entries.csv"
    with entries.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow({
            "strategy": "A", "variant": "V3_FROZEN", "direction": "BUY",
            "setup_time_utc": start, "entry_time_utc": start, "entry_proxy": "100",
            "sl_initial": "95", "target": "110", "risk_price": "5",
            "exit_time_utc": "", "exit_price": "", "exit_reason": "",
            "status": "OPEN", "r_multiple": "",
        })
    return start, end


def test_catalog_create_session_evaluate_and_compare(tmp_path):
    start, end = write_artifacts(tmp_path)
    app = V3ResearchHTTPApplication(data_roots=[tmp_path])

    status, catalog = app.dispatch("GET", "/api/catalog")
    assert status == 200
    m1 = next(x for x in catalog["items"] if x["kind"] == "M1_JSON")
    entries = next(x for x in catalog["items"] if x["kind"] == "FROZEN_ENTRY_CSV")

    status, health = app.dispatch("GET", "/api/health")
    assert status == 200 and health["production_decisions"] is False

    status, session = app.dispatch("POST", "/api/sessions", {
        "m1_artifact_id": m1["id"], "entry_artifact_id": entries["id"],
        "symbol": "XAUUSD.ecn",
        "mt5_point": 0.01, "contract_size": 100, "volume": 0.01,
        "engine_revision": "HTTP-TEST-1",
    })
    assert status == 201
    session_id = session["session_id"]
    assert session["artifact_selection"]["dataset_sha256"] == hashlib.sha256((tmp_path / "xauusd_m1.json").read_bytes()).hexdigest()
    assert session["artifact_selection"]["start_utc"] == start
    assert session["artifact_selection"]["end_utc"] == end
    assert session["artifact_selection"]["window_source"] == "M1_JSON_DECLARED_WINDOW"

    status, left = app.dispatch("POST", f"/api/sessions/{session_id}/evaluate", {
        "rr": 2, "activation_points": 100, "distance_points": 20,
    })
    assert status == 200
    status, right = app.dispatch("POST", f"/api/sessions/{session_id}/evaluate", {
        "rr": 3, "activation_points": 100, "distance_points": 20,
    })
    assert status == 200

    status, comparison = app.dispatch("POST", f"/api/sessions/{session_id}/compare", {
        "left_variant_id": left["variant_id"], "right_variant_id": right["variant_id"],
    })
    assert status == 200
    assert comparison["comparison"]["paired_trade_count"] == 1

    status, management = app.dispatch("POST", f"/api/sessions/{session_id}/management", {
        "spec": {"mode": "TIME_EXIT", "max_bars": 1},
    })
    assert status == 200
    assert management["research_only"] is True
    assert management["variant"]["management"]["mode"] == "TIME_EXIT"
    assert management["variant"]["summary"]["net_profit_usd"] == pytest.approx(1.9)


def test_catalog_artifact_id_cannot_escape_configured_root(tmp_path):
    start, end = write_artifacts(tmp_path)
    outside = tmp_path.parent / "outside_m1.json"
    outside.write_text("{}", encoding="utf-8")
    app = V3ResearchHTTPApplication(data_roots=[tmp_path])

    with pytest.raises(V3ResearchHTTPError, match="outside configured roots"):
        app.resolve_artifact("0:../outside_m1.json", "M1_JSON")


def test_rejects_unconfigured_roots_and_non_loopback_bind(tmp_path):
    with pytest.raises(V3ResearchHTTPError, match="at least one"):
        V3ResearchHTTPApplication(data_roots=[tmp_path / "missing"])

    from strategy_factory.v3_research_http import serve
    with pytest.raises(V3ResearchHTTPError, match="loopback"):
        serve(host="0.0.0.0", port=8791)



def test_dashboard_exposes_complete_replay_evidence_export():
    dashboard = Path(__file__).resolve().parents[1] / "scripts" / "v3_research_dashboard.html"
    html = dashboard.read_text(encoding="utf-8")
    assert 'id="exportEvidence"' in html
    assert "V3_RESEARCH_REPLAY_EXPORT" in html
    assert "session_manifest:sessionManifest" in html
    assert "session_request:sessionRequest" in html
    assert "trade_rows_sha256:tradeHash" in html
    assert "trades:v.trades" in html
    assert '["profit_factor","Profit factor (R)"]' in html
