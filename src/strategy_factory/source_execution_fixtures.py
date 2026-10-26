"""Source-pinned execution-path fixtures for RR2/TRAIL4 research only.

These functions model pre-send guards visible in the pinned Python source. They
do not submit orders, predict broker acceptance, infer fills, or define
canonical SP2L semantics. A guard passing means only that the source would
proceed to the next code branch under the supplied inputs.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SourcePathStatus(str, Enum):
    REJECTED_BY_SOURCE_GUARD = "REJECTED_BY_SOURCE_GUARD"
    REQUEST_ELIGIBLE = "REQUEST_ELIGIBLE"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class PendingLimitInputs:
    direction: str
    entry: float
    sl: float
    tp: float
    bid: float
    ask: float
    stops_level_points: int
    point: float


@dataclass(frozen=True)
class SourcePathResult:
    status: SourcePathStatus
    reason: str
    order_type: str | None = None
    min_stop_distance: float | None = None


def evaluate_pending_limit_preflight(inputs: PendingLimitInputs) -> SourcePathResult:
    """Mirror the gateway's PENDING_LIMIT_RESEARCH pre-send guards."""
    vals = (inputs.entry, inputs.sl, inputs.tp, inputs.bid, inputs.ask, inputs.point)
    if any(v != v or v in (float("inf"), float("-inf")) for v in vals):
        return SourcePathResult(SourcePathStatus.UNRESOLVED, "NON_FINITE_INPUT")
    if inputs.direction not in {"BUY", "SELL"}:
        return SourcePathResult(SourcePathStatus.UNRESOLVED, "UNKNOWN_DIRECTION")
    if inputs.stops_level_points < 0 or inputs.point < 0:
        return SourcePathResult(SourcePathStatus.UNRESOLVED, "INVALID_BROKER_CONSTRAINT")
    if inputs.bid <= 0 or inputs.ask <= 0 or inputs.bid > inputs.ask:
        return SourcePathResult(SourcePathStatus.UNRESOLVED, "INVALID_QUOTE")

    if inputs.direction == "BUY":
        if inputs.entry >= inputs.ask:
            return SourcePathResult(
                SourcePathStatus.REJECTED_BY_SOURCE_GUARD,
                "LIMIT_ENTRY_NOT_PLACEABLE_AT_CURRENT_MARKET",
                "BUY_LIMIT",
            )
        sl_distance = inputs.entry - inputs.sl
        tp_distance = inputs.tp - inputs.entry
        order_type = "BUY_LIMIT"
    else:
        if inputs.entry <= inputs.bid:
            return SourcePathResult(
                SourcePathStatus.REJECTED_BY_SOURCE_GUARD,
                "LIMIT_ENTRY_NOT_PLACEABLE_AT_CURRENT_MARKET",
                "SELL_LIMIT",
            )
        sl_distance = inputs.sl - inputs.entry
        tp_distance = inputs.entry - inputs.tp
        order_type = "SELL_LIMIT"

    if sl_distance <= 0 or tp_distance <= 0:
        return SourcePathResult(
            SourcePathStatus.REJECTED_BY_SOURCE_GUARD,
            "INVALID_STOPS_AT_THEORETICAL_ENTRY",
            order_type,
        )
    min_distance = inputs.stops_level_points * inputs.point
    if min_distance > 0 and (
        sl_distance < min_distance or tp_distance < min_distance
    ):
        return SourcePathResult(
            SourcePathStatus.REJECTED_BY_SOURCE_GUARD,
            "BELOW_BROKER_MIN_STOP_DISTANCE",
            order_type,
            min_distance,
        )
    return SourcePathResult(
        SourcePathStatus.REQUEST_ELIGIBLE,
        "PRE_SEND_GUARDS_PASSED_BROKER_RESULT_UNRESOLVED",
        order_type,
        min_distance,
    )


@dataclass(frozen=True)
class TrailingInputs:
    direction: str
    entry: float
    old_sl: float
    new_sl: float
    tp: float
    favorable_extreme: float
    bid: float
    ask: float
    min_distance: float
    trail_distance: float


def evaluate_trailing_preflight(inputs: TrailingInputs) -> SourcePathResult:
    """Mirror RR2/TRAIL4's pre-order_send trailing guards only."""
    vals = (
        inputs.entry, inputs.old_sl, inputs.new_sl, inputs.tp,
        inputs.favorable_extreme, inputs.bid, inputs.ask,
        inputs.min_distance, inputs.trail_distance,
    )
    if any(v != v or v in (float("inf"), float("-inf")) for v in vals):
        return SourcePathResult(SourcePathStatus.UNRESOLVED, "NON_FINITE_INPUT")
    if inputs.direction not in {"BUY", "SELL"}:
        return SourcePathResult(SourcePathStatus.UNRESOLVED, "UNKNOWN_DIRECTION")
    if inputs.entry <= 0 or inputs.new_sl <= 0 or inputs.trail_distance < 0 or inputs.min_distance < 0:
        return SourcePathResult(SourcePathStatus.UNRESOLVED, "INVALID_INPUT")
    if inputs.direction == "BUY":
        if inputs.favorable_extreme - inputs.entry < inputs.trail_distance:
            return SourcePathResult(SourcePathStatus.REJECTED_BY_SOURCE_GUARD, "FAVORABLE_MOVE_BELOW_TRAIL_DISTANCE")
        if inputs.new_sl <= inputs.old_sl:
            return SourcePathResult(SourcePathStatus.REJECTED_BY_SOURCE_GUARD, "BUY_SL_NOT_IMPROVED")
        if inputs.new_sl >= inputs.favorable_extreme:
            return SourcePathResult(SourcePathStatus.REJECTED_BY_SOURCE_GUARD, "BUY_SL_NOT_BELOW_BAR_HIGH")
        if inputs.bid <= 0 or inputs.new_sl >= inputs.bid - inputs.min_distance:
            return SourcePathResult(SourcePathStatus.REJECTED_BY_SOURCE_GUARD, "BUY_SL_TOO_CLOSE_TO_BID")
    else:
        if inputs.entry - inputs.favorable_extreme < inputs.trail_distance:
            return SourcePathResult(SourcePathStatus.REJECTED_BY_SOURCE_GUARD, "FAVORABLE_MOVE_BELOW_TRAIL_DISTANCE")
        if inputs.old_sl > 0 and inputs.new_sl >= inputs.old_sl:
            return SourcePathResult(SourcePathStatus.REJECTED_BY_SOURCE_GUARD, "SELL_SL_NOT_IMPROVED")
        if inputs.new_sl <= inputs.favorable_extreme:
            return SourcePathResult(SourcePathStatus.REJECTED_BY_SOURCE_GUARD, "SELL_SL_NOT_ABOVE_BAR_LOW")
        if inputs.ask <= 0 or inputs.new_sl <= inputs.ask + inputs.min_distance:
            return SourcePathResult(SourcePathStatus.REJECTED_BY_SOURCE_GUARD, "SELL_SL_TOO_CLOSE_TO_ASK")
    return SourcePathResult(
        SourcePathStatus.REQUEST_ELIGIBLE,
        "SLTP_REQUEST_ELIGIBLE_BROKER_RESULT_UNRESOLVED",
    )
