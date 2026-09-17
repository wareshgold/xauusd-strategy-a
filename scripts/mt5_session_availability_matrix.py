#!/usr/bin/env python3
"""Build a multi-week raw XAUUSD.ecn M1 availability matrix.

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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--out-dir", default="data/mt5-session-availability")
    args = p.parse_args()

    start, end = parse_utc(args.start), parse_utc(args.end)
    if end <= start:
        raise SystemExit("end must be after start")
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

        rates = mt5.copy_rates_range(SYMBOL, TIMEFRAME, start, end)
        if rates is None or len(rates) == 0:
            raise SystemExit(f"no M1 data returned: {mt5.last_error()}")

        timestamps = [datetime.fromtimestamp(int(x["time"]), tz=timezone.utc) for x in rates]
        gaps = []
        for a, b in zip(timestamps, timestamps[1:]):
            minutes = (b - a).total_seconds() / 60
            if minutes != 1:
                gaps.append({
                    "previous_bar_utc": a.isoformat().replace("+00:00", "Z"),
                    "next_bar_utc": b.isoformat().replace("+00:00", "Z"),
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
            day_start = day_ts[0]
            day_end = day_ts[-1]
            day_gaps = []
            for g in gaps:
                if g["previous_bar_utc"][:10] == day or g["next_bar_utc"][:10] == day:
                    day_gaps.append(g)
            boundary_0100 = [g for g in day_gaps if g["next_bar_utc"].endswith("T01:00:00Z")]
            matrix.append({
                "utc_date": day,
                "weekday": day_ts[0].strftime("%A"),
                "first_m1_utc": day_start.isoformat().replace("+00:00", "Z"),
                "last_m1_utc": day_end.isoformat().replace("+00:00", "Z"),
                "m1_bar_count": len(day_ts),
                "gap_count_touching_day": len(day_gaps),
                "gap_boundaries_ending_0100_utc": len(boundary_0100),
            })

        out = Path(args.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        matrix_path = out / f"{args.dataset_id}.daily.csv"
        gaps_path = out / f"{args.dataset_id}.gaps.json"
        manifest_path = out / f"{args.dataset_id}.manifest.json"

        with matrix_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(matrix[0].keys()), lineterminator="\n")
            writer.writeheader()
            writer.writerows(matrix)
        gaps_path.write_text(json.dumps(gaps, indent=2) + "\n", encoding="utf-8")

        manifest = {
            "dataset_id": args.dataset_id,
            "provider": "MetaTrader5 terminal API",
            "terminal": getattr(terminal, "name", None),
            "server": server,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "requested_interval_utc": {
                "start": start.isoformat().replace("+00:00", "Z"),
                "end": end.isoformat().replace("+00:00", "Z"),
            },
            "actual_first_utc": timestamps[0].isoformat().replace("+00:00", "Z"),
            "actual_last_utc": timestamps[-1].isoformat().replace("+00:00", "Z"),
            "actual_bar_count": len(timestamps),
            "day_count": len(matrix),
            "gap_count": len(gaps),
            "non_chronological_count": sum(g["kind"] == "non_chronological" for g in gaps),
            "daily_artifact": matrix_path.name,
            "gap_artifact": gaps_path.name,
            "daily_artifact_sha256": sha256(matrix_path),
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
