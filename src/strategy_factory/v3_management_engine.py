from __future__ import annotations

"""Deterministic, research-only trade-management experiments over frozen entries.

Supported modes are deliberately limited to mechanics that can be represented
without inventing tick fills: FIXED_RR, NO_TARGET, BREAK_EVEN, TRAILING_R,
BREAK_EVEN_TRAILING, and TIME_EXIT. Partial exits and ATR-based rules are
excluded until their sizing/fill semantics and data requirements are specified.
"""

from dataclasses import dataclass
import math
from datetime import datetime, timezone
from typing import Any, Sequence

from .m1_integrity import m1_gap_detected
from .v3_exit_engine import V3ExitEngineError, summarize


@dataclass(frozen=True)
class V3ManagementVariant:
    session_fingerprint: str
    name: str
    spec: dict[str, Any]
    summary: dict[str, Any]
    trades: tuple[dict[str, Any], ...]


def _positive(spec: dict[str, Any], key: str) -> float:
    try:
        value = float(spec[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise V3ExitEngineError(f"{key} must be a positive number") from exc
    if not math.isfinite(value) or value <= 0:
        raise V3ExitEngineError(f"{key} must be a finite positive number")
    return value


def normalize_management_spec(spec: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(spec, dict):
        raise V3ExitEngineError("management spec must be an object")
    mode = str(spec.get("mode", "")).upper()
    allowed = {"FIXED_RR", "NO_TARGET", "BREAK_EVEN", "TRAILING_R", "BREAK_EVEN_TRAILING", "TIME_EXIT"}
    if mode not in allowed:
        raise V3ExitEngineError("unsupported management mode")
    result: dict[str, Any] = {"mode": mode}
    if mode == "NO_TARGET":
        return result
    if mode == "FIXED_RR":
        result["rr"] = _positive(spec, "rr")
    elif mode == "BREAK_EVEN":
        result["rr"] = _positive(spec, "rr")
        result["activation_r"] = _positive(spec, "activation_r")
        result["offset_r"] = float(spec.get("offset_r", 0.0))
        if not math.isfinite(result["offset_r"]) or result["offset_r"] < 0:
            raise V3ExitEngineError("offset_r must be finite and non-negative")
    elif mode == "TRAILING_R":
        result["rr"] = None if spec.get("rr") is None else _positive(spec, "rr")
        result["activation_r"] = _positive(spec, "activation_r")
        result["distance_r"] = _positive(spec, "distance_r")
    elif mode == "BREAK_EVEN_TRAILING":
        result["rr"] = _positive(spec, "rr")
        result["be_activation_r"] = _positive(spec, "be_activation_r")
        result["be_offset_r"] = float(spec.get("be_offset_r", 0.0))
        result["trail_activation_r"] = _positive(spec, "trail_activation_r")
        result["trail_distance_r"] = _positive(spec, "trail_distance_r")
        if not math.isfinite(result["be_offset_r"]) or result["be_offset_r"] < 0:
            raise V3ExitEngineError("be_offset_r must be finite and non-negative")
    else:  # TIME_EXIT
        result["rr"] = None if spec.get("rr") is None else _positive(spec, "rr")
        try:
            result["max_bars"] = int(spec["max_bars"])
        except (KeyError, TypeError, ValueError) as exc:
            raise V3ExitEngineError("max_bars must be a positive integer") from exc
        if result["max_bars"] <= 0 or float(spec["max_bars"]) != result["max_bars"]:
            raise V3ExitEngineError("max_bars must be a positive integer")
    return result


def replay_management_trade(
    candidate: dict[str, Any],
    bars: Sequence[Any],
    spec: dict[str, Any],
    *,
    mt5_point: float,
    contract_size: float,
    volume: float,
) -> dict[str, Any]:
    mode = spec["mode"]
    entry_idx = int(candidate["entry_idx"])
    entry = float(candidate["theoretical_entry"])
    risk = float(candidate["risk"])
    direction = str(candidate["direction"])
    initial_sl = float(candidate["sl"])
    if direction not in {"BUY", "SELL"}:
        raise V3ExitEngineError("candidate direction must be BUY or SELL")
    if risk <= 0 or mt5_point <= 0 or contract_size <= 0 or volume <= 0:
        raise V3ExitEngineError("risk, MT5 point, contract size, and volume must be positive")
    if not 0 <= entry_idx < len(bars):
        raise V3ExitEngineError("candidate entry_idx is outside loaded M1 bars")

    rr = spec.get("rr")
    target = None if rr is None else (entry + rr * risk if direction == "BUY" else entry - rr * risk)
    current_sl = initial_sl
    stop_origin = "SL"
    activated = False
    be_activated = False
    trail_activated = False
    exit_price = None
    exit_time = None
    reason = "OPEN_OR_UNRESOLVED"
    ambiguous = False
    max_fav = 0.0
    max_adverse = 0.0
    bars_held = 0
    updates = 0
    deferred = 0
    previous_time = int(bars[entry_idx]["time"])

    for k in range(entry_idx + 1, len(bars)):
        bar = bars[k]
        now = int(bar["time"])
        if m1_gap_detected(previous_time, now):
            ambiguous = True
            reason = "M1_GAP_WHILE_OPEN"
            exit_time = now
            break
        previous_time = now
        bars_held += 1
        high, low, close = float(bar["high"]), float(bar["low"]), float(bar["close"])
        favorable = high - entry if direction == "BUY" else entry - low
        adverse = entry - low if direction == "BUY" else high - entry
        max_fav, max_adverse = max(max_fav, favorable), max(max_adverse, adverse)
        hit_sl = low <= current_sl if direction == "BUY" else high >= current_sl
        hit_tp = target is not None and (high >= target if direction == "BUY" else low <= target)
        if hit_sl and hit_tp:
            ambiguous, reason, exit_time = True, "SL_AND_TP_SAME_BAR", now
            break
        if hit_sl:
            exit_price, exit_time = current_sl, now
            reason = f"{stop_origin}_SL" if stop_origin != "SL" else "SL"
            break
        if hit_tp:
            exit_price, exit_time, reason = target, now, "TP"
            break

        # Stops updated from a completed bar become active only on the next bar.
        if mode == "BREAK_EVEN" and not be_activated and favorable >= spec["activation_r"] * risk:
            proposed = entry + spec["offset_r"] * risk if direction == "BUY" else entry - spec["offset_r"] * risk
            valid_side = proposed < close if direction == "BUY" else proposed > close
            if valid_side:
                improved = proposed > current_sl if direction == "BUY" else proposed < current_sl
                if improved:
                    current_sl, updates, be_activated = proposed, updates + 1, True
                    stop_origin = "BREAK_EVEN"
            else:
                deferred += 1
        elif mode == "TRAILING_R":
            if not trail_activated and favorable >= spec["activation_r"] * risk:
                trail_activated = activated = True
            if trail_activated:
                distance = spec["distance_r"] * risk
                proposed = high - distance if direction == "BUY" else low + distance
                valid_side = proposed < close if direction == "BUY" else proposed > close
                improved = proposed > current_sl if direction == "BUY" else proposed < current_sl
                if valid_side and improved:
                    current_sl, updates = proposed, updates + 1
                    stop_origin = "TRAIL"
                elif not valid_side:
                    deferred += 1
        elif mode == "BREAK_EVEN_TRAILING":
            if not be_activated and favorable >= spec["be_activation_r"] * risk:
                proposed = entry + spec["be_offset_r"] * risk if direction == "BUY" else entry - spec["be_offset_r"] * risk
                valid_side = proposed < close if direction == "BUY" else proposed > close
                improved = proposed > current_sl if direction == "BUY" else proposed < current_sl
                if valid_side and improved:
                    current_sl, be_activated, updates = proposed, True, updates + 1
                    stop_origin = "BREAK_EVEN"
                elif not valid_side:
                    deferred += 1
            if not trail_activated and favorable >= spec["trail_activation_r"] * risk:
                trail_activated = activated = True
            if trail_activated:
                distance = spec["trail_distance_r"] * risk
                proposed = high - distance if direction == "BUY" else low + distance
                valid_side = proposed < close if direction == "BUY" else proposed > close
                improved = proposed > current_sl if direction == "BUY" else proposed < current_sl
                if valid_side and improved:
                    current_sl, updates = proposed, updates + 1
                    stop_origin = "TRAIL"
                elif not valid_side:
                    deferred += 1

        if mode == "TIME_EXIT" and bars_held >= spec["max_bars"]:
            exit_price, exit_time, reason = close, now, "TIME_EXIT"
            break

    realized_price = None if exit_price is None else (exit_price - entry if direction == "BUY" else entry - exit_price)
    realized_r = None if realized_price is None else realized_price / risk
    realized_usd = None if realized_price is None else realized_price * volume * contract_size
    return {
        "direction": direction, "trigger_time": candidate["trigger_time"],
        "signal_time_utc": candidate["signal_time_utc"], "theoretical_entry": entry,
        "risk": risk, "initial_sl": initial_sl, "initial_tp": target, "rr": rr,
        "trailing_enabled": mode in {"TRAILING_R", "BREAK_EVEN_TRAILING"},
        "trailing_activated": trail_activated, "break_even_activated": be_activated,
        "entry_bar_excluded_from_exit_replay": True, "trailing_updates": updates,
        "deferred_trailing_updates": deferred, "bars_held": bars_held,
        "final_sl": current_sl, "max_favorable_price": max_fav,
        "max_adverse_price": max_adverse, "exit_time_utc": (
            datetime.fromtimestamp(exit_time, timezone.utc).isoformat()
            if exit_time is not None else None
        ), "exit_price": exit_price, "reason": reason, "ambiguous": ambiguous,
        "realized_price": realized_price, "realized_R": realized_r,
        "risk_usd": risk * volume * contract_size, "realized_usd": realized_usd,
        "management_mode": mode,
    }


class V3ManagementReplayEngine:
    def __init__(self, *, bars: Sequence[Any], population: Sequence[dict[str, Any]],
                 mt5_point: float, contract_size: float, volume: float,
                 session_fingerprint: str) -> None:
        if not bars or not population:
            raise V3ExitEngineError("bars and frozen population must be non-empty")
        self._bars, self._population = bars, tuple(dict(x) for x in population)
        self._point, self._contract, self._volume = float(mt5_point), float(contract_size), float(volume)
        if min(self._point, self._contract, self._volume) <= 0:
            raise V3ExitEngineError("MT5 point, contract size, and volume must be positive")
        self.session_fingerprint = session_fingerprint
        self._cache: dict[str, V3ManagementVariant] = {}

    @property
    def cache_entries(self) -> int:
        return len(self._cache)

    def evaluate(self, spec: dict[str, Any]) -> V3ManagementVariant:
        normalized = normalize_management_spec(spec)
        import hashlib, json
        key = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
        if key in self._cache:
            return self._cache[key]
        trades = tuple(replay_management_trade(
            candidate, self._bars, normalized, mt5_point=self._point,
            contract_size=self._contract, volume=self._volume,
        ) for candidate in self._population)
        name = normalized["mode"] + "_" + hashlib.sha256(key.encode()).hexdigest()[:8]
        result = V3ManagementVariant(self.session_fingerprint, name, normalized, summarize(trades), trades)
        self._cache[key] = result
        return result

    def compare(self, left: V3ManagementVariant, right: V3ManagementVariant) -> dict[str, Any]:
        if left.session_fingerprint != self.session_fingerprint or right.session_fingerprint != self.session_fingerprint:
            raise V3ExitEngineError("variants do not belong to this exact research session")
        paired = []
        for index, (a, b, candidate) in enumerate(zip(left.trades, right.trades, self._population)):
            identity = (int(candidate["trigger_time"]), str(candidate["direction"]),
                        float(candidate["theoretical_entry"]), float(candidate["sl"]), float(candidate["risk"]))
            for row in (a, b):
                actual = (int(row["trigger_time"]), str(row["direction"]), float(row["theoretical_entry"]),
                          float(row["initial_sl"]), float(row["risk"]))
                if actual != identity:
                    raise V3ExitEngineError("frozen trade identity mismatch")
            paired.append({
                "population_index": index, "trigger_time": identity[0],
                "left_variant": left.name, "right_variant": right.name,
                "left_reason": a["reason"], "right_reason": b["reason"],
                "left_ambiguous": a["ambiguous"], "right_ambiguous": b["ambiguous"],
                "left_realized_R": a["realized_R"], "right_realized_R": b["realized_R"],
                "delta_R": b["realized_R"] - a["realized_R"] if a["realized_R"] is not None and b["realized_R"] is not None else None,
                "outcome_changed": (a["reason"], a["ambiguous"], a["realized_R"]) != (b["reason"], b["ambiguous"], b["realized_R"]),
            })
        if len(left.trades) != len(self._population) or len(right.trades) != len(self._population):
            raise V3ExitEngineError("variants do not share this engine's frozen population")
        return {"left_variant": left.name, "right_variant": right.name,
                "paired_trade_count": len(paired),
                "changed_outcome_count": sum(x["outcome_changed"] for x in paired),
                "paired_trades": paired}
