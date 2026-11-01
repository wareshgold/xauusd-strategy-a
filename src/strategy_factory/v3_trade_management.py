from __future__ import annotations

"""Research-only trade-management policies over an existing frozen V3 population.

All prices are replayed from completed M1 OHLC bars. This module does not
infer bid/ask fills, partial-fill behavior, spread, commission, slippage, or
broker execution semantics. It does not alter entry identity or geometry.
"""

import copy
import json
from datetime import datetime, timezone
from typing import Any

from .v3_exit_engine import V3ExitVariant, summarize


_ALLOWED_MODES = {
    "fixed_rr", "no_target", "breakeven", "trailing",
    "breakeven_trailing", "time_exit",
}
_ALLOWED_KEYS = {
    "mode", "target_rr", "breakeven_trigger_r",
    "trailing_activation_r", "trailing_distance_points", "time_exit_bars",
}


class V3TradeManagementError(ValueError):
    """Raised when a management policy is invalid."""


def normalize_policy(policy: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(policy, dict):
        raise V3TradeManagementError("management policy must be an object")
    unknown = sorted(set(policy) - _ALLOWED_KEYS)
    if unknown:
        raise V3TradeManagementError("unsupported management fields: " + ", ".join(unknown))
    mode = str(policy.get("mode", ""))
    if mode not in _ALLOWED_MODES:
        raise V3TradeManagementError("mode must be one of: " + ", ".join(sorted(_ALLOWED_MODES)))

    result = {"mode": mode}
    for key in ("target_rr", "breakeven_trigger_r", "trailing_activation_r",
                "trailing_distance_points", "time_exit_bars"):
        value = policy.get(key)
        if value is None:
            result[key] = None
        elif key == "time_exit_bars":
            if isinstance(value, bool) or int(value) != value or int(value) <= 0:
                raise V3TradeManagementError("time_exit_bars must be a positive integer")
            result[key] = int(value)
        else:
            number = float(value)
            if number <= 0:
                raise V3TradeManagementError(key + " must be positive")
            result[key] = number

    permitted = {
        "fixed_rr": {"target_rr"},
        "no_target": set(),
        "breakeven": {"target_rr", "breakeven_trigger_r"},
        "trailing": {"target_rr", "trailing_activation_r", "trailing_distance_points"},
        "breakeven_trailing": {"target_rr", "breakeven_trigger_r", "trailing_activation_r", "trailing_distance_points"},
        "time_exit": {"target_rr", "time_exit_bars"},
    }[mode]
    supplied_but_unused = sorted(
        key for key in _ALLOWED_KEYS - {"mode"}
        if result[key] is not None and key not in permitted
    )
    if supplied_but_unused:
        raise V3TradeManagementError(
            "parameters are not valid for " + mode + ": " + ", ".join(supplied_but_unused)
        )

    if mode == "fixed_rr" and result["target_rr"] is None:
        raise V3TradeManagementError("fixed_rr requires target_rr")
    if mode == "no_target" and any(result[k] is not None for k in (
        "target_rr", "breakeven_trigger_r", "trailing_activation_r",
        "trailing_distance_points", "time_exit_bars",
    )):
        raise V3TradeManagementError("no_target accepts no additional management parameters")
    if mode == "breakeven" and result["breakeven_trigger_r"] is None:
        raise V3TradeManagementError("breakeven requires breakeven_trigger_r")
    if mode == "trailing" and (
        result["trailing_activation_r"] is None or result["trailing_distance_points"] is None
    ):
        raise V3TradeManagementError("trailing requires trailing_activation_r and trailing_distance_points")
    if mode == "breakeven_trailing" and any(result[k] is None for k in (
        "breakeven_trigger_r", "trailing_activation_r", "trailing_distance_points",
    )):
        raise V3TradeManagementError(
            "breakeven_trailing requires breakeven_trigger_r, trailing_activation_r, and trailing_distance_points"
        )
    if mode == "time_exit" and result["time_exit_bars"] is None:
        raise V3TradeManagementError("time_exit requires time_exit_bars")
    if mode not in {"fixed_rr", "no_target"} and mode != "time_exit" and result["target_rr"] is None:
        # No target is a valid independent choice for BE/trailing policies.
        result["target_rr"] = None
    return result


class V3TradeManagementEngine:
    """Evaluate deterministic management policies using one existing V3 engine."""

    def __init__(self, base_engine: Any) -> None:
        self._base = base_engine
        self._cache: dict[str, V3ExitVariant] = {}

    @property
    def cache_entries(self) -> int:
        return len(self._cache)

    def evaluate(self, policy: dict[str, Any]) -> V3ExitVariant:
        config = normalize_policy(policy)
        key = json.dumps(config, sort_keys=True, separators=(",", ":"))
        if key in self._cache:
            return copy.deepcopy(self._cache[key])

        rows = [self._replay(candidate, config) for candidate in self._base._population]
        label = config["mode"].upper()
        details = ",".join(
            f"{name}={config[name]}" for name in (
                "target_rr", "breakeven_trigger_r", "trailing_activation_r",
                "trailing_distance_points", "time_exit_bars",
            ) if config[name] is not None
        )
        name = "MGMT_" + label + (("_" + details.replace("=", "").replace(",", "_")) if details else "")
        variant = V3ExitVariant(
            session_fingerprint=self._base.session_fingerprint,
            name=name,
            rr=config["target_rr"],
            activation_points=None,
            distance_points=None,
            summary=summarize(rows),
            trades=tuple(rows),
            management_config=config,
        )
        self._cache[key] = variant
        return copy.deepcopy(variant)

    def _replay(self, candidate: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        bars = self._base._bars
        point = self._base._mt5_point
        volume = self._base._volume
        contract = self._base._contract_size
        direction = str(candidate["direction"])
        if direction not in {"BUY", "SELL"}:
            raise V3TradeManagementError("candidate direction must be BUY or SELL")

        entry_idx = int(candidate["entry_idx"])
        entry = float(candidate["theoretical_entry"])
        risk = float(candidate["risk"])
        initial_sl = float(candidate["sl"])
        if risk <= 0:
            raise V3TradeManagementError("candidate risk must be positive")
        target_rr = config["target_rr"]
        target = (
            entry + target_rr * risk if direction == "BUY" else entry - target_rr * risk
        ) if target_rr is not None else None

        mode = config["mode"]
        be_trigger = config["breakeven_trigger_r"]
        trail_trigger = config["trailing_activation_r"]
        trail_distance = (
            config["trailing_distance_points"] * point
            if config["trailing_distance_points"] is not None else None
        )
        time_limit = config["time_exit_bars"]

        current_sl = initial_sl
        be_activated = False
        trail_activated = False
        trail_updates = 0
        deferred_updates = 0
        max_fav = max_adverse = 0.0
        exit_price = exit_time = None
        reason = "OPEN_OR_UNRESOLVED"
        ambiguous = False
        bars_held = 0
        previous_time = int(bars[entry_idx]["time"])

        for k in range(entry_idx + 1, len(bars)):
            bar = bars[k]
            now = int(bar["time"])
            if (now - previous_time) != 60:
                ambiguous = True
                reason = "M1_GAP_WHILE_OPEN"
                exit_time = now
                break
            previous_time = now
            bars_held += 1
            high, low, close = float(bar["high"]), float(bar["low"]), float(bar["close"])

            if direction == "BUY":
                favorable, adverse = high - entry, entry - low
                hit_sl = low <= current_sl
                hit_target = target is not None and high >= target
            else:
                favorable, adverse = entry - low, high - entry
                hit_sl = high >= current_sl
                hit_target = target is not None and low <= target
            max_fav = max(max_fav, favorable)
            max_adverse = max(max_adverse, adverse)

            if hit_sl and hit_target:
                ambiguous, reason, exit_time = True, "SL_AND_TP_SAME_BAR", now
                break
            if hit_sl:
                exit_price, exit_time = current_sl, now
                if be_activated and current_sl == entry:
                    reason = "BREAKEVEN_SL"
                elif trail_activated and (
                    (direction == "BUY" and current_sl > initial_sl)
                    or (direction == "SELL" and current_sl < initial_sl)
                ):
                    reason = "TRAIL_SL"
                else:
                    reason = "SL"
                break
            if hit_target:
                exit_price, exit_time, reason = target, now, "TP"
                break

            # Policy updates use the completed bar and become effective on the
            # next bar. This avoids using the current bar's high/low to stop it.
            if be_trigger is not None and not be_activated and favorable >= be_trigger * risk:
                be_activated = True
                current_sl = max(current_sl, entry) if direction == "BUY" else min(current_sl, entry)

            if trail_trigger is not None and favorable >= trail_trigger * risk:
                trail_activated = True
                proposed = high - trail_distance if direction == "BUY" else low + trail_distance
                can_install = proposed < close if direction == "BUY" else proposed > close
                if can_install:
                    new_sl = max(current_sl, proposed) if direction == "BUY" else min(current_sl, proposed)
                    if new_sl != current_sl:
                        trail_updates += 1
                    current_sl = new_sl
                else:
                    deferred_updates += 1

            if time_limit is not None and bars_held >= time_limit:
                exit_price, exit_time, reason = close, now, "TIME_EXIT"
                break

        realized_price = None
        realized_r = None
        realized_usd = None
        if exit_price is not None:
            realized_price = exit_price - entry if direction == "BUY" else entry - exit_price
            realized_r = realized_price / risk
            realized_usd = realized_price * volume * contract

        return {
            "variant": "MANAGEMENT",
            "management_policy": dict(config),
            "direction": direction,
            "trigger_time": candidate["trigger_time"],
            "signal_time_utc": candidate["signal_time_utc"],
            "theoretical_entry": entry,
            "risk": risk,
            "initial_sl": initial_sl,
            "initial_tp": target,
            "rr": target_rr,
            "trailing_activated": trail_activated,
            "breakeven_activated": be_activated,
            "trailing_updates": trail_updates,
            "deferred_trailing_updates": deferred_updates,
            "bars_held": bars_held,
            "final_sl": current_sl,
            "max_favorable_price": max_fav,
            "max_adverse_price": max_adverse,
            "exit_time_utc": (
                datetime.fromtimestamp(exit_time, timezone.utc).isoformat()
                if exit_time is not None else None
            ),
            "exit_price": exit_price,
            "reason": reason,
            "ambiguous": ambiguous,
            "realized_price": realized_price,
            "realized_R": realized_r,
            "risk_usd": risk * volume * contract,
            "realized_usd": realized_usd,
        }
