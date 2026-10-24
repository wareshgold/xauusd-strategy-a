#!/usr/bin/env python3
"""Read-only integrity audit for an MT5 M1 CSV snapshot. Research-only; no trading logic."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED = (
    "time_epoch_seconds", "time_utc_iso", "open", "high", "low", "close",
    "tick_volume", "spread", "real_volume",
)

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp has no timezone")
    return parsed.astimezone(timezone.utc)

def audit(csv_path: Path, manifest_path: Path) -> dict[str, Any]:
    raw_hash = sha256_file(csv_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_hash = manifest.get("csv_sha256")
    hash_match = raw_hash == manifest_hash

    rows: list[dict[str, str]] = []
    rejected: list[dict[str, Any]] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        missing_columns = [name for name in REQUIRED if name not in header]
        if missing_columns:
            raise ValueError(f"Missing required CSV columns: {missing_columns}")
        for line_no, row in enumerate(reader, start=2):
            try:
                epoch = int(row["time_epoch_seconds"])
                dt = parse_utc(row["time_utc_iso"])
                if int(dt.timestamp()) != epoch:
                    raise ValueError("epoch/ISO timestamp mismatch")
                prices = {key: float(row[key]) for key in ("open", "high", "low", "close")}
                if any(value <= 0 for value in prices.values()):
                    raise ValueError("non-positive OHLC price")
                if prices["high"] < max(prices["open"], prices["close"], prices["low"]):
                    raise ValueError("high below another OHLC value")
                if prices["low"] > min(prices["open"], prices["close"], prices["high"]):
                    raise ValueError("low above another OHLC value")
                rows.append({
                    "epoch": epoch,
                    "iso": dt.isoformat(),
                    "weekday": dt.strftime("%A"),
                    "hour_utc": dt.strftime("%H"),
                    "open": row["open"], "high": row["high"],
                    "low": row["low"], "close": row["close"],
                })
            except Exception as exc:
                rejected.append({"line": line_no, "reason": str(exc)})

    epochs = [row["epoch"] for row in rows]
    counts = Counter(epochs)
    duplicates = sorted(epoch for epoch, count in counts.items() if count > 1)
    sorted_epochs = sorted(epochs)
    non_chronological = epochs != sorted_epochs
    gaps = []
    for before, after in zip(sorted_epochs, sorted_epochs[1:]):
        delta = after - before
        if delta > 60:
            gaps.append({
                "after_utc": datetime.fromtimestamp(before, timezone.utc).isoformat(),
                "before_utc": datetime.fromtimestamp(after, timezone.utc).isoformat(),
                "delta_seconds": delta,
                "missing_minute_slots": max(0, delta // 60 - 1),
                "classification": "UNCLASSIFIED_NEEDS_SESSION_AND_HISTORY_CONTEXT",
            })

    requested_start = parse_utc(manifest["requested_start_utc"])
    requested_end = parse_utc(manifest["requested_end_utc"])
    requested_start_epoch = int(requested_start.timestamp())
    requested_end_epoch = int(requested_end.timestamp())
    expected_window_slots = max(0, (requested_end_epoch - requested_start_epoch) // 60 + 1)
    in_window_epochs = sorted({
        epoch for epoch in epochs
        if requested_start_epoch <= epoch <= requested_end_epoch
    })
    first_in_window = in_window_epochs[0] if in_window_epochs else None
    last_in_window = in_window_epochs[-1] if in_window_epochs else None
    leading_unobserved_slots = (
        max(0, (first_in_window - requested_start_epoch) // 60)
        if first_in_window is not None else expected_window_slots
    )
    trailing_unobserved_slots = (
        max(0, (requested_end_epoch - last_in_window) // 60)
        if last_in_window is not None else 0
    )
    unique_observed_in_window = len(in_window_epochs)
    total_unobserved_slots_in_requested_window = max(
        0, expected_window_slots - unique_observed_in_window
    )
    weekday_counts = Counter(row["weekday"] for row in rows)
    hour_counts = Counter(row["hour_utc"] for row in rows)
    data = {
        "research_only": True,
        "csv_path": str(csv_path),
        "manifest_path": str(manifest_path),
        "csv_sha256_actual": raw_hash,
        "csv_sha256_manifest": manifest_hash,
        "csv_hash_matches_manifest": hash_match,
        "symbol": manifest.get("symbol"),
        "timeframe": manifest.get("timeframe"),
        "requested_start_utc": manifest.get("requested_start_utc"),
        "requested_end_utc": manifest.get("requested_end_utc"),
        "manifest_first_bar_utc": manifest.get("actual_first_bar_utc"),
        "manifest_last_bar_utc": manifest.get("actual_last_bar_utc"),
        "requested_window_expected_minute_slots": expected_window_slots,
        "unique_observed_timestamps_inside_requested_window": unique_observed_in_window,
        "unobserved_minute_slots_in_requested_window_including_closures": total_unobserved_slots_in_requested_window,
        "leading_unobserved_minute_slots_before_first_returned_bar": leading_unobserved_slots,
        "trailing_unobserved_minute_slots_after_last_returned_bar": trailing_unobserved_slots,
        "rows_read": len(rows) + len(rejected),
        "valid_rows": len(rows),
        "rejected_rows": rejected,
        "first_valid_utc": rows[0]["iso"] if rows else None,
        "last_valid_utc": rows[-1]["iso"] if rows else None,
        "timestamps_chronological": not non_chronological,
        "unique_timestamp_count": len(set(epochs)),
        "duplicate_timestamp_values": [
            datetime.fromtimestamp(epoch, timezone.utc).isoformat() for epoch in duplicates
        ],
        "duplicate_timestamp_count": len(duplicates),
        "gap_segment_count": len(gaps),
        "missing_minute_slots_between_observed_bars": sum(g["missing_minute_slots"] for g in gaps),
        "gap_segments": gaps,
        "bars_by_weekday_utc": dict(sorted(weekday_counts.items())),
        "bars_by_hour_utc": dict(sorted(hour_counts.items())),
        "bar_count_matches_manifest": len(rows) == manifest.get("returned_bars"),
        "data_quality_gate": (
            "PASS_STRUCTURAL_ONLY"
            if hash_match and not rejected and not duplicates and not non_chronological
               and len(rows) == manifest.get("returned_bars")
            else "REVIEW_REQUIRED"
        ),
        "limitations": [
            "Gap segments are not automatically classified as market closures or missing history.",
            "A structural pass does not validate broker timestamp mapping, fills, costs, or profitability.",
            "No candles were synthesized, shifted, dropped silently, or rewritten.",
        ],
    }
    return data

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if not args.csv.is_file() or not args.manifest.is_file():
        parser.error("CSV and manifest must be existing files")
    if args.output.exists():
        parser.error(f"Refusing to overwrite existing report: {args.output}")
    report = audit(args.csv, args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps({
        "status": report["data_quality_gate"],
        "valid_rows": report["valid_rows"],
        "rejected_rows": len(report["rejected_rows"]),
        "duplicates": report["duplicate_timestamp_count"],
        "gap_segments": report["gap_segment_count"],
        "missing_minute_slots": report["missing_minute_slots_between_observed_bars"],
        "hash_matches_manifest": report["csv_hash_matches_manifest"],
        "report": str(args.output),
    }, indent=2))
    return 0 if report["data_quality_gate"] == "PASS_STRUCTURAL_ONLY" else 2

if __name__ == "__main__":
    raise SystemExit(main())
