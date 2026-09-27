"""Research-only historical replay of the current SP2L demo-forward semantics.

This is NOT the V2 historical backtest. It replays the current forward runner's
3-candle geometry, first post-setup trigger, session gate, pending-limit
execution, 30-minute TTL, and price-path exits on MT5 M1 data.

Because MT5 Python history is bar data, pending fills are modeled as an M1
touch at the theoretical limit price. This is explicitly research-only.
No production BUY/SELL decision is emitted.
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

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "artifacts" / "forward-test-replay"
OUT_DIR.mkdir(parents=True, exist_ok=True)
LONDON = ZoneInfo("Europe/London")
NEW_YORK = ZoneInfo("America/New_York")
IRAN = timezone(timedelta(hours=3, minutes=30))

def resolve_symbol(requested):
    names = {str(s.name) for s in (mt5.symbols_get() or [])}
    c = requested.upper()
    for x in (c, c+".ecn", c+".ECN", c+"m", c+".c.ecn"):
        if x in names: return x
    n = "".join(ch for ch in c if ch.isalnum())
    m = [x for x in names if "".join(ch for ch in x.upper() if ch.isalnum()).startswith(n)]
    if m: return sorted(m, key=lambda x:(len(x),x))[0]
    raise RuntimeError(f"symbol discovery failed: {requested}")

def fetch_rates(symbol, start, end):
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"symbol_select failed: {symbol} {mt5.last_error()}")
    chunks=[]; cur=start.astimezone(timezone.utc); end=end.astimezone(timezone.utc)
    while cur < end:
        ce=min(cur+timedelta(days=7), end)
        r=mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, cur, ce)
        if r is None or len(r)==0:
            raise RuntimeError(f"history failed {cur.isoformat()}..{ce.isoformat()}: {mt5.last_error()}")
        chunks.append(r.copy()); cur=ce+timedelta(minutes=1)
    out=np.concatenate(chunks); out.sort(order="time")
    _,idx=np.unique(out["time"],return_index=True)
    return out[np.sort(idx)]

def session_ok(ts, server_offset_hours):
    # Historical replay uses an explicit fixed broker-server offset. This is
    # a replay assumption, not a new Strategy A rule.
    utc_dt=datetime.fromtimestamp(int(ts),timezone.utc)-timedelta(hours=server_offset_hours)
    london=utc_dt.astimezone(LONDON); ny=utc_dt.astimezone(NEW_YORK)
    start=london.replace(hour=8,minute=0,second=0,microsecond=0).astimezone(timezone.utc)
    end=ny.replace(hour=17,minute=0,second=0,microsecond=0).astimezone(timezone.utc)
    return start <= utc_dt <= end

def candidate_from_window(window, symbol):
    if len(window)<3: return None
    setup=detect_setup(window[-3:])
    if setup is None: return None
    e=find_first_entry(window, len(window)-1, setup)
    if e is None: return None
    # Current forward runner exposes these levels; keep the same 2X relation
    # for reporting only. It is never executed.
    risk=float(e["risk"]); entry=float(e["entry"]); sl=float(e["sl"])
    e["symbol"]=symbol; e["theoretical_entry"]=entry
    e["secondary_entry_2x"]=entry + 0.5*(sl-entry)
    e["tp"]=float(e["tp"])
    return e

def money_per_price(symbol_info, volume):
    # Broker metadata, not a strategy rule. Used only to translate R/price
    # movement into account-currency USD for the historical report.
    contract=float(getattr(symbol_info,"trade_contract_size",0) or 0)
    return contract*volume

def replay(rates, symbol, volume, ttl_minutes, server_offset_hours, max_sl):
    pending=None; seen=set(); trades=[]; events=[]
    for i in range(3,len(rates)):
        ts=int(rates[i]["time"])
        # First process existing pending order on this bar.
        if pending is not None:
            age=(ts-pending["trigger_time"])/60.0
            b=rates[i]; hi=float(b["high"]); lo=float(b["low"])
            filled = (lo <= pending["entry"]) if pending["direction"]=="BUY" else (hi >= pending["entry"])
            if filled:
                pending["fill_time"]=ts; pending["status"]="FILLED"; trades.append(dict(pending)); pending=None
            elif age >= ttl_minutes:
                pending["status"]="EXPIRED"; pending["expiry_time"]=ts; events.append(dict(pending)); pending=None
        # Manage filled trade on the same bar only after fill: entry bar is
        # allowed to participate in exits, matching the live broker position
        # lifecycle rather than the V2 historical backtest contract.
        if trades and trades[-1].get("status")=="FILLED" and trades[-1].get("exit_time") is None:
            t=trades[-1]; b=rates[i]; hi=float(b["high"]); lo=float(b["low"])
            if ts >= t["fill_time"]:
                if t["direction"]=="BUY":
                    hit_sl=lo<=t["sl"]; hit_tp=hi>=t["tp"]
                else:
                    hit_sl=hi>=t["sl"]; hit_tp=lo<=t["tp"]
                if hit_sl or hit_tp:
                    t["exit_time"]=ts
                    t["result"]="LOSS" if hit_sl else "WIN"
                    t["r"]=-1.0 if hit_sl else 1.0
                    if hit_sl and hit_tp: t["result"]="AMBIGUOUS"; t["r"]=None; t["exit_reason"]="BOTH_SAME_M1"
                    else: t["exit_reason"]="SL_TOUCH" if hit_sl else "TP_TOUCH"
        # Current runner scans a rolling 10-bar window. Replay evaluates the
        # window at each completed M1 bar; this avoids inventing intrabar data.
        w=rates[max(0,i-9):i+1]
        c=candidate_from_window(w,symbol)
        if c is None: continue
        key=f"{symbol}:{int(c['trigger_time'])}:{c['direction']}"
        if key in seen: continue
        seen.add(key)
        if c["risk"]<=0 or c["risk"]>max_sl: continue
        if not session_ok(int(c["trigger_time"]),server_offset_hours): continue
        c["signal_id"]=key; c["volume"]=volume; c["status"]="PENDING"
        c["entry"]=float(c["theoretical_entry"]); c["sl"]=float(c["sl"]); c["tp"]=float(c["tp"])
        c["trigger_time"]=int(c["trigger_time"])
        c["pending_expiry_time"]=c["trigger_time"]+int(ttl_minutes*60)
        # A new pending order replaces no existing order; the live runner can
        # have multiple pending positions across time/symbols.
        if pending is None:
            pending=c
        else:
            events.append({**c,"status":"SKIPPED_PENDING_ALREADY_ACTIVE"})
    return trades, events, seen

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--symbol",default="XAUUSD")
    ap.add_argument("--start",required=True)
    ap.add_argument("--end",required=True)
    ap.add_argument("--mt5-path",default=None)
    ap.add_argument("--volume",type=float,default=float(os.getenv("SP2L_VOLUME","0.01")))
    ap.add_argument("--ttl-minutes",type=float,default=float(os.getenv("SP2L_PENDING_TTL_MINUTES","30")))
    ap.add_argument("--server-offset-hours",type=float,default=None)
    ap.add_argument("--max-sl",type=float,default=float(os.getenv("SP2L_MAX_SL_DISTANCE","10.0")))
    ap.add_argument("--output",default=None)
    args=ap.parse_args()
    start=datetime.fromisoformat(args.start.replace("Z","+00:00")); end=datetime.fromisoformat(args.end.replace("Z","+00:00"))
    if not mt5.initialize(path=args.mt5_path) if args.mt5_path else not mt5.initialize():
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        symbol=resolve_symbol(args.symbol); info=mt5.symbol_info(symbol)
        if info is None: raise RuntimeError(f"symbol_info unavailable: {symbol}")
        # Prefer explicit replay assumption; otherwise derive the current
        # broker offset from a fresh tick exactly as the live runner does.
        if args.server_offset_hours is None:
            tick=mt5.symbol_info_tick(symbol)
            if not tick or not getattr(tick,"time",0): raise RuntimeError("server offset unavailable; pass --server-offset-hours")
            args.server_offset_hours=round((int(tick.time)-datetime.now(timezone.utc).timestamp())/3600)
        rates=fetch_rates(symbol,start,end)
        trades,events,seen=replay(rates,symbol,args.volume,args.ttl_minutes,args.server_offset_hours,args.max_sl)
        closed=[t for t in trades if t.get("exit_time") is not None and t.get("r") is not None]
        wins=sum(t["r"]>0 for t in closed); losses=sum(t["r"]<0 for t in closed)
        net_r=sum(t["r"] for t in closed)
        contract=float(getattr(info,"trade_contract_size",0) or 0)
        usd_per_price=contract*args.volume
        net_usd=net_r*usd_per_price* (closed[0]["risk"] if False else 0) if False else sum((t["r"]*t["risk"]*usd_per_price) for t in closed)
        # The above is risk-variable USD, so report it separately from net R.
        out={
          "status":"COMPLETE","canonical":False,"mode":"HISTORICAL_FORWARD_REPLAY_RESEARCH",
          "symbol_requested":args.symbol,"symbol":symbol,"timeframe":"M1",
          "window":{"start":start.isoformat(),"end":end.isoformat()},
          "config":{"pGapPrice":1.0,"spikeMultiplier":1.5,"maxSlDistance":args.max_sl,"tpR":1.0,
                    "orderMode":"PENDING_LIMIT_RESEARCH","pendingTtlMinutes":args.ttl_minutes,
                    "volume":args.volume,"session":"London 08:00 -> New York 17:00",
                    "serverOffsetHours":args.server_offset_hours,
                    "fillModel":"M1_TOUCH_AT_THEORETICAL_LIMIT","exitModel":"M1_TOUCH_SL_FIRST_AMBIGUOUS"},
          "data":{"bars":int(len(rates)),"contractSize":contract},
          "population":{"candidate_keys_seen":len(seen),"filled":sum(t.get("status")=="FILLED" for t in trades),
                        "expired":sum(e.get("status")=="EXPIRED" for e in events),"skipped_pending":sum(e.get("status")=="SKIPPED_PENDING_ALREADY_ACTIVE" for e in events),
                        "closed":len(closed),"wins":wins,"losses":losses,"ambiguous":sum(t.get("result")=="AMBIGUOUS" for t in trades)},
          "performance":{"netR":net_r,"netUSD":net_usd,"usdPerPriceUnit":usd_per_price},
          "trades":trades,"events":events,
          "warning":"Research-only replay. Historical M1 cannot reproduce live intrabar polling, bid/ask spread, broker fill price, slippage, or order rejection exactly."
        }
        outpath=Path(args.output) if args.output else OUT_DIR/f"SP2L_HISTORICAL_FORWARD_REPLAY_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
        outpath.parent.mkdir(parents=True,exist_ok=True); outpath.write_text(json.dumps(out,indent=2),encoding="utf-8")
        print(json.dumps({"status":"COMPLETE","symbol":symbol,"bars":len(rates),"filled":out["population"]["filled"],"closed":len(closed),"wins":wins,"losses":losses,"netR":net_r,"netUSD":net_usd,"output":str(outpath)},indent=2))
    finally: mt5.shutdown()

if __name__=="__main__": main()
