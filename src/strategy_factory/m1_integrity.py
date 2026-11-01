from __future__ import annotations

"""Structural integrity checks for immutable XAUUSD M1 research artifacts.

This gate validates artifact structure and provenance only. It does not infer
market sessions, repair missing bars, define SP2L geometry, or judge strategy
performance. Missing-minute intervals are reported, not silently filled.
"""

from dataclasses import dataclass
import csv
import io
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from typing import Any


class M1IntegrityError(ValueError):
    """Raised when an M1 artifact violates its declared data contract."""


@dataclass(frozen=True)
class M1IntegrityReport:
    status: str
    symbol: str
    timeframe: str
    start_utc: str
    end_utc: str
    bars: int
    byte_size: int
    content_sha256: str
    gap_count: int
    missing_minute_slots: int
    largest_gap_minutes: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "start_utc": self.start_utc,
            "end_utc": self.end_utc,
            "bars": self.bars,
            "byte_size": self.byte_size,
            "content_sha256": self.content_sha256,
            "gap_count": self.gap_count,
            "missing_minute_slots": self.missing_minute_slots,
            "largest_gap_minutes": self.largest_gap_minutes,
            "gap_policy": "REPORTED_NOT_FILLED_OR_CLASSIFIED",
        }


def _utc(value: str, field: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise M1IntegrityError(f"{field} must be a non-empty ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise M1IntegrityError(f"{field} is not a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise M1IntegrityError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def same_utc_instant(left: str, right: str) -> bool:
    """Compare two timezone-aware ISO-8601 timestamps as UTC instants."""
    return _utc(left, "left timestamp") == _utc(right, "right timestamp")


def m1_gap_detected(previous_time: int, current_time: int) -> bool:
    """Return whether two ordered M1 bar timestamps contain a missing minute slot."""
    return current_time - previous_time > 60


def _number(row: dict[str, Any], field: str, index: int) -> float:
    value = row.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise M1IntegrityError(f"bar[{index}].{field} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise M1IntegrityError(f"bar[{index}].{field} must be finite")
    return result


def validate_m1_csv_artifact(
    path: str | Path,
    *,
    expected_symbol: str,
    expected_start: str,
    expected_end: str,
) -> M1IntegrityReport:
    artifact = Path(path)
    if not artifact.is_file():
        raise M1IntegrityError(f"M1 artifact not found: {artifact}")
    raw = artifact.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    try:
        decoded = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise M1IntegrityError("M1 CSV must be valid UTF-8") from exc
    reader = csv.DictReader(io.StringIO(decoded, newline=""))
    expected_fields = [
        "time_epoch_seconds", "time_utc_iso", "open", "high", "low", "close",
        "tick_volume", "spread", "real_volume",
    ]
    if reader.fieldnames != expected_fields:
        raise M1IntegrityError("M1 CSV header does not match the declared source schema")

    start = _utc(expected_start, "expected_start")
    end = _utc(expected_end, "expected_end")
    if end <= start:
        raise M1IntegrityError("expected M1 CSV window end must follow start")
    start_epoch = int(start.timestamp())
    end_epoch = int(end.timestamp())
    previous_time: int | None = None
    gap_count = 0
    missing_slots = 0
    largest_gap = 0
    count = 0

    for index, row in enumerate(reader):
        if None in row or any(value is None for value in row.values()):
            raise M1IntegrityError(f"M1 CSV row[{index}] has an invalid field count")
        try:
            timestamp = int(row["time_epoch_seconds"])
        except (TypeError, ValueError) as exc:
            raise M1IntegrityError(f"M1 CSV row[{index}] has an invalid epoch timestamp") from exc
        row_dt = _utc(row["time_utc_iso"], f"row[{index}].time_utc_iso")
        if row_dt.microsecond != 0:
            raise M1IntegrityError(f"M1 CSV row[{index}] timestamp has sub-second precision")
        if int(row_dt.timestamp()) != timestamp:
            raise M1IntegrityError(f"M1 CSV row[{index}] epoch and ISO timestamps disagree")
        if timestamp % 60 != 0:
            raise M1IntegrityError(f"M1 CSV row[{index}] timestamp is not aligned to M1")
        if timestamp < start_epoch or timestamp > end_epoch:
            raise M1IntegrityError(f"M1 CSV row[{index}] falls outside the inclusive declared window")
        if previous_time is not None:
            if timestamp == previous_time:
                raise M1IntegrityError(f"duplicate M1 CSV timestamp at row[{index}]")
            if timestamp < previous_time:
                raise M1IntegrityError(f"out-of-order M1 CSV timestamp at row[{index}]")
            delta_minutes = (timestamp - previous_time) // 60
            if delta_minutes > 1:
                gap_count += 1
                missing_slots += delta_minutes - 1
                largest_gap = max(largest_gap, delta_minutes - 1)
        previous_time = timestamp

        values: dict[str, float] = {}
        for field in ("open", "high", "low", "close"):
            try:
                values[field] = float(row[field])
            except (TypeError, ValueError) as exc:
                raise M1IntegrityError(f"M1 CSV row[{index}].{field} must be numeric") from exc
            if not math.isfinite(values[field]):
                raise M1IntegrityError(f"M1 CSV row[{index}].{field} must be finite")
            if values[field] <= 0:
                raise M1IntegrityError(f"M1 CSV row[{index}].{field} must be positive")
        if values["high"] < max(values["open"], values["close"], values["low"]):
            raise M1IntegrityError(f"M1 CSV row[{index}] high is inconsistent with OHLC")
        if values["low"] > min(values["open"], values["close"], values["high"]):
            raise M1IntegrityError(f"M1 CSV row[{index}] low is inconsistent with OHLC")

        for field in ("tick_volume", "spread", "real_volume"):
            try:
                number = int(row[field])
            except (TypeError, ValueError) as exc:
                raise M1IntegrityError(f"M1 CSV row[{index}].{field} must be an integer") from exc
            if number < 0:
                raise M1IntegrityError(f"M1 CSV row[{index}].{field} must be non-negative")
        count += 1

    if count == 0:
        raise M1IntegrityError("M1 CSV contains no data rows")
    return M1IntegrityReport(
        status="PASS_WITH_GAPS" if gap_count else "PASS",
        symbol=expected_symbol,
        timeframe="M1",
        start_utc=start.isoformat(),
        end_utc=end.isoformat(),
        bars=count,
        byte_size=len(raw),
        content_sha256=digest,
        gap_count=gap_count,
        missing_minute_slots=missing_slots,
        largest_gap_minutes=largest_gap,
    )


def validate_m1_artifact(
    path: str | Path,
    *,
    expected_symbol: str,
    expected_start: str,
    expected_end: str,
) -> M1IntegrityReport:
    artifact = Path(path)
    if artifact.suffix.lower() == ".csv":
        return validate_m1_csv_artifact(
            artifact,
            expected_symbol=expected_symbol,
            expected_start=expected_start,
            expected_end=expected_end,
        )
    if not artifact.is_file():
        raise M1IntegrityError(f"M1 artifact not found: {artifact}")
    raw = artifact.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise M1IntegrityError("M1 artifact must be valid UTF-8 JSON") from exc

    if not isinstance(payload, dict):
        raise M1IntegrityError("M1 artifact root must be a JSON object")
    if payload.get("schema_version") != 1:
        raise M1IntegrityError("unsupported M1 artifact schema_version")
    if payload.get("research_only") is not True:
        raise M1IntegrityError("M1 artifact must declare research_only=true")
    if payload.get("symbol") != expected_symbol:
        raise M1IntegrityError("M1 artifact symbol does not match the declared symbol")
    if payload.get("timeframe") != "M1":
        raise M1IntegrityError("M1 artifact timeframe must be M1")

    window = payload.get("window_utc")
    if not isinstance(window, dict):
        raise M1IntegrityError("M1 artifact window_utc metadata is required")
    start = _utc(window.get("start"), "window_utc.start")
    end = _utc(window.get("end"), "window_utc.end")
    expected_start_dt = _utc(expected_start, "expected_start")
    expected_end_dt = _utc(expected_end, "expected_end")
    if end <= start:
        raise M1IntegrityError("M1 artifact window end must follow start")
    if start != expected_start_dt or end != expected_end_dt:
        raise M1IntegrityError("M1 artifact window does not match the declared test window")

    rows = payload.get("bars")
    if not isinstance(rows, list) or not rows:
        raise M1IntegrityError("M1 artifact must contain a non-empty bars array")

    previous_time: int | None = None
    gap_count = 0
    missing_slots = 0
    largest_gap = 0
    required = ("time", "open", "high", "low", "close", "tick_volume", "spread", "real_volume")
    start_epoch = int(start.timestamp())
    end_epoch = int(end.timestamp())

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise M1IntegrityError(f"bar[{index}] must be a JSON object")
        missing = [field for field in required if field not in row]
        if missing:
            raise M1IntegrityError(f"bar[{index}] missing fields: {','.join(missing)}")

        timestamp = row["time"]
        if isinstance(timestamp, bool) or not isinstance(timestamp, int):
            raise M1IntegrityError(f"bar[{index}].time must be an integer Unix timestamp")
        if timestamp % 60 != 0:
            raise M1IntegrityError(f"bar[{index}].time is not aligned to an M1 boundary")
        if timestamp < start_epoch or timestamp > end_epoch:
            raise M1IntegrityError(f"bar[{index}].time falls outside the declared inclusive [start,end] window")
        if previous_time is not None:
            if timestamp == previous_time:
                raise M1IntegrityError(f"duplicate M1 timestamp at bar[{index}]")
            if timestamp < previous_time:
                raise M1IntegrityError(f"out-of-order M1 timestamp at bar[{index}]")
            delta_minutes = (timestamp - previous_time) // 60
            if delta_minutes > 1:
                gap_count += 1
                missing_slots += delta_minutes - 1
                largest_gap = max(largest_gap, delta_minutes - 1)
        previous_time = timestamp

        open_price = _number(row, "open", index)
        high_price = _number(row, "high", index)
        low_price = _number(row, "low", index)
        close_price = _number(row, "close", index)
        if min(open_price, high_price, low_price, close_price) <= 0:
            raise M1IntegrityError(f"bar[{index}] OHLC prices must be positive")
        if high_price < max(open_price, close_price, low_price):
            raise M1IntegrityError(f"bar[{index}] high is inconsistent with OHLC")
        if low_price > min(open_price, close_price, high_price):
            raise M1IntegrityError(f"bar[{index}] low is inconsistent with OHLC")
        for field in ("tick_volume", "spread", "real_volume"):
            value = row[field]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise M1IntegrityError(f"bar[{index}].{field} must be a non-negative integer")

    return M1IntegrityReport(
        status="PASS_WITH_GAPS" if gap_count else "PASS",
        symbol=expected_symbol,
        timeframe="M1",
        start_utc=start.isoformat(),
        end_utc=end.isoformat(),
        bars=len(rows),
        byte_size=len(raw),
        content_sha256=digest,
        gap_count=gap_count,
        missing_minute_slots=missing_slots,
        largest_gap_minutes=largest_gap,
    )
