import csv
import hashlib
import json

import pytest

from strategy_factory.v3_research_api import V3ResearchAPI, V3ResearchAPIError


FIELDS = [
    "strategy", "variant", "direction", "setup_time_utc", "entry_time_utc",
    "entry_proxy", "sl_initial", "target", "risk_price", "exit_time_utc",
    "exit_price", "exit_reason", "status", "r_multiple",
]


def artifacts(tmp_path, suffix=""):
    start = "2027-01-15T08:00:00+00:00"
    end = "2027-01-15T08:02:00+00:00"
    bars = [
        {"time": 1_800_000_000, "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "tick_volume": 1, "spread": 0, "real_volume": 0},
        {"time": 1_800_000_060, "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.9, "tick_volume": 1, "spread": 0, "real_volume": 0},
        {"time": 1_800_000_120, "open": 101.9, "high": 102.0, "low": 101.7, "close": 101.8, "tick_volume": 1, "spread": 0, "real_volume": 0},
    ]
    m1 = tmp_path / f"m1{suffix}.json"
    m1.write_text(json.dumps({
        "schema_version": 1, "research_only": True, "symbol": "XAUUSD.ecn",
        "timeframe": "M1", "window_utc": {"start": start, "end": end}, "bars": bars,
    }, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    entry = tmp_path / f"entries{suffix}.csv"
    with entry.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow({
            "strategy": "A", "variant": "V3_FROZEN", "direction": "BUY",
            "setup_time_utc": start, "entry_time_utc": start, "entry_proxy": "100",
            "sl_initial": "95", "target": "110", "risk_price": "5",
            "exit_time_utc": "", "exit_price": "", "exit_reason": "",
            "status": "OPEN", "r_multiple": "",
        })
    return {
        "m1_artifact": m1, "entry_artifact": entry,
        "expected_dataset_sha256": hashlib.sha256(m1.read_bytes()).hexdigest(),
        "expected_entry_sha256": hashlib.sha256(entry.read_bytes()).hexdigest(),
        "expected_symbol": "XAUUSD.ecn", "expected_start_utc": start,
        "expected_end_utc": end, "mt5_point": 0.01, "contract_size": 100,
        "volume": 0.01, "engine_revision": "TEST-ENGINE-1",
    }


def test_api_creates_session_evaluates_and_compares_paired_variants(tmp_path):
    api = V3ResearchAPI()
    session = api.create_session(**artifacts(tmp_path))
    session_id = session["session_id"]

    left = api.evaluate(session_id, rr=5, activation_points=100, distance_points=20)
    right = api.evaluate(session_id, rr=5, activation_points=150, distance_points=20)

    assert left["research_only"] and left["canonical"] is False
    assert left["validation_status"] == "NOT_VALIDATED"
    assert left["variant"]["summary"]["signals"] == 1
    assert len(left["variant"]["trades"]) == 1
    assert left["variant_id"] != right["variant_id"]

    comparison = api.compare(session_id, left["variant_id"], right["variant_id"])
    assert comparison["comparison"]["paired_trade_count"] == 1
    assert comparison["research_only"] is True
    assert api.describe_session(session_id)["variant_count"] == 2


def test_api_is_process_local_and_deduplicates_identical_session_fingerprint(tmp_path):
    api = V3ResearchAPI()
    config = artifacts(tmp_path)
    first = api.create_session(**config)
    second = api.create_session(**config)

    assert first["session_id"] == second["session_id"]
    assert api.session_count == 1
    assert first["persistence"] == "NONE"
    assert first["api_scope"] == "PROCESS_LOCAL"


def test_api_rejects_unknown_session_and_cross_session_variant(tmp_path):
    api = V3ResearchAPI()
    first_session = api.create_session(**artifacts(tmp_path, "_a"))["session_id"]
    second_config = artifacts(tmp_path, "_b")
    second_config["engine_revision"] = "TEST-ENGINE-2"
    second_session = api.create_session(**second_config)["session_id"]
    variant = api.evaluate(first_session, rr=2, activation_points=100, distance_points=20)

    with pytest.raises(V3ResearchAPIError, match="unknown"):
        api.describe_session("missing")

    with pytest.raises(V3ResearchAPIError, match="different research session"):
        api.compare(second_session, variant["variant_id"], variant["variant_id"])


def test_api_rejects_invalid_parameters_without_creating_variant(tmp_path):
    api = V3ResearchAPI()
    session_id = api.create_session(**artifacts(tmp_path))["session_id"]

    with pytest.raises(V3ResearchAPIError, match="rejected"):
        api.evaluate(session_id, rr=-1, activation_points=100, distance_points=20)

    assert api.variant_count == 0


def test_api_evaluates_management_policy_and_distinguishes_variant_ids(tmp_path):
    api = V3ResearchAPI()
    session_id = api.create_session(**artifacts(tmp_path))["session_id"]
    be = api.evaluate_management(session_id, {
        "mode": "breakeven", "breakeven_trigger_r": 0.5,
    })
    trailing = api.evaluate_management(session_id, {
        "mode": "trailing", "trailing_activation_r": 0.5,
        "trailing_distance_points": 20,
    })
    assert be["research_only"] is True
    assert be["canonical"] is False
    assert be["validation_status"] == "NOT_VALIDATED"
    assert be["variant"]["management_config"]["mode"] == "breakeven"
    assert be["variant_id"] != trailing["variant_id"]
    paired = api.compare(session_id, be["variant_id"], trailing["variant_id"])
    assert paired["comparison"]["paired_trade_count"] == 1


def test_api_rejects_invalid_management_policy_without_variant(tmp_path):
    api = V3ResearchAPI()
    session_id = api.create_session(**artifacts(tmp_path))["session_id"]
    with pytest.raises(V3ResearchAPIError, match="management evaluation rejected"):
        api.evaluate_management(session_id, {"mode": "trailing"})
    assert api.variant_count == 0
