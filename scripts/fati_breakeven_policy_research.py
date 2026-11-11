"""Research-only, offline breakeven arithmetic and decision fixtures for Fati.

This module does not connect to MT5, send/modify orders, or define canonical
SP2L geometry. Broker execution, tick-size normalization, and the source of
favorable_move_price remain outside this pure policy helper.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BreakevenAction(str, Enum):
    WAIT = "WAIT"
    REQUEST_SL_CHANGE = "REQUEST_SL_CHANGE"
    ALREADY_PROTECTED = "ALREADY_PROTECTED"
    ALREADY_CONFIRMED = "ALREADY_CONFIRMED"


@dataclass(frozen=True)
class BreakevenModel:
    """Explicit assumptions for one 0.01-lot XAUUSD research fixture."""

    pip_size_price: float = 0.10
    contract_size: float = 100.0
    volume_lots: float = 0.01
    commission_per_side_usd: float = 0.05
    activation_pips: float = 5.0

    def __post_init__(self) -> None:
        values = (
            self.pip_size_price,
            self.contract_size,
            self.volume_lots,
            self.commission_per_side_usd,
            self.activation_pips,
        )
        if any(value <= 0 for value in values):
            raise ValueError("all model inputs must be positive and finite")
        if any(value != value or value in (float("inf"), float("-inf")) for value in values):
            raise ValueError("all model inputs must be finite")

    @property
    def value_per_pip_usd(self) -> float:
        return self.contract_size * self.volume_lots * self.pip_size_price

    @property
    def round_trip_commission_usd(self) -> float:
        return 2.0 * self.commission_per_side_usd

    @property
    def commission_offset_pips(self) -> float:
        return self.round_trip_commission_usd / self.value_per_pip_usd

    @property
    def commission_offset_price(self) -> float:
        return self.commission_offset_pips * self.pip_size_price

    @property
    def activation_move_price(self) -> float:
        return self.activation_pips * self.pip_size_price

    def desired_sl(self, direction: str, entry_price: float) -> float:
        if direction == "BUY":
            return entry_price + self.commission_offset_price
        if direction == "SELL":
            return entry_price - self.commission_offset_price
        raise ValueError("direction must be BUY or SELL")


def evaluate_breakeven(
    *,
    model: BreakevenModel,
    direction: str,
    entry_price: float,
    current_sl: float,
    favorable_move_price: float,
    be_confirmed: bool,
) -> tuple[BreakevenAction, float | None]:
    """Return a proposed SL only; never call a broker or mutate position state.

    favorable_move_price is deliberately supplied by the caller. This module
    does not decide whether activation is measured from Bid/Ask, ticks, or bars.
    A broker rejection must leave be_confirmed=False, allowing a controlled
    retry by an external manager. Only broker-confirmed success should set it.
    """
    if direction not in {"BUY", "SELL"}:
        raise ValueError("direction must be BUY or SELL")
    if entry_price <= 0 or favorable_move_price < 0:
        raise ValueError("entry_price must be positive and favorable move non-negative")
    if be_confirmed:
        return BreakevenAction.ALREADY_CONFIRMED, None
    if favorable_move_price < model.activation_move_price:
        return BreakevenAction.WAIT, None

    target_sl = model.desired_sl(direction, entry_price)
    if current_sl > 0:
        if direction == "BUY" and current_sl >= target_sl:
            return BreakevenAction.ALREADY_PROTECTED, None
        if direction == "SELL" and current_sl <= target_sl:
            return BreakevenAction.ALREADY_PROTECTED, None
    return BreakevenAction.REQUEST_SL_CHANGE, target_sl
