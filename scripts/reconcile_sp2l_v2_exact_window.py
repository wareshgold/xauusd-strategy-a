#!/usr/bin/env python3
"""Trade-level reconciliation for the legacy SP2L V2 forensic contract.

Compares the exact Aug-26 00:00 UTC -> Sep-25 00:00 UTC population between
the runtime-M1 independent replay trade CSV and an MT5 backtest JSON/CSV.

Non-canonical forensic tooling only.
"""

from __future__ import annotations

import argparse, csv, json, re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

START = "2026-08-26 00:00:00"
END = "2026-09-25 00:00:00"

ALIASES = {
    "entry_time_utc": ["entry_time_utc","entry_time","entry_utc","entryTimeUtc","signal_time_utc","time_utc"],
    "setup_time_utc": ["setup_time_utc","setup_time","setup_utc","setupTimeUtc"],
    "direction": ["direction","side","type"],
    "entry": ["entry","entry_price","entryPrice"],
    "sl": ["sl","stop_loss","stopLoss","stop"],
    "result": ["result","outcome","status"],
    "r": ["r","R","result_r","net_r"],
}

def pick(d, names):
    for n in names:
        if n in d and d[n] not in ("", None):
            return d[n]
    return None

def normalize(d):
    out = {k: pick(d, v) for k,v in ALIASES.items()}
    if out["entry_time_utc"] is None and d.get("timestamp") is not None:
        out["entry_time_utc"] = d["timestamp"]
    if out["direction"] is not None:
        out["direction"] = str(out["direction"]).upper()
    return out

def flatten(obj):
    if isinstance(obj, list):
        for x in obj:
            if isinstance(x, dict):
                yield x
            yield from flatten(x)
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from flatten(v)

def parse_time(x):
    if x is None: return None
    s = str(x).strip().replace("Z","+00:00")
    for f in (lambda: datetime.fromisoformat(s),
              lambda: datetime.strptime(s,"%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
              lambda: datetime.strptime(s,"%Y.%m.%d %H:%M:%S").replace(tzinfo=timezone.utc)):
        try:
            dt=f()
            if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception: pass
    return None

def load_rows(path):
    if path.suffix.lower()==".csv":
        with path.open("r",encoding="utf-8-sig",newline="") as f:
            return [normalize(x) for x in csv.DictReader(f)]
    obj=json.loads(path.read_text(encoding="utf-8"))
    candidates=[]
    for d in flatten(obj):
        n=normalize(d)
        if n["entry_time_utc"] is not None and (n["direction"] is not None or n["entry"] is not None):
            candidates.append(n)
    return candidates

def in_window(r):
    t=parse_time(r["entry_time_utc"])
    return t is not None and START <= t.strftime("%Y-%m-%d %H:%M:%S") < END

def key(r):
    t=parse_time(r["entry_time_utc"])
    return (
        t.strftime("%Y-%m-%d %H:%M:%S") if t else "",
        r["direction"] or "",
        round(float(r["entry"]),5) if r["entry"] is not None else None,
        round(float(r["sl"]),5) if r["sl"] is not None else None,
    )

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--runtime",required=True,type=Path)
    ap.add_argument("--backtest",required=True,type=Path)
    ap.add_argument("--output-dir",type=Path,default=Path("artifacts/forensic/runtime-m1-replay"))
    args=ap.parse_args()

    rt=[r for r in load_rows(args.runtime) if in_window(r)]
    bt=[r for r in load_rows(args.backtest) if in_window(r)]
    if not rt: raise RuntimeError("No runtime trades found in exact window.")
    if not bt: raise RuntimeError("No backtest trades found in exact window. If the backtest artifact stores only a summary, supply its trade-level CSV/export.")

    rk=[key(r) for r in rt]; bk=[key(r) for r in bt]
    rc=Counter(rk); bc=Counter(bk)
    common=sum((rc&bc).values())
    runtime_only=sum((rc-bc).values())
    backtest_only=sum((bc-rc).values())

    def stats(rows):
        counts=Counter(str(r["result"]).upper() for r in rows if r["result"] is not None)
        decisive=counts["WIN"]+counts["LOSS"]+counts["BREAKEVEN"]
        wr=100*counts["WIN"]/decisive if decisive else 0
        net=sum(float(r["r"]) for r in rows if r["r"] not in (None,""))
        return {"signals":len(rows),"decisive":decisive,**dict(counts),"win_rate_decisive_pct":wr,"net_R":net}

    unmatched_rt=[r for r in rt if rc[key(r)]>bc[key(r)]]
    unmatched_bt=[r for r in bt if bc[key(r)]>rc[key(r])]

    result={
      "mode":"NON_CANONICAL_FORENSIC",
      "experiment":"SP2L_V2_EXACT_WINDOW_RECONCILIATION",
      "window_utc":{"start":START,"end_exclusive":END},
      "runtime":stats(rt),
      "backtest":stats(bt),
      "matching_key":"entry_time_utc + direction + entry + sl",
      "common_trades":common,
      "runtime_only":runtime_only,
      "backtest_only":backtest_only,
      "coverage_match_pct":100*common/max(len(rt),len(bt)),
      "runtime_only_examples":unmatched_rt[:25],
      "backtest_only_examples":unmatched_bt[:25],
      "notes":["Diagnostic only; does not alter geometry or execution semantics.","A JSON summary without trade-level records cannot support trade-level reconciliation."]
    }
    args.output_dir.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out=args.output_dir/f"SP2L_EXACT_WINDOW_RECON_{stamp}.json"
    out.write_text(json.dumps(result,indent=2,default=str)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    print(f"RECON_JSON={out}")

if __name__=="__main__":
    main()
