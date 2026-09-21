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
STATE = Path("runtime/telegram_forward_monitor_state.json")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def send(text: str) -> dict:
    r = send_telegram_message(text)
    return {"success": r.success, "detail": r.detail}


def deal_message(deal) -> str:
    entry = getattr(deal, "entry", None)
    reason = getattr(deal, "reason", None)
    side = "BUY" if getattr(deal, "type", None) == mt5.DEAL_TYPE_BUY else "SELL"
    profit = float(getattr(deal, "profit", 0.0))
    return (
        f"📌 XAUUSD {side} DEAL\n\n"
        f"Price: {float(deal.price):.2f}\n"
        f"Volume: {float(deal.volume):.2f}\n"
        f"Profit: {profit:.2f}\n"
        f"Deal: {int(deal.ticket)}\n"
        f"Order: {int(deal.order)}\n"
        f"Entry code: {entry}\n"
        f"Reason code: {reason}\n"
        f"Time UTC: {datetime.fromtimestamp(int(deal.time), timezone.utc).isoformat()}\n"
        f"Mode: RESEARCH_FORWARD_MONITOR"
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
