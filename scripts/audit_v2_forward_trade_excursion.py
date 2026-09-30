"""Research-only V2 Forward trade excursion forensic audit.

This tool is NON_CANONICAL_FORENSIC. It never places/modifies orders and never
promotes an exit rule to Strategy A.

For the historical Forward lifecycle population it reports:
- MFE/MAE in R from actual broker entry using the runner-recorded theoretical SL.
- first +1R / +2R reach timestamps.
- whether those levels were reached before the historical broker exit.
- hypothetical R1/R2 and BE-at-1R outcomes using fail-closed M1 replay.
- optional broker-authoritative MT5 history cross-validation by deal/order/
  position ticket.

M1 OHLC cannot prove intrabar ordering. Stop/target/BE conflicts are marked
AMBIGUOUS_INTRABAR rather than resolved by an invented tie-break.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

TIMEFRAME = mt5.TIMEFRAME_M1
POLICIES = (
    ("R1_NO_TRAIL", 1.0, False),
    ("R1_BE_AT_1R", 1.0, True),
    ("R2_NO_TRAIL", 2.0, False),
    ("R2_BE_AT_1R", 2.0, True),
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--events", required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--symbol", default="XAUUSD.ecn")
    p.add_argument("--mt5-path", default=os.getenv("MT5_TERMINAL_PATH"))
    p.add_argument("--output", required=True)
    p.add_argument(
        "--skip-broker-cross-validation",
        action="store_true",
        help="Do not query MT5 history_orders/history_deals.",
    )
    return p.parse_args()


def ts(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def iso(epoch: int | None) -> str | None:
    if epoch is None:
        return None
    return datetime.fromtimestamp(int(epoch), timezone.utc).isoformat().replace("+00:00", "Z")


def event_ticket(event, *names):
    for name in names:
        value = event.get(name)
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def load_trades(path: str, start: int, end: int, symbol: str):
    rows = {}
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
            event_ts = ts(str(e.get("ts_utc")))
        except Exception:
            continue
        if not start <= event_ts < end:
            continue

        sid = str(e["signal_id"])
        rec = rows.setdefault(sid, {"signal_id": sid, "symbol": symbol, "events": []})
        rec["events"].append(e)
        if int(e.get("entry", -1)) == 0:
            rec["entry_event"] = e
        elif int(e.get("entry", -1)) == 1:
            rec["exit_event"] = e

    trades = []
    for sid, rec in rows.items():
        ent = rec.get("entry_event")
        ex = rec.get("exit_event")
        if not ent or not ex:
            continue
        direction = str(sid.rsplit(":", 1)[-1]).upper()
        if direction not in {"BUY", "SELL"}:
            continue
        vals = (ent.get("entry_price"), ent.get("theoretical_entry"), ent.get("theoretical_sl"))
        if not all(isinstance(x, (int, float)) for x in vals):
            continue
        entry_ts = ts(str(ent["ts_utc"]))
        exit_ts = ts(str(ex["ts_utc"]))
        risk = (
            float(ent["theoretical_entry"]) - float(ent["theoretical_sl"])
            if direction == "BUY"
            else float(ent["theoretical_sl"]) - float(ent["theoretical_entry"])
        )
        if exit_ts < entry_ts or risk <= 0:
            continue
        trades.append(
            {
                "signal_id": sid,
                "direction": direction,
                "entry_ts": entry_ts,
                "exit_ts": exit_ts,
                "actual_entry": float(ent["entry_price"]),
                "theoretical_entry": float(ent["theoretical_entry"]),
                "theoretical_sl": float(ent["theoretical_sl"]),
                "risk": risk,
                "actual_exit": ex.get("exit_price"),
                "actual_r": ex.get("actual_r"),
                "actual_net": ex.get("net"),
                "entry_deal_ticket": event_ticket(ent, "deal", "entry_deal", "deal_ticket"),
                "entry_order_ticket": event_ticket(ent, "order", "entry_order", "order_ticket"),
                "entry_position_ticket": event_ticket(ent, "position", "position_ticket"),
                "exit_deal_ticket": event_ticket(ex, "deal", "exit_deal", "deal_ticket"),
                "exit_order_ticket": event_ticket(ex, "order", "exit_order", "order_ticket"),
                "exit_position_ticket": event_ticket(ex, "position", "position_ticket"),
            }
        )
    return sorted(trades, key=lambda x: (x["entry_ts"], x["signal_id"]))


def load_bars(symbol: str, start_ts: int, end_ts: int):
    start = datetime.fromtimestamp(start_ts, timezone.utc) - timedelta(minutes=1)
    end = datetime.fromtimestamp(end_ts, timezone.utc) + timedelta(minutes=1)
    rates = mt5.copy_rates_range(symbol, TIMEFRAME, start, end)
    if rates is None or len(rates) == 0:
        return []
    return [
        {
            "time": int(r["time"]),
            "open": float(r["open"]),
            "high": float(r["high"]),
            "low": float(r["low"]),
            "close": float(r["close"]),
        }
        for r in rates
    ]


def level_prices(trade):
    entry = trade["actual_entry"]
    risk = trade["risk"]
    if trade["direction"] == "BUY":
        return entry + risk, entry + 2 * risk, entry - risk
    return entry - risk, entry - 2 * risk, entry + risk


def excursion(trade, bars):
    r1, r2, initial_sl = level_prices(trade)
    d = trade["direction"]
    max_fav = float("-inf")
    max_adv = float("inf")
    first_r1 = first_r2 = None
    first_r1_after_entry = first_r2_after_entry = None

    for bar in bars:
        if bar["time"] < trade["entry_ts"] or bar["time"] > trade["exit_ts"]:
            continue
        if d == "BUY":
            fav = (bar["high"] - trade["actual_entry"]) / trade["risk"]
            adv = (bar["low"] - trade["actual_entry"]) / trade["risk"]
            hit1 = bar["high"] >= r1
            hit2 = bar["high"] >= r2
        else:
            fav = (trade["actual_entry"] - bar["low"]) / trade["risk"]
            adv = (trade["actual_entry"] - bar["high"]) / trade["risk"]
            hit1 = bar["low"] <= r1
            hit2 = bar["low"] <= r2

        max_fav = max(max_fav, fav)
        max_adv = min(max_adv, adv)
        if hit1 and first_r1 is None:
            first_r1 = bar["time"]
        if hit2 and first_r2 is None:
            first_r2 = bar["time"]

    return {
        "mfe_r": None if max_fav == float("-inf") else max_fav,
        "mae_r": None if max_adv == float("inf") else max_adv,
        "first_1r_ts": first_r1,
        "first_2r_ts": first_r2,
        "first_1r_before_historical_exit": bool(first_r1 is not None),
        "first_2r_before_historical_exit": bool(first_r2 is not None),
        "initial_sl_price": initial_sl,
    }


def replay_policy(trade, bars, target_r, be_at_1r, analysis_end_ts):
    d = trade["direction"]
    entry = trade["actual_entry"]
    risk = trade["risk"]
    target = entry + target_r * risk if d == "BUY" else entry - target_r * risk
    be_level = entry + risk if d == "BUY" else entry - risk
    active_sl = trade["theoretical_sl"]
    be_armed = False

    for bar in bars:
        if bar["time"] < trade["entry_ts"] or bar["time"] > analysis_end_ts:
            continue

        if d == "BUY":
            stop_hit = bar["low"] <= active_sl
            target_hit = bar["high"] >= target
            be_hit = be_at_1r and not be_armed and bar["high"] >= be_level
        else:
            stop_hit = bar["high"] >= active_sl
            target_hit = bar["low"] <= target
            be_hit = be_at_1r and not be_armed and bar["low"] <= be_level

        if stop_hit and target_hit:
            return {"status": "AMBIGUOUS_INTRABAR", "exit_ts": bar["time"], "r": None,
                    "reason": "ACTIVE_STOP_AND_TARGET_SAME_M1_BAR"}
        if be_hit and stop_hit:
            return {"status": "AMBIGUOUS_INTRABAR", "exit_ts": bar["time"], "r": None,
                    "reason": "BE_TRIGGER_AND_STOP_SAME_M1_BAR"}

        if be_hit:
            be_armed = True
            active_sl = entry

        if stop_hit:
            r = ((active_sl - entry) / risk) if d == "BUY" else ((entry - active_sl) / risk)
            return {"status": "STOP", "exit_ts": bar["time"], "r": r, "reason": None}
        if target_hit:
            return {"status": "TARGET", "exit_ts": bar["time"], "r": target_r, "reason": None}

    return {"status": "OPEN_AT_DATA_END", "exit_ts": None, "r": None,
            "reason": "NO_HYPOTHETICAL_EXIT_BEFORE_ANALYSIS_END"}


def mt5_rows_to_dicts(rows):
    return [dict(zip(r._asdict().keys(), r)) if hasattr(r, "_asdict") else {} for r in (rows or [])]


def cross_validate(trades, start_ts, end_ts, symbol):
    start = datetime.fromtimestamp(start_ts, timezone.utc) - timedelta(minutes=2)
    end = datetime.fromtimestamp(end_ts, timezone.utc) + timedelta(minutes=2)
    orders = mt5.history_orders_get(start, end)
    deals = mt5.history_deals_get(start, end)
    order_rows = mt5_rows_to_dicts(orders)
    deal_rows = mt5_rows_to_dicts(deals)

    by_order = {int(r["ticket"]): r for r in order_rows if r.get("ticket") is not None}
    by_deal = {int(r["ticket"]): r for r in deal_rows if r.get("ticket") is not None}

    out = []
    for t in trades:
        checks = {}
        for label, ticket, table in (
            ("entry_order", t["entry_order_ticket"], by_order),
            ("entry_deal", t["entry_deal_ticket"], by_deal),
            ("exit_order", t["exit_order_ticket"], by_order),
            ("exit_deal", t["exit_deal_ticket"], by_deal),
        ):
            checks[label] = {
                "ticket": ticket,
                "found": ticket is not None and ticket in table,
            }

        entry_deal = by_deal.get(t["entry_deal_ticket"])
        exit_deal = by_deal.get(t["exit_deal_ticket"])
        mismatches = []

        if entry_deal:
            if str(entry_deal.get("symbol")) != symbol:
                mismatches.append("ENTRY_DEAL_SYMBOL_MISMATCH")
            if abs(float(entry_deal.get("price", 0.0)) - t["actual_entry"]) > 1e-9:
                mismatches.append("ENTRY_DEAL_PRICE_MISMATCH")
            if t["entry_position_ticket"] is not None and int(entry_deal.get("position_id", -1)) != t["entry_position_ticket"]:
                mismatches.append("ENTRY_POSITION_MISMATCH")

        if exit_deal:
            if str(exit_deal.get("symbol")) != symbol:
                mismatches.append("EXIT_DEAL_SYMBOL_MISMATCH")
            if t["actual_exit"] is not None and abs(float(exit_deal.get("price", 0.0)) - float(t["actual_exit"])) > 1e-9:
                mismatches.append("EXIT_DEAL_PRICE_MISMATCH")
            if t["exit_position_ticket"] is not None and int(exit_deal.get("position_id", -1)) != t["exit_position_ticket"]:
                mismatches.append("EXIT_POSITION_MISMATCH")
            if t["entry_position_ticket"] is not None and int(exit_deal.get("position_id", -1)) != t["entry_position_ticket"]:
                mismatches.append("ENTRY_EXIT_POSITION_LINK_MISMATCH")

        checks["status"] = (
            "BROKER_CONFIRMED"
            if all(x["found"] for x in checks.values())
            and not mismatches
            else "BROKER_MISMATCH_OR_MISSING"
        )
        checks["mismatches"] = mismatches
        out.append({"signal_id": t["signal_id"], **checks})

    return {
        "queried_window_utc": {"start": start.isoformat(), "end": end.isoformat()},
        "orders_returned": len(order_rows),
        "deals_returned": len(deal_rows),
        "trades": out,
    }


def summarize_policy(rows):
    decisive = [r for r in rows if r["replay"]["status"] in {"STOP", "TARGET"}]
    rs = [float(r["replay"]["r"]) for r in decisive]
    return {
        "trades": len(rows),
        "decisive": len(decisive),
        "ambiguous": sum(r["replay"]["status"] == "AMBIGUOUS_INTRABAR" for r in rows),
        "open_at_data_end": sum(r["replay"]["status"] == "OPEN_AT_DATA_END" for r in rows),
        "wins": sum(r["replay"]["r"] > 0 for r in decisive),
        "losses": sum(r["replay"]["r"] < 0 for r in decisive),
        "net_r": sum(rs),
    }


def main():
    args = parse_args()
    start_ts, end_ts = ts(args.start), ts(args.end)
    trades = load_trades(args.events, start_ts, end_ts, args.symbol)
    if not trades:
        raise SystemExit("No completed historical Forward lifecycle trades found.")

    if args.mt5_path:
        initialized = mt5.initialize(path=args.mt5_path)
    else:
        initialized = mt5.initialize()
    if not initialized:
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        broker = None
        if not args.skip_broker_cross_validation:
            broker = cross_validate(trades, start_ts, end_ts, args.symbol)

        rows = []
        for trade in trades:
            bars = load_bars(args.symbol, trade["entry_ts"], end_ts)
            ex = excursion(trade, bars) if bars else {
                "mfe_r": None, "mae_r": None, "first_1r_ts": None, "first_2r_ts": None,
                "first_1r_before_historical_exit": False,
                "first_2r_before_historical_exit": False,
                "initial_sl_price": trade["theoretical_sl"],
            }
            policies = {}
            for name, target_r, be in POLICIES:
                policies[name] = {
                    "target_r": target_r,
                    "be_at_1r": be,
                    "replay": replay_policy(trade, bars, target_r, be, end_ts) if bars else {
                        "status": "NO_MT5_M1_HISTORY", "exit_ts": None, "r": None,
                        "reason": "NO_M1_HISTORY"
                    },
                }
            rows.append({
                **trade,
                "entry_ts_iso": iso(trade["entry_ts"]),
                "historical_exit_ts_iso": iso(trade["exit_ts"]),
                "excursion": {
                    **ex,
                    "first_1r_ts_iso": iso(ex["first_1r_ts"]),
                    "first_2r_ts_iso": iso(ex["first_2r_ts"]),
                },
                "policies": policies,
            })
    finally:
        mt5.shutdown()

    report = {
        "status": "COMPLETE",
        "mode": "NON_CANONICAL_FORENSIC",
        "scope": {
            "symbol": args.symbol,
            "start_utc": args.start,
            "end_utc": args.end,
            "timeframe": "M1",
            "historical_trades": len(trades),
        },
        "broker_cross_validation": broker,
        "trade_level": rows,
        "policy_summaries": {
            name: summarize_policy([{"replay": r["policies"][name]["replay"]} for r in rows])
            for name, _, _ in POLICIES
        },
        "counts": {
            "historical_trades": len(rows),
            "reached_1r_before_exit": sum(r["excursion"]["first_1r_before_historical_exit"] for r in rows),
            "reached_2r_before_exit": sum(r["excursion"]["first_2r_before_historical_exit"] for r in rows),
            "broker_confirmed": (
                sum(x["status"] == "BROKER_CONFIRMED" for x in broker["trades"])
                if broker else None
            ),
        },
        "limitations": [
            "NON_CANONICAL_FORENSIC only; no Strategy A geometry or exit rule is changed.",
            "Historical lifecycle events define the initial population; broker cross-validation is reported separately.",
            "MFE/MAE and level reachability are measured from actual broker entry and runner-recorded theoretical SL.",
            "M1 OHLC cannot establish intrabar ordering; conflicts are fail-closed as AMBIGUOUS_INTRABAR.",
            "A broker-missing/mismatched lifecycle record is not treated as authoritative merely because Telegram contains it.",
        ],
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "status": report["status"],
        "mode": report["mode"],
        "output": str(out),
        "counts": report["counts"],
        "policy_summaries": report["policy_summaries"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
