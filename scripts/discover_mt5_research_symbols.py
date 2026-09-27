"""Discover broker-native MT5 symbols for the SP2L research population.

Research-only: this module never invents broker symbols. It enumerates symbols
from the connected terminal and resolves a requested market symbol only when
there is an exact base-symbol match or a unique normalized variant.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import MetaTrader5 as mt5

from mt5_terminal_resolver import find_mt5_terminal


@dataclass(frozen=True)
class SymbolResolution:
    requested_symbol: str
    broker_symbol: str | None
    status: str
    candidates: tuple[str, ...]


def _base_name(name: str) -> str:
    """Normalize common broker suffixes without guessing a concrete symbol."""
    value = name.upper().strip()
    # Keep the market root before broker decoration such as .ecn, -ECN, m, etc.
    return re.split(r"[._-]", value, maxsplit=1)[0].rstrip("M")


def init_mt5(path: str | None = None) -> str:
    if path and mt5.initialize(path=path):
        return path
    terminal = find_mt5_terminal()
    if terminal is not None and mt5.initialize(path=str(terminal)):
        return str(terminal)
    raise RuntimeError(f"MT5 initialization failed: {mt5.last_error()}")


def discover_symbols(requested_symbols: tuple[str, ...]) -> list[SymbolResolution]:
    all_symbols = mt5.symbols_get() or []
    names = tuple(sorted({s.name for s in all_symbols}))
    results: list[SymbolResolution] = []

    for requested in requested_symbols:
        req = requested.upper().strip()
        exact = tuple(n for n in names if n.upper() == req)
        if len(exact) == 1:
            results.append(SymbolResolution(req, exact[0], "EXACT", exact))
            continue

        variants = tuple(
            n for n in names
            if _base_name(n) == req
        )
        if len(variants) == 1:
            results.append(SymbolResolution(req, variants[0], "UNIQUE_VARIANT", variants))
        elif len(variants) > 1:
            results.append(SymbolResolution(req, None, "AMBIGUOUS", variants))
        else:
            results.append(SymbolResolution(req, None, "NOT_FOUND", ()))

    return results


def require_unique_resolution(requested_symbols: tuple[str, ...]) -> dict[str, str]:
    resolutions = discover_symbols(requested_symbols)
    failures = [
        r for r in resolutions
        if r.status not in {"EXACT", "UNIQUE_VARIANT"}
    ]
    if failures:
        detail = "; ".join(
            f"{r.requested_symbol}={r.status}"
            + (f" candidates={list(r.candidates)}" if r.candidates else "")
            for r in failures
        )
        raise RuntimeError(f"MT5 research symbol resolution failed: {detail}")
    return {r.requested_symbol: r.broker_symbol for r in resolutions if r.broker_symbol}


if __name__ == "__main__":
    requested = (
        "XAUUSD", "USDJPY", "EURJPY", "GBPUSD",
        "GBPJPY", "EURUSD", "USDCHF", "USDCAD",
    )
    terminal = init_mt5()
    try:
        print(f"MT5 terminal: {terminal}")
        print(f"MT5 symbols available: {len(mt5.symbols_get() or ())}")
        for resolution in discover_symbols(requested):
            print(
                f"{resolution.requested_symbol} -> "
                f"{resolution.broker_symbol or '-'} "
                f"[{resolution.status}] "
                f"candidates={list(resolution.candidates)}"
            )
    finally:
        mt5.shutdown()
