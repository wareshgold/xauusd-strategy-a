from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from profile_xauusd_tick_timestamps import profile_dataset  # noqa: E402


def _row(time_msc: int, bid: str = "2500.00", ask: str = "2500.20", flags: str = "3") -> dict[str, str]:
    utc_dt = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(milliseconds=time_msc)
    return {
        "time_msc": str(time_msc),
        "time_utc": utc_dt.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "bid": bid,
        "ask": ask,
        "last": "0",
        "volume": "1",
        "flags": flags,
    }


def _fixture(tmp_path: Path, rows: list[dict[str, str]]) -> tuple[Path, Path]:
    source = tmp_path / "ticks.csv.gz"
    fields = ["time_msc", "time_utc", "bid", "ask", "last", "volume", "flags"]
    with gzip.open(source, "wt", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({
        "status": "ACQUIRED",
        "artifact_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "artifact_size_bytes": source.stat().st_size,
        "tick_count": len(rows),
    }), encoding="utf-8")
    return source, manifest


def test_profiles_contiguous_duplicate_groups_without_reordering(tmp_path: Path) -> None:
    rows = [
        _row(100),
        _row(101),
        _row(101),
        _row(101, bid="2500.10", ask="2500.30", flags="7"),
        _row(102),
        _row(102, bid="2500.10", ask="2500.30"),
    ]
    source, manifest = _fixture(tmp_path, rows)
    before_source = source.read_bytes()
    before_manifest = manifest.read_bytes()

    result = profile_dataset(source, manifest, sample_limit=10)

    assert result["csv_row_count"] == 6
    assert result["unique_timestamp_groups"] == 3
    assert result["duplicate_timestamp_rows_beyond_first_occurrence"] == 3
    assert result["duplicate_timestamp_groups"] == 2
    assert result["groups_with_multiple_distinct_valid_bidask_pairs"] == 2
    assert result["within_millisecond_event_order"] == "UNRESOLVED"
    assert result["tick_order_sensitive_execution_validation"] == "NOT_CERTIFIED"
    assert result["duplicate_rows_with_bidask_different_from_first_occurrence"] == 2
    assert result["group_size_distribution"] == {"1": 1, "2": 1, "3": 1}
    assert result["maximum_group_size"] == 3
    example = result["different_bidask_group_examples"][0]
    assert example["time_msc"] == 101
    assert example["rows"][2]["flags"] == "7"
    assert result["adjacent_out_of_order_transitions"] == 0
    assert source.read_bytes() == before_source
    assert manifest.read_bytes() == before_manifest


def test_reports_out_of_order_transitions_and_utc_mismatches(tmp_path: Path) -> None:
    first = _row(100)
    second = _row(99)
    second["time_utc"] = first["time_utc"]
    source, manifest = _fixture(tmp_path, [first, second])
    result = profile_dataset(source, manifest)

    assert result["adjacent_out_of_order_transitions"] == 1
    assert result["time_utc_timestamp_mismatch_rows"] == 1
    assert result["unique_timestamp_groups"] == 2
    assert result["duplicate_timestamp_rows_beyond_first_occurrence"] == 0

def test_does_not_claim_event_order_is_resolved_when_duplicate_quotes_match(tmp_path: Path) -> None:
    rows = [
        _row(100),
        _row(101, bid="2500.00", ask="2500.20"),
        _row(101, bid="2500.00", ask="2500.20"),
    ]
    source, manifest = _fixture(tmp_path, rows)

    result = profile_dataset(source, manifest)

    # Matching quotes in this sample do not establish the provider's ordering
    # semantics for same-millisecond events in general.
    assert result["groups_with_multiple_distinct_valid_bidask_pairs"] == 0
    assert result["within_millisecond_event_order"] == "UNRESOLVED"
    assert result["tick_order_sensitive_execution_validation"] == "NOT_ESTABLISHED"

