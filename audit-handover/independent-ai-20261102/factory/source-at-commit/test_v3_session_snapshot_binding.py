"""Synthetic-only regressions for binding M1 validation and replay to one read.

Every artifact is created under pytest's fresh tmp_path; no market datasets,
holdout artifacts, broker adapters or MT5 modules are used.
"""
import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from strategy_factory import m1_integrity
from strategy_factory.v3_research_session import V3ResearchSession, V3ResearchSessionError


START = "2027-01-15T08:00:00+00:00"
END = "2027-01-15T08:01:00+00:00"
T0 = int(datetime(2027, 1, 15, 8, tzinfo=timezone.utc).timestamp())
M1_FIELDS = ["time_epoch_seconds", "time_utc_iso", "open", "high", "low", "close", "tick_volume", "spread", "real_volume"]
ENTRY_FIELDS = ["strategy", "variant", "direction", "setup_time_utc", "entry_time_utc", "entry_proxy", "sl_initial", "target", "risk_price", "exit_time_utc", "exit_price", "exit_reason", "status", "r_multiple"]


def m1_bytes(artifact_format, *, changed=False):
    bars = [
        dict(time=T0, open=100, high=100, low=100, close=100, tick_volume=1, spread=0, real_volume=0),
        dict(time=T0 + 60, open=100, high=106 if changed else 101, low=99, close=105 if changed else 100, tick_volume=1, spread=0, real_volume=0),
    ]
    if artifact_format == "json":
        return json.dumps(dict(schema_version=1, research_only=True, symbol="SYNTHETIC", timeframe="M1", window_utc=dict(start=START, end=END), bars=bars)).encode("utf-8")
    text = io.StringIO(newline="")
    writer = csv.DictWriter(text, fieldnames=M1_FIELDS, lineterminator="\r\n")
    writer.writeheader()
    for bar in bars:
        writer.writerow(dict(time_epoch_seconds=bar["time"], time_utc_iso=datetime.fromtimestamp(bar["time"], timezone.utc).isoformat(), **{k: v for k, v in bar.items() if k != "time"}))
    # Preserve BOM and CRLF: provenance is over raw bytes, not normalized text.
    return text.getvalue().encode("utf-8-sig")


def fixture_config(tmp_path, artifact_format):
    raw = m1_bytes(artifact_format)
    m1 = tmp_path / ("synthetic_m1." + artifact_format)
    m1.write_bytes(raw)
    entry = tmp_path / "synthetic_entries.csv"
    row = dict.fromkeys(ENTRY_FIELDS, "")
    row.update(strategy="A", variant="SYNTHETIC_FROZEN", direction="BUY", setup_time_utc=START, entry_time_utc=START, entry_proxy="100", sl_initial="95", target="105", risk_price="5", status="OPEN")
    with entry.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ENTRY_FIELDS)
        writer.writeheader()
        writer.writerow(row)
    return raw, dict(m1_artifact=m1, entry_artifact=entry, expected_dataset_sha256=hashlib.sha256(raw).hexdigest(), expected_entry_sha256=hashlib.sha256(entry.read_bytes()).hexdigest(), expected_symbol="SYNTHETIC", expected_start_utc=START, expected_end_utc=END, mt5_point=0.01, contract_size=100, volume=0.01, engine_revision="SYNTHETIC-SNAPSHOT-TEST")


@pytest.mark.parametrize("artifact_format", ["json", "csv"])
@pytest.mark.parametrize("replacement", ["changed", "invalid", "removed"])
def test_session_uses_captured_bytes_after_source_changes(tmp_path, monkeypatch, artifact_format, replacement):
    raw, config = fixture_config(tmp_path, artifact_format)
    m1 = config["m1_artifact"]
    original_read = Path.read_bytes
    reads = []

    def replace_after_read(path):
        captured = original_read(path)
        if path == m1:
            reads.append(captured)
            if len(reads) == 1:
                if replacement == "removed":
                    path.unlink()  # Only this test's fresh tmp_path artifact.
                else:
                    path.write_bytes(m1_bytes(artifact_format, changed=True) if replacement == "changed" else b"INVALID-SYNTHETIC-REPLACEMENT")
        return captured

    monkeypatch.setattr(Path, "read_bytes", replace_after_read)
    lab = V3ResearchSession(**config)
    result = lab.evaluate(rr=1, activation_points=None, distance_points=None)
    assert result.trades[0]["reason"] == "OPEN_OR_UNRESOLVED"
    assert result.trades[0]["realized_R"] is None
    assert lab.manifest()["dataset"]["content_sha256"] == hashlib.sha256(raw).hexdigest()
    assert lab.manifest()["dataset"]["byte_size"] == len(raw)
    assert reads == [raw]
    # The management engine must consume the same captured M1 population.
    managed = lab.evaluate_management({"mode": "FIXED_RR", "rr": 1})
    assert managed.trades[0]["reason"] == "OPEN_OR_UNRESOLVED"


@pytest.mark.parametrize("artifact_format", ["json", "csv"])
def test_replaced_source_before_capture_fails_hash_gate(tmp_path, monkeypatch, artifact_format):
    _, config = fixture_config(tmp_path, artifact_format)
    config["m1_artifact"].write_bytes(m1_bytes(artifact_format, changed=True))
    original_read = Path.read_bytes

    def forbid_entry_read(path):
        assert path != config["entry_artifact"], "hash failure must precede entry loading"
        return original_read(path)

    monkeypatch.setattr(Path, "read_bytes", forbid_entry_read)
    with pytest.raises(V3ResearchSessionError, match="SHA-256"):
        V3ResearchSession(**config)


@pytest.mark.parametrize("artifact_format", ["json", "csv"])
def test_invalid_captured_bytes_are_not_rescued_by_valid_replacement(tmp_path, monkeypatch, artifact_format):
    _, config = fixture_config(tmp_path, artifact_format)
    m1 = config["m1_artifact"]
    m1.write_bytes(b"INVALID-CAPTURED-SNAPSHOT")
    config["expected_dataset_sha256"] = hashlib.sha256(b"INVALID-CAPTURED-SNAPSHOT").hexdigest()
    original_read = Path.read_bytes

    def replace_invalid_after_read(path):
        assert path != config["entry_artifact"], "invalid snapshot must precede entry loading"
        captured = original_read(path)
        if path == m1:
            path.write_bytes(m1_bytes(artifact_format))
        return captured

    monkeypatch.setattr(Path, "read_bytes", replace_invalid_after_read)
    with pytest.raises(V3ResearchSessionError, match="validation failed"):
        V3ResearchSession(**config)


@pytest.mark.parametrize("artifact_format", ["json", "csv"])
def test_snapshot_read_failure_is_wrapped_before_entry_loading(tmp_path, monkeypatch, artifact_format):
    _, config = fixture_config(tmp_path, artifact_format)

    def read_failure(path):
        assert path == config["m1_artifact"], "failed capture must precede entry loading"
        raise OSError("synthetic read failure")

    monkeypatch.setattr(Path, "read_bytes", read_failure)
    with pytest.raises(V3ResearchSessionError, match="M1 artifact validation failed: synthetic read failure"):
        V3ResearchSession(**config)


def test_csv_specific_path_api_retains_report(tmp_path):
    raw, config = fixture_config(tmp_path, "csv")
    report = m1_integrity.validate_m1_csv_artifact(config["m1_artifact"], expected_symbol="SYNTHETIC", expected_start=START, expected_end=END)
    assert report.content_sha256 == hashlib.sha256(raw).hexdigest()
    assert report.byte_size == len(raw)
    assert report.bars == 2


@pytest.mark.parametrize("artifact_format", ["json", "csv"])
def test_byte_validator_matches_path_report_without_io(tmp_path, monkeypatch, artifact_format):
    raw, config = fixture_config(tmp_path, artifact_format)
    expected = m1_integrity.validate_m1_artifact(config["m1_artifact"], expected_symbol="SYNTHETIC", expected_start=START, expected_end=END)

    def no_read(path):
        pytest.fail("byte validation must not reopen a file")

    monkeypatch.setattr(Path, "read_bytes", no_read)
    actual = m1_integrity.validate_m1_artifact_bytes(raw, artifact_format=artifact_format, expected_symbol="SYNTHETIC", expected_start=START, expected_end=END)
    assert actual == expected
    assert actual.content_sha256 == hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize("artifact_format", ["json", "csv"])
def test_byte_validator_retains_structure_checks(artifact_format):
    raw = m1_bytes(artifact_format)
    if artifact_format == "json":
        payload = json.loads(raw)
        payload["bars"][1]["high"] = 98
        malformed = json.dumps(payload).encode()
    else:
        malformed = raw.replace(b"100,101,99,100", b"100,98,99,100")
    with pytest.raises(m1_integrity.M1IntegrityError, match="high is inconsistent"):
        m1_integrity.validate_m1_artifact_bytes(malformed, artifact_format=artifact_format, expected_symbol="SYNTHETIC", expected_start=START, expected_end=END)


@pytest.mark.parametrize("raw", [bytearray(b"{}"), memoryview(b"{}"), "{}"])
def test_byte_validator_requires_immutable_bytes(raw):
    with pytest.raises(m1_integrity.M1IntegrityError, match="immutable bytes"):
        m1_integrity.validate_m1_artifact_bytes(raw, artifact_format="json", expected_symbol="SYNTHETIC", expected_start=START, expected_end=END)


def test_byte_validator_rejects_unknown_format():
    with pytest.raises(m1_integrity.M1IntegrityError, match="format"):
        m1_integrity.validate_m1_artifact_bytes(b"{}", artifact_format="parquet", expected_symbol="SYNTHETIC", expected_start=START, expected_end=END)
