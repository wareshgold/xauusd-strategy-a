"""Research-only MT5 deal outcome monitor for SP2L demo forward testing.

Reporting/infrastructure only. This module does not calculate Strategy A geometry,
change orders, or generate BUY/SELL decisions. It observes completed MT5 deals
for the research magic number and forwards each newly observed deal to Telegram.
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
# Reporting convention only: XAUUSD 1 pip = 0.01 price unit.
# This does not define Strategy A geometry or execution semantics.
PIP_SIZE = float(os.getenv("XAUUSD_PIP_SIZE", "0.01"))
IRAN_UTC_OFFSET = timezone(timedelta(hours=3, minutes=30))
STATE = Path("runtime/telegram_forward_monitor_state.json")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def send(text: str) -> dict:
    r = send_telegram_message(text)
    return {"success": r.success, "detail": r.detail}


def resolve_trade_levels(deal) -> tuple[float | None, float | None]:
    """Resolve SL/TP from the MT5 order/position; never infer them."""
    sl = None
    tp = None

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
            if sl is None:
                sl = float(getattr(order, "sl", 0.0) or 0.0) or None
            if tp is None:
                tp = float(getattr(order, "tp", 0.0) or 0.0) or None

    return sl, tp


def pips(distance: float | None) -> str:
    if distance is None:
        return "N/A"
    return f"{abs(distance) / PIP_SIZE:.1f} pip"


def deal_message(deal) -> str:
    side = "BUY" if getattr(deal, "type", None) == mt5.DEAL_TYPE_BUY else "SELL"
    entry_price = float(deal.price)
    sl, tp = resolve_trade_levels(deal)
    sl_distance = abs(entry_price - sl) if sl is not None else None
    tp_distance = abs(tp - entry_price) if tp is not None else None
    profit = float(getattr(deal, "profit", 0.0))
    iran_time = datetime.fromtimestamp(int(deal.time), timezone.utc).astimezone(IRAN_UTC_OFFSET)
    status = "OPEN" if int(getattr(deal, "entry", -1)) == mt5.DEAL_ENTRY_IN else "CLOSE"

    sl_text = f"{sl:.2f} ({pips(sl_distance)})" if sl is not None else "NOT SET"
    tp_text = f"{tp:.2f} ({pips(tp_distance)})" if tp is not None else "NOT SET"

    return (
        f"🟢 XAUUSD {side} — {status}\n\n"
        f"Entry: {entry_price:.2f}\n"
        f"SL: {sl_text}\n"
        f"TP: {tp_text}\n\n"
        f"Volume: {float(deal.volume):.2f}\n"
        f"Profit: {profit:.2f}\n\n"
        f"Date: {iran_time.strftime('%Y-%m-%d')}\n"
        f"Time: {iran_time.strftime('%H:%M:%S')} (UTC+3:30)\n\n"
        f"Deal: {int(deal.ticket)}\n"
        f"Order: {int(deal.order)}\n"
        f"Mode: RESEARCH FORWARD MONITOR"
    )


def load_seen() -> set[int]:
    try:
        payload = json.loads(STATE.read_text(encoding="utf-8"))
        return {int(x) for x in payload.get("deal_tickets", [])}
    except Exception:
        return set()


def save_seen(seen: set[int]) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    # Keep a bounded audit state.
    STATE.write_text(
        json.dumps({"deal_tickets": sorted(seen)[-500:]}, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        seen = load_seen()
        start = utc_now() - timedelta(minutes=int(os.getenv("TELEGRAM_MONITOR_LOOKBACK_MINUTES", "5")))
        print(json.dumps({
            "event": "START",
            "symbol": SYMBOL,
            "magic": MAGIC,
            "lookback_minutes": int(os.getenv("TELEGRAM_MONITOR_LOOKBACK_MINUTES", "5")),
            "canonical": False,
        }, indent=2))

        while True:
            deals = mt5.history_deals_get(start, utc_now())
            if deals is not None:
                for deal in sorted(deals, key=lambda x: int(x.time)):
                    ticket = int(deal.ticket)
                    if ticket in seen:
                        continue
                    if str(deal.symbol) != SYMBOL or int(deal.magic) != MAGIC:
                        seen.add(ticket)
                        continue

                    result = send(deal_message(deal))
                    print(json.dumps({
                        "event": "TELEGRAM_DEAL_OUTCOME",
                        "deal": ticket,
                        "result": result,
                        "canonical": False,
                    }, indent=2))
                    seen.add(ticket)
                    save_seen(seen)

            start = utc_now() - timedelta(minutes=5)
            time.sleep(POLL_SECONDS)
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
