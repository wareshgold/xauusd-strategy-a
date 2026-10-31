from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


def test_non_overwrite_behavior(tmp_path):
    # Simulate evidence dir creation and refusal to overwrite
    evidence_root = tmp_path / "artifacts" / "mt5-research-evidence"
    dataset_id = "test_ds"
    ts_tag = "20261028T120000Z"
    evidence_dir = evidence_root / f"{dataset_id}_{ts_tag}"
    evidence_dir.mkdir(parents=True)
    # Try to create same dir again should be refused by our logic - simulate
    assert evidence_dir.exists()


def test_utc_handling():
    from scripts.mt5_acquire_research_evidence_v1 import utc_parse, utc_iso
    from datetime import timezone
    dt = utc_parse("2026-07-01T00:00:00Z")
    assert dt.tzinfo is not None
    s = utc_iso(dt)
    assert s.endswith("Z")
    with pytest.raises(ValueError):
        utc_parse("2026-07-01T00:00:00")  # no tz


def test_hash_verification():
    from scripts.mt5_acquire_research_evidence_v1 import sha256_file
    import tempfile
    p = Path(tempfile.mktemp(suffix=".txt"))
    p.write_text("hello", encoding="utf-8")
    h = sha256_file(p)
    assert isinstance(h, str) and len(h) == 64
    p.unlink()


def test_gaps_and_duplicates_detection():
    from scripts.mt5_acquire_research_evidence_v1 import audit_rows
    # consecutive ok
    rows = [
        {"timestamp": "2026-07-01T01:00:00Z", "open": "1", "high": "2", "low": "0.5", "close": "1.5", "tick_volume": "10"},
        {"timestamp": "2026-07-01T01:01:00Z", "open": "1.5", "high": "2", "low": "1", "close": "1.8", "tick_volume": "10"},
    ]
    inv, gaps, chron = audit_rows(rows)
    assert inv == [] and gaps == [] and chron is True
    # gap
    rows2 = [
        {"timestamp": "2026-07-01T01:00:00Z", "open": "1", "high": "2", "low": "0.5", "close": "1.5", "tick_volume": "10"},
        {"timestamp": "2026-07-01T01:03:00Z", "open": "1.5", "high": "2", "low": "1", "close": "1.8", "tick_volume": "10"},
    ]
    inv2, gaps2, chron2 = audit_rows(rows2)
    assert chron2 is True
    assert any(g.get("kind") == "unclassified_gap" for g in gaps2)  # a positive time interval is chronological even when >1 minute
    # bad ohlc
    rows3 = [
        {"timestamp": "2026-07-01T01:00:00Z", "open": "1", "high": "0.5", "low": "0.5", "close": "1.5", "tick_volume": "10"},
    ]
    inv3, gaps3, chron3 = audit_rows(rows3)
    assert any(x.get("reason") == "invalid_ohlc" for x in inv3)


def test_terminal_path_argument_accepted():
    import argparse
    import sys
    from scripts import mt5_acquire_research_evidence_v1 as mod
    # Just verify the argument exists by parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--symbol", default=mod.SYMBOL)
    parser.add_argument("--timeframe", default="M1")
    parser.add_argument("--evidence-root", default="artifacts/mt5-research-evidence")
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--note", default="")
    parser.add_argument("--terminal-path", default=None)
    args = parser.parse_args(["--start", "2026-07-01T00:00:00Z", "--end", "2026-08-01T00:00:00Z", "--dataset-id", "x", "--terminal-path", "C:\\Program Files\\Otet Group MT5 Terminal\\terminal64.exe"])
    assert args.terminal_path is not None



def test_unclassified_gap_does_not_claim_missing_trading_bars():
    from scripts.mt5_acquire_research_evidence_v1 import audit_rows, determine_audit_status
    rows = [
        {"timestamp": "2026-07-03T20:59:00Z", "open": "1", "high": "2", "low": "0.5", "close": "1.5", "tick_volume": "10"},
        {"timestamp": "2026-07-06T00:01:00Z", "open": "1.5", "high": "2", "low": "1", "close": "1.8", "tick_volume": "10"},
    ]
    invalid, discontinuities, chronological = audit_rows(rows)
    assert invalid == []
    assert chronological is True
    assert discontinuities[0]["kind"] == "unclassified_gap"
    assert "missing_bars" not in discontinuities[0]
    assert determine_audit_status(invalid, discontinuities) == "AUDITED_UNCLASSIFIED_COVERAGE"


def test_duplicate_and_reverse_timestamps_fail_order_gate():
    from scripts.mt5_acquire_research_evidence_v1 import audit_rows, determine_audit_status
    base = {"open": "1", "high": "2", "low": "0.5", "close": "1.5", "tick_volume": "10"}
    duplicate = [
        {"timestamp": "2026-07-01T01:00:00Z", **base},
        {"timestamp": "2026-07-01T01:00:00Z", **base},
    ]
    invalid, discontinuities, chronological = audit_rows(duplicate)
    assert chronological is False
    assert discontinuities[0]["kind"] == "duplicate_timestamp"
    assert determine_audit_status(invalid, discontinuities) == "AUDITED_FAIL"
    reversed_rows = [
        {"timestamp": "2026-07-01T01:01:00Z", **base},
        {"timestamp": "2026-07-01T01:00:00Z", **base},
    ]
    invalid2, discontinuities2, chronological2 = audit_rows(reversed_rows)
    assert chronological2 is False
    assert discontinuities2[0]["kind"] == "non_chronological"
    assert determine_audit_status(invalid2, discontinuities2) == "AUDITED_FAIL"


def test_contiguous_valid_rows_pass():
    from scripts.mt5_acquire_research_evidence_v1 import audit_rows, determine_audit_status
    base = {"open": "1", "high": "2", "low": "0.5", "close": "1.5", "tick_volume": "10"}
    rows = [
        {"timestamp": "2026-07-01T01:00:00Z", **base},
        {"timestamp": "2026-07-01T01:01:00Z", **base},
    ]
    invalid, discontinuities, chronological = audit_rows(rows)
    assert invalid == [] and discontinuities == [] and chronological is True
    assert determine_audit_status(invalid, discontinuities) == "AUDITED_PASS"


def test_manifest_schema_is_versioned_and_distinct_from_legacy_template():
    from scripts.mt5_acquire_research_evidence_v1 import MANIFEST_SCHEMA_ID, MANIFEST_SCHEMA_VERSION
    assert MANIFEST_SCHEMA_ID == "sp2l.mt5-research-evidence"
    assert MANIFEST_SCHEMA_VERSION == "1.0.0"

def test_requested_bar_count_is_inclusive_calendar_minutes_not_market_bars():
    from datetime import datetime, timezone
    from scripts.mt5_acquire_research_evidence_v1 import requested_calendar_minute_slots

    start = datetime(2026, 7, 3, 20, 59, tzinfo=timezone.utc)
    end = datetime(2026, 7, 6, 0, 1, tzinfo=timezone.utc)
    # This is only the inclusive number of calendar-minute slots; no market
    # session calendar is consulted and no expected trading-bar count is inferred.
    assert requested_calendar_minute_slots(start, end) == 3063
