"""Reconcile recorded live trades against MT5 account history.

This does not create or modify signals. It only attaches broker-side facts
to existing signal IDs using the SP2L magic/comment convention.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

from live_journal import read_jsonl, record_trade, TRADES

SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
MAGIC = int(os.getenv("MT5_MAGIC", "26091901"))


def main() -> None:
    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        rows = read_jsonl(TRADES)
        candidates = [r for r in rows if r.get("status") in {"OPEN", "EXECUTION_FAILED"}]
        now = datetime.now(timezone.utc)
        deals = mt5.history_deals_get(now - timedelta(days=30), now) or []

        by_comment = {
            str(getattr(deal, "comment", "")): deal
            for deal in deals
            if getattr(deal, "symbol", None) == SYMBOL
            and int(getattr(deal, "magic", -1)) == MAGIC
        }

        for row in candidates:
            signal_id = row.get("signal_id")
            deal = by_comment.get(f"SP2L:{signal_id}")
            if deal is None:
                continue

            record_trade({
                "signal_id": signal_id,
                "symbol": SYMBOL,
                "status": "BROKER_RECONCILED",
                "deal_id": getattr(deal, "ticket", None),
                "order_id": getattr(deal, "order", None),
                "broker_time": getattr(deal, "time", None),
                "broker_price": getattr(deal, "price", None),
                "broker_volume": getattr(deal, "volume", None),
                "broker_profit": getattr(deal, "profit", None),
                "broker_swap": getattr(deal, "swap", None),
                "broker_commission": getattr(deal, "commission", None),
                "broker_comment": getattr(deal, "comment", None),
            })

        print(f"reconciled_candidates={len(candidates)} matched={sum(1 for r in candidates if by_comment.get(f'SP2L:{r.get("signal_id")}'))}")
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
