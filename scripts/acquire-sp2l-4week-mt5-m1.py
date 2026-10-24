#!/usr/bin/env python3
"""Research-only four-week MT5 M1 acquisition for SP2L evidence expansion.

No strategy geometry, signal generation, parameter tuning, or trading decisions.
Preserves terminal-returned timestamps under the existing acquisition convention
and records provenance/audit metadata.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1
SERVER_EXPECTED = "OtetGroup-MT5"


def parse_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp must include UTC offset")
    return dt.astimezone(timezone.utc).replace(second=0, microsecond=0)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def audit(rows):
    invalid, gaps = [], []
    for i, row in enumerate(rows):
        try:
            ts = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
            vals = [float(row[k]) for k in ("open", "high", "low", "close", "tick_volume")]
            if ts.tzinfo is None or any(x != x for x in vals):
                invalid.append({"index": i, "reason": "invalid_timestamp_or_number"})
            o, h, l, c = [float(row[k]) for k in ("open", "high", "low", "close")]
            if not (h >= max(o, c) and l <= min(o, c) and h >= l):
                invalid.append({"index": i, "reason": "invalid_ohlc"})
        except (KeyError, TypeError, ValueError):
            invalid.append({"index": i, "reason": "malformed_row"})
        if i:
            prev = datetime.fromisoformat(rows[i-1]["timestamp"].replace("Z", "+00:00"))
            cur = datetime.fromisoformat(rows[i]["timestamp"].replace("Z", "+00:00"))
            minutes = (cur - prev).total_seconds() / 60
            if minutes != 1:
                gaps.append({
                    "from": rows[i-1]["timestamp"],
                    "to": rows[i]["timestamp"],
                    "minutes": minutes,
                    "missing_bars": max(0, int(round(minutes)) - 1) if minutes > 1 else 0,
                    "kind": "gap" if minutes > 1 else "non_chronological",
                })
    return invalid, gaps


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--start", default="2026-08-21T00:00:00Z")
    p.add_argument("--end", default="2026-09-18T23:59:00Z")
    p.add_argument("--dataset-id", default="xauusd_ecn_m1_2026-08-21_2026-09-18")
    p.add_argument("--out-dir", default="data/mt5-acquisition")
    args = p.parse_args()

    start, end = parse_utc(args.start), parse_utc(args.end)
    if end <= start:
        raise SystemExit("end must be after start")

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        if terminal is None:
            raise SystemExit("MT5 terminal_info unavailable")
        server = getattr(account, "server", None) if account else None
        if server and server != SERVER_EXPECTED:
            raise SystemExit(f"unexpected MT5 server: {server!r}")
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"symbol_select failed: {mt5.last_error()}")

        rates = mt5.copy_rates_range(SYMBOL, TIMEFRAME, start, end)
        if rates is None:
            raise SystemExit(f"copy_rates_range failed: {mt5.last_error()}")
        if len(rates) == 0:
            raise SystemExit("MT5 returned zero bars")

        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        csv_path = out_dir / f"{args.dataset_id}.csv"
        manifest_path = out_dir / f"{args.dataset_id}.manifest.json"

        rows = []
        for r in rates:
            ts = datetime.fromtimestamp(int(r["time"]), timezone.utc)
            rows.append({
                "timestamp": ts.isoformat().replace("+00:00", "Z"),
                "open": repr(float(r["open"])),
                "high": repr(float(r["high"])),
                "low": repr(float(r["low"])),
                "close": repr(float(r["close"])),
                "tick_volume": repr(int(r["tick_volume"])),
                "spread": repr(int(r["spread"])),
                "real_volume": repr(int(r["real_volume"])),
            })

        invalid, gaps = audit(rows)
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)

        manifest = {
            "dataset_id": args.dataset_id,
            "research_only": True,
            "provider": "MetaTrader5 terminal API",
            "terminal": getattr(terminal, "name", None),
            "server": server,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "requested_interval_utc": {
                "start": start.isoformat().replace("+00:00", "Z"),
                "end": end.isoformat().replace("+00:00", "Z"),
            },
            "actual_first_utc": rows[0]["timestamp"],
            "actual_last_utc": rows[-1]["timestamp"],
            "requested_bar_count": int((end - start).total_seconds() / 60) + 1,
            "actual_bar_count": len(rows),
            "gap_count": len(gaps),
            "gap_ranges": gaps,
            "invalid_row_count": len(invalid),
            "invalid_rows": invalid,
            "retrieval_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "artifact": csv_path.name,
            "artifact_sha256": sha256_file(csv_path),
            "purpose": "expand historical M1 evidence before tick-level management research",
            "strategy_geometry_changed": False,
            "parameter_tuning": False,
            "live_trading": False,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        print(json.dumps(manifest, indent=2))
        print(f"\nCSV: {csv_path}")
        print(f"MANIFEST: {manifest_path}")
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
