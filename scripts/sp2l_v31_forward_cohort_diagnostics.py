#!/usr/bin/env python3
"""Read-only cohort diagnostics for the locally generated V3.1 positions CSV.

No MT5 import, network access, runner/state writes, or trading decisions.
"""
from __future__ import annotations
import argparse, csv, json, math, statistics, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DURATION_EDGES = (5, 15, 30, 60)  # minutes; buckets: <5, 5-15, 15-30, 30-60, >=60

def number(row, key):
    value = row.get(key, "")
    try:
        return float(value) if value not in ("", None) else None
    except (TypeError, ValueError):
        return None

def duration_minutes(row):
    a, b = row.get("entry_time_utc"), row.get("exit_time_utc")
    if not a or not b:
        return None
    try:
        start = datetime.fromisoformat(a.replace("Z", "+00:00"))
        end = datetime.fromisoformat(b.replace("Z", "+00:00"))
        if start.tzinfo is None or end.tzinfo is None:
            return None
        return (end - start).total_seconds() / 60.0
    except (TypeError, ValueError):
        return None

def trail_bucket(value):
    try:
        n = int(value or 0)
    except (TypeError, ValueError):
        return "UNKNOWN"
    return "0" if n == 0 else ("1" if n == 1 else "2+")

def metrics(rows):
    vals = [number(r, "net_account_currency") for r in rows]
    vals = [v for v in vals if v is not None]
    wins = sum(v > 0 for v in vals)
    losses = sum(v < 0 for v in vals)
    gp = sum(v for v in vals if v > 0)
    gl = -sum(v for v in vals if v < 0)
    return {
        "count": len(vals), "wins": wins, "losses": losses,
        "breakeven": len(vals) - wins - losses,
        "win_rate_pct": round(100 * wins / len(vals), 2) if vals else None,
        "net": round(sum(vals), 2) if vals else 0.0,
        "gross_profit": round(gp, 2), "gross_loss_abs": round(gl, 2),
        "profit_factor": round(gp / gl, 4) if gl else (None if not gp else "infinity"),
        "average_net": round(statistics.mean(vals), 2) if vals else None,
        "median_net": round(statistics.median(vals), 2) if vals else None,
    }

def quantile(values, q):
    if not values:
        return None
    x = sorted(values)
    pos = (len(x) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    value = x[lo] if lo == hi else x[lo] * (hi - pos) + x[hi] * (pos - lo)
    return round(value, 2)

def duration_bucket(minutes):
    if minutes is None or minutes < 0:
        return "UNKNOWN_OR_NEGATIVE"
    if minutes < 5: return "<5m"
    if minutes < 15: return "5-15m"
    if minutes < 30: return "15-30m"
    if minutes < 60: return "30-60m"
    return ">=60m"

def analyze(rows):
    all_rows = [r for r in rows if r.get("status") == "CLOSED"]
    anomalies = []
    for r in rows:
        vin, vout = number(r, "volume_in"), number(r, "volume_out")
        if r.get("status") != "CLOSED":
            anomalies.append({"position_id":r.get("position_id"),"flags":[r.get("status","UNKNOWN")]})
            continue
        flags = []
        if vin is None or vout is None:
            flags.append("MISSING_VOLUME")
        elif abs(vin - vout) > 1e-6:
            flags.append("ENTRY_EXIT_VOLUME_MISMATCH")
        if r.get("side") not in ("BUY", "SELL"):
            flags.append("UNKNOWN_SIDE")
        if duration_minutes(r) is None:
            flags.append("MISSING_OR_INVALID_TIME")
        if flags:
            anomalies.append({"position_id":r.get("position_id"),"flags":flags})

    def grouped(key_fn):
        groups = defaultdict(list)
        for r in all_rows:
            groups[key_fn(r)].append(r)
        return {str(k):metrics(v) for k,v in sorted(groups.items(), key=lambda kv: str(kv[0]))}

    side = grouped(lambda r: r.get("side","UNKNOWN"))
    trail = grouped(lambda r: trail_bucket(r.get("trail_update_count")))
    side_trail = grouped(lambda r: (r.get("side","UNKNOWN"), trail_bucket(r.get("trail_update_count"))))
    durations = [(r, duration_minutes(r)) for r in all_rows]
    valid_durations = [d for _,d in durations if d is not None and d >= 0]
    duration_groups = defaultdict(list)
    for r,d in durations:
        duration_groups[duration_bucket(d)].append(r)

    movement = {"BUY": [], "SELL": []}
    for r in all_rows:
        ep, xp = number(r,"entry_price_volume_weighted"), number(r,"exit_price_volume_weighted")
        side_name = r.get("side")
        if ep is not None and xp is not None and side_name in movement:
            signed = xp-ep if side_name == "BUY" else ep-xp
            movement[side_name].append(signed)

    volume_flags = [x for x in anomalies if "ENTRY_EXIT_VOLUME_MISMATCH" in x["flags"]]
    return {
        "input_rows":len(rows), "closed_rows":len(all_rows),
        "closed_net_reconciled":round(sum(number(r,"net_account_currency") or 0 for r in all_rows),2),
        "by_side":side, "by_trailing_bucket":trail, "by_side_and_trailing_bucket":side_trail,
        "hold_duration_minutes":{
            "valid_count":len(valid_durations),
            "min":round(min(valid_durations),2) if valid_durations else None,
            "q25":quantile(valid_durations,.25), "median":quantile(valid_durations,.5),
            "q75":quantile(valid_durations,.75),
            "max":round(max(valid_durations),2) if valid_durations else None,
            "buckets":{k:metrics(v) for k,v in sorted(duration_groups.items())},
            "bucket_boundaries_minutes":[0,5,15,30,60,"infinity"],
        },
        "signed_price_movement_raw_price_units":{
            side_name: {
                "count":len(vals),
                "average":round(statistics.mean(vals),5) if vals else None,
                "median":round(statistics.median(vals),5) if vals else None,
            } for side_name,vals in movement.items()
        },
        "anomalies":{"count":len(anomalies),"volume_mismatch_count":len(volume_flags),"rows":anomalies},
        "interpretation":"Descriptive cohorts only. Trailing-count groups are selected by realized price path; no causal effect or strategy rule is inferred. Price movement is raw price units, not pips, points, or R.",
    }

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv",required=True,type=Path)
    p.add_argument("--out",type=Path,default=Path("artifacts/forensic/v31-local-20261108/cohort_diagnostics.json"))
    a=p.parse_args(argv)
    if not a.csv.is_file(): p.error(f"CSV not found: {a.csv}")
    try:
        with a.csv.open("r",encoding="utf-8-sig",newline="") as f:
            rows=list(csv.DictReader(f))
        report=analyze(rows)
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    except (OSError,ValueError,KeyError) as e:
        print(f"COHORT_ERROR={type(e).__name__}: {e}",file=sys.stderr); return 2
    print("SP2L V3.1 LOCAL COHORT DIAGNOSTICS")
    print(f"INPUT_ROWS={report['input_rows']} CLOSED_ROWS={report['closed_rows']}")
    print(f"CLOSED_NET_RECONCILED={report['closed_net_reconciled']}")
    print("BY_SIDE="+json.dumps(report["by_side"],sort_keys=True))
    print("BY_TRAIL_BUCKET="+json.dumps(report["by_trailing_bucket"],sort_keys=True))
    print("BY_SIDE_AND_TRAIL="+json.dumps(report["by_side_and_trailing_bucket"],sort_keys=True))
    print("HOLD_DURATION="+json.dumps(report["hold_duration_minutes"],sort_keys=True))
    print("PRICE_MOVEMENT_RAW_UNITS="+json.dumps(report["signed_price_movement_raw_price_units"],sort_keys=True))
    print("ANOMALIES="+json.dumps(report["anomalies"],sort_keys=True))
    print(f"REPORT_JSON={a.out.resolve()}")
    print("READ_ONLY=True MT5_CONNECTION=False RUNNER_MODIFIED=False")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
