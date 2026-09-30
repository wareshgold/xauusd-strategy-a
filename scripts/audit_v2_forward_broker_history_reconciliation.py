"""Deterministic broker reconciliation with ticket, position and time-window fallbacks.

NON_CANONICAL_FORENSIC / read-only. Never places or modifies orders.
This tool is intentionally independent from the excursion replay so that
missing direct-ticket lookups can be diagnosed without changing that report.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--events", required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--symbol", default="XAUUSD.ecn")
    p.add_argument("--mt5-path", default=os.getenv("MT5_TERMINAL_PATH"))
    p.add_argument("--output", required=True)
    p.add_argument("--window-seconds", type=int, default=30)
    return p.parse_args()


def epoch(value):
    return int(datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp())


def iso(value):
    if value is None:
        return None
    return datetime.fromtimestamp(int(value), timezone.utc).isoformat().replace("+00:00", "Z")


def ticket(event, *names):
    for name in names:
        value = event.get(name)
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def load_trades(path, start_ts, end_ts, symbol):
    grouped = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("event") != "TELEGRAM_DEAL_LIFECYCLE":
            continue
        if e.get("symbol") != symbol or not e.get("signal_id"):
            continue
        try:
            et = epoch(e["ts_utc"])
        except Exception:
            continue
        if not start_ts <= et < end_ts:
            continue
        rec = grouped.setdefault(e["signal_id"], {})
        if int(e.get("entry", -1)) == 0:
            rec["entry"] = e
        elif int(e.get("entry", -1)) == 1:
            rec["exit"] = e

    rows = []
    for sid, rec in grouped.items():
        ent, ex = rec.get("entry"), rec.get("exit")
        if not ent or not ex:
            continue
        rows.append({
            "signal_id": sid,
            "direction": sid.rsplit(":", 1)[-1].upper(),
            "entry_ts": epoch(ent["ts_utc"]),
            "exit_ts": epoch(ex["ts_utc"]),
            "entry_price": ent.get("entry_price"),
            "exit_price": ex.get("exit_price"),
            "entry_order_ticket": ticket(ent, "order", "entry_order", "order_ticket"),
            "entry_deal_ticket": ticket(ent, "deal", "entry_deal", "deal_ticket"),
            "entry_position_ticket": ticket(ent, "position", "position_ticket"),
            "exit_order_ticket": ticket(ex, "order", "exit_order", "order_ticket"),
            "exit_deal_ticket": ticket(ex, "deal", "exit_deal", "deal_ticket"),
            "exit_position_ticket": ticket(ex, "position", "position_ticket"),
        })
    return sorted(rows, key=lambda r: (r["entry_ts"], r["signal_id"]))


def as_dict(row):
    if hasattr(row, "_asdict"):
        return row._asdict()
    return {}


def safe_history(call, *args, **kwargs):
    try:
        result = call(*args, **kwargs)
        return [as_dict(x) for x in (result or [])], None
    except Exception as exc:
        return [], f"{type(exc).__name__}: {exc}"


def lookup_ticket(ticket_value, kind):
    if ticket_value is None:
        return {"ticket": None, "found": False, "method": "NO_TICKET"}

    fn = mt5.history_orders_get if kind == "order" else mt5.history_deals_get
    rows, error = safe_history(fn, ticket=ticket_value)
    if rows:
        exact = [r for r in rows if int(r.get("ticket", -1)) == int(ticket_value)]
        if exact:
            return {"ticket": ticket_value, "found": True, "method": "DIRECT_TICKET", "rows": exact, "error": error}
    return {"ticket": ticket_value, "found": False, "method": "DIRECT_TICKET_NOT_FOUND", "rows": rows, "error": error}


def lookup_time_window(start_ts, end_ts, symbol, window_seconds):
    start = datetime.fromtimestamp(start_ts - window_seconds, timezone.utc)
    end = datetime.fromtimestamp(end_ts + window_seconds, timezone.utc)
    orders, oe = safe_history(mt5.history_orders_get, start, end)
    deals, de = safe_history(mt5.history_deals_get, start, end)
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "orders": [r for r in orders if str(r.get("symbol")) == symbol],
        "deals": [r for r in deals if str(r.get("symbol")) == symbol],
        "errors": {"orders": oe, "deals": de},
    }


def summarize_ticket(found, expected_price=None, expected_position=None, symbol=None):
    rows = found.get("rows", [])
    out = {
        "ticket": found.get("ticket"),
        "found": bool(rows),
        "method": found.get("method"),
        "error": found.get("error"),
        "candidates": [],
    }
    for r in rows:
        item = {
            "ticket": r.get("ticket"),
            "symbol": r.get("symbol"),
            "price": r.get("price"),
            "position_id": r.get("position_id"),
            "time": r.get("time"),
            "time_msc": r.get("time_msc"),
            "type": r.get("type"),
            "order": r.get("order"),
            "deal": r.get("deal"),
        }
        if expected_price is not None and r.get("price") is not None:
            item["price_delta"] = float(r["price"]) - float(expected_price)
        if expected_position is not None and r.get("position_id") is not None:
            item["position_matches"] = int(r["position_id"]) == int(expected_position)
        if symbol is not None:
            item["symbol_matches"] = str(r.get("symbol")) == symbol
        out["candidates"].append(item)
    return out


def reconcile_trade(trade, symbol, window_seconds):
    raw = {}
    specs = (
        ("entry_order", trade["entry_order_ticket"], "order", None, trade["entry_position_ticket"]),
        ("entry_deal", trade["entry_deal_ticket"], "deal", trade["entry_price"], trade["entry_position_ticket"]),
        ("exit_order", trade["exit_order_ticket"], "order", None, trade["exit_position_ticket"]),
        ("exit_deal", trade["exit_deal_ticket"], "deal", trade["exit_price"], trade["exit_position_ticket"]),
    )
    for label, tk, kind, price, pos in specs:
        raw[label] = summarize_ticket(lookup_ticket(tk, kind), price, pos, symbol)

    tw = lookup_time_window(
        min(trade["entry_ts"], trade["exit_ts"]),
        max(trade["entry_ts"], trade["exit_ts"]),
        symbol,
        window_seconds,
    )

    fallback = {}
    for label, tk, kind, price, pos in specs:
        direct = raw[label]
        if direct["found"]:
            continue
        candidates = tw["orders"] if kind == "order" else tw["deals"]
        matched = []
        for r in candidates:
            if int(r.get("ticket", -1)) == int(tk or -999999):
                matched.append(r)
            elif kind == "deal" and pos is not None and int(r.get("position_id", -1)) == int(pos):
                matched.append(r)
        fallback[label] = [
            {
                "ticket": r.get("ticket"),
                "symbol": r.get("symbol"),
                "price": r.get("price"),
                "position_id": r.get("position_id"),
                "time": r.get("time"),
                "time_msc": r.get("time_msc"),
                "type": r.get("type"),
                "order": r.get("order"),
                "deal": r.get("deal"),
            }
            for r in matched
        ]

    reasons = []
    for label, info in raw.items():
        if info["found"]:
            for c in info["candidates"]:
                if c.get("symbol_matches") is False:
                    reasons.append(label.upper() + "_SYMBOL_MISMATCH")
                if c.get("position_matches") is False:
                    reasons.append(label.upper() + "_POSITION_MISMATCH")
        else:
            if fallback.get(label):
                reasons.append(label.upper() + "_DIRECT_TICKET_MISSING_BUT_TIME_WINDOW_MATCH")
            else:
                reasons.append(label.upper() + "_TRUE_MISSING")

    status = "BROKER_CONFIRMED" if not reasons else "BROKER_MISMATCH_OR_MISSING"
    if all(not raw[x]["found"] for x in raw) and any(fallback.values()):
        status = "BROKER_FOUND_BY_FALLBACK"

    return {
        "signal_id": trade["signal_id"],
        "direction": trade["direction"],
        "entry_ts": iso(trade["entry_ts"]),
        "exit_ts": iso(trade["exit_ts"]),
        "tickets": {k: trade[k + "_ticket"] for k in (
            "entry_order", "entry_deal", "entry_position",
            "exit_order", "exit_deal", "exit_position"
        )},
        "direct_ticket_checks": raw,
        "time_window_fallback": {
            "window_seconds": window_seconds,
            "query_start": tw["start"],
            "query_end": tw["end"],
            "orders_returned": len(tw["orders"]),
            "deals_returned": len(tw["deals"]),
            "matches": fallback,
            "errors": tw["errors"],
        },
        "reasons": sorted(set(reasons)),
        "status": status,
    }


def main():
    args = parse_args()
    start_ts, end_ts = epoch(args.start), epoch(args.end)
    trades = load_trades(args.events, start_ts, end_ts, args.symbol)
    if not trades:
        raise SystemExit("No completed lifecycle trades found.")

    ok = mt5.initialize(path=args.mt5_path) if args.mt5_path else mt5.initialize()
    if not ok:
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        results = [reconcile_trade(t, args.symbol, args.window_seconds) for t in trades]
    finally:
        mt5.shutdown()

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    reason_counts = {}
    for r in results:
        for reason in r["reasons"]:
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

    report = {
        "status": "COMPLETE",
        "mode": "NON_CANONICAL_FORENSIC",
        "scope": {
            "symbol": args.symbol,
            "start_utc": args.start,
            "end_utc": args.end,
            "window_seconds": args.window_seconds,
        },
        "counts": counts | {"historical_trades": len(results)},
        "reason_counts": dict(sorted(reason_counts.items())),
        "trades": results,
        "interpretation_guard": [
            "Direct ticket lookup is tested first.",
            "A time-window/position match is evidence for reconciliation only; it does not silently rewrite the lifecycle ticket.",
            "TRUE_MISSING means neither direct ticket lookup nor the configured local time-window fallback found a candidate.",
            "NON_CANONICAL_FORENSIC: this report does not define Strategy A geometry, fills, stops, targets, or trailing rules.",
        ],
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "counts": report["counts"],
        "reason_counts": report["reason_counts"],
        "output": str(out),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
