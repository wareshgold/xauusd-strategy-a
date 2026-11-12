"""Offline-only Fati RR1 -> one-time BE+5 pip protection policy.

Pure decision logic only. No MT5 imports, broker calls, order placement,
position closing, TP management, Telegram, or trailing-stop implementation.
The caller must supply the actual fill price, original SL, and favorable
price movement derived from a separately verified quote/market-data contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite


class FatiProtectionAction(str, Enum):
    WAIT_FOR_RR1 = "WAIT_FOR_RR1"
    REQUEST_BE_PLUS_5_SL = "REQUEST_BE_PLUS_5_SL"
    ALREADY_PROTECTED = "ALREADY_PROTECTED"
    ALREADY_CONFIRMED = "ALREADY_CONFIRMED"


@dataclass(frozen=True)
class FatiProtectionPolicy:
    """Explicit symbol pip-size input; never infer XAUUSD pip geometry."""

    pip_size_price: float
    be_offset_pips: float = 5.0

    def __post_init__(self) -> None:
        if not isfinite(self.pip_size_price) or self.pip_size_price <= 0:
            raise ValueError("pip_size_price must be finite and positive")
        if not isfinite(self.be_offset_pips) or self.be_offset_pips <= 0:
            raise ValueError("be_offset_pips must be finite and positive")

    @property
    def be_offset_price(self) -> float:
        return self.pip_size_price * self.be_offset_pips

    @property
    def initial_order_take_profit_price(self) -> float:
        """Explicit no-TP contract for the initial Fati order."""
        return 0.0


def evaluate_fati_protection(
    *,
    policy: FatiProtectionPolicy,
    direction: str,
    actual_fill_price: float,
    initial_sl_price: float,
    current_sl_price: float,
    favorable_move_price: float,
    be_change_confirmed: bool,
) -> tuple[FatiProtectionAction, float | None]:
    """Return a proposed SL price; never mutate state or contact a broker.

    RR1 is measured from actual_fill_price against the immutable initial_sl_price.
    favorable_move_price is a caller-supplied favorable movement in price units;
    this helper intentionally does not choose Bid/Ask, tick, candle, or quote
    semantics. Only a broker-confirmed SL modification should set
    be_change_confirmed=True.

    After a rejection, the caller may re-evaluate only after reconciling the
    broker's current position/SL. This function does not implement retry loops.
    """
    if direction not in {"BUY", "SELL"}:
        raise ValueError("direction must be BUY or SELL")

    values = (
        actual_fill_price,
        initial_sl_price,
        current_sl_price,
        favorable_move_price,
    )
    if any(not isfinite(value) for value in values):
        raise ValueError("all prices and movement must be finite")
    if actual_fill_price <= 0:
        raise ValueError("actual_fill_price must be positive")
    if initial_sl_price <= 0 or current_sl_price < 0:
        raise ValueError("initial SL must be positive and current SL non-negative")
    if favorable_move_price < 0:
        raise ValueError("favorable_move_price must be non-negative")

    if direction == "BUY" and initial_sl_price >= actual_fill_price:
        raise ValueError("BUY initial SL must be below actual fill")
    if direction == "SELL" and initial_sl_price <= actual_fill_price:
        raise ValueError("SELL initial SL must be above actual fill")

    if be_change_confirmed:
        return FatiProtectionAction.ALREADY_CONFIRMED, None

    initial_risk_price = abs(actual_fill_price - initial_sl_price)
    if favorable_move_price < initial_risk_price:
        return FatiProtectionAction.WAIT_FOR_RR1, None

    offset = policy.be_offset_price
    target_sl = (
        actual_fill_price + offset
        if direction == "BUY"
        else actual_fill_price - offset
    )

    # Never loosen an already-better stop. This is not a second modification.
    if current_sl_price > 0:
        if direction == "BUY" and current_sl_price >= target_sl:
            return FatiProtectionAction.ALREADY_PROTECTED, None
        if direction == "SELL" and current_sl_price <= target_sl:
            return FatiProtectionAction.ALREADY_PROTECTED, None

    return FatiProtectionAction.REQUEST_BE_PLUS_5_SL, target_sl
