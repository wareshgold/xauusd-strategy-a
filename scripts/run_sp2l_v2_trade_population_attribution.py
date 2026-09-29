"""Research-only V2 trade-population attribution harness.

Keeps the historically reconstructed 1,472 signal population and tests a
separate trade-lifecycle boundary: whether signals whose first valid entry
occurs before the previous accepted trade exits are excluded from the trade
population.

This does not change detector geometry or canonical rules.
"""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path
import MetaTrader5 as mt5
from mt5_terminal_resolver import find_mt5_terminal
from run_sp2l_strategy_a_v2_xauusd_mt5_backtest import fetch_rates, resolve_xauusd
from sp2l_strategy_a_v2_detector import detect_setup, find_first_entry

REFERENCE={"bars":87673,"signals":1472,"trades":1356,"wins":836,"losses":520}

def outcome(candles, entry_index, signal):
    direction=signal["direction"]; sl=float(signal["sl"]); tp=float(signal["tp"])
    for j in range(entry_index,len(candles)):
        high=float(candles[j]["high"]); low=float(candles[j]["low"])
        if direction=="BUY": hit_sl,hit_tp=low<=sl,high>=tp
        else: hit_sl,hit_tp=high>=sl,low<=tp
        if hit_sl and hit_tp: return "AMBIGUOUS",j
        if hit_tp: return "WIN",j
        if hit_sl: return "LOSS",j
    return "OPEN_AT_END",None

def run(rates):
    signals=[]; used_entry_until=-1
    for i in range(2,len(rates)):
        if i<=used_entry_until: continue
        setup=detect_setup(rates[:i+1])
        if setup is None: continue
        signal=find_first_entry(rates,i,setup)
        if signal is None: continue
        entry_index=int(signal["entry_index"])
        result,exit_index=outcome(rates,entry_index,signal)
        signals.append({
            "setup_index":i,"entry_index":entry_index,"exit_index":exit_index,
            "setup_time":int(signal["setup_time"]),"entry_time":int(signal["entry_time"]),
            "direction":signal["direction"],"result":result
        })
        used_entry_until=entry_index

    trades=[]; skipped=0; active_exit=-1
    for s in signals:
        # Candidate trade is rejected if its entry occurs before the previous
        # accepted trade has exited. This is a lifecycle hypothesis only.
        if s["entry_index"] <= active_exit:
            skipped+=1
            continue
        trades.append(s)
        if s["exit_index"] is not None:
            active_exit=s["exit_index"]

    wins=sum(x["result"]=="WIN" for x in trades)
    losses=sum(x["result"]=="LOSS" for x in trades)
    ambiguous=sum(x["result"]=="AMBIGUOUS" for x in trades)
    decisive=wins+losses
    return {
        "signal_population":len(signals),
        "trade_population":len(trades),
        "skipped_by_trade_overlap":skipped,
        "wins":wins,"losses":losses,"ambiguous":ambiguous,
        "decisive":decisive,
        "win_rate_pct":100*wins/decisive if decisive else None,
        "net_r":wins-losses,
        "reference":REFERENCE,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--start",default="2026-06-29T01:00:00Z")
    p.add_argument("--end",default="2026-09-24T20:30:00Z")
    p.add_argument("--mt5-path",default=None)
    a=p.parse_args()
    ok=mt5.initialize(path=str(a.mt5_path)) if a.mt5_path else mt5.initialize()
    if not ok:
        terminal=None if a.mt5_path else find_mt5_terminal()
        if terminal is None or not mt5.initialize(path=str(terminal)):
            print(json.dumps({"status":"MT5_INIT_FAILED","error":mt5.last_error()},indent=2)); return 2
    try:
        symbol=resolve_xauusd()
        start=datetime.fromisoformat(a.start.replace("Z","+00:00")); end=datetime.fromisoformat(a.end.replace("Z","+00:00"))
        rates=fetch_rates(symbol,start,end); result=run(rates)
        report={"status":"COMPLETE","mode":"RESEARCH_ONLY_V2_TRADE_POPULATION_ATTRIBUTION","generated_utc":datetime.now(timezone.utc).isoformat(),"resolved_symbol":symbol,"bars":len(rates),"period":{"start_utc":start.isoformat(),"end_utc":end.isoformat()},"results":result,"semantic_limits":["Lifecycle overlap is a hypothesis for historical attribution, not a canonical rule.","Signal population is reconstructed with the previously verified historical entry-boundary suppression.","Same-bar SL/TP remains AMBIGUOUS."]}
        out=Path(__file__).resolve().parents[1]/"artifacts/forensic/2026-09-29"/f"V2_TRADE_POPULATION_ATTRIBUTION_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2),encoding="utf-8")
        print(json.dumps({"status":"COMPLETE","report":str(out),"bars":len(rates),"results":result},indent=2)); return 0
    finally: mt5.shutdown()

if __name__=="__main__": raise SystemExit(main())
