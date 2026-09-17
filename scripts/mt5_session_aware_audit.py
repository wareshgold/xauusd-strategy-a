#!/usr/bin/env python3
"""Audit MT5 XAUUSD.ecn M1 bars against an explicit session calendar.

Acquisition/provenance only. The calendar is evidence supplied by native MQL5;
this script never infers, shifts, fills, or fabricates market data.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timedelta, timezone, time
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


def expected_timestamps(start: datetime, end: datetime) -> list[datetime]:
    out: list[datetime] = []
    cur = start
    while cur <= end:
        # Native MQL5 evidence: Monday-Friday 01:00 inclusive through 23:59 UTC;
        # Sunday/Saturday have no returned session.
        if cur.weekday() <= 4 and cur.time() >= time(1, 0):
            out.append(cur)
        cur += timedelta(minutes=1)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--calendar-id", required=True)
    p.add_argument("--calendar-evidence-date", required=True)
    p.add_argument("--out-dir", default="data/mt5-acquisition")
    args = p.parse_args()

    start, end = utc(args.start), utc(args.end)
    if end <= start:
        raise SystemExit("end must be after start")

    expected = expected_timestamps(start, end)
    expected_set = {iso(x) for x in expected}

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
        if rates is None:
            raise SystemExit(f"MT5 returned None: {mt5.last_error()}")

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

        returned = [r["timestamp"] for r in rows]
        returned_set = set(returned)
        missing = sorted(expected_set - returned_set)
        unexpected = sorted(returned_set - expected_set)
        unique = len(returned) == len(returned_set)
        chronological = all(
            datetime.fromisoformat(returned[i].replace("Z", "+00:00")) >
            datetime.fromisoformat(returned[i-1].replace("Z", "+00:00"))
            for i in range(1, len(returned))
        )
        jumps = []
        for i in range(1, len(returned)):
            a = datetime.fromisoformat(returned[i-1].replace("Z", "+00:00"))
            b = datetime.fromisoformat(returned[i].replace("Z", "+00:00"))
            delta = int((b - a).total_seconds())
            if delta != 60:
                jumps.append({"from": returned[i-1], "to": returned[i], "delta_seconds": delta})

        out = Path(args.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        artifact = out / f"{args.dataset_id}.csv"
        manifest = out / f"{args.dataset_id}.manifest.json"
        if rows:
            with artifact.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
                w.writeheader(); w.writerows(rows)
            digest = sha256(artifact)
        else:
            artifact.write_text("", encoding="utf-8")
            digest = sha256(artifact)

        passed = (
            bool(expected_set) and
            returned_set == expected_set and
            unique and chronological and not jumps
        )
        result = {
            "dataset_id": args.dataset_id,
            "provider": "MetaTrader5 terminal API",
            "terminal": getattr(terminal, "name", None),
            "server": server,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "requested_interval_utc": {"start": iso(start), "end": iso(end)},
            "session_calendar_id": args.calendar_id,
            "session_calendar_evidence_date": args.calendar_evidence_date,
            "session_calendar_historical_applicability": "UNVERIFIED",
            "expected_active_bar_count": len(expected_set),
            "returned_bar_count": len(returned),
            "missing_expected_timestamps": missing,
            "unexpected_returned_timestamps": unexpected,
            "unique_timestamps": unique,
            "chronological": chronological,
            "timestamp_jumps": jumps,
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
