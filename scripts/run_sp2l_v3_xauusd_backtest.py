"""SP2L V3 XAUUSD 3-month MT5 backtest.

Uses the exact V3 geometry/trailing definitions in sp2l_v3_config.py.
Writes JSON trade journal, CSV trade journal, and an official run snapshot.
Research only; no production decisioning.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import MetaTrader5 as mt5
import numpy as np
import sp2l_v3_config as cfg

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "v3"
OUT.mkdir(parents=True, exist_ok=True)

def iso(ts): return datetime.fromtimestamp(int(ts), timezone.utc).isoformat()

def fetch_m1_rates(symbol, start, end):
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"symbol_select failed: {symbol} {mt5.last_error()}")

    chunks=[]; cur=start.astimezone(timezone.utc); end=end.astimezone(timezone.utc)
    while cur < end:
        chunk_end=min(cur+timedelta(days=7), end)
        rates=mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, cur, chunk_end)
        if rates is None or len(rates)==0:
            raise RuntimeError(
                f"history failed {cur.isoformat()}..{chunk_end.isoformat()}: {mt5.last_error()}"
            )
        chunks.append(rates.copy())
        cur=chunk_end+timedelta(minutes=1)

    bars=np.concatenate(chunks)
    bars.sort(order="time")
    _, idx=np.unique(bars["time"], return_index=True)
    return bars[np.sort(idx)]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mt5-path", required=True)
    ap.add_argument("--symbol", default="XAUUSD.ecn")
    ap.add_argument("--start", default="2026-07-01T00:00:00+00:00")
    ap.add_argument("--end", default="2026-10-01T00:00:00+00:00")
    args=ap.parse_args()
    start=datetime.fromisoformat(args.start); end=datetime.fromisoformat(args.end)
    if not mt5.initialize(path=args.mt5_path):
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        info=mt5.symbol_info(args.symbol)
        if info is None: raise RuntimeError(f"Symbol unavailable: {args.symbol}")
        if not mt5.symbol_select(args.symbol, True): raise RuntimeError("symbol_select failed")
        bars=fetch_m1_rates(args.symbol, start, end)
        if bars is None or len(bars)<10: raise RuntimeError(f"Insufficient M1 data: {mt5.last_error()}")
        trades=[]; seen=set()
        # A candidate is evaluated using completed bars only. Outcome is then
        # simulated on subsequent completed M1 bars. Same-bar TP/trail/SL
        # conflicts are explicitly marked ambiguous rather than guessed.
        for i in range(2, len(bars)-2):
            setup=cfg.detect(bars[i-2:i+1], args.symbol)
            if not setup: continue
            c=cfg.find_first_entry(bars, i, setup)
            if not c: continue
            key=(c["trigger_time"], c["direction"])
            if key in seen: continue
            seen.add(key)
            entry_idx=next((k for k in range(i+1,len(bars)) if int(bars[k]["time"])==c["trigger_time"]), None)
            if entry_idx is None: continue
            trail_active=False; final_sl=c["sl"]; max_fav=0.0; exit_price=None; reason="OPEN_OR_UNRESOLVED"; ambiguous=False
            for k in range(entry_idx+1,len(bars)):
                b=bars[k]; high=float(b["high"]); low=float(b["low"])
                if c["direction"]=="BUY":
                    favorable=high-c["theoretical_entry"]
                    adverse=c["theoretical_entry"]-low
                    max_fav=max(max_fav,favorable)
                    new_sl=cfg.trail_stop("BUY", high) if favorable >= cfg.TRAIL_DISTANCE_PRICE else final_sl
                    if favorable >= cfg.TRAIL_DISTANCE_PRICE:
                        trail_active=True; final_sl=max(final_sl,new_sl)
                    hit_sl=low <= final_sl
                    hit_tp=high >= c["tp"]
                    if hit_sl and hit_tp:
                        ambiguous=True; reason="SL_AND_TP_SAME_BAR"; break
                    if hit_sl: exit_price=final_sl; reason="TRAIL_SL" if trail_active and final_sl>c["sl"] else "SL"; break
                    if hit_tp: exit_price=c["tp"]; reason="TP"; break
                else:
                    favorable=c["theoretical_entry"]-low
                    adverse=high-c["theoretical_entry"]
                    max_fav=max(max_fav,favorable)
                    new_sl=cfg.trail_stop("SELL", low) if favorable >= cfg.TRAIL_DISTANCE_PRICE else final_sl
                    if favorable >= cfg.TRAIL_DISTANCE_PRICE:
                        trail_active=True; final_sl=min(final_sl,new_sl)
                    hit_sl=high >= final_sl
                    hit_tp=low <= c["tp"]
                    if hit_sl and hit_tp:
                        ambiguous=True; reason="SL_AND_TP_SAME_BAR"; break
                    if hit_sl: exit_price=final_sl; reason="TRAIL_SL" if trail_active and final_sl<c["sl"] else "SL"; break
                    if hit_tp: exit_price=c["tp"]; reason="TP"; break
            realized=None
            if exit_price is not None:
                realized=(exit_price-c["theoretical_entry"] if c["direction"]=="BUY" else c["theoretical_entry"]-exit_price)
            trades.append({**c,"signal_time_utc":iso(c["trigger_time"]),"initial_sl":c["sl"],
                "initial_tp":c["tp"],"trail_pips":cfg.TRAIL_PIPS,"trail_distance_price":cfg.TRAIL_DISTANCE_PRICE,
                "final_sl":final_sl,"trailing_activated":trail_active,"max_favorable_price":max_fav,
                "exit_price":exit_price,"reason":reason,"ambiguous":ambiguous,"realized_price":realized,
                "realized_R":(realized/c["risk"] if realized is not None else None)})
        decisive=[t for t in trades if not t["ambiguous"] and t["realized_R"] is not None]
        wins=[t for t in decisive if t["realized_R"]>0]; losses=[t for t in decisive if t["realized_R"]<0]
        net_R=sum(t["realized_R"] for t in decisive)
        gross_profit=sum(t["realized_R"] for t in wins); gross_loss=abs(sum(t["realized_R"] for t in losses))
        result={"version":cfg.VERSION,"research_only":True,"symbol":args.symbol,"timeframe":"M1",
          "start_utc":start.isoformat(),"end_utc":end.isoformat(),"bars":len(bars),
          "config":{"pGapPrice":cfg.P_GAP_PRICE,"spikeMultiplier":cfg.SPIKE_MULTIPLIER,"maxSlDistance":cfg.MAX_SL_DISTANCE,
                    "tpR":cfg.TP_R,"trailPips":cfg.TRAIL_PIPS,"trailDistancePrice":cfg.TRAIL_DISTANCE_PRICE,
                    "trailPolicy":"M1_COMPLETED_BAR_HIGH_LOW","tpPolicy":"FIXED_INITIAL_TP",
                    "sameBarPolicy":"AMBIGUOUS_WHEN_SL_AND_TP_BOTH_TOUCHED","sessionPolicy":cfg.SESSION_POLICY},
          "summary":{"signals":len(trades),"decisive":len(decisive),"wins":len(wins),"losses":len(losses),
                     "ambiguous":sum(t["ambiguous"] for t in trades),
                     "winRateDecisivePct":(100*len(wins)/len(decisive) if decisive else None),
                     "netR":net_R,"profitFactor":(gross_profit/gross_loss if gross_loss else None)},
          "trades":trades}
        stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base=OUT/f"SP2L_V3_XAUUSD_TRAIL10_3M_{stamp}"
        raw=json.dumps(result,indent=2,ensure_ascii=False)
        (base.with_suffix(".json")).write_text(raw,encoding="utf-8")
        with (base.with_suffix(".csv")).open("w",newline="",encoding="utf-8") as f:
            if trades:
                w=csv.DictWriter(f,fieldnames=sorted(trades[0])); w.writeheader(); w.writerows(trades)
        sha=hashlib.sha256(raw.encode()).hexdigest()
        snap=f"""# SP2L V3 Official Run Snapshot
Version: {cfg.VERSION}
Commit/branch must be recorded from Git after pull.
Symbol: {args.symbol}
Window UTC: {start.isoformat()} → {end.isoformat()}
Bars: {len(bars)}
Trail: {cfg.TRAIL_PIPS} pip = {cfg.TRAIL_DISTANCE_PRICE:.2f} price units
Geometry: pGap={cfg.P_GAP_PRICE}, spike={cfg.SPIKE_MULTIPLIER}, maxSL={cfg.MAX_SL_DISTANCE}, TP={cfg.TP_R}R
Session: {cfg.SESSION_POLICY}
Trailing policy: completed M1 bar high/low; fixed initial TP
Ambiguity: SL and TP both touched on one M1 bar => ambiguous, excluded from decisive win rate
JSON SHA256: {sha}
"""
        (base.with_name(base.name+"_SNAPSHOT.md")).write_text(snap,encoding="utf-8")
        print(json.dumps({"status":"COMPLETE","version":cfg.VERSION,"json":str(base.with_suffix(".json")),
          "csv":str(base.with_suffix(".csv")),"snapshot":str(base.with_name(base.name+"_SNAPSHOT.md")),
          "summary":result["summary"],"sha256":sha},indent=2))
    finally:
        mt5.shutdown()
if __name__=="__main__": main()
