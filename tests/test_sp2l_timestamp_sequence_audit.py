import csv
import hashlib
import json
from pathlib import Path

import pytest

from sp2l_timestamp_sequence_audit import audit_timestamp_sequence, main


def _write_csv(path: Path, timestamps: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["time", "close"], lineterminator="\n")
        writer.writeheader()
        for index, stamp in enumerate(timestamps):
            writer.writerow({"time": stamp, "close": 2000 + index})


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_ordered_unique_timestamps_pass_and_gaps_remain_unclassified(tmp_path):
    source = tmp_path / "bars.csv"
    _write_csv(source, [
        "2026-10-12T10:00:00Z",
        "2026-10-12T10:01:00Z",
        "2026-10-12T10:04:00Z",
    ])
    before = _sha(source)

    report = audit_timestamp_sequence(source, "time")

    assert report["status"] == "STRUCTURAL_INTEGRITY_PASS"
    assert report["row_count"] == 3
    assert report["unique_timestamp_count"] == 3
    assert report["duplicate_timestamp_count"] == 0
    assert report["forward_gap_interval_count"] == 1
    assert report["estimated_missing_intervals_when_exactly_aligned"] == 2
    assert report["market_session_approval"] == "NOT_ESTABLISHED"
    assert report["canonical"] is False
    assert report["source_artifacts_modified"] is False
    assert _sha(source) == before


def test_duplicate_timestamps_fail_and_report_excess_rows(tmp_path):
    source = tmp_path / "bars.csv"
    _write_csv(source, [
        "2026-10-12T10:00:00Z",
        "2026-10-12T10:01:00Z",
        "2026-10-12T10:01:00+00:00",
    ])

    report = audit_timestamp_sequence(source, "time")

    assert report["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert report["duplicate_timestamp_count"] == 1
    assert report["duplicate_timestamp_group_count"] == 1
    assert report["duplicate_examples"][0]["occurrences"] == 2


def test_backward_order_fails_without_reordering_source(tmp_path):
    source = tmp_path / "bars.csv"
    _write_csv(source, [
        "2026-10-12T10:01:00Z",
        "2026-10-12T10:00:00Z",
    ])
    before = source.read_bytes()

    report = audit_timestamp_sequence(source, "time")

    assert report["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert report["backward_transition_count"] == 1
    assert source.read_bytes() == before


@pytest.mark.parametrize("bad_timestamp", [
    "",
    "not-a-time",
    "2026-10-12T10:00:00",
    "2026-10-12T10:00:00+03:00",
])
def test_invalid_or_non_utc_timestamps_fail_closed(tmp_path, bad_timestamp):
    source = tmp_path / "bars.csv"
    _write_csv(source, ["2026-10-12T10:00:00Z", bad_timestamp])

    report = audit_timestamp_sequence(source, "time")

    assert report["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert report["invalid_timestamp_count"] == 1


def test_missing_timestamp_column_fails_closed(tmp_path):
    source = tmp_path / "bars.csv"
    _write_csv(source, ["2026-10-12T10:00:00Z"])

    report = audit_timestamp_sequence(source, "timestamp")

    assert report["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert any("not found in CSV header" in error for error in report["errors"])


def test_invalid_interval_fails_closed(tmp_path):
    source = tmp_path / "bars.csv"
    _write_csv(source, ["2026-10-12T10:00:00Z"])

    report = audit_timestamp_sequence(source, "time", 0)

    assert report["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert any("positive number" in error for error in report["errors"])


def test_cli_emits_machine_readable_json_and_exit_code(tmp_path, monkeypatch, capsys):
    source = tmp_path / "bars.csv"
    _write_csv(source, ["2026-10-12T10:00:00Z", "2026-10-12T10:00:00Z"])
    monkeypatch.setattr(
        "sys.argv",
        ["sp2l_timestamp_sequence_audit", str(source), "--timestamp-column", "time"],
    )

    assert main() == 1
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert report["canonical"] is False
