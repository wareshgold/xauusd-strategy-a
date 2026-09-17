#!/usr/bin/env python3
"""Audit raw XAUUSD.ecn M1 availability from a local MT5 terminal.

This tool is evidence acquisition only. It records returned M1 bars and
chronological gaps without deciding whether any gap is a market/session close.
It does not apply the MT5 session calendar, UTC offsets, DST rules, holidays,
SP2L geometry, signals, entries, exits, or trade decisions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import MetaTrader5 as mt5
except ImportError as exc:  # pragma: no cover
    raise SystemExit("MetaTrader5 Python package is required") from exc

SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1
SERVER_EXPECTED = "OtetGroup-MT5"
PROVIDER = "MetaTrader5 terminal API"


def parse_utc(value: str) -> datetime:
    text = value.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"timestamp must include UTC offset: {value}")
    return dt.astimezone(timezone.utc).replace(second=0, microsecond=0)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="UTC ISO timestamp")
    parser.add_argument("--end", required=True, help="UTC ISO timestamp")
    parser.add_argument("--out-dir", default="data/mt5-session-availability")
    parser.add_argument("--dataset-id", required=True)
    args = parser.parse_args()

    start = parse_utc(args.start)
    end = parse_utc(args.end)
    if end <= start:
        raise SystemExit("end must be after start")

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        if terminal is None:
            raise SystemExit("MT5 terminal_info() unavailable")
        server = getattr(account, "server", None) if account is not None else None
        if server and server != SERVER_EXPECTED:
            raise SystemExit(f"unexpected MT5 server: {server!r}; expected {SERVER_EXPECTED!r}")
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"cannot select {SYMBOL}: {mt5.last_error()}")

        rates = mt5.copy_rates_range(SYMBOL, TIMEFRAME, start, end)
        if rates is None:
            raise SystemExit(f"copy_rates_range failed: {mt5.last_error()}")
        if len(rates) == 0:
            raise SystemExit("MT5 returned zero bars")

        rows = []
        for item in rates:
            ts = datetime.fromtimestamp(int(item["time"]), tz=timezone.utc)
            rows.append({
                "timestamp_utc": ts.isoformat().replace("+00:00", "Z"),
                "open": repr(float(item["open"])),
                "high": repr(float(item["high"])),
                "low": repr(float(item["low"])),
                "close": repr(float(item["close"])),
                "tick_volume": repr(int(item["tick_volume"])),
                "spread": repr(int(item["spread"])),
                "real_volume": repr(int(item["real_volume"])),
            })

        gaps = []
        for index in range(1, len(rows)):
            previous = datetime.fromisoformat(rows[index - 1]["timestamp_utc"].replace("Z", "+00:00"))
            current = datetime.fromisoformat(rows[index]["timestamp_utc"].replace("Z", "+00:00"))
            diff_minutes = (current - previous).total_seconds() / 60
            if diff_minutes != 1:
                gaps.append({
                    "previous_bar_utc": rows[index - 1]["timestamp_utc"],
                    "next_bar_utc": rows[index]["timestamp_utc"],
                    "interval_minutes": diff_minutes,
                    "missing_m1_bars": max(0, int(round(diff_minutes)) - 1) if diff_minutes > 1 else 0,
                    "kind": "gap" if diff_minutes > 1 else "non_chronological",
                })

        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        artifact = out_dir / f"{args.dataset_id}.csv"
        manifest_path = out_dir / f"{args.dataset_id}.manifest.json"
        gaps_path = out_dir / f"{args.dataset_id}.gaps.json"

        with artifact.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

        gaps_path.write_text(json.dumps(gaps, indent=2) + "\n", encoding="utf-8")
        artifact_hash = sha256_file(artifact)
        retrieval_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        non_chronological = any(item["kind"] == "non_chronological" for item in gaps)
        manifest = {
            "dataset_id": args.dataset_id,
            "provider": PROVIDER,
            "terminal": getattr(terminal, "name", None),
            "server": server,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "requested_interval_utc": {"start": start.isoformat().replace("+00:00", "Z"), "end": end.isoformat().replace("+00:00", "Z")},
            "actual_first_utc": rows[0]["timestamp_utc"],
            "actual_last_utc": rows[-1]["timestamp_utc"],
            "actual_bar_count": len(rows),
            "gap_count": len(gaps),
            "non_chronological_count": sum(1 for item in gaps if item["kind"] == "non_chronological"),
            "gap_ranges_artifact": gaps_path.name,
            "retrieval_timestamp_utc": retrieval_time,
            "artifact": artifact.name,
            "artifact_sha256": artifact_hash,
            "interpretation_status": "RAW_AVAILABILITY_ONLY",
            "session_close_inference": "NOT_PERFORMED",
            "utc_offset_inference": "NOT_PERFORMED",
            "dst_inference": "NOT_PERFORMED",
            "holiday_inference": "NOT_PERFORMED",
            "audit_status": "ACQUIRED_WITHOUT_GAP_INTERPRETATION" if not non_chronological else "ACQUIRED_NON_CHRONOLOGICAL",
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(manifest, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    sys.exit(main())
