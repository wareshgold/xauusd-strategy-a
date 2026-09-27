"""Research-only FX matrix using the current SP2L Forward-style replay model.

Purpose: inspect major FX symbols under the same research execution semantics.
This is not a canonical cross-symbol rule-selection tool and does not rank
symbols or authorize production trading.
"""
from __future__ import annotations
import argparse,json,os
from datetime import datetime,timezone,timedelta
from pathlib import Path
import MetaTrader5 as mt5
import numpy as np

try:
    from run_sp2l_historical_forward_replay import fetch_rates,resolve_symbol,replay
except ImportError:
    from scripts.run_sp2l_historical_forward_replay import fetch_rates,resolve_symbol,replay

DEFAULT_SYMBOLS=["EURUSD","GBPUSD","USDJPY","USDCHF","USDCAD","AUDUSD","NZDUSD"]
OUT_DIR=Path(__file__).resolve().parents[1]/"artifacts"/"forward-test-fx-matrix"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--symbols",default=",".join(DEFAULT_SYMBOLS))
    ap.add_argument("--start",required=True); ap.add_argument("--end",required=True)
    ap.add_argument("--mt5-path",default=None)
    ap.add_argument("--volume",type=float,default=float(os.getenv("SP2L_FX_VOLUME","0.01")))
    ap.add_argument("--ttl-minutes",type=float,default=30.0)
    ap.add_argument("--server-offset-hours",type=float,default=None)
    ap.add_argument("--max-sl",type=float,default=10.0)
    ap.add_argument("--output",default=None)
    args=ap.parse_args()
    start=datetime.fromisoformat(args.start.replace("Z","+00:00")); end=datetime.fromisoformat(args.end.replace("Z","+00:00"))
    ok=mt5.initialize(path=args.mt5_path) if args.mt5_path else mt5.initialize()
    if not ok: raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        if args.server_offset_hours is None:
            tick=None
            for base in args.symbols.split(","):
                s=resolve_symbol(base.strip())
                if s:
                    tick=mt5.symbol_info_tick(s)
                    if tick and getattr(tick,"time",0): break
            if not tick: raise RuntimeError("server offset unavailable; pass --server-offset-hours")
            args.server_offset_hours=round((int(tick.time)-datetime.now(timezone.utc).timestamp())/3600)
        rows=[]; errors=[]
        for requested in [x.strip() for x in args.symbols.split(",") if x.strip()]:
            try:
                symbol=resolve_symbol(requested); info=mt5.symbol_info(symbol)
                rates=fetch_rates(symbol,start,end)
                closed,expired,skipped,seen,open_trades,pending=replay(rates,symbol,args.volume,args.ttl_minutes,args.server_offset_hours,args.max_sl)
                decisive=[t for t in closed if t.get("r") is not None]
                wins=sum(t["r"]>0 for t in decisive); losses=sum(t["r"]<0 for t in decisive); net_r=sum(t["r"] for t in decisive)
                contract=float(getattr(info,"trade_contract_size",0) or 0)
                net_usd=sum(t["r"]*float(t["risk"])*contract*args.volume for t in decisive)
                rows.append({"requested":requested,"symbol":symbol,"bars":len(rates),"candidate_keys_seen":len(seen),"filled":sum(t.get("status")=="FILLED" for t in closed),"closed":len(closed),"wins":wins,"losses":losses,"ambiguous":sum(t.get("result")=="AMBIGUOUS" for t in closed),"expired":len(expired),"netR":net_r,"netUSD":net_usd,"volume":args.volume,"contractSize":contract})
            except Exception as e:
                errors.append({"requested":requested,"error":str(e)})
        out={"status":"COMPLETE","canonical":False,"mode":"HISTORICAL_FORWARD_FX_MATRIX_RESEARCH","window":{"start":start.isoformat(),"end":end.isoformat()},"config":{"pGapPrice":1.0,"spikeMultiplier":1.5,"maxSlDistance":args.max_sl,"tpR":1.0,"orderMode":"PENDING_LIMIT_RESEARCH","pendingTtlMinutes":args.ttl_minutes,"session":"London 08:00 -> New York 17:00","fillModel":"M1_TOUCH_AT_THEORETICAL_LIMIT","exitModel":"M1_SL_TP_TOUCH_AMBIGUOUS","serverOffsetHours":args.server_offset_hours},"rows":rows,"errors":errors,"warning":"Research-only cross-symbol matrix. Absolute P-Gap=1.0 is inherited from current XAUUSD Forward configuration; no FX normalization or ranking is introduced. Results are descriptive and not a canonical symbol-selection rule."}
        path=Path(args.output) if args.output else OUT_DIR/f"SP2L_HISTORICAL_FORWARD_FX_MATRIX_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
        path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(out,indent=2),encoding="utf-8")
        print(json.dumps({"status":"COMPLETE","symbols":len(rows),"errors":len(errors),"output":str(path)},indent=2))
    finally: mt5.shutdown()

if __name__=="__main__": main()
