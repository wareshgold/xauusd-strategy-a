from __future__ import annotations

"""Research-only X2 continuation/pyramiding replay. No MT5 dependencies."""

from datetime import datetime, timezone
from typing import Any, Sequence
import math


def _side_price(direction: str, buy_value: float, sell_value: float) -> float:
    return buy_value if direction == "BUY" else sell_value


def _hit_stop(bar: dict[str, Any], direction: str, stop: float) -> bool:
    return float(bar["low"]) <= stop if direction == "BUY" else float(bar["high"]) >= stop


def _favorable(bar: dict[str, Any], direction: str, entry: float) -> float:
    return float(bar["high"]) - entry if direction == "BUY" else entry - float(bar["low"])


def _stop_valid(stop: float, price: float, direction: str) -> bool:
    return stop < price if direction == "BUY" else stop > price


def _remaining_risk(entry: float, stop: float, direction: str, volume: float, contract: float) -> float:
    adverse_distance = entry - stop if direction == "BUY" else stop - entry
    return max(0.0, adverse_distance) * volume * contract


def _iso(ts: int) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).isoformat()


def replay_x2_signal(
    candidate: dict[str, Any],
    bars: Sequence[dict[str, Any]],
    *,
    activation_price: float,
    trail_distance_price: float,
    threshold_r: float,
    pullback_r: float = 0.25,
    volume: float = 0.01,
    contract_size: float = 100.0,
    risk_tolerance: float = 1e-9,
) -> dict[str, Any]:
    """Replay X1 plus at most one X2, using completed M1 bars and next-open X2 fills.

    Candidate keys: entry_idx, theoretical_entry, sl, risk, direction, trigger_time.
    Bars keys: time, open, high, low, close.
    """
    direction = str(candidate["direction"]).upper()
    if direction not in {"BUY", "SELL"}:
        raise ValueError("direction must be BUY or SELL")
    vals = (activation_price, trail_distance_price, threshold_r, pullback_r, volume, contract_size)
    if not all(math.isfinite(float(x)) for x in vals) or min(activation_price, trail_distance_price, threshold_r, pullback_r, volume, contract_size) <= 0:
        raise ValueError("all experiment parameters must be finite and positive")
    idx = int(candidate["entry_idx"])
    entry, initial_sl, risk = float(candidate["theoretical_entry"]), float(candidate["sl"]), float(candidate["risk"])
    if risk <= 0 or not 0 <= idx < len(bars):
        raise ValueError("invalid candidate risk or entry index")
    if not _stop_valid(initial_sl, entry, direction):
        raise ValueError("X1 initial stop is on the invalid side")
    if abs(abs(entry - initial_sl) - risk) > max(1e-8, risk * 1e-6):
        raise ValueError("X1 frozen risk does not match entry-to-stop distance")

    x1_sl, x1_origin = initial_sl, "SL"
    x1_exit, x1_exit_time, x1_reason = None, None, "OPEN_OR_UNRESOLVED"
    x1_ambiguous = False
    x1_updates = 0
    x1_max_fav = 0.0

    state = "WAIT_THRESHOLD"
    best_favorable = None
    pullback_extreme = None
    x2_pending_idx = None
    x2_status = "NOT_TRIGGERED"
    x2_skip_reason = None
    x2_entry = x2_sl = None
    x2_exit = x2_exit_time = None
    x2_reason = "NOT_OPENED"
    x2_ambiguous = False
    x2_updates = 0
    x2_entry_idx = None
    x2_bars_held = 0
    x2_origin = "SL"
    x2_max_fav = 0.0
    x2_admission_risk = 0.0
    max_combined_open_risk = risk * volume * contract_size
    opportunities = 0

    previous_time = int(bars[idx]["time"])
    for bi in range(idx + 1, len(bars)):
        bar = bars[bi]
        now = int(bar["time"])
        if now - previous_time != 60:
            if x1_exit is None:
                x1_ambiguous, x1_reason, x1_exit_time = True, "M1_GAP_WHILE_OPEN", now
            if x2_entry is not None and x2_exit is None:
                x2_ambiguous, x2_reason, x2_exit_time = True, "M1_GAP_WHILE_OPEN", now
            if state not in {"DONE", "CANCELLED"}:
                x2_status, x2_skip_reason, state = "AMBIGUOUS", "M1_GAP_DURING_SETUP", "CANCELLED"
            break
        previous_time = now
        high, low, close, opn = (float(bar[k]) for k in ("high", "low", "close", "open"))

        # Check stops already active at the start of this completed bar.
        x1_hit = x1_exit is None and _hit_stop(bar, direction, x1_sl)
        x2_hit = x2_entry is not None and x2_exit is None and _hit_stop(bar, direction, x2_sl)
        if x1_hit:
            x1_exit, x1_exit_time = x1_sl, now
            x1_reason = f"{x1_origin}_SL" if x1_origin != "SL" else "SL"
        if x2_hit:
            x2_exit, x2_exit_time = x2_sl, now
            x2_reason = f"{x2_origin}_SL" if x2_origin != "SL" else "SL"
        if x1_hit and state not in {"DONE", "CANCELLED"}:
            # An exit on a potential confirmation bar cannot be ordered against
            # a close-confirmation using OHLC alone.
            if state == "PULLBACK_ARMED" and (
                (direction == "BUY" and close > float(bars[bi - 1]["high"])) or
                (direction == "SELL" and close < float(bars[bi - 1]["low"]))
            ):
                x2_status, x2_skip_reason = "AMBIGUOUS", "X1_EXIT_AND_X2_CONFIRMATION_SAME_BAR"
            else:
                x2_status, x2_skip_reason = "CANCELLED", "X1_EXIT_BEFORE_X2"
            state = "CANCELLED"

        if x2_entry is not None and x2_exit is None:
            x2_bars_held += 1
            x2_fav = _favorable(bar, direction, x2_entry)
            x2_max_fav = max(x2_max_fav, x2_fav)
            if bi > int(x2_entry_idx) and x2_fav >= activation_price:
                proposed_x2 = high - trail_distance_price if direction == "BUY" else low + trail_distance_price
                if _stop_valid(proposed_x2, close, direction):
                    improved_x2 = proposed_x2 > x2_sl if direction == "BUY" else proposed_x2 < x2_sl
                    if improved_x2:
                        x2_sl, x2_origin, x2_updates = proposed_x2, "TRAIL", x2_updates + 1
        if x1_exit is not None and x2_entry is None:
            break
        if x1_exit is not None and x2_exit is not None:
            break

        # A next-open X2 fill is pending from the prior completed bar.
        if x2_pending_idx == bi and state == "PENDING_FILL":
            if not _stop_valid(float(pullback_extreme), opn, direction):
                x2_status, x2_skip_reason, state = "SKIPPED", "NEXT_OPEN_THROUGH_X2_STOP", "CANCELLED"
            else:
                x2_entry, x2_sl = opn, float(pullback_extreme)
                x2_entry_idx = bi
                x2_risk = abs(x2_entry - x2_sl) * volume * contract_size
                x1_open_risk = _remaining_risk(entry, x1_sl, direction, volume, contract_size) if x1_exit is None else 0.0
                initial_budget = risk * volume * contract_size
                residual = max(0.0, initial_budget - x1_open_risk)
                x2_admission_risk = x2_risk
                if x2_risk > residual + risk_tolerance:
                    x2_status, x2_skip_reason, state = "SKIPPED", "X2_SKIPPED_RISK_BUDGET", "CANCELLED"
                    x2_entry = x2_sl = None
                else:
                    x2_status, state = "OPENED", "DONE"
                    # The X2 fill occurs at this bar's open; subsequent range
                    # on this same bar can hit its initial stop, but no trail
                    # update is calculated from this entry bar.
                    if _hit_stop(bar, direction, x2_sl):
                        x2_exit, x2_exit_time, x2_reason = x2_sl, now, "SL_ON_ENTRY_BAR"
            x2_pending_idx = None

        # Manage X1 trailing after stop checks; updated stop starts next bar.
        if x1_exit is None:
            fav = _favorable(bar, direction, entry)
            x1_max_fav = max(x1_max_fav, fav)
            if fav >= activation_price:
                proposed = high - trail_distance_price if direction == "BUY" else low + trail_distance_price
                if _stop_valid(proposed, close, direction):
                    improved = proposed > x1_sl if direction == "BUY" else proposed < x1_sl
                    if improved:
                        x1_sl, x1_origin, x1_updates = proposed, "TRAIL", x1_updates + 1

        # Trigger state machine. Each transition is based on a completed bar.
        if state == "WAIT_THRESHOLD" and x1_exit is None:
            if _favorable(bar, direction, entry) >= threshold_r * risk:
                state = "WAIT_PULLBACK"
                best_favorable = high if direction == "BUY" else low
        elif state == "WAIT_PULLBACK" and x1_exit is None:
            best_favorable = max(best_favorable, high) if direction == "BUY" else min(best_favorable, low)
            retrace = best_favorable - low if direction == "BUY" else high - best_favorable
            if retrace + 1e-12 >= pullback_r * risk:
                pullback_extreme = low if direction == "BUY" else high
                state = "PULLBACK_ARMED"
        elif state == "PULLBACK_ARMED" and x1_exit is None:
            pullback_extreme = min(pullback_extreme, low) if direction == "BUY" else max(pullback_extreme, high)
            prev = bars[bi - 1]
            confirmed = close > float(prev["high"]) if direction == "BUY" else close < float(prev["low"])
            if confirmed:
                opportunities += 1
                x2_status, state = "PENDING", "PENDING_FILL"
                x2_pending_idx = bi + 1
                if x2_pending_idx >= len(bars):
                    x2_status, x2_skip_reason, state = "CANCELLED", "NO_NEXT_BAR_FOR_FILL", "CANCELLED"

        if x1_exit is None:
            x1_open_risk = _remaining_risk(entry, x1_sl, direction, volume, contract_size)
        else:
            x1_open_risk = 0.0
        x2_open_risk = _remaining_risk(x2_entry, x2_sl, direction, volume, contract_size) if x2_entry is not None and x2_exit is None else 0.0
        max_combined_open_risk = max(max_combined_open_risk, x1_open_risk + x2_open_risk)

        if x2_entry is not None and x2_exit is not None and x1_exit is not None:
            break

    def leg_result(leg_entry: float, stop: float, exit_price: float | None, exit_time: int | None,
                   reason: str, ambiguous: bool, origin: str, updates: int, bars_held: int) -> dict[str, Any]:
        pnl = None if exit_price is None else (exit_price - leg_entry if direction == "BUY" else leg_entry - exit_price)
        return {
            "entry": leg_entry, "initial_sl": stop, "exit_price": exit_price,
            "exit_time_utc": _iso(exit_time) if exit_time is not None else None,
            "reason": reason, "ambiguous": ambiguous,
            "realized_R": pnl / abs(leg_entry - stop) if pnl is not None else None,
            "realized_usd": pnl * volume * contract_size if pnl is not None else None,
            "final_sl": x1_sl if origin == "X1" else x2_sl,
            "trailing_updates": updates, "bars_held": bars_held,
        }

    x1 = leg_result(entry, initial_sl, x1_exit, x1_exit_time, x1_reason, x1_ambiguous, "X1", x1_updates, 0)
    x1["final_sl"] = x1_sl
    x1["realized_R"] = ((x1_exit - entry) if direction == "BUY" else (entry - x1_exit)) / risk if x1_exit is not None else None
    x1["risk_usd"] = risk * volume * contract_size
    x2 = None
    if x2_entry is not None:
        x2 = leg_result(x2_entry, x2_sl, x2_exit, x2_exit_time, x2_reason, x2_ambiguous, "X2", x2_updates, x2_bars_held)
        x2["final_sl"] = x2_sl
        x2["risk_usd"] = abs(x2_entry - x2_sl) * volume * contract_size
    combined_usd = sum(float(x["realized_usd"]) for x in (x1, x2) if x and x["realized_usd"] is not None)
    combined_decisive = (x1["realized_usd"] is not None and not x1["ambiguous"] and
                         (x2 is None or (x2["realized_usd"] is not None and not x2["ambiguous"])))
    return {
        "population_index": candidate.get("population_index"),
        "direction": direction, "trigger_time": candidate.get("trigger_time"),
        "x1": x1, "x2": x2, "x2_status": x2_status,
        "x2_skip_reason": x2_skip_reason, "x2_opportunities": opportunities,
        "combined_gross_usd": combined_usd if combined_decisive else None,
        "combined_decisive": combined_decisive,
        "combined_ambiguous": x1_ambiguous or x2_ambiguous,
        "max_combined_open_risk_usd": max_combined_open_risk,
        "x2_admission_risk_usd": x2_admission_risk,
    }
