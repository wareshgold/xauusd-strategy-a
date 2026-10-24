"""Deterministic journal analytics.

This module only summarizes recorded outcomes. It does not alter Strategy A rules.
"""

from __future__ import annotations

import json
from pathlib import Path

from live_journal import read_jsonl, TRADES


def summarize(path: Path = TRADES) -> dict:
    rows = read_jsonl(path)
    closed = [r for r in rows if str(r.get("status", "")).upper() == "CLOSED"]
    wins = [r for r in closed if str(r.get("result", "")).upper() == "WIN"]
    losses = [r for r in closed if str(r.get("result", "")).upper() == "LOSS"]

    r_values = [float(r["r_multiple"]) for r in closed if r.get("r_multiple") is not None]
    positive = sum(v for v in r_values if v > 0)
    negative = -sum(v for v in r_values if v < 0)

    return {
        "total_trade_records": len(rows),
        "closed_trades": len(closed),
        "wins": len(wins),
        "losses": len(losses),
        "decisive_win_rate_pct": (
            100.0 * len(wins) / (len(wins) + len(losses))
            if wins or losses else None
        ),
        "sum_r": sum(r_values) if r_values else 0.0,
        "profit_factor_by_r": positive / negative if negative else None,
    }


if __name__ == "__main__":
    print(json.dumps(summarize(), indent=2))
