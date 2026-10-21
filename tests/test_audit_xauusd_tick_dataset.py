from __future__ import annotations

import csv
import gzip
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from audit_xauusd_tick_dataset import audit_dataset  # noqa: E402


def _write_fixture(tmp_path: Path, rows: list[dict[str, str]]) -> tuple[Path, Path]:
    source = tmp_path / "fixture.csv.gz"
    fields = ["time_msc", "time_utc", "bid", "ask", "last", "volume", "flags"]
    with gzip.open(source, "wt", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    import hashlib

    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest = tmp_path / "fixture.manifest.json"
    manifest.write_text(
        json.dumps({
            "status": "ACQUIRED",
            "artifact_sha256": digest,
            "artifact_size_bytes": source.stat().st_size,
            "tick_count": len(rows),
            "duplicate_or_out_of_order_timestamp_count": 2,
        }),
        encoding="utf-8",
    )
    return source, manifest


def _row(
    time_msc: int,
    bid: str = "2500.00",
    ask: str = "2500.20",
    time_utc_msc: int | None = None,
) -> dict[str, str]:
    utc_msc = time_msc if time_utc_msc is None else time_utc_msc
    utc_dt = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(milliseconds=utc_msc)
    time_utc = utc_dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    return {
        "time_msc": str(time_msc),
        "time_utc": time_utc,
        "bid": bid,
        "ask": ask,
        "last": "0",
        "volume": "0",
        "flags": "3",
    }


def test_audit_separates_duplicate_timestamp_classes_and_out_of_order(tmp_path: Path) -> None:
    source, manifest = _write_fixture(
        tmp_path,
        [
            _row(100),
            _row(101),
            _row(101),
            _row(101, bid="2500.10", ask="2500.30"),
            _row(101, time_utc_msc=102),
            _row(99),
        ],
    )
    result = audit_dataset(source, manifest)
    assert result["integrity_gate"] == "FAIL"
    assert result["duplicate_timestamp_rows_beyond_first_occurrence"] == 3
    assert result["duplicate_timestamp_rows_same_time_utc_same_bidask"] == 1
    assert result["duplicate_timestamp_rows_same_time_utc_different_bidask"] == 1
    assert result["duplicate_timestamp_rows_different_time_utc"] == 1
    assert result["tick_order_sensitive_execution_validation"] == "NOT_CERTIFIED"
    assert result["adjacent_out_of_order_transitions"] == 1
    assert result["time_utc_timestamp_mismatch_rows"] == 1
    assert result["invalid_time_utc_rows"] == 0
    assert result["csv_row_count"] == result["manifest_tick_count"] == 6
    assert result["status"] == "FAIL"


def test_audit_fails_when_manifest_row_count_does_not_match(tmp_path: Path) -> None:
    source, manifest = _write_fixture(tmp_path, [_row(100), _row(101)])
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["tick_count"] = 3
    manifest.write_text(json.dumps(data), encoding="utf-8")
    result = audit_dataset(source, manifest)
    assert result["integrity_gate"] == "FAIL"
    assert result["row_count_matches_manifest"] is False


def test_audit_does_not_modify_source_artifacts(tmp_path: Path) -> None:
    source, manifest = _write_fixture(tmp_path, [_row(100), _row(101)])
    before_source = source.read_bytes()
    before_manifest = manifest.read_bytes()
    result = audit_dataset(source, manifest)
    assert result["tick_order_sensitive_execution_validation"] == "NOT_ESTABLISHED"
    assert source.read_bytes() == before_source
    assert manifest.read_bytes() == before_manifest
