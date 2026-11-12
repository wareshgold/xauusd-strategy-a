"""Offline-only Fati adapter orchestration primitives.

No MT5 imports, network calls, broker actions, Telegram, or primary Runner imports.
This module coordinates policy decisions and broker-confirmation state only.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite

from scripts.fati_rr1_be5_no_tp_policy_research import (
    FatiProtectionAction,
    FatiProtectionPolicy,
    evaluate_fati_protection,
)


class FatiAdapterState(str, Enum):
    SIGNAL_ACCEPTED = "SIGNAL_ACCEPTED"
    ORDER_SUBMITTED = "ORDER_SUBMITTED"
    ORDER_CONFIRMED = "ORDER_CONFIRMED"
    FILL_PENDING = "FILL_PENDING"
    POSITION_RECONCILED = "POSITION_RECONCILED"
    WAITING_FOR_RR1 = "WAITING_FOR_RR1"
    BE_REQUEST_PENDING = "BE_REQUEST_PENDING"
    BE_CONFIRMED = "BE_CONFIRMED"
    MANUAL_MANAGEMENT = "MANUAL_MANAGEMENT"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"
    HALTED = "HALTED"


@dataclass(frozen=True)
class FatiAccountProfile:
    """Account-specific fields; values must come from an approved source.

    No defaults are provided intentionally. This profile is a validation
    contract, not a source of broker specifications.
    """
    account_server: str
    account_type: str
    account_currency: str
    symbol: str
    digits: int
    point: float
    tick_size: float
    tick_value: float
    contract_size: float
    volume_min: float
    volume_max: float
    volume_step: float
    stops_level_points: int
    freeze_level_points: int
    filling_mode: str
    commission_amount: float
    commission_currency: str
    commission_convention: str
    pip_size_price: float
    rr1_quote_semantics: str
    rr1_sampling_rule: str

    def validate(self) -> None:
        strings = (
            self.account_server, self.account_type, self.account_currency,
            self.symbol, self.filling_mode, self.commission_currency,
            self.commission_convention, self.rr1_quote_semantics,
            self.rr1_sampling_rule,
        )
        if any(not isinstance(value, str) or not value.strip() for value in strings):
            raise ValueError("all account profile text fields must be explicit")
        if not isinstance(self.digits, int) or self.digits < 0:
            raise ValueError("digits must be a non-negative integer")
        if not isinstance(self.stops_level_points, int) or self.stops_level_points < 0:
            raise ValueError("stops_level_points must be a non-negative integer")
        if not isinstance(self.freeze_level_points, int) or self.freeze_level_points < 0:
            raise ValueError("freeze_level_points must be a non-negative integer")
        positive = (
            self.point, self.tick_size, self.tick_value, self.contract_size,
            self.volume_min, self.volume_max, self.volume_step, self.pip_size_price,
        )
        if any(not isfinite(value) or value <= 0 for value in positive):
            raise ValueError("price, contract, volume and pip fields must be finite and positive")
        if not isfinite(self.commission_amount) or self.commission_amount < 0:
            raise ValueError("commission_amount must be finite and non-negative")
        if self.volume_min > self.volume_max:
            raise ValueError("volume_min cannot exceed volume_max")
        if self.volume_step > self.volume_max:
            raise ValueError("volume_step cannot exceed volume_max")


@dataclass(frozen=True)
class ApprovedSignal:
    signal_id: str
    direction: str
    symbol: str
    volume: float
    entry_price: float
    initial_sl_price: float

    def validate(self, profile: FatiAccountProfile) -> None:
        if not self.signal_id.strip():
            raise ValueError("signal_id is required")
        if self.direction not in {"BUY", "SELL"}:
            raise ValueError("direction must be BUY or SELL")
        if self.symbol != profile.symbol:
            raise ValueError("signal symbol does not match the approved Fati profile")
        if not isfinite(self.volume) or self.volume <= 0:
            raise ValueError("volume must be finite and positive")
        if not isfinite(self.entry_price) or self.entry_price <= 0:
            raise ValueError("entry_price must be finite and positive")
        if not isfinite(self.initial_sl_price) or self.initial_sl_price <= 0:
            raise ValueError("initial_sl_price must be finite and positive")
        if self.direction == "BUY" and self.initial_sl_price >= self.entry_price:
            raise ValueError("BUY initial SL must be below entry")
        if self.direction == "SELL" and self.initial_sl_price <= self.entry_price:
            raise ValueError("SELL initial SL must be above entry")
        steps = self.volume / profile.volume_step
        if self.volume < profile.volume_min or self.volume > profile.volume_max:
            raise ValueError("volume outside approved profile bounds")
        if abs(steps - round(steps)) > 1e-8:
            raise ValueError("volume is not aligned to the approved volume step")


@dataclass(frozen=True)
class InitialOrderIntent:
    signal_id: str
    symbol: str
    direction: str
    volume: float
    requested_entry: float
    initial_sl: float
    take_profit: float = 0.0


def build_initial_order_intent(
    signal: ApprovedSignal,
    profile: FatiAccountProfile,
) -> InitialOrderIntent:
    """Build an inert order intent; it does not submit anything."""
    profile.validate()
    signal.validate(profile)
    return InitialOrderIntent(
        signal_id=signal.signal_id,
        symbol=signal.symbol,
        direction=signal.direction,
        volume=signal.volume,
        requested_entry=signal.entry_price,
        initial_sl=signal.initial_sl_price,
        take_profit=0.0,
    )


@dataclass(frozen=True)
class QuoteObservation:
    favorable_move_price: float
    semantics_id: str
    sampling_rule_id: str
    observed_at: str


@dataclass(frozen=True)
class ProtectionDecision:
    action: FatiProtectionAction
    proposed_sl_price: float | None
    next_state: FatiAdapterState


def evaluate_protection(
    *,
    profile: FatiAccountProfile,
    direction: str,
    actual_fill_price: float,
    initial_sl_price: float,
    current_sl_price: float,
    quote: QuoteObservation,
    broker_confirmed: bool,
) -> ProtectionDecision:
    """Evaluate a supplied observation; does not select quote semantics or call a broker."""
    profile.validate()
    if quote.semantics_id != profile.rr1_quote_semantics:
        raise ValueError("quote semantics do not match the approved profile")
    if quote.sampling_rule_id != profile.rr1_sampling_rule:
        raise ValueError("quote sampling rule does not match the approved profile")
    if not quote.observed_at.strip():
        raise ValueError("quote observation timestamp is required")

    action, target = evaluate_fati_protection(
        policy=FatiProtectionPolicy(pip_size_price=profile.pip_size_price),
        direction=direction,
        actual_fill_price=actual_fill_price,
        initial_sl_price=initial_sl_price,
        current_sl_price=current_sl_price,
        favorable_move_price=quote.favorable_move_price,
        be_change_confirmed=broker_confirmed,
    )
    if action == FatiProtectionAction.REQUEST_BE_PLUS_5_SL:
        state = FatiAdapterState.BE_REQUEST_PENDING
    elif action == FatiProtectionAction.ALREADY_CONFIRMED:
        state = FatiAdapterState.BE_CONFIRMED
    elif action == FatiProtectionAction.ALREADY_PROTECTED:
        state = FatiAdapterState.MANUAL_MANAGEMENT
    else:
        state = FatiAdapterState.WAITING_FOR_RR1
    return ProtectionDecision(action, target, state)


def reconcile_sl_modification(
    *,
    requested_sl_price: float,
    broker_sl_price: float | None,
    broker_result: str,
    tolerance: float,
) -> FatiAdapterState:
    """Classify a broker result; never retries or assumes success."""
    if not isfinite(requested_sl_price) or requested_sl_price <= 0:
        raise ValueError("requested_sl_price must be finite and positive")
    if not isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and non-negative")
    if broker_result == "CONFIRMED":
        if broker_sl_price is None or not isfinite(broker_sl_price):
            return FatiAdapterState.RECONCILIATION_REQUIRED
        if abs(broker_sl_price - requested_sl_price) <= tolerance:
            return FatiAdapterState.BE_CONFIRMED
        return FatiAdapterState.RECONCILIATION_REQUIRED
    if broker_result in {"REJECTED", "UNKNOWN", "TIMEOUT"}:
        return FatiAdapterState.RECONCILIATION_REQUIRED
    raise ValueError("broker_result must be CONFIRMED, REJECTED, UNKNOWN, or TIMEOUT")
