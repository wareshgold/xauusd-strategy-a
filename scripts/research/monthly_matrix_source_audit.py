#!/usr/bin/env python3
"""Research-only source-aligned XAUUSD M1 candidate replay.

Does not claim fills, exits, P&L, PF, win rate, or drawdown. OHLC does not
establish A pending-limit fills, B market execution prices, or intrabar order.
Strategy B risk handling follows source snapshot 0037c540: non-positive risk
returns None (continue searching); risk above maximum returns INVALID (stop).
"""
import argparse, csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

A_PGAP, A_SPIKE, A_MAXSL, A_TPR, A_TTL = 1.0, 1.5, 10.0, 2.0, 1800
B_PGAP, B_SPIKE, B_MAXSL, B_TPR, B_EMA, B_OPPOSITE = 1.0, 1.5, 10.0, 0.9, 60, 1
B_SOURCE_COMMIT = "0037c540"

def parse_ts(s):
    s=s.strip()
    if s.endswith("Z"): s=s[:-1]+"+00:00"
    d=datetime.fromisoformat(s)
    if d.tzinfo is None: raise ValueError("timestamp lacks timezone: "+s)
    return int(d.astimezone(timezone.utc).timestamp())

def iso(t): return datetime.fromtimestamp(t,timezone.utc).isoformat().replace("+00:00","Z")

def load(path):
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open(newline="",encoding="utf-8-sig") as f:
        rd=csv.DictReader(f)
        if not rd.fieldnames: raise ValueError("CSV has no header")
        cols={c.strip().lower():c for c in rd.fieldnames}
        tc=next((cols[k] for k in ("time_utc_iso","timestamp_utc","timestamp","datetime","time","date") if k in cols),None)
        if not tc: raise ValueError("No recognized timestamp column: "+repr(rd.fieldnames))
        if any(k not in cols for k in ("open","high","low","close")): raise ValueError("OHLC columns missing")
        bars=[]
        for line,row in enumerate(rd,2):
            b={"time":parse_ts(row[tc])}
            for k in ("open","high","low","close"): b[k]=float(row[cols[k]])
            if b["high"] < max(b["open"],b["close"],b["low"]) or b["low"] > min(b["open"],b["close"],b["high"]):
                raise ValueError(f"invalid OHLC at CSV line {line}")
            if bars and b["time"]<=bars[-1]["time"]: raise ValueError("timestamps must be strictly increasing; no sorting/deduplication")
            b["i"]=len(bars); b["segment"]=0 if not bars else bars[-1]["segment"]+(b["time"]-bars[-1]["time"]>60)
            bars.append(b)
    if not bars: raise ValueError("no bars")
    return bars,digest,tc

def body(b): return abs(b["close"]-b["open"])

def a_detect(p,s,a):
    pb,sb,ab=body(p),body(s),body(a)
    buy=(a["close"]>s["close"] and a["open"]>s["open"] and s["close"]>p["close"] and s["open"]>p["open"] and a["close"]>a["open"] and s["close"]>s["open"] and p["close"]>p["open"] and a["low"]>p["high"]+A_PGAP and sb>A_SPIKE*pb and sb>A_SPIKE*ab)
    sell=(a["close"]<s["close"] and a["open"]<s["open"] and s["close"]<p["close"] and s["open"]<p["open"] and a["close"]<a["open"] and s["close"]<s["open"] and p["close"]<p["open"] and a["high"]<p["low"]-A_PGAP and sb>A_SPIKE*pb and sb>A_SPIKE*ab)
    return "BUY" if buy and not sell else "SELL" if sell and not buy else None

def b_detect(p,s,a,c):
    buy=(c["low"]<a["low"] and a["close"]>s["close"] and a["open"]>s["open"] and s["close"]>p["close"] and s["open"]>p["open"] and a["close"]>a["open"] and s["close"]>s["open"] and p["close"]>p["open"] and a["low"]>p["high"]+B_PGAP and (s["close"]-s["open"])>B_SPIKE*(a["close"]-a["open"]) and (s["close"]-s["open"])>B_SPIKE*(p["close"]-p["open"]))
    sell=(c["high"]>a["high"] and a["close"]<s["close"] and a["open"]<s["open"] and s["close"]<p["close"] and s["open"]<p["open"] and a["close"]<a["open"] and s["close"]<s["open"] and p["close"]<p["open"] and a["high"]<p["low"]-B_PGAP and (s["open"]-s["close"])>B_SPIKE*(a["open"]-a["close"]) and (s["open"]-s["close"])>B_SPIKE*(p["open"]-p["close"]))
    return "BUY" if buy and not sell else "SELL" if sell and not buy else None

def ema(bars,period):
    alpha=2/(period+1); out=[]; prev=None
    for b in bars:
        prev=b["close"] if prev is None else alpha*b["close"]+(1-alpha)*prev
        out.append(prev)
    return out

def trend_ok(bars,start,end,direction):
    opp=0
    for k in range(start+1,end+1):
        favorable=bars[k]["high"]>bars[k-1]["high"] if direction=="BUY" else bars[k]["low"]<bars[k-1]["low"]
        opp=0 if favorable else opp+1
        if opp>B_OPPOSITE: return False
    return True

def replay_a(bars):
    rows=[]; counts={"setups":0,"trigger_candidates":0,"invalid_risk":0,"ttl_expired":0,"gap_terminated":0,"no_trigger_in_ttl":0}
    for i in range(2,len(bars)):
        if len({bars[k]["segment"] for k in (i-2,i-1,i)})!=1: continue
        d=a_detect(bars[i-2],bars[i-1],bars[i])
        if not d: continue
        counts["setups"]+=1; sl=bars[i-2]["low"] if d=="BUY" else bars[i-2]["high"]
        status="NO_TRIGGER_IN_TTL"; found=None; deadline=bars[i]["time"]+A_TTL
        for j in range(i+1,len(bars)):
            if bars[j]["segment"]!=bars[i]["segment"]: status="GAP_TERMINATED"; counts["gap_terminated"]+=1; break
            if bars[j]["time"]>deadline: status="TTL_EXPIRED"; counts["ttl_expired"]+=1; break
            trig=bars[j]["low"]<bars[j-1]["low"] if d=="BUY" else bars[j]["high"]>bars[j-1]["high"]
            if not trig: continue
            entry=bars[j]["low"] if d=="BUY" else bars[j]["high"]; risk=entry-sl if d=="BUY" else sl-entry
            found={"j":j,"entry":entry,"risk":risk}
            if risk<=0 or risk>A_MAXSL: status="INVALID_RISK_FIRST_TRIGGER"; counts["invalid_risk"]+=1
            else: status="THEORETICAL_TRIGGER_ONLY"; counts["trigger_candidates"]+=1
            break
        if status=="NO_TRIGGER_IN_TTL": counts["no_trigger_in_ttl"]+=1
        tp=(found["entry"]+A_TPR*found["risk"] if d=="BUY" else found["entry"]-A_TPR*found["risk"]) if found and status=="THEORETICAL_TRIGGER_ONLY" else ""
        rows.append({"strategy":"A_RR2_TRAIL4","direction":d,"setup_time_utc":iso(bars[i]["time"]),"setup_index":i,"segment":bars[i]["segment"],"event_status":status,"sl_theoretical":sl,"trigger_time_utc":iso(bars[found["j"]]["time"]) if found else "","entry_theoretical":found["entry"] if found else "","risk_theoretical":found["risk"] if found else "","tp_2r_theoretical":tp,"fill_status":"UNRESOLVED_FROM_M1_OHLC","exit_status":"NOT_SIMULATED"})
    return rows,counts

def b_risk_action(risk):
    """Mirror Strategy B check_pending_buy/sell risk branch ordering."""
    if risk <= 0:
        return "IGNORE_AND_CONTINUE"
    if risk > B_MAXSL:
        return "INVALID_AND_STOP"
    return "CONTINUE_TO_FILTERS"


def replay_b(bars):
    em=ema(bars,B_EMA); rows=[]; counts={"setup_trigger_bars":0,"valid_theoretical_entries":0,"ema_blocked_trigger_attempts":0,"trend_blocked_trigger_attempts":0,"nonpositive_risk_trigger_attempts":0,"over_max_risk_trigger_attempts":0,"gap_terminated":0,"no_following_entry_trigger":0}
    for i in range(3,len(bars)):
        if len({bars[k]["segment"] for k in range(i-3,i+1)})!=1: continue
        d=b_detect(bars[i-3],bars[i-2],bars[i-1],bars[i])
        if not d: continue
        counts["setup_trigger_bars"]+=1; sl=bars[i-3]["low"] if d=="BUY" else bars[i-3]["high"]; status="NO_FOLLOWING_ENTRY_TRIGGER"; found=None
        for j in range(i+1,len(bars)):
            if bars[j]["segment"]!=bars[i]["segment"]: status="GAP_TERMINATED"; counts["gap_terminated"]+=1; break
            trig=bars[j]["low"]<bars[j-1]["low"] if d=="BUY" else bars[j]["high"]>bars[j-1]["high"]
            if not trig: continue
            entry=bars[j]["low"] if d=="BUY" else bars[j]["high"]; risk=entry-sl if d=="BUY" else sl-entry
            # Source fidelity: check_pending_buy/sell returns None for risk <= 0,
            # so that trigger is ignored and the pending setup keeps searching.
            risk_action = b_risk_action(risk)
            if risk_action == "IGNORE_AND_CONTINUE":
                counts["nonpositive_risk_trigger_attempts"] += 1
                continue
            # Source fidelity: risk above the configured maximum returns "INVALID"
            # and terminates the pending setup immediately.
            if risk_action == "INVALID_AND_STOP":
                status="INVALID_RISK_OVER_MAX_FIRST_TRIGGER"
                counts["over_max_risk_trigger_attempts"] += 1
                found={"j":j,"entry":entry,"risk":risk}
                break
            if not trend_ok(bars,i,j,d): counts["trend_blocked_trigger_attempts"]+=1; continue
            if not (bars[j]["close"]>em[j] if d=="BUY" else bars[j]["close"]<em[j]): counts["ema_blocked_trigger_attempts"]+=1; continue
            found={"j":j,"entry":entry,"risk":risk}; status="THEORETICAL_TRIGGER_ONLY"; counts["valid_theoretical_entries"]+=1; break
        if status=="NO_FOLLOWING_ENTRY_TRIGGER": counts["no_following_entry_trigger"]+=1
        tp=(found["entry"]+B_TPR*found["risk"] if d=="BUY" else found["entry"]-B_TPR*found["risk"]) if found and status=="THEORETICAL_TRIGGER_ONLY" else ""
        rows.append({"strategy":"B_SOURCE_SNAPSHOT","direction":d,"setup_time_utc":iso(bars[i]["time"]),"setup_index":i,"segment":bars[i]["segment"],"event_status":status,"sl_theoretical":sl,"trigger_time_utc":iso(bars[found["j"]]["time"]) if found else "","entry_theoretical":found["entry"] if found else "","risk_theoretical":found["risk"] if found else "","tp_0_9r_theoretical":tp,"fill_status":"MARKET_EXECUTION_PRICE_UNRESOLVED_FROM_M1_OHLC","exit_status":"NOT_SIMULATED"})
    return rows,counts

def write_csv(path,rows,empty_fields):
    fields=list(rows[0]) if rows else empty_fields
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--csv",required=True,type=Path); ap.add_argument("--out",required=True,type=Path); ap.add_argument("--expected-sha256",default=""); a=ap.parse_args()
    if a.out.exists() and any(a.out.iterdir()): raise SystemExit("Refusing to overwrite non-empty output: "+str(a.out))
    bars,digest,time_col=load(a.csv)
    if a.expected_sha256 and digest.lower()!=a.expected_sha256.lower(): raise SystemExit(f"SHA256 mismatch: expected {a.expected_sha256}, got {digest}")
    gaps=[]
    for i in range(1,len(bars)):
        delta=bars[i]["time"]-bars[i-1]["time"]
        if delta>60: gaps.append({"left_time_utc":iso(bars[i-1]["time"]),"right_time_utc":iso(bars[i]["time"]),"delta_seconds":delta,"missing_minute_slots":max(0,delta//60-1),"left_segment":bars[i-1]["segment"],"right_segment":bars[i]["segment"]})
    ar,ac=replay_a(bars); br,bc=replay_b(bars); a.out.mkdir(parents=True,exist_ok=True)
    write_csv(a.out/"strategy_a_events.csv",ar,["strategy","event_status"]); write_csv(a.out/"strategy_b_events.csv",br,["strategy","event_status"]); write_csv(a.out/"data_gaps.csv",gaps,["left_time_utc","right_time_utc","delta_seconds","missing_minute_slots","left_segment","right_segment"])
    summary={"status":"CANDIDATE_REPLAY_COMPLETE_EXECUTION_METRICS_BLOCKED","research_only":True,"canonical":False,"input_file":str(a.csv),"input_sha256":digest,"timestamp_column":time_col,"bars":len(bars),"first_bar_utc":iso(bars[0]["time"]),"last_bar_utc":iso(bars[-1]["time"]),"segments":1+len(gaps),"gaps_over_one_minute":len(gaps),"missing_minute_slots":sum(g["missing_minute_slots"] for g in gaps),"strategy_a":ac,"strategy_b":bc,"execution_metrics":{"closed_trades":None,"wins":None,"losses":None,"net_pnl":None,"total_r":None,"profit_factor":None,"max_drawdown":None,"reason":"No fill/exit semantics are fabricated. A pending-limit fill and B market execution price cannot be established from M1 OHLC alone; intrabar SL/TP ordering is unresolved."},"source_notes":{"A":{"p_gap_price":A_PGAP,"spike_multiplier":A_SPIKE,"max_sl_distance":A_MAXSL,"tp_r":A_TPR,"configured_pending_ttl_seconds":A_TTL,"trail_distance_price":0.4,"trail_note":"Legacy config is 4 * 0.1; not silently changed to current broker point."},"B":{"source_commit":B_SOURCE_COMMIT,"p_gap_price":B_PGAP,"spike_multiplier":B_SPIKE,"max_sl_distance":B_MAXSL,"tp_r":B_TPR,"ema_period":B_EMA,"max_opposite_moves":B_OPPOSITE},"portfolio_replay":"NOT_PERFORMED; independent candidates may overlap"},"artifacts":["strategy_a_events.csv","strategy_b_events.csv","data_gaps.csv"]}
    (a.out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (a.out/"README.md").write_text("# Monthly XAUUSD candidate replay audit\n\nResearch-only; not a P&L backtest.\n\nInput SHA256: "+digest+"\nBars: "+str(len(bars))+"\nA setups/candidates: "+str(ac["setups"])+"/"+str(ac["trigger_candidates"])+"\nB setup trigger bars/theoretical entries: "+str(bc["setup_trigger_bars"])+"/"+str(bc["valid_theoretical_entries"])+"\n\nFills and exits remain uncomputed because M1 OHLC cannot establish the A pending-limit fill, B market execution price, or intrabar SL/TP order. Existing outputs are not overwritten; pass a new empty --out directory.\n",encoding="utf-8")
    print(json.dumps({"status":summary["status"],"output":str(a.out),"sha256":digest,"bars":len(bars),"a":ac,"b":bc,"gaps":len(gaps)},indent=2))
if __name__=="__main__": main()
