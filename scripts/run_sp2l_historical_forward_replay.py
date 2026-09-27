"""Research-only historical replay of current SP2L demo-forward semantics.

Replays the current forward runner on MT5 M1 history: V2 3-candle geometry,
first post-setup trigger, London/New York session gate, pending-limit research
execution, 30-minute TTL, and M1 SL/TP touch outcomes.

Not canonical and never emits production BUY/SELL decisions. Historical M1
cannot reproduce live bid/ask, intrabar polling, slippage, broker fill price,
or broker order rejection exactly.
"""
from __future__ import annotations
import argparse, json, os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import MetaTrader5 as mt5
import numpy as np

try:
    from sp2l_strategy_a_v2_detector import detect_setup, find_first_entry
except ImportError:
    from scripts.sp2l_strategy_a_v2_detector import detect_setup, find_first_entry

ROOT=Path(__file__).resolve().parents[1]
OUT_DIR=ROOT/"artifacts"/"forward-test-replay"; OUT_DIR.mkdir(parents=True,exist_ok=True)
LONDON=ZoneInfo("Europe/London"); NEW_YORK=ZoneInfo("America/New_York")

def resolve_symbol(requested):
    names={str(s.name) for s in (mt5.symbols_get() or [])}; c=requested.upper()
    for x in (c,c+".ecn",c+".ECN",c+"m",c+".c.ecn"):
        if x in names:return x
    n="".join(ch for ch in c if ch.isalnum())
    m=[x for x in names if "".join(ch for ch in x.upper() if ch.isalnum()).startswith(n)]
    if m:return sorted(m,key=lambda x:(len(x),x))[0]
    raise RuntimeError(f"symbol discovery failed: {requested}")

def fetch_rates(symbol,start,end):
    if not mt5.symbol_select(symbol,True): raise RuntimeError(f"symbol_select failed: {symbol} {mt5.last_error()}")
    chunks=[]; cur=start.astimezone(timezone.utc); end=end.astimezone(timezone.utc)
    while cur<end:
        ce=min(cur+timedelta(days=7),end); r=mt5.copy_rates_range(symbol,mt5.TIMEFRAME_M1,cur,ce)
        if r is None or len(r)==0: raise RuntimeError(f"history failed {cur.isoformat()}..{ce.isoformat()}: {mt5.last_error()}")
        chunks.append(r.copy()); cur=ce+timedelta(minutes=1)
    out=np.concatenate(chunks); out.sort(order="time"); _,idx=np.unique(out["time"],return_index=True)
    return out[np.sort(idx)]

def session_ok(ts,server_offset_hours):
    # MT5 timestamps are treated with the same fixed broker-offset assumption
    # used by the replay. This is a research assumption, not canonical geometry.
    broker_dt=datetime.fromtimestamp(int(ts),timezone.utc)-timedelta(hours=server_offset_hours)
    london=broker_dt.astimezone(LONDON); ny=broker_dt.astimezone(NEW_YORK)
    start=london.replace(hour=8,minute=0,second=0,microsecond=0).astimezone(timezone.utc)
    end=ny.replace(hour=17,minute=0,second=0,microsecond=0).astimezone(timezone.utc)
    return start<=broker_dt<=end

def candidate_from_window(window,symbol):
    if len(window)<3:return None
    candidates=[]
    # This mirrors find_latest_candidate() in the current forward runner:
    # each completed 3-candle setup in the rolling window gets its first
    # later trigger; the latest trigger wins.
    for setup_end in range(2,len(window)-1):
        setup=detect_setup(window[setup_end-2:setup_end+1])
        if setup is None: continue
        e=find_first_entry(window,setup_end,setup)
        if e is not None:
            e=dict(e); e["symbol"]=symbol; e["theoretical_entry"]=float(e["entry"])
            e["secondary_entry_2x"]=e["theoretical_entry"]+0.5*(float(e["sl"])-e["theoretical_entry"])
            e["tp"]=float(e["tp"]); candidates.append(e)
    return max(candidates,key=lambda x:(int(x["entry_time"]),x["direction"])) if candidates else None

def replay(rates,symbol,volume,ttl_minutes,server_offset_hours,max_sl):
    pending=[]; open_trades=[]; closed=[]; expired=[]; skipped=[]; seen=set()
    for i in range(3,len(rates)):
        ts=int(rates[i]["time"]); hi=float(rates[i]["high"]); lo=float(rates[i]["low"])
        remaining=[]
        for p in pending:
            age=(ts-p["trigger_time"])/60.0
            touched=(lo<=p["entry"]) if p["direction"]=="BUY" else (hi>=p["entry"])
            if touched:
                p["fill_time"]=ts; p["status"]="FILLED"; p["exit_time"]=None; open_trades.append(p)
            elif age>=ttl_minutes:
                p["status"]="EXPIRED"; p["expiry_time"]=ts; expired.append(p)
            else: remaining.append(p)
        pending=remaining
        still_open=[]
        for t in open_trades:
            if ts<t["fill_time"]: still_open.append(t); continue
            hit_sl=(lo<=t["sl"]) if t["direction"]=="BUY" else (hi>=t["sl"])
            hit_tp=(hi>=t["tp"]) if t["direction"]=="BUY" else (lo<=t["tp"])
            if not(hit_sl or hit_tp): still_open.append(t); continue
            t["exit_time"]=ts
            if hit_sl and hit_tp: t["result"]="AMBIGUOUS"; t["r"]=None; t["exit_reason"]="BOTH_SAME_M1"
            elif hit_sl: t["result"]="LOSS"; t["r"]=-1.0; t["exit_reason"]="SL_TOUCH"
            else: t["result"]="WIN"; t["r"]=1.0; t["exit_reason"]="TP_TOUCH"
            closed.append(t)
        open_trades=still_open
        # Live rates() requests 10 bars including the current bar. We explicitly
        # replay the same 10-bar observation window over historical bars.
        w=rates[max(0,i-9):i+1]; c=candidate_from_window(w,symbol)
        if c is None: continue
        key=f"{symbol}:{int(c['entry_time'])}:{c['direction']}"
        if key in seen: continue
        seen.add(key)
        if float(c["risk"])<=0 or float(c["risk"])>max_sl: continue
        if not session_ok(int(c["entry_time"]),server_offset_hours): continue
        c["signal_id"]=key; c["volume"]=volume; c["status"]="PENDING"
        c["entry"]=float(c["theoretical_entry"]); c["sl"]=float(c["sl"]); c["tp"]=float(c["tp"])
        c["trigger_time"]=int(c["entry_time"]); c["pending_expiry_time"]=c["trigger_time"]+int(ttl_minutes*60)
        pending.append(c)
    return closed,expired,skipped,seen,open_trades,pending

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--symbol",default="XAUUSD"); ap.add_argument("--start",required=True); ap.add_argument("--end",required=True)
    ap.add_argument("--mt5-path",default=None); ap.add_argument("--volume",type=float,default=float(os.getenv("SP2L_VOLUME","0.01")))
    ap.add_argument("--ttl-minutes",type=float,default=float(os.getenv("SP2L_PENDING_TTL_MINUTES","30"))); ap.add_argument("--server-offset-hours",type=float,default=None)
    ap.add_argument("--max-sl",type=float,default=float(os.getenv("SP2L_MAX_SL_DISTANCE","10.0"))); ap.add_argument("--output",default=None); args=ap.parse_args()
    start=datetime.fromisoformat(args.start.replace("Z","+00:00")); end=datetime.fromisoformat(args.end.replace("Z","+00:00"))
    ok=mt5.initialize(path=args.mt5_path) if args.mt5_path else mt5.initialize()
    if not ok: raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        symbol=resolve_symbol(args.symbol); info=mt5.symbol_info(symbol)
        if info is None: raise RuntimeError(f"symbol_info unavailable: {symbol}")
        if args.server_offset_hours is None:
            tick=mt5.symbol_info_tick(symbol)
            if not tick or not getattr(tick,"time",0): raise RuntimeError("server offset unavailable; pass --server-offset-hours")
            args.server_offset_hours=round((int(tick.time)-datetime.now(timezone.utc).timestamp())/3600)
        rates=fetch_rates(symbol,start,end)
        closed,expired,skipped,seen,open_trades,pending=replay(rates,symbol,args.volume,args.ttl_minutes,args.server_offset_hours,args.max_sl)
        decisive=[t for t in closed if t.get("r") is not None]; wins=sum(t["r"]>0 for t in decisive); losses=sum(t["r"]<0 for t in decisive); net_r=sum(t["r"] for t in decisive)
        contract=float(getattr(info,"trade_contract_size",0) or 0); usd_per_price=contract*args.volume
        net_usd=sum(t["r"]*float(t["risk"])*usd_per_price for t in decisive)
        out={"status":"COMPLETE","canonical":False,"mode":"HISTORICAL_FORWARD_REPLAY_RESEARCH","symbol_requested":args.symbol,"symbol":symbol,"timeframe":"M1",
          "window":{"start":start.isoformat(),"end":end.isoformat()},
          "config":{"pGapPrice":1.0,"spikeMultiplier":1.5,"maxSlDistance":args.max_sl,"tpR":1.0,"orderMode":"PENDING_LIMIT_RESEARCH","pendingTtlMinutes":args.ttl_minutes,"volume":args.volume,"session":"London 08:00 -> New York 17:00","serverOffsetHours":args.server_offset_hours,"fillModel":"M1_TOUCH_AT_THEORETICAL_LIMIT","exitModel":"M1_TOUCH_SL_TP_AMBIGUOUS"},
          "data":{"bars":int(len(rates)),"contractSize":contract},
          "population":{"candidate_keys_seen":len(seen),"filled":sum(t.get("status")=="FILLED" for t in closed),"expired":len(expired),"open_at_end":len(open_trades),"pending_at_end":len(pending),"closed":len(closed),"wins":wins,"losses":losses,"ambiguous":sum(t.get("result")=="AMBIGUOUS" for t in closed)},
          "performance":{"netR":net_r,"netUSD":net_usd,"usdPerPriceUnit":usd_per_price},"trades":closed,"expired_orders":expired,"open_at_end":open_trades,"skipped":skipped,
          "warning":"Research-only replay. Historical M1 cannot reproduce live intrabar polling, bid/ask spread, broker fill price, slippage, or order rejection exactly."}
        path=Path(args.output) if args.output else OUT_DIR/f"SP2L_HISTORICAL_FORWARD_REPLAY_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
        path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(out,indent=2),encoding="utf-8")
        print(json.dumps({"status":"COMPLETE","symbol":symbol,"bars":len(rates),"filled":out["population"]["filled"],"closed":len(closed),"wins":wins,"losses":losses,"netR":net_r,"netUSD":net_usd,"expired":len(expired),"openAtEnd":len(open_trades),"pendingAtEnd":len(pending),"output":str(path)},indent=2))
    finally: mt5.shutdown()
if __name__=="__main__": main()
