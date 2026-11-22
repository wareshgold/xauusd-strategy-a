"""Fail-closed identity and execution guards for the SP2L V3.1 DEMO runner.

This module is infrastructure-only. It does not define or modify strategy geometry.
"""
from __future__ import annotations

import os
from pathlib import PureWindowsPath

EXPECTED_LOGIN = 853018
EXPECTED_SERVER = "OtetGroup-MT5"
EXPECTED_TERMINAL_ROOT = PureWindowsPath(r"C:\\Program Files\\Otet Group MT5 Terminal")
EXPECTED_SYMBOL = "XAUUSD.ecn"
OPENABLE_SYMBOL_TRADE_MODES = {1, 2, 4}


def _norm_windows_path(value: str) -> str:
    return str(PureWindowsPath(str(value or "").strip())).casefold().rstrip("\\")


def validate_mt5_identity(mt5, *, symbol: str | None = None, require_execution: bool = False) -> None:
    """Raise RuntimeError unless MT5 is attached to the explicitly approved DEMO."""
    if require_execution:
        if os.getenv("LIVE_TRADING_ENABLE", "false").strip().lower() != "true":
            raise RuntimeError("EXECUTION_GUARD: LIVE_TRADING_ENABLE is not true")
        if os.getenv("ALLOW_REAL_EXECUTION", "false").strip().lower() != "true":
            raise RuntimeError("EXECUTION_GUARD: ALLOW_REAL_EXECUTION is not true")

    terminal = mt5.terminal_info()
    if terminal is None:
        raise RuntimeError("EXECUTION_GUARD: terminal_info unavailable")
    actual_root = getattr(terminal, "path", None)
    if _norm_windows_path(actual_root) != _norm_windows_path(str(EXPECTED_TERMINAL_ROOT)):
        raise RuntimeError(f"EXECUTION_GUARD: unexpected terminal path: {actual_root!r}")

    account = mt5.account_info()
    if account is None:
        raise RuntimeError("EXECUTION_GUARD: account_info unavailable")
    if int(getattr(account, "login", -1)) != EXPECTED_LOGIN:
        raise RuntimeError("EXECUTION_GUARD: unexpected account login")
    if str(getattr(account, "server", "")) != EXPECTED_SERVER:
        raise RuntimeError("EXECUTION_GUARD: unexpected account server")
    if int(getattr(account, "trade_mode", -1)) != 0:
        raise RuntimeError("EXECUTION_GUARD: DEMO account required")

    if symbol is not None:
        if symbol != EXPECTED_SYMBOL:
            raise RuntimeError(f"EXECUTION_GUARD: unexpected symbol: {symbol!r}")
        info = mt5.symbol_info(symbol)
        mode = int(getattr(info, "trade_mode", -1)) if info is not None else -1
        if mode not in OPENABLE_SYMBOL_TRADE_MODES:
            raise RuntimeError(f"EXECUTION_GUARD: symbol not openable (trade_mode={mode})")
