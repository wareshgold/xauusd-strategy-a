"""Read-only forensic audit for one Forward OPENED lifecycle event."""
from __future__ import annotations
import argparse, json, os
from pathlib import Path
import MetaTrader5 as mt5

def d(x): return x._asdict() if hasattr(x, "_asdict") else {}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--events",required=True); p.add_argument("--signal-id",required=True)
    p.add_argument("--mt5-path",default=os.getenv("MT5_TERMINAL_PATH")); p.add_argument("--output",required=True)
    a=p.parse_args()
    ev=[]
    for line in Path(a.events).read_text(encoding="utf-8").splitlines():
        try: e=json.loads(line)
        except: continue
        if e.get("event")=="TELEGRAM_DEAL_LIFECYCLE" and e.get("signal_id")==a.signal_id: ev.append(e)
    if not ev: raise SystemExit("No lifecycle event found")
    latest=sorted(ev,key=lambda x:x.get("ts_utc",""))[-1]
    symbol=latest.get("symbol"); ot=int(latest["order"]); dt=int(latest["deal"]); pt=int(latest["position"])
    ok=mt5.initialize(path=a.mt5_path) if a.mt5_path else mt5.initialize()
    if not ok: raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        orders=[d(x) for x in (mt5.history_orders_get(ticket=ot) or [])]
        deals=[d(x) for x in (mt5.history_deals_get(ticket=dt) or [])]
        positions=[d(x) for x in (mt5.positions_get(ticket=pt) or [])]
        oe=[x for x in orders if int(x.get("ticket",-1))==ot]
        de=[x for x in deals if int(x.get("ticket",-1))==dt]
        pe=[x for x in positions if int(x.get("ticket",-1))==pt]
        checks={
          "telegram_entry":int(latest.get("entry",-1))==0,
          "order_found":bool(oe),"deal_found":bool(de),"position_found":bool(pe),
          "order_symbol_matches":bool(oe) and str(oe[0].get("symbol"))==symbol,
          "deal_symbol_matches":bool(de) and str(de[0].get("symbol"))==symbol,
          "position_symbol_matches":bool(pe) and str(pe[0].get("symbol"))==symbol,
          "deal_order_matches":bool(de) and int(de[0].get("order",-1))==ot,
          "deal_position_matches":bool(de) and int(de[0].get("position_id",-1))==pt,
          "order_position_matches":bool(oe) and int(oe[0].get("position_id",-1))==pt,
          "entry_price_matches":bool(de) and abs(float(de[0].get("price",0))-float(latest.get("entry_price",0)))<1e-9,
          "volume_matches":bool(de) and abs(float(de[0].get("volume",0))-float(latest.get("volume",0.01)))<1e-9
        }
        report={"status":"COMPLETE","mode":"NON_CANONICAL_FORENSIC","signal_id":a.signal_id,
          "telegram_latest_event":latest,"tickets":{"order":ot,"deal":dt,"position":pt},
          "broker":{"orders":oe,"deals":de,"positions":pe},"checks":checks,
          "conclusion":"BROKER_CONFIRMED_OPEN_ENTRY" if all(checks.values()) else "BROKER_RECONCILIATION_REQUIRES_REVIEW"}
        out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2,sort_keys=True),encoding="utf-8")
        print(json.dumps({"status":"COMPLETE","conclusion":report["conclusion"],"checks":checks,"output":str(out)},indent=2))
    finally: mt5.shutdown()
if __name__=="__main__": main()
