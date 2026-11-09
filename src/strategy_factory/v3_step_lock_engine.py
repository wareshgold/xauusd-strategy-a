from __future__ import annotations

"""Pure, offline Step-Lock replay over a frozen entry and M1 OHLC bars.

No MT5 dependency, signal generation, order execution, or final TP.
Completed-bar stop updates become active on the following bar.
"""

from datetime import datetime, timezone
import math
from typing import Any, Sequence

from .m1_integrity import m1_gap_detected
from .v3_exit_engine import V3ExitEngineError


def validate_frozen_risk(candidate: dict[str, Any], *, tolerance: float = 1e-8) -> None:
    direction = str(candidate["direction"]).upper()
    entry = float(candidate["theoretical_entry"])
    stop = float(candidate["sl"])
    risk = float(candidate["risk"])
    if direction not in {"BUY", "SELL"}:
        raise V3ExitEngineError("candidate direction must be BUY or SELL")
    if not all(math.isfinite(x) for x in (entry, stop, risk)) or risk <= 0:
        raise V3ExitEngineError("entry, initial stop and risk must be finite; risk must be positive")
    observed = abs(entry - stop)
    if not math.isclose(observed, risk, rel_tol=0.0, abs_tol=tolerance):
        raise V3ExitEngineError(
            f"frozen risk mismatch: risk={risk:.12g}, abs(entry-stop)={observed:.12g}"
        )
    if (direction == "BUY" and not stop < entry) or (direction == "SELL" and not stop > entry):
        raise V3ExitEngineError("initial stop is on the invalid side of entry for trade direction")


def replay_step_lock_no_tp(
    candidate: dict[str, Any],
    bars: Sequence[Any],
    *,
    contract_size: float,
    volume: float,
    risk_tolerance: float = 1e-6,
) -> dict[str, Any]:
    """Replay +nR milestones locking +(n-1)R, with no final target.

    Conservative OHLC policy:
    - entry bar is excluded;
    - if a bar touches the active stop and reaches one or more new milestones,
      ordering is unknowable, so the trade is AMBIGUOUS;
    - if only milestones are reached, lock the highest fully crossed integer R;
    - the newly calculated stop becomes active on the next bar;
    - a gap while open is AMBIGUOUS and never filled.
    """
    validate_frozen_risk(candidate, tolerance=risk_tolerance)
    entry_idx = int(candidate["entry_idx"])
    if not 0 <= entry_idx < len(bars):
        raise V3ExitEngineError("candidate entry_idx is outside loaded M1 bars")
    contract_size, volume = float(contract_size), float(volume)
    if not math.isfinite(contract_size) or not math.isfinite(volume) or min(contract_size, volume) <= 0:
        raise V3ExitEngineError("contract_size and volume must be finite and positive")

    entry = float(candidate["theoretical_entry"])
    risk = float(candidate["risk"])
    initial_sl = float(candidate["sl"])
    direction = str(candidate["direction"]).upper()
    current_sl = initial_sl
    highest_milestone = 0
    updates = 0
    max_favorable = 0.0
    max_adverse = 0.0
    bars_held = 0
    previous_time = int(bars[entry_idx]["time"])
    exit_price = None
    exit_time = None
    reason = "OPEN_OR_UNRESOLVED"
    ambiguous = False

    for index in range(entry_idx + 1, len(bars)):
        bar = bars[index]
        now = int(bar["time"])
        if m1_gap_detected(previous_time, now):
            ambiguous = True
            reason = "M1_GAP_WHILE_OPEN"
            exit_time = now
            break
        previous_time = now
        bars_held += 1
        high, low = float(bar["high"]), float(bar["low"])
        if direction == "BUY":
            favorable = high - entry
            adverse = entry - low
            hit_stop = low <= current_sl
        else:
            favorable = entry - low
            adverse = high - entry
            hit_stop = high >= current_sl
        max_favorable = max(max_favorable, favorable)
        max_adverse = max(max_adverse, adverse)
        reached = max(0, int(math.floor((favorable + risk_tolerance) / risk)))

        if hit_stop and reached > highest_milestone:
            ambiguous = True
            reason = "ACTIVE_SL_AND_NEW_MILESTONE_SAME_BAR"
            exit_time = now
            break
        if hit_stop:
            exit_price, exit_time = current_sl, now
            reason = "STEP_LOCK_SL" if highest_milestone else "SL"
            break
        if reached > highest_milestone:
            highest_milestone = reached
            locked_r = highest_milestone - 1
            current_sl = entry + locked_r * risk if direction == "BUY" else entry - locked_r * risk
            updates += 1

    realized_price = None
    realized_r = None
    realized_usd = None
    if exit_price is not None and not ambiguous:
        realized_price = exit_price - entry if direction == "BUY" else entry - exit_price
        realized_r = realized_price / risk
        realized_usd = realized_price * volume * contract_size

    return {
        "direction": direction,
        "trigger_time": candidate["trigger_time"],
        "signal_time_utc": candidate.get("signal_time_utc"),
        "theoretical_entry": entry,
        "risk": risk,
        "initial_sl": initial_sl,
        "initial_tp": None,
        "final_sl": current_sl,
        "highest_milestone_R": highest_milestone,
        "step_lock_updates": updates,
        "bars_held": bars_held,
        "entry_bar_excluded_from_exit_replay": True,
        "max_favorable_price": max_favorable,
        "max_adverse_price": max_adverse,
        "exit_time_utc": datetime.fromtimestamp(exit_time, timezone.utc).isoformat() if exit_time is not None else None,
        "exit_price": exit_price,
        "reason": reason,
        "ambiguous": ambiguous,
        "realized_price": realized_price,
        "realized_R": realized_r,
        "risk_usd": risk * volume * contract_size,
        "realized_usd": realized_usd,
        "management_mode": "STEP_LOCK_NO_TP",
    }
