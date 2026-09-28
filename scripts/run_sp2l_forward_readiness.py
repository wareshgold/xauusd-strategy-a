"""Research-only SP2L V2 forward-test readiness check.

This script never submits orders. It validates the demo terminal, XAUUSD
resolution, broker constraints, runner configuration, session window, and
Telegram configuration before a forward-test session.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

try:
    from mt5_terminal_resolver import find_mt5_terminal
except ImportError:
    from scripts.mt5_terminal_resolver import find_mt5_terminal

try:
    import run_sp2l_author_replica_multi_symbol_forward_test as runner
except ImportError:
    from scripts import run_sp2l_author_replica_multi_symbol_forward_test as runner

try:
    import live_mt5_gateway as gateway
except ImportError:
    from scripts import live_mt5_gateway as gateway


def check(label: str, ok: bool, detail: str) -> dict:
    print(f"[{'PASS' if ok else 'FAIL'}] {label}: {detail}")
    return {"label": label, "ok": ok, "detail": detail}


def main() -> int:
    results = []
    mt5_path = os.getenv("MT5_TERMINAL_PATH") or str(find_mt5_terminal() or "")
    results.append(check("MT5_PATH", bool(mt5_path), mt5_path or "not found"))
    if not mt5_path:
        return 1

    if not mt5.initialize(path=mt5_path):
        results.append(check("MT5_INIT", False, str(mt5.last_error())))
        return 1
    results.append(check("MT5_INIT", True, "connected"))

    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        results.append(check(
            "TERMINAL_CONNECTED",
            bool(terminal and terminal.connected),
            f"connected={getattr(terminal, 'connected', None)} trade_allowed={getattr(terminal, 'trade_allowed', None)}",
        ))
        results.append(check(
            "DEMO_ACCOUNT",
            bool(account and int(account.trade_mode) == 0),
            f"trade_mode={getattr(account, 'trade_mode', None)} server={getattr(account, 'server', None)}",
        ))

        symbol = runner.resolve_symbol("XAUUSD")
        results.append(check("XAUUSD_RESOLUTION", bool(symbol), symbol or "not found"))
        if not symbol:
            return 1

        if not mt5.symbol_select(symbol, True):
            results.append(check("SYMBOL_SELECT", False, str(mt5.last_error())))
            return 1
        info = mt5.symbol_info(symbol)
        tick = mt5.symbol_info_tick(symbol)
        results.append(check(
            "SYMBOL_INFO",
            info is not None,
            f"digits={getattr(info, 'digits', None)} point={getattr(info, 'point', None)} trade_mode={getattr(info, 'trade_mode', None)}",
        ))
        if info is None:
            return 1

        mode = int(info.trade_mode)
        results.append(check(
            "SYMBOL_OPENABLE",
            mode in gateway.OPENABLE_SYMBOL_TRADE_MODES,
            gateway.SYMBOL_TRADE_MODE_NAMES.get(mode, str(mode)),
        ))

        volume = runner._volume_for("XAUUSD")
        minimum = float(getattr(info, "volume_min", 0.0) or 0.0)
        maximum = float(getattr(info, "volume_max", 0.0) or 0.0)
        step = float(getattr(info, "volume_step", 0.0) or 0.0)
        volume_ok = volume >= minimum and (maximum <= 0 or volume <= maximum)
        if volume_ok and step > 0 and minimum > 0:
            steps = round((volume - minimum) / step)
            volume_ok = abs(minimum + steps * step - volume) <= max(step * 1e-6, 1e-9)
        results.append(check(
            "VOLUME",
            volume_ok,
            f"requested={volume} min={minimum} max={maximum} step={step}",
        ))

        results.append(check(
            "TICK",
            tick is not None and float(getattr(tick, "bid", 0.0)) > 0 and float(getattr(tick, "ask", 0.0)) > 0,
            f"bid={getattr(tick, 'bid', None)} ask={getattr(tick, 'ask', None)}",
        ))

        results.append(check(
            "V2_GEOMETRY_CONFIG",
            runner.P_GAP_PRICE == 1.0 and runner.SPIKE_MULTIPLIER == 1.5
            and runner.MAX_SL_DISTANCE == 10.0 and runner.TP_R == 1.0,
            f"pGap={runner.P_GAP_PRICE} spike={runner.SPIKE_MULTIPLIER} maxSL={runner.MAX_SL_DISTANCE} tpR={runner.TP_R}",
        ))
        results.append(check(
            "FORWARD_ORDER_MODE",
            runner.ORDER_MODE == "PENDING_LIMIT_RESEARCH",
            runner.ORDER_MODE,
        ))
        results.append(check(
            "SESSION_WINDOW",
            runner.SESSION_START_LONDON == "08:00" and runner.SESSION_END_NEW_YORK == "17:00",
            f"London {runner.SESSION_START_LONDON} -> New York {runner.SESSION_END_NEW_YORK}",
        ))
        results.append(check(
            "F13_2X",
            True,
            "relation-only; not executed because lifecycle semantics remain unresolved",
        ))

        telegram_ok = bool(os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"))
        results.append(check(
            "TELEGRAM_CONFIG",
            True,
            "configured" if telegram_ok else "optional; notifications disabled",
        ))

        demo_execution_flags = (
            os.getenv("LIVE_TRADING_ENABLE", "false").lower() == "true"
            and os.getenv("ALLOW_REAL_EXECUTION", "false").lower() == "true"
        )
        results.append(check(
            "DEMO_EXECUTION_FLAGS",
            demo_execution_flags,
            "both enabled for DEMO order submission" if demo_execution_flags
            else "not enabled; runner remains DRY-RUN and submits no broker orders",
        ))

        failures = [x for x in results if not x["ok"]]
        print("")
        print("SP2L V2 FORWARD READINESS")
        print(f"checked_utc={datetime.now(timezone.utc).isoformat()}")
        print(f"status={'READY_FOR_DEMO_FORWARD' if not failures else 'NOT_READY'}")
        print(f"checks={len(results)} failures={len(failures)}")
        print("NO ORDERS WERE SUBMITTED.")
        return 0 if not failures else 2
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
