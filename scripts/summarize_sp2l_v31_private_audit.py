#!/usr/bin/env python
"""Create a disclosure-safe aggregate from the private SP2L weekly audit ZIP.

No ticket, account identifier, exact price, exact timestamp, comment, or raw row
is printed or written. The ZIP is read-only; output is aggregate JSON locally.
"""
from __future__ import annotations
import argparse, json, zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone

SYMBOL = "XAUUSD.ecn"
MAGIC = 26092301
ENTRY = {0: "IN", 1: "OUT", 2: "INOUT", 3: "OUT_BY"}
DEAL_TYPE = {0: "BUY", 1: "SELL", 2: "BALANCE", 3: "CREDIT", 4: "CHARGE",
             5: "CORRECTION", 6: "BONUS", 7: "COMMISSION", 8: "COMMISSION_DAILY",
             9: "COMMISSION_MONTHLY", 10: "COMMISSION_AGENT_DAILY",
             11: "COMMISSION_AGENT_MONTHLY", 12: "INTEREST", 13: "BUY_CANCELED",
             14: "SELL_CANCELED", 15: "DIVIDEND", 16: "DIVIDEND_FRANKED",
             17: "TAX"}
REASON = {0: "CLIENT", 1: "MOBILE", 2: "WEB", 3: "EXPERT", 4: "SL", 5: "TP",
          6: "SO", 7: "ROLLOVER", 8: "VMARGIN", 9: "SPLIT", 10: "CORPORATE_ACTION"}

def read_json(z, name):
    with z.open(name) as f:
        return json.load(f)

def n(v):
    try: return float(v or 0)
    except (TypeError, ValueError): return 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle", help="Path to private SP2L audit ZIP")
    ap.add_argument("--output", default="", help="Optional local aggregate JSON output path")
    a = ap.parse_args()
    with zipfile.ZipFile(a.bundle) as z:
        names = set(z.namelist())
        deals = read_json(z, "raw/mt5_history_deals.json")
        orders = read_json(z, "raw/mt5_history_orders.json")
        events = []
        with z.open("raw/runner_files/forward_events.jsonl") as f:
            for line in f:
                try: events.append(json.loads(line))
                except Exception: pass

    selected = [d for d in deals if d.get("symbol") == SYMBOL and int(d.get("magic", -1)) == MAGIC]
    selected_orders = [o for o in orders if o.get("symbol") == SYMBOL and int(o.get("magic", -1)) == MAGIC]
    entry_counts = Counter(ENTRY.get(int(d.get("entry", -1)), "OTHER") for d in selected)
    type_counts = Counter(DEAL_TYPE.get(int(d.get("type", -1)), "OTHER") for d in selected)
    reason_counts = Counter(REASON.get(int(d.get("reason", -1)), "OTHER") for d in selected)
    daily = defaultdict(lambda: {"deals": 0, "profit": 0.0, "commission": 0.0, "swap": 0.0, "fee": 0.0})
    pos = defaultdict(lambda: {"in": 0, "out": 0, "inout": 0, "other": 0, "net": 0.0})
    order_tickets = {int(o.get("ticket", 0)) for o in selected_orders if o.get("ticket") is not None}
    matched_order = 0
    for d in selected:
        e = ENTRY.get(int(d.get("entry", -1)), "OTHER")
        p = pos[str(d.get("position_id", "MISSING"))]
        p[{"IN":"in", "OUT":"out", "INOUT":"inout"}.get(e, "other")] += 1
        p["net"] += sum(n(d.get(k)) for k in ("profit", "commission", "swap", "fee"))
        if d.get("order") is not None and int(d["order"]) in order_tickets: matched_order += 1
        ts = d.get("time")
        try: day = datetime.fromtimestamp(int(ts), timezone.utc).date().isoformat()
        except Exception: day = "UNKNOWN"
        row = daily[day]; row["deals"] += 1
        for k in ("profit", "commission", "swap", "fee"): row[k] += n(d.get(k))
    def rnd(x): return round(x, 2)
    profit = sum(n(d.get("profit")) for d in selected)
    commission = sum(n(d.get("commission")) for d in selected)
    swap = sum(n(d.get("swap")) for d in selected)
    fee = sum(n(d.get("fee")) for d in selected)
    net = profit + commission + swap + fee
    pos_net = [v["net"] for k, v in pos.items() if k != "MISSING"]
    result = {
        "scope": {"symbol_filter": SYMBOL, "magic_filter": MAGIC, "note": "Aggregate only; UTC dates; no raw identifiers."},
        "source_counts": {"deals_total": len(deals), "orders_total": len(orders), "events_total": len(events)},
        "filtered_counts": {"deals": len(selected), "orders": len(selected_orders), "unique_positions": len(pos_net)},
        "deal_entry_counts": dict(sorted(entry_counts.items())),
        "deal_type_counts": dict(sorted(type_counts.items())),
        "deal_reason_counts": dict(sorted(reason_counts.items())),
        "order_linkage": {"deals_with_order_ticket_matching_filtered_order": matched_order,
                          "deals_without_matching_filtered_order": len(selected)-matched_order},
        "realized_accounting": {"profit": rnd(profit), "commission": rnd(commission),
                                "swap": rnd(swap), "fee": rnd(fee), "net_after_costs": rnd(net),
                                "positive_net_positions": sum(x > 0.005 for x in pos_net),
                                "negative_net_positions": sum(x < -0.005 for x in pos_net),
                                "flat_net_positions": sum(abs(x) <= 0.005 for x in pos_net)},
        "daily_utc": {k: {m: rnd(v[m]) if m != "deals" else v[m] for m in v}
                      for k, v in sorted(daily.items())},
        "position_lifecycle_aggregate": {
            "positions_with_in": sum(v["in"] > 0 for k,v in pos.items() if k != "MISSING"),
            "positions_with_out": sum(v["out"] > 0 for k,v in pos.items() if k != "MISSING"),
            "positions_with_inout": sum(v["inout"] > 0 for k,v in pos.items() if k != "MISSING"),
            "positions_with_missing_position_id": pos.get("MISSING", {}).get("in", 0)
                + pos.get("MISSING", {}).get("out", 0)
                + pos.get("MISSING", {}).get("inout", 0)
                + pos.get("MISSING", {}).get("other", 0),
        },
        "limitations": ["No per-trade identifiers or rows emitted.",
                        "Position net classification is based only on filtered deal profit, commission, swap and fee.",
                        "MFE/MAE and runner-event reconciliation require a separate timestamp/price-level private analysis."]
    }
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if a.output:
        with open(a.output, "w", encoding="utf-8") as f: f.write(text + "\n")
    print(text)

if __name__ == "__main__": main()
