"""Run the frozen RR2/TRAIL4 research backtest for selected daily windows.

This wrapper is intentionally research-only. It reuses the existing V3 backtest
engine and exact RR2/TRAIL4 config; it does not modify or interact with the
forward runner/state. Default windows are Monday 2026-10-05 and Wednesday
2026-10-07, the day before the current 2026-10-08 session.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKTEST = ROOT / "scripts" / "run_sp2l_v3_xauusd_backtest.py"
CONFIG = "sp2l_v3_rr2_trail4_config"


def parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError("Datetime must include an explicit UTC offset")
    return dt.astimezone(timezone.utc)


def run_one(mt5_path: str, symbol: str, start: datetime, end: datetime) -> dict:
    cmd = [
        sys.executable,
        str(BACKTEST),
        "--mt5-path",
        mt5_path,
        "--symbol",
        symbol,
        "--start",
        start.isoformat(),
        "--end",
        end.isoformat(),
        "--config-module",
        CONFIG,
    ]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Backtest failed for {start.date()}:\n{proc.stdout}\n{proc.stderr}"
        )

    # The underlying backtest prints pretty-printed JSON across many lines.
    # Parse the complete JSON object instead of assuming one-line output.
    decoder = json.JSONDecoder()
    payload = None
    text_out = proc.stdout
    for pos, ch in enumerate(text_out):
        if ch != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(text_out[pos:])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("status") == "COMPLETE":
            payload = obj
            break
    if payload is None:
        raise RuntimeError(
            f"Backtest completed without a COMPLETE payload for {start.date()}:\\n"
            f"{proc.stdout}"
        )

    return {
        "date_utc": start.date().isoformat(),
        "start_utc": start.isoformat(),
        "end_utc": end.isoformat(),
        **payload,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--mt5-path",
        default=r"C:\Program Files\Otet Group MT5 Terminal\terminal64.exe",
    )
    ap.add_argument("--symbol", default="XAUUSD.ecn")
    ap.add_argument(
        "--dates",
        nargs="+",
        default=["2026-10-05", "2026-10-07"],
        help="UTC dates to replay as full M1 calendar days",
    )
    args = ap.parse_args()

    results = []
    for day in args.dates:
        start = parse_dt(f"{day}T00:00:00+00:00")
        end = start.replace(hour=0)  # explicit, keeps timezone
        from datetime import timedelta

        end = start + timedelta(days=1)
        results.append(run_one(args.mt5_path, args.symbol, start, end))

    print(json.dumps({
        "status": "COMPLETE",
        "research_only": True,
        "config_module": CONFIG,
        "symbol": args.symbol,
        "windows": results,
    }, indent=2))


if __name__ == "__main__":
    main()
