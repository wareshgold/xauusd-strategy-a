#!/usr/bin/env python3
"""Strict MT5 XAUUSD.ecn M1 acquisition wrapper.

Fails closed unless the returned bars exactly cover the requested inclusive
UTC M1 interval. Acquisition/provenance only; no SP2L decision logic.
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


def utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
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


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--out-dir", default="data/mt5-acquisition")
    args = p.parse_args()

    start, end = utc(args.start), utc(args.end)
    if end <= start:
        raise SystemExit("end must be after start")
    expected = int((end - start).total_seconds() // 60) + 1

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        server = getattr(account, "server", None) if account else None
        if terminal is None:
            raise SystemExit("MT5 terminal_info() unavailable")
        if server and server != SERVER_EXPECTED:
            raise SystemExit(f"unexpected MT5 server: {server!r}")
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"cannot select {SYMBOL}: {mt5.last_error()}")

        rates = mt5.copy_rates_range(SYMBOL, TIMEFRAME, start, end)
        if rates is None or len(rates) == 0:
            raise SystemExit(f"MT5 returned no bars: {mt5.last_error()}")

        rows = []
        for item in rates:
            ts = datetime.fromtimestamp(int(item["time"]), tz=timezone.utc)
            rows.append({
                "timestamp": iso(ts),
                "open": repr(float(item["open"])),
                "high": repr(float(item["high"])),
                "low": repr(float(item["low"])),
                "close": repr(float(item["close"])),
                "tick_volume": repr(int(item["tick_volume"])),
                "spread": repr(int(item["spread"])),
                "real_volume": repr(int(item["real_volume"])),
            })

        actual_first, actual_last = rows[0]["timestamp"], rows[-1]["timestamp"]
        chronological = all(
            datetime.fromisoformat(rows[i]["timestamp"].replace("Z", "+00:00"))
            > datetime.fromisoformat(rows[i-1]["timestamp"].replace("Z", "+00:00"))
            and (datetime.fromisoformat(rows[i]["timestamp"].replace("Z", "+00:00")) - datetime.fromisoformat(rows[i-1]["timestamp"].replace("Z", "+00:00"))).total_seconds() == 60
            for i in range(1, len(rows))
        )
        boundary_ok = actual_first == iso(start) and actual_last == iso(end)
        count_ok = len(rows) == expected

        out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
        artifact = out / f"{args.dataset_id}.csv"
        manifest = out / f"{args.dataset_id}.manifest.json"
        with artifact.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader(); w.writerows(rows)
        digest = sha256(artifact)
        passed = count_ok and boundary_ok and chronological
        result = {
            "dataset_id": args.dataset_id,
            "provider": "MetaTrader5 terminal API",
            "terminal": getattr(terminal, "name", None),
            "server": server,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "requested_interval_utc": {"start": iso(start), "end": iso(end)},
            "actual_first_utc": actual_first,
            "actual_last_utc": actual_last,
            "requested_bar_count": expected,
            "actual_bar_count": len(rows),
            "count_match": count_ok,
            "boundary_match": boundary_ok,
            "chronology_continuity_match": chronological,
            "artifact": artifact.name,
            "artifact_sha256": digest,
            "retrieval_timestamp_utc": iso(datetime.now(timezone.utc)),
            "audit_status": "AUDITED_PASS" if passed else "AUDITED_FAIL",
        }
        manifest.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 0 if passed else 2
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
