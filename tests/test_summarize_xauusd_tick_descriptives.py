from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from summarize_xauusd_tick_descriptives import summarize_dataset  # noqa: E402


def _fixture(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "ticks.csv.gz"
    rows = [
        {"time_msc": "1000", "time_utc": "2026-08-21T00:00:01.000Z", "bid": "3000.00", "ask": "3000.20", "last": "3000.10", "volume": "0", "flags": "134"},
        {"time_msc": "1000", "time_utc": "2026-08-21T00:00:01.000Z", "bid": "3000.01", "ask": "3000.21", "last": "3000.11", "volume": "0", "flags": "226"},
        {"time_msc": "2000", "time_utc": "2026-08-21T00:00:02.000Z", "bid": "3000.00", "ask": "3000.30", "last": "3000.10", "volume": "0", "flags": "96"},
        {"time_msc": "3000", "time_utc": "2026-08-21T00:00:03.000Z", "bid": "3000.40", "ask": "3000.30", "last": "3000.35", "volume": "0", "flags": "130"},
    ]
    with gzip.open(source, "wt", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest = tmp_path / "ticks.manifest.json"
    manifest.write_text(json.dumps({
        "status": "ACQUIRED",
        "artifact_sha256": digest,
        "artifact_size_bytes": source.stat().st_size,
        "tick_count": len(rows),
    }), encoding="utf-8")
    return source, manifest


def test_descriptive_summary_reports_raw_flags_spreads_and_input_order(tmp_path: Path) -> None:
    source, manifest = _fixture(tmp_path)
    source_before = source.read_bytes()
    manifest_before = manifest.read_bytes()

    result = summarize_dataset(source, manifest)

    assert result["csv_row_count"] == 4
    assert result["row_count_matches_manifest"] is True
    assert result["sha256_matches_manifest"] is True
    assert result["quote_rows"] == {
        "valid_non_crossed_bidask": 3,
        "missing_or_invalid_bidask": 0,
        "crossed_bidask": 1,
    }
    assert result["spread"]["count"] == 3
    assert result["spread"]["minimum"] == 0.2
    assert result["spread"]["maximum"] == 0.3
    assert result["flag_value_counts"] == {"96": 1, "130": 1, "134": 1, "226": 1}
    assert result["input_row_order_diagnostics"]["bid_changes_vs_previous_input_row"] == 3
    assert result["eligibility"] == "DESCRIPTIVE_ONLY_NOT_EXECUTION_CERTIFICATION"
    assert source.read_bytes() == source_before
    assert manifest.read_bytes() == manifest_before


def test_descriptive_summary_does_not_infer_flag_semantics(tmp_path: Path) -> None:
    source, manifest = _fixture(tmp_path)
    result = summarize_dataset(source, manifest)
    assert result["flag_value_counts"]["134"] == 1
    assert "undocumented bit meanings are not inferred" in result["interpretation"]
    assert "equal-millisecond event order is unresolved" in result["input_row_order_diagnostics"]["warning"]
