"""Local, strategy-neutral audit for Twelve Data-shaped OHLC JSON."""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass(frozen=True)
class AuditResult:
    status: str
    symbol: str
    interval: str
    source_timezone: str | None
    row_count: int
    first_timestamp_utc: str | None
    last_timestamp_utc: str | None
    duplicate_timestamps: list[str]
    non_monotonic_pairs: int
    expected_cadence_seconds: int | None
    cadence_mode_seconds: int | None
    cadence_anomalies: int
    missing_bar_count: int
    invalid_ohlc_rows: list[int]
    raw_sha256: str
    normalized_sha256: str


def _parse_dt(value: str, source_timezone: str | None) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        if not source_timezone:
            raise ValueError("naive timestamp requires explicit source timezone")
        try:
            dt = dt.replace(tzinfo=ZoneInfo(source_timezone))
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"unknown source timezone: {source_timezone}") from exc
    return dt.astimezone(timezone.utc)


def _expected_seconds(interval: str) -> int | None:
    units = {"min": 60, "h": 3600, "day": 86400, "week": 604800}
    for suffix, multiplier in units.items():
        if interval.endswith(suffix):
            try:
                return int(interval[: -len(suffix)]) * multiplier
            except ValueError:
                return None
    return None


def audit_file(path: str | Path, source_timezone: str | None = None) -> AuditResult:
    p = Path(path)
    raw = p.read_bytes()
    payload: dict[str, Any] = json.loads(raw.decode("utf-8"))
    meta = payload.get("meta") or {}
    values = payload.get("values") or []
    symbol = str(meta.get("symbol", ""))
    interval = str(meta.get("interval", ""))
    if not symbol or not interval:
        raise ValueError("missing meta.symbol or meta.interval")

    candles = []
    invalid: list[int] = []
    for idx, row in enumerate(values):
        try:
            dt = _parse_dt(str(row["datetime"]), source_timezone)
        except (KeyError, TypeError):
            invalid.append(idx)
            continue
        o, h, l, c = (float(row[k]) for k in ("open", "high", "low", "close"))
        if not (l <= o <= h and l <= c <= h):
            invalid.append(idx)
        candles.append((dt, o, h, l, c))

    candles.sort(key=lambda x: x[0])
    timestamps = [x[0] for x in candles]
    duplicate_timestamps = sorted({t.isoformat() for t in timestamps if timestamps.count(t) > 1})
    non_monotonic_pairs = sum(1 for a, b in zip(timestamps, timestamps[1:]) if b <= a)

    deltas = [int((b - a).total_seconds()) for a, b in zip(timestamps, timestamps[1:]) if b > a]
    cadence_mode = None
    if deltas:
        counts: dict[int, int] = {}
        for d in deltas:
            counts[d] = counts.get(d, 0) + 1
        cadence_mode = max(counts, key=counts.get)
    expected = _expected_seconds(interval)
    cadence_anomalies = sum(1 for d in deltas if expected is not None and d != expected)
    missing = sum(max(d // expected - 1, 0) for d in deltas) if expected else 0

    normalized = [
        {"datetime": t.isoformat().replace("+00:00", "Z"), "open": o, "high": h, "low": l, "close": c}
        for t, o, h, l, c in candles
    ]
    normalized_bytes = json.dumps(normalized, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    blocked = bool(invalid or duplicate_timestamps or non_monotonic_pairs)
    status = "BLOCKED" if blocked else ("WARN" if cadence_anomalies else "PASS")
    return AuditResult(status, symbol, interval, source_timezone, len(candles),
                       timestamps[0].isoformat() if timestamps else None,
                       timestamps[-1].isoformat() if timestamps else None,
                       duplicate_timestamps, non_monotonic_pairs, expected,
                       cadence_mode, cadence_anomalies, missing, invalid,
                       hashlib.sha256(raw).hexdigest(), hashlib.sha256(normalized_bytes).hexdigest())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--source-timezone", default=None)
    parser.add_argument("--output-dir", default="reports")
    args = parser.parse_args()
    result = audit_file(args.input, source_timezone=args.source_timezone)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "quality_audit.json").write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    print(f"STATUS: {result.status}")
    print(f"SYMBOL: {result.symbol} | INTERVAL: {result.interval}")
    print(f"SOURCE_TIMEZONE: {result.source_timezone}")
    print(f"ROWS: {result.row_count}")
    print(f"UTC: {result.first_timestamp_utc} -> {result.last_timestamp_utc}")
    print(f"DUPLICATES: {len(result.duplicate_timestamps)} | INVALID_OHLC: {len(result.invalid_ohlc_rows)}")
    print(f"CADENCE: mode={result.cadence_mode_seconds}s anomalies={result.cadence_anomalies} missing={result.missing_bar_count}")
    print(f"RAW_SHA256: {result.raw_sha256}")
    print(f"NORMALIZED_SHA256: {result.normalized_sha256}")
    return 0 if result.status != "BLOCKED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
