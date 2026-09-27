"""Deterministic instrument-unit and transaction-cost helpers.

Research only. Pip size is an accounting/reporting convention and must not
silently change candidate geometry.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PipContract:
    symbol: str
    point: float
    digits: int
    pip_size: float
    pip_label: str
    volume_lots: float
    commission_per_lot_round_turn: float = 0.0
    spread_price: float = 0.0

    def price_to_pips(self, price_move: float) -> float:
        return price_move / self.pip_size

    def pips_to_price(self, pips: float) -> float:
        return pips * self.pip_size

    def gross_pips(self, entry: float, exit: float, direction: str) -> float:
        move = exit - entry if direction == "BUY" else entry - exit
        return self.price_to_pips(move)

    def commission_total(self) -> float:
        return self.commission_per_lot_round_turn * self.volume_lots

    def net_price_equivalent(self, entry: float, exit: float, direction: str) -> float:
        gross = exit - entry if direction == "BUY" else entry - exit
        return gross - self.spread_price - self.commission_total()


def default_pip_size(symbol: str, point: float) -> float:
    """FX: 0.0001, JPY pairs: 0.01; XAU reports broker point as pip-equivalent."""
    upper = symbol.upper().replace(".ECN", "")
    if upper == "XAUUSD":
        return point
    if upper.endswith("JPY"):
        return 0.01
    return 0.0001


def make_contract(
    symbol: str,
    point: float,
    digits: int,
    volume_lots: float,
    *,
    commission_per_lot_round_turn: float = 0.0,
    spread_price: float = 0.0,
) -> PipContract:
    if point <= 0:
        raise ValueError("point must be positive")
    if digits < 0:
        raise ValueError("digits must be non-negative")
    if volume_lots <= 0:
        raise ValueError("volume_lots must be positive")

    return PipContract(
        symbol=symbol,
        point=point,
        digits=digits,
        pip_size=default_pip_size(symbol, point),
        pip_label="pip",
        volume_lots=volume_lots,
        commission_per_lot_round_turn=commission_per_lot_round_turn,
        spread_price=spread_price,
    )
