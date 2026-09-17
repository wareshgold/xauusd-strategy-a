#!/usr/bin/env python3
"""Build a multi-window raw XAUUSD.ecn M1 availability matrix.

Evidence acquisition only. This tool reports UTC-day availability and raw
chronological gaps. It does NOT interpret gaps as session closes, infer UTC
offsets/DST/holidays, merge sessions, modify M1 data, or generate SP2L signals.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1
SERVER_EXPECTED = "OtetGroup-MT5"


def parse_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp must include UTC offset")
    return dt.astimezone(timezone.utc).replace(second=0, microsecond=0)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def acquire_window(start: datetime, end: datetime) -> dict:
    rates = mt5.copy_rates_range(SYMBOL, TIMEFRAME, start, end)
    if rates is None or len(rates) == 0:
        return {
            "status": "EMPTY",
            "requested_start_utc": iso(start),
            "requested_end_utc": iso(end),
            "error": str(mt5.last_error()),
        }

    timestamps = [datetime.fromtimestamp(int(x["time"]), tz=timezone.utc) for x in rates]
    gaps = []
    for a, b in zip(timestamps, timestamps[1:]):
        minutes = (b - a).total_seconds() / 60
        if minutes != 1:
            gaps.append({
                "previous_bar_utc": iso(a),
                "next_bar_utc": iso(b),
                "interval_minutes": minutes,
                "missing_m1_bars": max(0, int(round(minutes)) - 1) if minutes > 1 else 0,
                "kind": "gap" if minutes > 1 else "non_chronological",
            })

    by_day = defaultdict(list)
    for ts in timestamps:
        by_day[ts.date().isoformat()].append(ts)

    matrix = []
    for day in sorted(by_day):
        day_ts = by_day[day]
        day_gaps = [g for g in gaps if g["previous_bar_utc"][:10] == day or g["next_bar_utc"][:10] == day]
        boundary_0100 = [g for g in day_gaps if g["next_bar_utc"].endswith("T01:00:00Z")]
        matrix.append({
            "window_start_utc": iso(start),
            "window_end_utc": iso(end),
            "utc_date": day,
            "weekday": day_ts[0].strftime("%A"),
            "first_m1_utc": iso(day_ts[0]),
            "last_m1_utc": iso(day_ts[-1]),
            "m1_bar_count": len(day_ts),
            "gap_count_touching_day": len(day_gaps),
            "gap_boundaries_ending_0100_utc": len(boundary_0100),
        })

    return {
        "status": "ACQUIRED",
        "requested_start_utc": iso(start),
        "requested_end_utc": iso(end),
        "actual_first_utc": iso(timestamps[0]),
        "actual_last_utc": iso(timestamps[-1]),
        "actual_bar_count": len(timestamps),
        "day_count": len(matrix),
        "gap_count": len(gaps),
        "non_chronological_count": sum(g["kind"] == "non_chronological" for g in gaps),
        "gaps": gaps,
        "daily_rows": matrix,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--window", nargs=2, action="append", metavar=("START", "END"), required=True,
                   help="repeatable UTC window, e.g. 2026-01-05T00:00:00Z 2026-01-12T00:00:00Z")
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--out-dir", default="data/mt5-session-availability")
    args = p.parse_args()

    windows = []
    for start_raw, end_raw in args.window:
        start, end = parse_utc(start_raw), parse_utc(end_raw)
        if end <= start:
            raise SystemExit(f"window end must be after start: {start_raw} -> {end_raw}")
        windows.append((start, end))

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        server = getattr(account, "server", None) if account else None
        if server and server != SERVER_EXPECTED:
            raise SystemExit(f"unexpected MT5 server: {server!r}")
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"cannot select {SYMBOL}: {mt5.last_error()}")

        results = []
        all_daily_rows = []
        all_gaps = []
        for index, (start, end) in enumerate(windows, start=1):
            result = acquire_window(start, end)
            result["window_index"] = index
            results.append({k: v for k, v in result.items() if k not in ("gaps", "daily_rows")})
            if result["status"] == "ACQUIRED":
                all_daily_rows.extend(result["daily_rows"])
                for gap in result["gaps"]:
                    gap = dict(gap)
                    gap["window_index"] = index
                    gap["window_start_utc"] = iso(start)
                    gap["window_end_utc"] = iso(end)
                    all_gaps.append(gap)

        out = Path(args.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        daily_path = out / f"{args.dataset_id}.daily.csv"
        gaps_path = out / f"{args.dataset_id}.gaps.json"
        manifest_path = out / f"{args.dataset_id}.manifest.json"

        daily_fields = [
            "window_index", "window_start_utc", "window_end_utc", "utc_date", "weekday",
            "first_m1_utc", "last_m1_utc", "m1_bar_count", "gap_count_touching_day",
            "gap_boundaries_ending_0100_utc",
        ]
        with daily_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=daily_fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(all_daily_rows)
        gaps_path.write_text(json.dumps(all_gaps, indent=2) + "\n", encoding="utf-8")

        manifest = {
            "dataset_id": args.dataset_id,
            "provider": "MetaTrader5 terminal API",
            "terminal": getattr(terminal, "name", None),
            "server": server,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "window_count": len(windows),
            "windows": results,
            "daily_artifact": daily_path.name,
            "gap_artifact": gaps_path.name,
            "daily_artifact_sha256": sha256(daily_path),
            "gap_artifact_sha256": sha256(gaps_path),
            "interpretation_status": "RAW_AVAILABILITY_MATRIX_ONLY",
            "session_close_inference": "NOT_PERFORMED",
            "utc_offset_inference": "NOT_PERFORMED",
            "dst_inference": "NOT_PERFORMED",
            "holiday_inference": "NOT_PERFORMED",
            "execution_or_signal_logic": "NOT_PERFORMED",
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(manifest, indent=2))
        print("\nRAW_AVAILABILITY_MATRIX_READY")
        print("No session interpretation was performed.")
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
