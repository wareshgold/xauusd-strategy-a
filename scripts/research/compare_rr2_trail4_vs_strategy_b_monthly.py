#!/usr/bin/env python3
"""Research-only independent signal-candidate replay; does not fabricate fills or P&L. Not a position-level trade simulation."""
import argparse, csv, hashlib, json, math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

START = int(datetime(2026, 9, 24, tzinfo=timezone.utc).timestamp())
END = int(datetime(2026, 10, 24, tzinfo=timezone.utc).timestamp())
PGAP, SPIKE, MAX_SL = 1.0, 1.5, 10.0
EXPECTED_DATA_SHA256 = "b0782e716e7ccbd29ef25e146c088b356f2aadf2ccd5d7ea24e6ac1488aa285"

def ts(v):
    v=v.strip()
    if v.isdigit():
        n=int(v); return n//1000 if n>10_000_000_000 else n
    d=datetime.fromisoformat(v.replace("Z","+00:00"))
    if d.tzinfo is None: raise ValueError("timestamp has no timezone: "+v)
    return int(d.astimezone(timezone.utc).timestamp())

def load(path):
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest.lower() != EXPECTED_DATA_SHA256:
        raise ValueError(f"CSV SHA-256 mismatch: expected {EXPECTED_DATA_SHA256}, got {digest}. Refusing to replay a different dataset.")
    with path.open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f)
        if not r.fieldnames: raise ValueError("CSV has no header")
        names={x.strip().lower():x for x in r.fieldnames}
        tc=next((names[x] for x in ("time","timestamp","datetime","date","time_utc","gmt time") if x in names),None)
        if not tc or any(k not in names for k in ("open","high","low","close")):
            raise ValueError("CSV needs timestamp/time and open,high,low,close columns; found "+repr(r.fieldnames))
        bars=[]
        for n,row in enumerate(r,2):
            try:
                b={"time":ts(row[tc])}
                b.update({k:float(row[names[k]]) for k in ("open","high","low","close")})
                if not all(math.isfinite(b[k]) for k in ("open","high","low","close")): raise ValueError("non-finite OHLC")
                if b["high"] < max(b["open"],b["close"],b["low"]) or b["low"] > min(b["open"],b["close"],b["high"]): raise ValueError("invalid OHLC bounds")
                bars.append(b)
            except Exception as e: raise ValueError(f"bad CSV row {n}: {e}") from e
    bars.sort(key=lambda b:b["time"])
    if len({b["time"] for b in bars}) != len(bars): raise ValueError("duplicate timestamps; refusing silent deduplication")
    bars=[b for b in bars if START <= b["time"] < END]
    if len(bars)<100: raise ValueError(f"only {len(bars)} rows in requested window: {len(bars)}")
    gaps=[bars[i]["time"]-bars[i-1]["time"] for i in range(1,len(bars)) if bars[i]["time"]-bars[i-1]["time"]>60]
    audit={"sha256":digest,"source_path":str(path.resolve()),"window_start_utc":"2026-09-24T00:00:00+00:00","window_end_utc_exclusive":"2026-10-24T00:00:00+00:00","rows":len(bars),"first_utc":datetime.fromtimestamp(bars[0]["time"],timezone.utc).isoformat(),"last_utc":datetime.fromtimestamp(bars[-1]["time"],timezone.utc).isoformat(),"gap_segments_gt_1m":len(gaps),"missing_minute_slots":sum(max(0,d//60-1) for d in gaps)}
    return bars,audit

def a_detect(bars,i):
    p,s,a=bars[i-2],bars[i-1],bars[i]
    pb,sb,ab=abs(p["close"]-p["open"]),abs(s["close"]-s["open"]),abs(a["close"]-a["open"])
    buy=(a["close"]>s["close"] and a["open"]>s["open"] and s["close"]>p["close"] and s["open"]>p["open"] and a["close"]>a["open"] and s["close"]>s["open"] and p["close"]>p["open"] and a["low"]>p["high"]+PGAP and sb>SPIKE*pb and sb>SPIKE*ab)
    sell=(a["close"]<s["close"] and a["open"]<s["open"] and s["close"]<p["close"] and s["open"]<p["open"] and a["close"]<a["open"] and s["close"]<s["open"] and p["close"]<p["open"] and a["high"]<p["low"]-PGAP and sb>SPIKE*pb and sb>SPIKE*ab)
    return "BUY" if buy and not sell else "SELL" if sell and not buy else None

def b_detect(bars,i):
    # Strategy B source: -4 pre-spike, -3 spike, -2 after, -1 detection candle.
    p,s,a,c=bars[i-3],bars[i-2],bars[i-1],bars[i]
    buy=(c["low"]<a["low"] and a["close"]>s["close"] and a["open"]>s["open"] and s["close"]>p["close"] and s["open"]>p["open"] and a["close"]>a["open"] and s["close"]>s["open"] and p["close"]>p["open"] and a["low"]>p["high"]+PGAP and (s["close"]-s["open"])>SPIKE*(a["close"]-a["open"]) and (s["close"]-s["open"])>SPIKE*(p["close"]-p["open"]) and (s["close"]-s["open"])>SPIKE*(c["close"]-c["open"]))
    sell=(c["high"]>a["high"] and a["close"]<s["close"] and a["open"]<s["open"] and s["close"]<p["close"] and s["open"]<p["open"] and a["close"]<a["open"] and s["close"]<s["open"] and p["close"]<p["open"] and a["high"]<p["low"]-PGAP and (s["open"]-s["close"])>SPIKE*(a["open"]-a["close"]) and (s["open"]-s["close"])>SPIKE*(p["open"]-p["close"]) and (s["open"]-s["close"])>SPIKE*(c["open"]-c["close"]))
    return "BUY" if buy and not sell else "SELL" if sell and not buy else None

def ema(values,period=60):
    alpha=2/(period+1); out=[]
    for x in values: out.append(x if not out else alpha*x+(1-alpha)*out[-1])
    return out

def trend_ok(bars,start,end,direction):
    opp=0
    for j in range(start+1,end+1):
        ok=bars[j]["high"]>bars[j-1]["high"] if direction=="BUY" else bars[j]["low"]<bars[j-1]["low"]
        opp=0 if ok else opp+1
        if opp>1:return False
    return True

def replay_a(bars):
    rows=[]; c=Counter()
    for i in range(2,len(bars)-1):
        d=a_detect(bars,i)
        if not d:continue
        c["setups"]+=1
        for j in range(i+1,len(bars)):
            trigger=bars[j]["low"]<bars[j-1]["low"] if d=="BUY" else bars[j]["high"]>bars[j-1]["high"]
            if not trigger:continue
            entry=bars[j]["low"] if d=="BUY" else bars[j]["high"]
            sl=bars[i-2]["low"] if d=="BUY" else bars[i-2]["high"]
            risk=entry-sl if d=="BUY" else sl-entry
            if risk<=0 or risk>MAX_SL:c["invalid_risk"]+=1
            else:
                rows.append({"strategy":"A_RR2_TRAIL4","direction":d,"setup_utc":datetime.fromtimestamp(bars[i]["time"],timezone.utc).isoformat(),"trigger_utc":datetime.fromtimestamp(bars[j]["time"],timezone.utc).isoformat(),"theoretical_entry":entry,"sl":sl,"risk_price":risk,"tp_2r":entry+2*risk if d=="BUY" else entry-2*risk,"trail_distance_price":0.4,"pending_ttl_minutes":30,"fill_status":"UNRESOLVED_NO_TICK_OR_CONFIRMED_FILL_RULE"})
                c["candidates"]+=1
            break
    return rows,c

def replay_b(bars):
    rows=[]; c=Counter(); emas=ema([b["close"] for b in bars]); pending=None
    for i in range(4,len(bars)):
        cur=bars[i]
        if pending:
            d=pending["direction"]
            trigger=cur["low"]<bars[i-1]["low"] if d=="BUY" else cur["high"]>bars[i-1]["high"]
            if trigger:
                entry=cur["low"] if d=="BUY" else cur["high"]; sl=pending["sl"]; risk=entry-sl if d=="BUY" else sl-entry
                if risk<=0 or risk>MAX_SL:c["invalid_risk"]+=1; pending=None
                elif not trend_ok(bars,pending["index"],i,d):c["blocked_trend"]+=1
                elif not (cur["close"]>emas[i] if d=="BUY" else cur["close"]<emas[i]):c["blocked_ema"]+=1
                else:
                    rows.append({"strategy":"B_PYTHONTRADERBOT","direction":d,"setup_utc":datetime.fromtimestamp(bars[pending["index"]]["time"],timezone.utc).isoformat(),"trigger_utc":datetime.fromtimestamp(cur["time"],timezone.utc).isoformat(),"theoretical_entry":entry,"sl":sl,"risk_price":risk,"tp_0_9r":entry+0.9*risk if d=="BUY" else entry-0.9*risk,"fill_status":"UNRESOLVED_MARKET_FILL_NOT_IN_M1_OHLC"})
                    c["candidates"]+=1; pending=None
        d=b_detect(bars,i)
        if d:
            c["setups"]+=1
            pending={"direction":d,"index":i,"sl":bars[i-3]["low"] if d=="BUY" else bars[i-3]["high"]}
    return rows,c

def write_csv(path,rows):
    if not rows:path.write_text("no_rows\n",encoding="utf-8");return
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv",required=True,type=Path)
    p.add_argument("--out",type=Path,default=Path("artifacts/monthly_strategy_comparison_20261024"))
    a=p.parse_args(); bars,audit=load(a.csv); ar,ac=replay_a(bars); br,bc=replay_b(bars); a.out.mkdir(parents=True,exist_ok=True)
    write_csv(a.out/"strategy_a_candidates.csv",ar);write_csv(a.out/"strategy_b_candidates.csv",br)
    result={"input":audit,"source_versions":{"A":"SP2L_V3_XAUUSD_RR2_TRAIL4_20261001","B":"Strategy B script at commit 0037c540; TP_R=0.9, EMA60, trend filter enabled, max opposite moves=1, second entry/range/session filters disabled"},"counts":{"A":dict(ac),"B":dict(bc)},"candidate_counts":{"A":len(ar),"B":len(br)},"performance_metrics":{"closed_trades":"NOT COMPUTED","wins_losses":"NOT COMPUTED","net_pnl":"NOT COMPUTED","total_R":"NOT COMPUTED","profit_factor":"NOT COMPUTED","max_drawdown":"NOT COMPUTED","filled_unfilled_cancelled":"NOT COMPUTED"},"reason":"Independent candidate counts only (not single-position portfolio replay). M1 OHLC alone cannot establish A pending-limit fills/TTL outcomes, B market fill prices and execution-based TP, or intrabar stop/target ordering. No fills or P&L are fabricated."}
    (a.out/"summary.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    md="# Monthly signal replay: RR2/TRAIL4 vs Strategy B\n\n"
    md+=f"- Input SHA-256: {audit['sha256']}\n- Rows: {audit['rows']}\n- Window: {audit['window_start_utc']} to {audit['window_end_utc_exclusive']}\n- Gap segments >1 minute: {audit['gap_segments_gt_1m']}\n\n"
    md+="| Metric | A RR2/TRAIL4 | B PythonTraderBot |\n|---|---:|---:|\n"
    md+=f"| Setups | {ac.get('setups',0)} | {bc.get('setups',0)} |\n| Valid trigger candidates | {len(ar)} | {len(br)} |\n| Invalid risk candidates | {ac.get('invalid_risk',0)} | {bc.get('invalid_risk',0)} |\n| Closed trades / W-L | NOT COMPUTED | NOT COMPUTED |\n| Net P&L / Total R | NOT COMPUTED | NOT COMPUTED |\n| Profit factor / Max DD | NOT COMPUTED | NOT COMPUTED |\n| Filled / unfilled / cancelled | NOT COMPUTED | NOT COMPUTED |\n\n"
    md+="This is a candidate replay, not a profitability backtest. Fill/exit semantics remain unresolved; no production or canonical rule is asserted. See summary.json and candidate CSVs.\n"
    (a.out/"comparison.md").write_text(md,encoding="utf-8")
    print(json.dumps({"output_dir":str(a.out.resolve()),"input_sha256":audit["sha256"],"rows":audit["rows"],"A_setups":ac.get("setups",0),"A_candidates":len(ar),"B_setups":bc.get("setups",0),"B_candidates":len(br),"note":"candidate counts only; realized P&L intentionally unresolved"},indent=2))
if __name__=="__main__":main()
