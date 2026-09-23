"""MT5 history reconciliation helper for SP2L forward audit.

Infrastructure only. Does not generate signals or change strategy rules.
Compares terminal deals with local journal records so missing lifecycle
updates can be identified.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json

import MetaTrader5 as mt5

try:
    from live_journal import read_jsonl, TRADES
except ModuleNotFoundError:
    from scripts.live_journal import read_jsonl, TRADES


def collect_history(symbol: str, days: int = 7) -> list[dict]:
    now = datetime.now(timezone.utc)
    deals = mt5.history_deals_get(now.timestamp() - days * 86400, now.timestamp()) or []
    rows = []
    for deal in deals:
        if symbol and deal.symbol != symbol:
            continue
        rows.append({
            "ticket": int(deal.ticket),
            "order": int(deal.order),
            "position_id": int(deal.position_id),
            "symbol": deal.symbol,
            "type": int(deal.type),
            "entry": int(deal.entry),
            "price": float(deal.price),
            "volume": float(deal.volume),
            "profit": float(deal.profit),
            "time": int(deal.time),
        })
    return rows


def reconcile(symbol: str = "XAUUSD.ecn") -> dict:
    terminal = collect_history(symbol)
    journal = read_jsonl(TRADES)
    journal_tickets = {int(x.get("deal")) for x in journal if x.get("deal")}
    missing = [x for x in terminal if x["ticket"] not in journal_tickets]
    return {
        "symbol": symbol,
        "terminal_deals": len(terminal),
        "journal_trade_records": len(journal),
        "missing_terminal_deals_in_journal": missing,
    }


if __name__ == "__main__":
    if not mt5.initialize():
        raise SystemExit(f"MT5 init failed: {mt5.last_error()}")
    print(json.dumps(reconcile(), indent=2))
    mt5.shutdown()
