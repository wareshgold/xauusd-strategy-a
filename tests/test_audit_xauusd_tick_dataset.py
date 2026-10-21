from __future__ import annotations

import csv
import gzip
import json
import sys
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


def _row(time_msc: int) -> dict[str, str]:
    return {
        "time_msc": str(time_msc),
        "time_utc": "2026-08-21T00:00:00.000Z",
        "bid": "2500.00",
        "ask": "2500.20",
        "last": "0",
        "volume": "0",
        "flags": "3",
    }


def test_audit_separates_duplicate_timestamps_from_out_of_order(tmp_path: Path) -> None:
    source, manifest = _write_fixture(
        tmp_path, [_row(100), _row(101), _row(101), _row(99)]
    )
    result = audit_dataset(source, manifest)
    assert result["integrity_gate"] == "PASS"
    assert result["duplicate_timestamp_rows_beyond_first_occurrence"] == 1
    assert result["adjacent_out_of_order_transitions"] == 1
    assert result["csv_row_count"] == result["manifest_tick_count"] == 4
    assert result["status"] == "PASS_WITH_TIMESTAMP_WARNINGS"


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
    audit_dataset(source, manifest)
    assert source.read_bytes() == before_source
    assert manifest.read_bytes() == before_manifest
