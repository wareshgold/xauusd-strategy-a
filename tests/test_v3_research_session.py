import csv
import hashlib
import json

import pytest

from strategy_factory.v3_research_session import V3ResearchSession


ENTRY_FIELDS = [
    "strategy", "variant", "direction", "setup_time_utc", "entry_time_utc",
    "entry_proxy", "sl_initial", "target", "risk_price", "exit_time_utc",
    "exit_price", "exit_reason", "status", "r_multiple",
]


def build_artifacts(tmp_path):
    start = "2027-01-15T08:00:00+00:00"
    end = "2027-01-15T08:02:00+00:00"
    bars = [
        {"time": 1_800_000_000, "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "tick_volume": 1, "spread": 0, "real_volume": 0},
        {"time": 1_800_000_060, "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.9, "tick_volume": 1, "spread": 0, "real_volume": 0},
        {"time": 1_800_000_120, "open": 101.9, "high": 102.0, "low": 101.7, "close": 101.8, "tick_volume": 1, "spread": 0, "real_volume": 0},
    ]
    payload = {
        "schema_version": 1,
        "research_only": True,
        "symbol": "XAUUSD.ecn",
        "timeframe": "M1",
        "window_utc": {"start": start, "end": end},
        "bars": bars,
    }
    m1 = tmp_path / "m1.json"
    m1.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    entry = tmp_path / "entries.csv"
    row = {
        "strategy": "A", "variant": "V3_FROZEN", "direction": "BUY",
        "setup_time_utc": start, "entry_time_utc": start,
        "entry_proxy": "100.0", "sl_initial": "95.0", "target": "110.0",
        "risk_price": "5.0", "exit_time_utc": "", "exit_price": "",
        "exit_reason": "", "status": "OPEN", "r_multiple": "",
    }
    with entry.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ENTRY_FIELDS)
        writer.writeheader()
        writer.writerow(row)
    return m1, entry, hashlib.sha256(m1.read_bytes()).hexdigest(), hashlib.sha256(entry.read_bytes()).hexdigest(), start, end


def session(paths, **overrides):
    m1, entry, m1_sha, entry_sha, start, end = paths
    args = {
        "m1_artifact": m1,
        "entry_artifact": entry,
        "expected_dataset_sha256": m1_sha,
        "expected_entry_sha256": entry_sha,
        "expected_symbol": "XAUUSD.ecn",
        "expected_start_utc": start,
        "expected_end_utc": end,
        "mt5_point": 0.01,
        "contract_size": 100.0,
        "volume": 0.01,
        "engine_revision": "TEST-V3-ENGINE-1",
    }
    args.update(overrides)
    return V3ResearchSession(**args)


def test_session_loads_and_binds_exact_dataset_and_frozen_entries(tmp_path):
    paths = build_artifacts(tmp_path)
    lab = session(paths)

    assert lab.research_only is True
    assert lab.population_size == 1
    assert lab.manifest()["symbol_identity_verified"] is True
    assert lab.dataset_report["content_sha256"] == paths[2]
    assert lab.entry_report["content_sha256"] == paths[3]
    assert lab.manifest()["canonical"] is False
    assert lab.manifest()["validation_status"] == "NOT_VALIDATED"

    first = lab.evaluate(rr=5, activation_points=100, distance_points=20)
    second = lab.evaluate(rr=5, activation_points=100, distance_points=20)
    assert first == second
    assert lab.cache_entries == 1
    assert first.trades[0]["reason"] == "TRAIL_SL"


def test_session_rejects_dataset_hash_mismatch(tmp_path):
    paths = build_artifacts(tmp_path)
    with pytest.raises(ValueError, match="SHA-256"):
        session(paths, expected_dataset_sha256="f" * 64)


def test_session_rejects_entry_population_hash_mismatch(tmp_path):
    paths = build_artifacts(tmp_path)
    with pytest.raises(ValueError, match="SHA-256"):
        session(paths, expected_entry_sha256="e" * 64)


def test_session_rejects_wrong_symbol_or_window(tmp_path):
    paths = build_artifacts(tmp_path)
    with pytest.raises(ValueError, match="symbol"):
        session(paths, expected_symbol="XAUUSD")
    with pytest.raises(ValueError, match="window"):
        session(paths, expected_end_utc="2027-01-15T08:03:00+00:00")


def test_session_rejects_non_research_m1_artifact(tmp_path):
    paths = build_artifacts(tmp_path)
    payload = json.loads(paths[0].read_text(encoding="utf-8"))
    payload["research_only"] = False
    paths[0].write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="research_only"):
        session(paths)

def test_session_loads_existing_validated_m1_csv(tmp_path):
    start = "2027-01-15T08:00:00+00:00"
    end = "2027-01-15T08:02:00+00:00"
    m1 = tmp_path / "xauusd_m1.csv"
    m1.write_text(
        "time_epoch_seconds,time_utc_iso,open,high,low,close,tick_volume,spread,real_volume\\n"
        "1800000000,2027-01-15T08:00:00+00:00,100,100,100,100,1,0,0\\n"
        "1800000060,2027-01-15T08:01:00+00:00,100,102,99,101.9,1,0,0\\n"
        "1800000120,2027-01-15T08:02:00+00:00,101.9,102,101.7,101.8,1,0,0\\n",
        encoding="utf-8",
    )
    entry = tmp_path / "entries.csv"
    row = {
        "strategy": "A", "variant": "V3_FROZEN", "direction": "BUY",
        "setup_time_utc": start, "entry_time_utc": start, "entry_proxy": "100",
        "sl_initial": "95", "target": "110", "risk_price": "5",
        "exit_time_utc": "", "exit_price": "", "exit_reason": "",
        "status": "OPEN", "r_multiple": "",
    }
    with entry.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ENTRY_FIELDS)
        writer.writeheader()
        writer.writerow(row)
    import hashlib
    lab = V3ResearchSession(
        m1_artifact=m1, entry_artifact=entry,
        expected_dataset_sha256=hashlib.sha256(m1.read_bytes()).hexdigest(),
        expected_entry_sha256=hashlib.sha256(entry.read_bytes()).hexdigest(),
        expected_symbol="XAUUSD.ecn", expected_start_utc=start, expected_end_utc=end,
        mt5_point=0.01, contract_size=100, volume=0.01,
        engine_revision="CSV-M1-TEST",
    )
    assert lab.dataset_report["bars"] == 3
    assert lab.manifest()["symbol_identity_verified"] is False
    assert lab.manifest()["m1_metadata_provenance"] == "CALLER_ASSERTED_CSV_IDENTITY_NO_EMBEDDED_SYMBOL_OR_WINDOW"
    assert lab.dataset_report["content_sha256"] == hashlib.sha256(m1.read_bytes()).hexdigest()
    assert lab.population_size == 1
