#!/usr/bin/env python3
"""Explicitly hypothetical OHLC execution proxy for the monthly A/B comparison.

This is NOT canonical execution and is NOT a substitute for tick replay. It uses
source-audit candidate logic, approximates both entry prices by the theoretical
trigger low/high, starts exit evaluation on the NEXT bar (avoids same-bar
lookahead), treats stop+target in the same bar as stop-first, uses open price
when a gap opens through an exit level, and records unresolved end-of-data trades.
A fixed-SL/TP and A trailing-distance proxy are both reported. No costs or
cash P&L are fabricated. Independent candidates may overlap; metrics are not
portfolio metrics. Do not use for production decisions.
"""
import argparse, csv, importlib.util, json, math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_SHA256 = "b0782e716c7eccbd29ef25e146c088b356f2aadf2ccd5d7ea24e6ac1488aa285"
A_TP_R = 2.0
B_TP_R = 0.9
A_TRAIL_DISTANCE = 0.40

def load_audit_module(script_path):
    spec = importlib.util.spec_from_file_location("monthly_matrix_source_audit", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def parse_iso(s):
    if not s:
        return None
    return int(datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc).timestamp())

def iso(ts):
    return datetime.fromtimestamp(ts, timezone.utc).isoformat().replace("+00:00", "Z")

def simulate_one(bars, candidate, strategy, trailing=False):
    direction = candidate["direction"]
    entry = float(candidate["entry_theoretical"])
    sl = float(candidate["sl_theoretical"])
    risk = float(candidate["risk_theoretical"])
    if not math.isfinite(risk) or risk <= 0:
        return None
    target_r = A_TP_R if strategy == "A" else B_TP_R
    target = entry + target_r*risk if direction == "BUY" else entry - target_r*risk
    stop = sl
    trigger_ts = parse_iso(candidate["trigger_time_utc"])
    trigger_i = next((i for i,b in enumerate(bars) if b["time"] == trigger_ts), None)
    if trigger_i is None:
        return {"strategy":strategy,"variant":"A_TRAIL_0.40_PROXY" if trailing else "FIXED_SL_TP_PROXY",
                "direction":direction,"entry_time_utc":candidate["trigger_time_utc"],
                "entry_proxy":entry,"sl_initial":sl,"target":target,"risk_price":risk,
                "status":"UNRESOLVED_TRIGGER_BAR_NOT_FOUND","exit_time_utc":"","exit_price":"",
                "r_multiple":"","exit_reason":"DATA_ALIGNMENT_ERROR"}
    # Entry candle is excluded from exit checks: its intrabar sequence is unknown.
    best = entry
    for i in range(trigger_i + 1, len(bars)):
        b = bars[i]
        # If the market reopens beyond a level after a timestamp gap, use open as
        # the proxy exit; never synthesize prices for the missing interval.
        gap_open = i > 0 and b["time"] - bars[i-1]["time"] > 60
        o,h,l = b["open"],b["high"],b["low"]
        if direction == "BUY":
            stop_hit_open = gap_open and o <= stop
            target_hit_open = gap_open and o >= target
            if stop_hit_open:
                px,reason=o,"GAP_STOP_AT_OPEN"
            elif target_hit_open:
                px,reason=o,"GAP_TARGET_AT_OPEN"
            else:
                sh = l <= stop
                th = h >= target
                if sh and th:
                    px,reason=stop,"BOTH_TOUCHED_STOP_FIRST"
                elif sh:
                    px,reason=stop,"SL"
                elif th:
                    px,reason=target,"TP"
                else:
                    px=reason=None
            if reason is not None:
                r=(px-entry)/risk
                return trade_row(strategy,trailing,candidate,entry,sl,target,risk,b,px,reason,r)
            if trailing:
                best=max(best,h)
                stop=max(stop,best-A_TRAIL_DISTANCE)
        else:
            stop_hit_open = gap_open and o >= stop
            target_hit_open = gap_open and o <= target
            if stop_hit_open:
                px,reason=o,"GAP_STOP_AT_OPEN"
            elif target_hit_open:
                px,reason=o,"GAP_TARGET_AT_OPEN"
            else:
                sh = h >= stop
                th = l <= target
                if sh and th:
                    px,reason=stop,"BOTH_TOUCHED_STOP_FIRST"
                elif sh:
                    px,reason=stop,"SL"
                elif th:
                    px,reason=target,"TP"
                else:
                    px=reason=None
            if reason is not None:
                r=(entry-px)/risk
                return trade_row(strategy,trailing,candidate,entry,sl,target,risk,b,px,reason,r)
            if trailing:
                best=min(best,l)
                stop=min(stop,best+A_TRAIL_DISTANCE)
    return {"strategy":strategy,"variant":"A_TRAIL_0.40_PROXY" if trailing else "FIXED_SL_TP_PROXY",
            "direction":direction,"setup_time_utc":candidate["setup_time_utc"],
            "entry_time_utc":candidate["trigger_time_utc"],"entry_proxy":entry,
            "sl_initial":sl,"target":target,"risk_price":risk,"exit_time_utc":"",
            "exit_price":"","exit_reason":"OPEN_AT_END_OF_DATA","status":"UNRESOLVED",
            "r_multiple":"","note":"No exit observed before data end"}

def trade_row(strategy,trailing,candidate,entry,sl,target,risk,b,px,reason,r):
    return {"strategy":strategy,"variant":"A_TRAIL_0.40_PROXY" if trailing else "FIXED_SL_TP_PROXY",
            "direction":candidate["direction"],"setup_time_utc":candidate["setup_time_utc"],
            "entry_time_utc":candidate["trigger_time_utc"],"entry_proxy":entry,
            "sl_initial":sl,"target":target,"risk_price":risk,"exit_time_utc":iso(b["time"]),
            "exit_price":px,"exit_reason":reason,"status":"CLOSED",
            "r_multiple":round(r,8),"note":""}

def summarize(rows):
    closed=[r for r in rows if r["status"]=="CLOSED"]
    unresolved=[r for r in rows if r["status"]!="CLOSED"]
    rs=[float(r["r_multiple"]) for r in closed]
    wins=sum(x>0 for x in rs); losses=sum(x<0 for x in rs); flats=sum(x==0 for x in rs)
    gross_win=sum(x for x in rs if x>0); gross_loss=-sum(x for x in rs if x<0)
    return {
      "candidate_trades":len(rows),"closed_proxy_trades":len(closed),"unresolved":len(unresolved),
      "wins":wins,"losses":losses,"flats":flats,
      "win_rate_pct_closed_only":round(100*wins/len(closed),4) if closed else None,
      "total_R_closed_only":round(sum(rs),6),
      "average_R_closed_only":round(sum(rs)/len(rs),6) if rs else None,
      "profit_factor_gross_R":round(gross_win/gross_loss,6) if gross_loss else ("INF" if gross_win else None),
      "gross_profit_R":round(gross_win,6),"gross_loss_R":round(gross_loss,6),
      "costs":"NOT INCLUDED","cash_pnl":"NOT COMPUTED",
      "portfolio_metrics":"NOT COMPUTED; candidate trades can overlap"
    }

def write_csv(path, rows):
    fields=list(rows[0]) if rows else ["strategy","variant","status"]
    with path.open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv",required=True,type=Path)
    ap.add_argument("--source-audit-script",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    ap.add_argument("--expected-sha256",default=EXPECTED_SHA256)
    args=ap.parse_args()
    if args.out.exists() and any(args.out.iterdir()):
        raise SystemExit("Refusing to overwrite non-empty output directory: "+str(args.out))
    mod=load_audit_module(args.source_audit_script)
    bars,digest,time_col=mod.load(args.csv)
    if digest.lower()!=args.expected_sha256.lower():
        raise SystemExit(f"SHA256 mismatch: expected {args.expected_sha256}, got {digest}")
    a_events,a_counts=mod.replay_a(bars)
    b_events,b_counts=mod.replay_b(bars)
    a_candidates=[r for r in a_events if r.get("event_status")=="THEORETICAL_TRIGGER_ONLY"]
    b_candidates=[r for r in b_events if r.get("event_status")=="THEORETICAL_TRIGGER_ONLY"]
    trades=[]
    for c in a_candidates:
        trades.append(simulate_one(bars,c,"A",False))
        trades.append(simulate_one(bars,c,"A",True))
    for c in b_candidates:
        trades.append(simulate_one(bars,c,"B",False))
    # A separate ledger per scenario avoids mixing results in a single metric.
    scenarios={}
    for name in ("A_FIXED_SL_TP","A_TRAIL_0.40_PROXY","B_FIXED_SL_TP"):
        variant={"A_FIXED_SL_TP":"FIXED_SL_TP_PROXY","A_TRAIL_0.40_PROXY":"A_TRAIL_0.40_PROXY","B_FIXED_SL_TP":"FIXED_SL_TP_PROXY"}[name]
        sr=[r for r in trades if (r["strategy"]=="A" if name.startswith("A_") else r["strategy"]=="B") and r["variant"]==variant]
        if name=="A_FIXED_SL_TP": sr=[r for r in sr if r["strategy"]=="A"]
        scenarios[name]=summarize(sr)
        write_csv(args.out/(name.lower()+"_trades.csv"),sr)
    gaps=[]
    for i in range(1,len(bars)):
        delta=bars[i]["time"]-bars[i-1]["time"]
        if delta>60:gaps.append({"left":iso(bars[i-1]["time"]),"right":iso(bars[i]["time"]),"delta_seconds":delta,"missing_minute_slots":max(0,delta//60-1)})
    result={
      "status":"OHLC_PROXY_COMPLETE_NOT_CANONICAL",
      "research_only":True,"canonical":False,
      "input":{"path":str(args.csv.resolve()),"sha256":digest,"bars":len(bars),
               "first_utc":iso(bars[0]["time"]),"last_utc":iso(bars[-1]["time"]),
               "timestamp_column":time_col,"gap_segments_gt_1m":len(gaps),
               "missing_minute_slots_not_synthesized":sum(g["missing_minute_slots"] for g in gaps)},
      "candidate_scan":{"A":a_counts,"B":b_counts,"A_valid_candidates":len(a_candidates),"B_valid_candidates":len(b_candidates)},
      "execution_proxy_assumptions":[
        "Entry is assumed filled at the candidate's theoretical trigger low/high; actual A limit fills and B Ask/Bid market fills are unknown.",
        "Exit checks begin on the bar AFTER the trigger bar to avoid inventing intrabar event order on the entry candle.",
        "If SL and TP are both touched in one bar, SL is assumed first (conservative proxy).",
        "If a post-gap bar opens through SL/TP, exit is marked at that bar's open; missing bars are never synthesized.",
        "A trailing variant trails 0.40 price units from the best completed-bar high/low, with changes effective only on the next bar. This is a sensitivity proxy, not source-certified trailing semantics.",
        "No spread, slippage, commission, swap, or cash P&L is included. Candidate trades may overlap; metrics are per-candidate, not a portfolio."
      ],
      "scenarios":scenarios,
      "interpretation":"These are assumption-bounded OHLC proxy results, not realized or canonical backtest performance. Use them to see sensitivity, not to authorize live trading.",
      "artifacts":["a_fixed_sl_tp_trades.csv","a_trail_0.40_proxy_trades.csv","b_fixed_sl_tp_trades.csv"]
    }
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/"summary.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    lines=["# Monthly XAUUSD OHLC proxy backtest","",f"- Input SHA256: {digest}",f"- Bars: {len(bars)}",f"- Gap segments: {len(gaps)} (preserved; no synthetic bars)", "", "| Scenario | Closed | Unresolved | Win rate | Total R | PF (gross R) |","|---|---:|---:|---:|---:|---:|"]
    for name,s in scenarios.items():
        lines.append(f"| {name} | {s['closed_proxy_trades']} | {s['unresolved']} | {s['win_rate_pct_closed_only']}% | {s['total_R_closed_only']} | {s['profit_factor_gross_R']} |")
    lines += ["","## Assumptions and limitations",""] + ["- "+x for x in result["execution_proxy_assumptions"]]
    lines += ["","**Not canonical. Not realized broker performance. No costs. Not a portfolio simulation.**",""]
    (args.out/"report.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({"status":result["status"],"out":str(args.out.resolve()),"sha256":digest,"scenarios":scenarios},indent=2))

if __name__=="__main__":
    main()
