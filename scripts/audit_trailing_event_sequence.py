"""Offline diagnostics for M1 bar/position event ordering; no trading actions.

This module labels timestamp relationships in supplied fixtures. It does not define
canonical SP2L geometry, recommend a stop update, or emulate MT5 execution.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal


def utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"Timestamp must include an offset: {value}")
    return dt.astimezone(timezone.utc)


def dec(value: str | int | float | Decimal) -> Decimal:
    return Decimal(str(value))


def audit_bar_event_order(
    *,
    entry_time_utc: str,
    decision_time_utc: str,
    bar_start_utc: str,
    bar_low_time_utc: str,
    bar_low: str | float,
    entry_price: str | float,
    direction: str,
    activation_distance: str | float,
    current_sl: str | float,
    trail_distance: str | float,
    current_bid: str | float,
    current_ask: str | float,
    min_broker_distance: str | float = "0",
) -> dict:
    """Report chronology and observed arithmetic/guards for one synthetic decision."""
    entry_time = utc(entry_time_utc)
    decision_time = utc(decision_time_utc)
    bar_start = utc(bar_start_utc)
    bar_end = bar_start + timedelta(minutes=1)
    low_time = utc(bar_low_time_utc)
    direction = direction.upper()
    if direction not in {"BUY", "SELL"}:
        raise ValueError("direction must be BUY or SELL")
    if not (bar_start <= low_time < bar_end):
        raise ValueError("bar-low timestamp is outside the M1 bar")
    if decision_time < bar_end:
        raise ValueError("decision timestamp precedes completion of the supplied M1 bar")
    if decision_time < entry_time:
        raise ValueError("decision timestamp precedes position entry")

    entry, low = dec(entry_price), dec(bar_low)
    activation, trail = dec(activation_distance), dec(trail_distance)
    old_sl, bid, ask, broker = map(dec, (current_sl, current_bid, current_ask, min_broker_distance))
    if direction == "SELL":
        favorable = entry - low
        candidate = low + trail
        activation_pass = favorable >= activation
        improves_existing_sl = old_sl <= 0 or candidate < old_sl
        broker_guard_pass = candidate > ask + broker
    else:
        favorable = dec(current_bid) - entry
        # BUY candidate uses a supplied bar high in the live implementation, but this
        # diagnostic accepts bar_low only; deliberately do not synthesize BUY geometry.
        candidate = None
        activation_pass = favorable >= activation
        improves_existing_sl = None
        broker_guard_pass = None

    if entry_time >= bar_end:
        bar_relation = "BAR_COMPLETED_BEFORE_ENTRY"
    elif low_time < entry_time:
        bar_relation = "ENTRY_BAR_LOW_PRE_ENTRY"
    else:
        bar_relation = "ENTRY_BAR_LOW_AT_OR_AFTER_ENTRY"

    return {
        "research_only": True,
        "canonical": False,
        "direction": direction,
        "bar_start_utc": bar_start.isoformat().replace("+00:00", "Z"),
        "bar_end_utc_exclusive": bar_end.isoformat().replace("+00:00", "Z"),
        "entry_time_utc": entry_time.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "decision_time_utc": decision_time.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "bar_low_time_utc": low_time.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "bar_completed_at_decision": bar_end <= decision_time,
        "low_observed_before_entry": low_time < entry_time,
        "low_observed_before_decision": low_time <= decision_time,
        "bar_relation": bar_relation,
        "sell_full_bar_favorable_move": str(favorable) if direction == "SELL" else None,
        "activation_pass_from_supplied_observation": activation_pass,
        "candidate_sl_from_supplied_low": str(candidate) if candidate is not None else None,
        "candidate_improves_existing_sl": improves_existing_sl,
        "sell_ask_distance_guard_pass": broker_guard_pass,
        "decision_time_after_entry": decision_time >= entry_time,
        "limitations": [
            "Timestamp/arithmetic diagnostic only; not a complete runner simulation.",
            "For BUY, favorable movement uses current Bid and does not derive a stop candidate.",
            "No tick coverage, polling cadence, order_send result, or broker state is inferred.",
            "No canonical Strategy A geometry or execution rule is established.",
        ],
    }
