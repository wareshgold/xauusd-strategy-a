#!/usr/bin/env python3
"""Acquire and audit the most recent four-week XAUUSD.ecn M1 window.

Research-only. Uses the observed native-MQL5 current session calendar:
Mon-Fri 01:00-23:59 UTC, no Sat/Sun session. This is NOT historical proof.
No filling, shifting, interpolation, or inferred calendar changes are allowed.
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
CALENDAR_ID = "xauusd-ecn-session-current-observation-2026-09-17"
CALENDAR_STATUS = "CURRENT_OBSERVATION_NOT_HISTORICALLY_VERIFIED"


def utc(s: str) -> datetime:
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if d.tzinfo is None:
        raise ValueError("timestamp must include UTC offset")
    return d.astimezone(timezone.utc).replace(second=0, microsecond=0)


def iso(d: datetime) -> str:
    return d.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def expected_ts(start: datetime, end: datetime) -> list[datetime]:
    out=[]; cur=start
    while cur <= end:
        if cur.weekday() <= 4 and cur.time() >= time(1,0):
            out.append(cur)
        cur += timedelta(minutes=1)
    return out


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--start", default="2026-08-21T00:00:00Z")
    p.add_argument("--end", default="2026-09-17T23:59:00Z")
    p.add_argument("--out-dir", default="artifacts")
    args=p.parse_args()
    start,end=utc(args.start),utc(args.end)
    if end <= start: raise SystemExit("end must be after start")
    expected=expected_ts(start,end); expected_set={iso(x) for x in expected}

    if not mt5.initialize(): raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        terminal=mt5.terminal_info(); account=mt5.account_info()
        if terminal is None: raise SystemExit("terminal_info unavailable")
        server=getattr(account,"server",None) if account else None
        if server != SERVER_EXPECTED: raise SystemExit(f"unexpected server: {server!r}")
        if not mt5.symbol_select(SYMBOL,True): raise SystemExit(f"symbol_select failed: {mt5.last_error()}")
        rates=mt5.copy_rates_range(SYMBOL,TIMEFRAME,start,end)
        if rates is None: raise SystemExit(f"copy_rates_range failed: {mt5.last_error()}")

        rows=[]
        for x in rates:
            ts=datetime.fromtimestamp(int(x["time"]),tz=timezone.utc)
            rows.append({"timestamp":iso(ts),"open":repr(float(x["open"])),"high":repr(float(x["high"])),"low":repr(float(x["low"])),"close":repr(float(x["close"])),"tick_volume":repr(int(x["tick_volume"])),"spread":repr(int(x["spread"])),"real_volume":repr(int(x["real_volume"]))})
        returned=[r["timestamp"] for r in rows]; returned_set=set(returned)
        missing=sorted(expected_set-returned_set); unexpected=sorted(returned_set-expected_set)
        unique=len(returned)==len(returned_set)
        chronological=all(returned[i]>returned[i-1] for i in range(1,len(returned)))

        jumps=[]; invalid=[]
        for i in range(1,len(returned)):
            a=datetime.fromisoformat(returned[i-1].replace("Z","+00:00")); b=datetime.fromisoformat(returned[i].replace("Z","+00:00"))
            delta=int((b-a).total_seconds())
            if delta != 60:
                j={"from":returned[i-1],"to":returned[i],"delta_seconds":delta}; jumps.append(j)
                cur=a+timedelta(minutes=1); bad=False
                while cur < b:
                    if iso(cur) in expected_set: bad=True; break
                    cur += timedelta(minutes=1)
                if delta < 60 or bad: invalid.append(j)

        out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
        stem="xauusd-ecn-m1-recent-4week-2026-08-21_2026-09-17"
        csv_path=out/(stem+".csv"); json_path=out/(stem+".audit.json")
        with csv_path.open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=["timestamp","open","high","low","close","tick_volume","spread","real_volume"]); w.writeheader(); w.writerows(rows)
        result={"dataset_id":stem,"provider":"MetaTrader5 terminal API","terminal":getattr(terminal,"name",None),"server":server,"symbol":SYMBOL,"timeframe":"M1","requested_interval_utc":{"start":iso(start),"end":iso(end)},"calendar_id":CALENDAR_ID,"calendar_status":CALENDAR_STATUS,"expected_active_bar_count":len(expected_set),"returned_bar_count":len(returned),"missing_expected_timestamps":missing,"unexpected_returned_timestamps":unexpected,"unique_timestamps":unique,"chronological":chronological,"timestamp_jumps":jumps,"invalid_timestamp_jumps":invalid,"artifact":csv_path.name,"artifact_sha256":sha256(csv_path),"retrieval_timestamp_utc":iso(datetime.now(timezone.utc)),"audit_status":"AUDITED_PASS" if expected_set and returned_set==expected_set and unique and chronological and not invalid else "AUDITED_FAIL"}
        json_path.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(result,indent=2))
        return 0 if result["audit_status"]=="AUDITED_PASS" else 2
    finally: mt5.shutdown()

if __name__ == "__main__": raise SystemExit(main())
