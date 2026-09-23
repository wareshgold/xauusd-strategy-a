"""Probe the local MT5 terminal for available gold symbols (ops tool).

Read-only: selects symbols, reads their specs, sends no orders, and always
shuts the terminal connection down. Helps resolve the CLOSEONLY state of the
currently configured XAUUSD.ecn by listing every gold-named symbol with its
trade mode and volume constraints.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

if __package__ in (None, ""):
    sys.path.insert(0, str(os.path.dirname(os.path.abspath(__file__))))

try:
    import mt5_terminal_resolver
except ModuleNotFoundError:  # pragma: no cover - resolver ships alongside
    mt5_terminal_resolver = None

# Gold symbol name fragments (lowercase); configurable, not exhaustive.
GOLD_PATTERNS = tuple(
    p.strip().lower()
    for p in os.getenv(
        "GOLD_SYMBOL_PATTERNS", "xau,gold,gc1!,xagusd,silver"
    ).split(",")
    if p.strip()
)

TRADE_MODE_NAMES = {
    0: "DISABLED",
    1: "LONGONLY",
    2: "SHORTONLY",
    3: "CLOSEONLY",
    4: "FULL",
}
# Modes that allow opening new positions (everything except DISABLED/CLOSEONLY).
OPENABLE_TRADE_MODES = {1, 2, 4}


def probe_symbols(mt5, patterns=GOLD_PATTERNS) -> list[dict]:
    """Return specs for every visible symbol whose name matches a pattern."""
    rows: list[dict] = []
    names = mt5.symbols_get()
    if names is None:
        return rows
    for sym in names:
        name = getattr(sym, "name", "")
        if not name or not any(p in name.lower() for p in patterns):
            continue
        if not mt5.symbol_select(name, True):
            continue
        info = mt5.symbol_info(name)
        if info is None:
            continue
        mode = int(info.trade_mode)
        rows.append({
            "name": name,
            "path": getattr(info, "path", ""),
            "visible": bool(info.visible),
            "trade_mode": mode,
            "trade_mode_name": TRADE_MODE_NAMES.get(mode, str(mode)),
            "openable": mode in OPENABLE_TRADE_MODES,
            "digits": int(info.digits),
            "stops_level_points": int(info.trade_stops_level),
            "volume_min": float(info.volume_min),
            "volume_step": float(info.volume_step),
            "volume_max": float(info.volume_max),
            "tick_value": float(info.trade_tick_value),
            "tick_size": float(info.trade_tick_size),
            "contract_size": float(info.trade_contract_size),
            "description": getattr(info, "description", ""),
        })
    rows.sort(key=lambda r: (not r["openable"], r["name"]))
    return rows


def _tick_summary(mt5, name: str) -> dict:
    tick = mt5.symbol_info_tick(name)
    if tick is None:
        return {"bid": None, "ask": None, "time_utc": None}
    return {
        "bid": float(tick.bid),
        "ask": float(tick.ask),
        "time_utc": datetime.fromtimestamp(tick.time, tz=timezone.utc).isoformat()
        if getattr(tick, "time", 0)
        else None,
    }


def main() -> int:
    try:
        import MetaTrader5 as mt5
    except ImportError:
        print("MetaTrader5 package not importable; cannot probe.", file=sys.stderr)
        return 1

    _mt5_path = (
        mt5_terminal_resolver.find_mt5_terminal() if mt5_terminal_resolver else None
    )
    initialized = (
        mt5.initialize(path=str(_mt5_path))
        if _mt5_path
        else mt5.initialize()
    )
    if not initialized:
        print(f"MT5 initialize failed: {mt5.last_error()}", file=sys.stderr)
        return 1
    try:
        rows = probe_symbols(mt5)
        # Live tick for each openable symbol (freshness sanity).
        for row in rows:
            if row["openable"]:
                row["last_tick"] = _tick_summary(mt5, row["name"])

        configured = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
        openable = [r for r in rows if r["openable"]]
        summary = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "configured_symbol": configured,
            "configured_openable": any(
                r["name"] == configured and r["openable"] for r in rows
            ),
            "openable_gold_symbols": [r["name"] for r in openable],
            "recommended_symbol": openable[0]["name"] if openable else None,
            "symbols": rows,
        }
        print(json.dumps(summary, indent=2))
    finally:
        mt5.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
