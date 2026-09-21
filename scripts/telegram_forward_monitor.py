"""Research-only MT5 deal lifecycle monitor for SP2L demo forward testing.

Reporting/infrastructure only. It does not calculate Strategy A geometry,
change orders, or generate BUY/SELL decisions. It observes research deals and
their linked order/position history and forwards lifecycle events to Telegram.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

from telegram_client import send_telegram_message

SYMBOL = "XAUUSD.ecn"
MAGIC = 26091901
POLL_SECONDS = 3
PIP_SIZE = float(os.getenv("XAUUSD_PIP_SIZE", "0.01"))
IRAN_UTC_OFFSET = timezone(timedelta(hours=3, minutes=30))
STATE = Path("runtime/telegram_forward_monitor_state.json")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def send(text: str) -> dict:
    r = send_telegram_message(text)
    return {"success": r.success, "detail": r.detail}


def resolve_trade_levels(deal) -> tuple[float | None, float | None]:
    sl = tp = None
    position_id = int(getattr(deal, "position_id", 0) or 0)
    if position_id:
        positions = mt5.positions_get(ticket=position_id) or []
        if positions:
            position = positions[0]
            sl = float(getattr(position, "sl", 0.0) or 0.0) or None
            tp = float(getattr(position, "tp", 0.0) or 0.0) or None

    order_ticket = int(getattr(deal, "order", 0) or 0)
    if (sl is None or tp is None) and order_ticket:
        orders = mt5.history_orders_get(ticket=order_ticket) or []
        if orders:
            order = orders[0]
            sl = sl if sl is not None else (float(getattr(order, "sl", 0.0) or 0.0) or None)
            tp = tp if tp is not None else (float(getattr(order, "tp", 0.0) or 0.0) or None)
    return sl, tp


def pips(distance: float | None) -> str:
    return "N/A" if distance is None else f"{abs(distance) / PIP_SIZE:.1f} pip"


def close_reason(deal) -> str:
    reason = int(getattr(deal, "reason", -1))
    if reason == getattr(mt5, "DEAL_REASON_TP", -999):
        return "TAKE PROFIT"
    if reason == getattr(mt5, "DEAL_REASON_SL", -998):
        return "STOP LOSS"
    return "CLOSE"


def deal_message(deal) -> str:
    side = "BUY" if getattr(deal, "type", None) == mt5.DEAL_TYPE_BUY else "SELL"
    price = float(deal.price)
    sl, tp = resolve_trade_levels(deal)
    is_open = int(getattr(deal, "entry", -1)) == mt5.DEAL_ENTRY_IN
    reason = "" if is_open else f"\nReason: {close_reason(deal)}"
    iran_time = datetime.fromtimestamp(int(deal.time), timezone.utc).astimezone(IRAN_UTC_OFFSET)

    sl_distance = abs(price - sl) if sl is not None else None
    tp_distance = abs(tp - price) if tp is not None else None
    sl_text = f"{sl:.2f} ({pips(sl_distance)})" if sl is not None else "NOT SET"
    tp_text = f"{tp:.2f} ({pips(tp_distance)})" if tp is not None else "NOT SET"

    headline = f"🟢 XAUUSD {side} — OPEN" if is_open else f"🔴 XAUUSD {side} — CLOSE"
    price_label = "Entry" if is_open else "Exit"

    return (
        f"{headline}{reason}\n\n"
        f"{price_label}: {price:.2f}\n"
        f"SL: {sl_text}\n"
        f"TP: {tp_text}\n\n"
        f"Volume: {float(deal.volume):.2f}\n"
        f"Profit: {float(getattr(deal, 'profit', 0.0)):.2f}\n\n"
        f"Date: {iran_time.strftime('%Y-%m-%d')}\n"
        f"Time: {iran_time.strftime('%H:%M:%S')} (UTC+3:30)\n\n"
        f"Deal: {int(deal.ticket)}\n"
        f"Order: {int(deal.order)}\n"
        f"Position: {int(getattr(deal, 'position_id', 0) or 0)}\n"
        f"Mode: RESEARCH FORWARD MONITOR"
    )


def load_state() -> dict:
    try:
        payload = json.loads(STATE.read_text(encoding="utf-8"))
        return {
            "deal_tickets": {int(x) for x in payload.get("deal_tickets", [])},
            "research_orders": {int(x) for x in payload.get("research_orders", [])},
            "research_positions": {int(x) for x in payload.get("research_positions", [])},
        }
    except Exception:
        return {"deal_tickets": set(), "research_orders": set(), "research_positions": set()}


def save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE["deal_tickets"] = set(sorted(state["deal_tickets"])[-500:])
    STATE["research_orders"] = set(sorted(state["research_orders"])[-500:])
    STATE["research_positions"] = set(sorted(state["research_positions"])[-500:])
    STATE.write_text(json.dumps({
        "deal_tickets": sorted(state["deal_tickets"]),
        "research_orders": sorted(state["research_orders"]),
        "research_positions": sorted(state["research_positions"]),
    }, indent=2), encoding="utf-8")


def is_research_deal(deal, state: dict) -> bool:
    if str(deal.symbol) != SYMBOL:
        return False
    magic = int(getattr(deal, "magic", 0) or 0)
    order = int(getattr(deal, "order", 0) or 0)
    position = int(getattr(deal, "position_id", 0) or 0)
    return magic == MAGIC or (order and order in state["research_orders"]) or (position and position in state["research_positions"])


def main() -> None:
    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        state = load_state()
        lookback = int(os.getenv("TELEGRAM_MONITOR_LOOKBACK_MINUTES", "5"))
        start = utc_now() - timedelta(minutes=lookback)
        print(json.dumps({
            "event": "START",
            "symbol": SYMBOL,
            "magic": MAGIC,
            "lookback_minutes": lookback,
            "canonical": False,
            "lifecycle_monitor": True,
            "tracks_order_and_position_links": True,
        }, indent=2))

        while True:
            deals = mt5.history_deals_get(start, utc_now())
            if deals is not None:
                for deal in sorted(deals, key=lambda x: (int(x.time), int(x.ticket))):
                    ticket = int(deal.ticket)
                    if ticket in state["deal_tickets"] or not is_research_deal(deal, state):
                        continue

                    order = int(getattr(deal, "order", 0) or 0)
                    position = int(getattr(deal, "position_id", 0) or 0)
                    if order:
                        state["research_orders"].add(order)
                    if position:
                        state["research_positions"].add(position)

                    result = send(deal_message(deal))
                    print(json.dumps({
                        "event": "TELEGRAM_DEAL_LIFECYCLE",
                        "deal": ticket,
                        "order": order,
                        "position": position,
                        "entry": int(getattr(deal, "entry", -1)),
                        "reason": int(getattr(deal, "reason", -1)),
                        "result": result,
                        "canonical": False,
                    }, indent=2))

                    state["deal_tickets"].add(ticket)
                    save_state(state)

            start = utc_now() - timedelta(minutes=5)
            time.sleep(POLL_SECONDS)
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
