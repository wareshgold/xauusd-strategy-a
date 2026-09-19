"""Reconcile recorded signals/trades against MT5 deal history.

This is an observation/reconciliation process only. It does not create
or modify Strategy A signals.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import MetaTrader5 as mt5

from live_journal import read_jsonl, record_trade, TRADES, SIGNALS

SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
MAGIC = int(os.getenv("MT5_MAGIC", "26091901"))


def _directional_r(signal: dict, exit_price: float) -> float | None:
    entry = float(signal.get("signal_entry") or 0)
    sl = float(signal.get("sl") or 0)
    if entry == 0 or sl == entry:
        return None
    direction = str(signal.get("direction", "")).upper()
    if direction == "BUY":
        return (exit_price - entry) / (entry - sl)
    if direction == "SELL":
        return (entry - exit_price) / (sl - entry)
    return None


def main() -> None:
    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        signals = read_jsonl(SIGNALS)
        existing = read_jsonl(TRADES)
        known_deals = {
            str(r.get("deal_id"))
            for r in existing
            if r.get("deal_id") is not None
        }

        now = datetime.now(timezone.utc)
        deals = list(mt5.history_deals_get(now - timedelta(days=30), now) or [])
        deals = [
            deal for deal in deals
            if getattr(deal, "symbol", None) == SYMBOL
            and int(getattr(deal, "magic", -1)) == MAGIC
        ]

        matched = 0
        closed = 0

        for signal in signals:
            signal_id = str(signal.get("signal_id"))
            if not signal_id:
                continue

            comment = f"SP2L:{signal_id}"
            signal_deals = [
                deal for deal in deals
                if str(getattr(deal, "comment", "")) == comment
            ]
            if not signal_deals:
                continue

            matched += 1

            for deal in signal_deals:
                deal_id = str(getattr(deal, "ticket", ""))
                if not deal_id or deal_id in known_deals:
                    continue

                entry_type = int(getattr(deal, "entry", -1))
                is_exit = entry_type == getattr(mt5, "DEAL_ENTRY_OUT", 1)

                profit = float(getattr(deal, "profit", 0.0))
                swap = float(getattr(deal, "swap", 0.0))
                commission = float(getattr(deal, "commission", 0.0))
                net = profit + swap + commission
                exit_price = float(getattr(deal, "price", 0.0))

                r_multiple = _directional_r(signal, exit_price) if is_exit else None
                result = None
                if is_exit:
                    result = "WIN" if net > 0 else ("LOSS" if net < 0 else "BREAKEVEN")
                    closed += 1

                record_trade({
                    "signal_id": signal_id,
                    "symbol": SYMBOL,
                    "direction": signal.get("direction"),
                    "status": "CLOSED" if is_exit else "BROKER_DEAL",
                    "result": result,
                    "r_multiple": r_multiple,
                    "deal_id": getattr(deal, "ticket", None),
                    "order_id": getattr(deal, "order", None),
                    "position_id": getattr(deal, "position_id", None),
                    "broker_time": getattr(deal, "time", None),
                    "broker_price": exit_price,
                    "broker_volume": getattr(deal, "volume", None),
                    "broker_profit": profit,
                    "broker_swap": swap,
                    "broker_commission": commission,
                    "broker_net": net,
                    "broker_entry_type": entry_type,
                    "broker_comment": getattr(deal, "comment", None),
                })
                known_deals.add(deal_id)

        print(f"signals={len(signals)} mt5_deals={len(deals)} matched_signals={matched} newly_recorded_closed={closed}")
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
