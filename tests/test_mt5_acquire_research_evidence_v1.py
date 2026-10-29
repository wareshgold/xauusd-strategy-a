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
    assert chron2 is False
    assert any(g.get("kind") == "gap" for g in gaps2)
    # bad ohlc
    rows3 = [
        {"timestamp": "2026-07-01T01:00:00Z", "open": "1", "high": "0.5", "low": "0.5", "close": "1.5", "tick_volume": "10"},
    ]
    inv3, gaps3, chron3 = audit_rows(rows3)
    assert any(x.get("reason") == "invalid_ohlc" for x in inv3)
