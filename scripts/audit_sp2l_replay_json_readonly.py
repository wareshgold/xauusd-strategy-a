#!/usr/bin/env python3
"""Read-only structural audit for SP2L replay JSON artifacts.

This tool never connects to MT5, mutates source artifacts, shifts timestamps,
fills missing bars, or recalculates strategy outcomes. It emits a JSON report
to stdout unless an explicit new output path is supplied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def first_present(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def audit(path: Path) -> dict[str, Any]:
    raw_bytes = path.read_bytes()
    data = json.loads(raw_bytes)
    if not isinstance(data, dict):
        raise ValueError("Top-level JSON value must be an object.")

    signals = data.get("signals")
    trades = data.get("trades")
    interval = data.get("requested_interval_utc")
    gaps = data.get("gaps")

    signal_count = len(signals) if isinstance(signals, list) else None
    trade_count = len(trades) if isinstance(trades, list) else None
    gap_count = len(gaps) if isinstance(gaps, list) else None

    reported_first = first_present(data, "actual_first_utc", "first_utc")
    reported_last = first_present(data, "actual_last_utc", "last_utc")
    first_dt = parse_datetime(reported_first)
    last_dt = parse_datetime(reported_last)

    interval_start = interval.get("start") if isinstance(interval, dict) else None
    interval_end = interval.get("end") if isinstance(interval, dict) else None
    start_dt = parse_datetime(interval_start)
    end_dt = parse_datetime(interval_end)

    warnings: list[str] = []
    if not isinstance(interval, dict):
        warnings.append("requested_interval_utc is absent or not an object.")
    elif start_dt is None or end_dt is None:
        warnings.append("Requested interval boundaries are not parseable timezone-aware datetimes.")
    if first_dt is None or last_dt is None:
        warnings.append("Actual first/last timestamps are absent or not parseable timezone-aware datetimes.")
    elif first_dt > last_dt:
        warnings.append("Actual first timestamp is later than actual last timestamp.")
    if data.get("timestamp_basis") and "unresolved" in str(data["timestamp_basis"]).lower():
        warnings.append("Artifact itself declares timestamp mapping unresolved.")
    if data.get("gap_count", 0) and not isinstance(gaps, list):
        warnings.append("gap_count is non-zero but detailed gaps array is missing.")
    if signal_count is not None and trade_count is not None and signal_count != trade_count:
        warnings.append("Signal count differs from trade count; reconcile one-to-one mapping.")
    if signal_count is None:
        warnings.append("signals array is missing or not an array.")
    if trade_count is None:
        warnings.append("trades array is missing or not an array.")

    if start_dt and end_dt and first_dt and last_dt:
        if first_dt < start_dt or last_dt > end_dt:
            warnings.append("Reported retained first/last timestamp lies outside requested interval.")
        if first_dt > start_dt:
            warnings.append("Retained data starts after requested interval start.")
        if last_dt < end_dt:
            warnings.append("Retained data ends before requested interval end.")

    return {
        "research_only": True,
        "audit_version": 1,
        "input_path": str(path),
        "input_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "input_size_bytes": len(raw_bytes),
        "source_metadata": {
            "source": data.get("source"),
            "terminal": data.get("terminal"),
            "server": data.get("server"),
            "symbol": data.get("symbol"),
            "timeframe": data.get("timeframe"),
            "timestamp_basis": data.get("timestamp_basis"),
        },
        "reported_counts": {
            "expected_minute_span": data.get("expected_minute_span"),
            "raw_returned_bars": data.get("raw_returned_bars"),
            "filtered_bars_in_interval": data.get("filtered_bars_in_interval"),
            "raw_bars_discarded_outside_interval": data.get("raw_bars_discarded_outside_interval"),
            "unique_timestamps": data.get("unique_timestamps"),
            "chronological": data.get("chronological"),
            "gap_count": data.get("gap_count", gap_count),
            "signals": signal_count if signal_count is not None else data.get("signals_detected"),
            "trades": trade_count if trade_count is not None else data.get("trades_closed_or_ambiguous"),
            "wins": data.get("wins"),
            "losses": data.get("losses"),
            "ambiguous": data.get("ambiguous"),
            "open_or_unresolved": data.get("open_or_unresolved"),
            "win_rate_decisive": data.get("win_rate_decisive"),
            "totalR": data.get("totalR"),
            "profit_factor": data.get("profit_factor"),
        },
        "timestamps": {
            "requested_start": interval_start,
            "requested_end": interval_end,
            "reported_first": reported_first,
            "reported_last": reported_last,
            "all_parsed_as_timezone_aware": all(
                item is not None for item in (start_dt, end_dt, first_dt, last_dt)
            ),
        },
        "detailed_gap_items": gap_count,
        "warnings": warnings,
        "interpretation": (
            "Structural audit only. This does not validate MT5 timestamp mapping, "
            "signal semantics, fill assumptions, outcome accounting, or profitability."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Existing replay JSON (read-only).")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional NEW report path. Existing paths are refused to preserve evidence.",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"Input file does not exist: {args.input}")
    report = audit(args.input)
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"

    if args.output:
        if args.output.exists():
            parser.error(f"Refusing to overwrite existing output: {args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
