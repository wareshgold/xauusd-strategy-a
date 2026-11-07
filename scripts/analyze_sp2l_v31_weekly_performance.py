#!/usr/bin/env python
"""Privacy-safe whole-population performance analysis for a private SP2L V3.1 audit ZIP.

Prints aggregates only: no ticket, position id, account id, exact price/time, comments,
or raw records. Reads the ZIP without modifying it and never connects to MT5.
"""
from __future__ import annotations
import argparse, json, zipfile, statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone

SYMBOL = "XAUUSD.ecn"
MAGIC = 26092301
ENTRY = {0: "IN", 1: "OUT", 2: "INOUT", 3: "OUT_BY"}
DEAL_TYPE = {0: "BUY", 1: "SELL"}
REASON = {0: "CLIENT", 1: "MOBILE", 2: "WEB", 3: "EXPERT", 4: "SL",
          5: "TP", 6: "SO", 7: "ROLLOVER", 8: "VMARGIN", 9: "SPLIT",
          10: "CORPORATE_ACTION"}
ORDER_STATE = {0:"STARTED",1:"PLACED",2:"CANCELED",3:"PARTIAL",4:"FILLED",
               5:"REJECTED",6:"EXPIRED",7:"REQUEST_ADD",8:"REQUEST_MODIFY",
               9:"REQUEST_CANCEL"}
ORDER_TYPE = {0:"BUY",1:"SELL",2:"BUY_LIMIT",3:"SELL_LIMIT",4:"BUY_STOP",
              5:"SELL_STOP",6:"BUY_STOP_LIMIT",7:"SELL_STOP_LIMIT",8:"CLOSE_BY"}

def load(z, name):
    with z.open(name) as f: return json.load(f)

def num(v):
    try: return float(v) if v is not None else 0.0
    except (TypeError, ValueError): return 0.0

def code(v, mapping):
    try: return mapping.get(int(v), "OTHER")
    except (TypeError, ValueError): return "MISSING"

def money(xs):
    return round(sum(xs), 2)

def stats(xs):
    xs = list(xs)
    wins = [x for x in xs if x > 0.005]
    losses = [x for x in xs if x < -0.005]
    gross_win, gross_loss = sum(wins), abs(sum(losses))
    return {
        "count": len(xs),
        "net": round(sum(xs), 2),
        "win_count": len(wins),
        "loss_count": len(losses),
        "flat_count": len(xs)-len(wins)-len(losses),
        "win_rate_pct": round(100*len(wins)/len(xs), 2) if xs else None,
        "average_net": round(statistics.mean(xs), 4) if xs else None,
        "median_net": round(statistics.median(xs), 4) if xs else None,
        "average_win": round(statistics.mean(wins), 4) if wins else None,
        "average_loss": round(statistics.mean(losses), 4) if losses else None,
        "profit_factor_net": round(gross_win/gross_loss, 4) if gross_loss else ("infinity" if gross_win else None),
        "payoff_ratio": round(statistics.mean(wins)/abs(statistics.mean(losses)), 4) if wins and losses else None,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("bundle")
    ap.add_argument("--output", default="")
    a=ap.parse_args()
    with zipfile.ZipFile(a.bundle) as z:
        deals=load(z,"raw/mt5_history_deals.json")
        orders=load(z,"raw/mt5_history_orders.json")
        with z.open("raw/runner_files/forward_events.jsonl") as f:
            events=[json.loads(line) for line in f if line.strip()]
    ds=[d for d in deals if d.get("symbol")==SYMBOL and str(d.get("magic"))==str(MAGIC)]
    os=[o for o in orders if o.get("symbol")==SYMBOL and str(o.get("magic"))==str(MAGIC)]
    pos=defaultdict(lambda: {"in":0,"out":0,"inout":0,"net":0.0,"profit":0.0,
                             "commission":0.0,"swap":0.0,"fee":0.0,"entry_type":None,
                             "exit_reason":Counter(),"exit_time":None,"exit_day":None})
    entry_counts, exit_reasons, exit_types = Counter(), Counter(), Counter()
    for d in ds:
        pid=str(d.get("position_id"))
        p=pos[pid]
        e=code(d.get("entry"),ENTRY)
        typ=code(d.get("type"),DEAL_TYPE)
        reason=code(d.get("reason"),REASON)
        p[{"IN":"in","OUT":"out","INOUT":"inout"}.get(e,"inout")]+=1
        for k in ("profit","commission","swap","fee"):
            p[k]+=num(d.get(k))
        p["net"]+=sum(num(d.get(k)) for k in ("profit","commission","swap","fee"))
        if e=="IN":
            p["entry_type"]=typ
        if e=="OUT":
            p["exit_reason"][reason]+=1
            p["exit_time"]=max(p["exit_time"] or 0, int(num(d.get("time"))))
            try: p["exit_day"]=datetime.fromtimestamp(int(d["time"]),timezone.utc).date().isoformat()
            except Exception: pass
            exit_reasons[reason]+=1
            exit_types[typ]+=1
        entry_counts[e]+=1
    valid=[p for k,p in pos.items() if k not in ("None","")]
    closed=[p for p in valid if p["out"]>0 or p["inout"]>0]
    open_pos=[p for p in valid if p["in"]>0 and p["out"]==0 and p["inout"]==0]
    closed.sort(key=lambda p:p["exit_time"] or 0)
    closed_net=[p["net"] for p in closed]
    closed_gross=[p["profit"] for p in closed]
    daily=defaultdict(list)
    direction=defaultdict(list)
    for p in closed:
        daily[p["exit_day"] or "UNKNOWN"].append(p["net"])
        direction[p["entry_type"] or "UNKNOWN"].append(p["net"])
    equity=peak=maxdd=0.0
    for x in closed_net:
        equity+=x
        peak=max(peak,equity)
        maxdd=max(maxdd,peak-equity)
    order_states=Counter(code(o.get("state"),ORDER_STATE) for o in os)
    order_types=Counter(code(o.get("type"),ORDER_TYPE) for o in os)
    result={
      "scope":{"symbol":SYMBOL,"magic":MAGIC,"time_basis":"UTC","privacy":"aggregate_only"},
      "population":{"filtered_deals":len(ds),"filtered_orders":len(os),"unique_positions":len(valid),
                    "closed_positions_by_deal_lifecycle":len(closed),"open_or_unclosed_positions":len(open_pos),
                    "missing_position_id_deals":sum(d.get("position_id") is None for d in ds)},
      "deal_lifecycle":{"entry_counts":dict(entry_counts),"exit_reason_counts":dict(exit_reasons),
                        "exit_deal_type_counts":dict(exit_types)},
      "closed_position_performance_net_after_costs":stats(closed_net),
      "closed_position_gross_profit_performance":stats(closed_gross),
      "closed_position_costs":{"commission":round(sum(p["commission"] for p in closed),2),
                               "swap":round(sum(p["swap"] for p in closed),2),
                               "fee":round(sum(p["fee"] for p in closed),2)},
      "closed_position_max_drawdown_currency":round(maxdd,2),
      "open_unclosed_position_accounting":{"count":len(open_pos),
          "net_deal_cashflow":round(sum(p["net"] for p in open_pos),2),
          "warning":"Not closed-trade P/L; excludes floating P/L."},
      "closed_net_by_entry_direction":{k:stats(v) for k,v in sorted(direction.items())},
      "closed_net_by_exit_day_utc":{k:stats(v) for k,v in sorted(daily.items())},
      "orders":{"state_counts":dict(order_states),"type_counts":dict(order_types)},
      "runner_event_counts":dict(Counter(str(e.get("event") or e.get("type") or "UNKNOWN") for e in events)),
      "limitations":[
        "Closed positions are inferred from deal IN/OUT lifecycle; broker-specific accounting should be checked.",
        "Net position result sums deal profit, commission, swap and fee; floating P/L is unavailable.",
        "Maximum drawdown is calculated on sequential realized closed-position net results, ordered by exit time; no intraday mark-to-market.",
        "MFE/MAE and price-path attribution require private tick or bar data not contained in this aggregate calculation.",
        "No canonical SP2L geometry or execution semantics are inferred."
      ]
    }
    out=json.dumps(result,indent=2,ensure_ascii=False)
    if a.output:
        with open(a.output,"w",encoding="utf-8") as f: f.write(out+"\n")
    print(out)

if __name__=="__main__": main()
