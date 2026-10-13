import csv
import hashlib
import json
from pathlib import Path

from sp2l_mt5_availability_integrity_gate import evaluate_availability_manifest


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_fixture(root: Path):
    daily = root / "fixture.daily.csv"
    gaps = root / "fixture.gaps.json"
    manifest = root / "fixture.manifest.json"

    with daily.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "window_index", "utc_date", "weekday", "first_m1_utc",
                "last_m1_utc", "m1_bar_count", "gap_count_touching_day",
                "gap_boundaries_ending_0100_utc",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerow({
            "window_index": 1,
            "utc_date": "2026-07-06",
            "weekday": "Monday",
            "first_m1_utc": "2026-07-06T01:00:00Z",
            "last_m1_utc": "2026-07-06T01:05:00Z",
            "m1_bar_count": 4,
            "gap_count_touching_day": 1,
            "gap_boundaries_ending_0100_utc": 0,
        })

    gaps.write_text(json.dumps([{
        "window_index": 1,
        "previous_bar_utc": "2026-07-06T01:01:00Z",
        "next_bar_utc": "2026-07-06T01:04:00Z",
        "interval_minutes": 3.0,
        "missing_m1_bars": 2,
        "kind": "gap",
    }], indent=2) + "\n", encoding="utf-8")

    data = {
        "dataset_id": "fixture",
        "provider": "MetaTrader5 terminal API",
        "terminal": "fixture terminal",
        "server": "OtetGroup-MT5",
        "symbol": "XAUUSD.ecn",
        "timeframe": "M1",
        "window_count": 2,
        "windows": [
            {
                "status": "ACQUIRED",
                "requested_start_utc": "2026-07-06T00:00:00Z",
                "requested_end_utc": "2026-07-07T00:00:00Z",
                "window_index": 1,
                "actual_first_utc": "2026-07-06T01:00:00Z",
                "actual_last_utc": "2026-07-06T01:05:00Z",
                "actual_bar_count": 4,
                "day_count": 1,
                "gap_count": 1,
                "non_chronological_count": 0,
            },
            {
                "status": "NO_DATA_IN_REQUESTED_INTERVAL",
                "requested_start_utc": "2026-01-05T00:00:00Z",
                "requested_end_utc": "2026-01-12T00:00:00Z",
                "window_index": 2,
            },
        ],
        "daily_artifact": daily.name,
        "gap_artifact": gaps.name,
        "daily_artifact_sha256": _sha(daily),
        "gap_artifact_sha256": _sha(gaps),
        "interpretation_status": "RAW_AVAILABILITY_MATRIX_ONLY",
        "session_close_inference": "NOT_PERFORMED",
        "utc_offset_inference": "NOT_PERFORMED",
        "dst_inference": "NOT_PERFORMED",
        "holiday_inference": "NOT_PERFORMED",
        "execution_or_signal_logic": "NOT_PERFORMED",
    }
    manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return manifest, data, daily, gaps


def test_valid_raw_availability_artifacts_pass_structure_only(tmp_path):
    manifest, _, _, _ = _write_fixture(tmp_path)

    result = evaluate_availability_manifest(manifest)

    assert result["status"] == "STRUCTURAL_INTEGRITY_PASS"
    assert result["canonical"] is False
    assert result["market_session_approval"] == "NOT_ESTABLISHED"
    assert result["research_interpretation"] == "RAW_AVAILABILITY_ONLY_NOT_SESSION_APPROVED"
    assert result["no_data_window_count"] == 1
    assert result["gap_record_count"] == 1
    assert result["source_artifacts_modified"] is False


def test_hash_mismatch_fails_closed(tmp_path):
    manifest, _, daily, _ = _write_fixture(tmp_path)
    daily.write_text(daily.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    result = evaluate_availability_manifest(manifest)

    assert result["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert any("SHA-256 mismatch" in error for error in result["errors"])


def test_manifest_count_mismatch_fails(tmp_path):
    manifest, data, _, _ = _write_fixture(tmp_path)
    data["windows"][0]["actual_bar_count"] = 5
    manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    result = evaluate_availability_manifest(manifest)

    assert result["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert any("actual_bar_count disagrees" in error for error in result["errors"])


def test_gap_missing_bar_count_mismatch_fails(tmp_path):
    manifest, _, _, gaps_path = _write_fixture(tmp_path)
    gaps = json.loads(gaps_path.read_text(encoding="utf-8"))
    gaps[0]["missing_m1_bars"] = 99
    gaps_path.write_text(json.dumps(gaps, indent=2) + "\n", encoding="utf-8")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["gap_artifact_sha256"] = _sha(gaps_path)
    manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    result = evaluate_availability_manifest(manifest)

    assert result["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert any("missing_m1_bars disagrees" in error for error in result["errors"])


def test_non_acquired_window_is_not_interpreted_as_market_closure(tmp_path):
    manifest, _, _, _ = _write_fixture(tmp_path)

    result = evaluate_availability_manifest(manifest)

    assert result["no_data_window_count"] == 1
    assert result["market_session_approval"] == "NOT_ESTABLISHED"
    assert "historical completeness remain unverified" in result["meaning"]


def test_manifest_cannot_reference_artifact_outside_its_directory(tmp_path):
    manifest, data, _, _ = _write_fixture(tmp_path)
    data["daily_artifact"] = "../outside.csv"
    manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    result = evaluate_availability_manifest(manifest)

    assert result["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert any("sibling filename" in error for error in result["errors"])

def test_line_ending_conversion_fails_byte_hash_validation(tmp_path):
    manifest, _, daily, _ = _write_fixture(tmp_path)
    original = daily.read_bytes()
    assert b"\r\n" not in original

    # Simulate a Windows checkout that rewrites LF bytes to CRLF.
    daily.write_bytes(original.replace(b"\n", b"\r\n"))

    result = evaluate_availability_manifest(manifest)

    assert result["status"] == "STRUCTURAL_INTEGRITY_FAIL"
    assert any("SHA-256 mismatch" in error for error in result["errors"])


def test_gitattributes_preserves_hashed_availability_artifact_bytes():
    attributes_path = Path(__file__).resolve().parents[1] / ".gitattributes"
    lines = attributes_path.read_text(encoding="utf-8").splitlines()

    assert "data/mt5-session-availability/*.csv -text" in lines
    assert "data/mt5-session-availability/*.gaps.json -text" in lines
    assert "data/mt5-session-availability/*.manifest.json -text" in lines

