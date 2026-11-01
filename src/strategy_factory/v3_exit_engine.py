from __future__ import annotations

"""Pure, in-process SP2L V3 exit replay primitives.

This module contains no MT5 connection, signal detection, entry geometry,
parameter ranking, or production decisioning. It consumes an already-frozen
entry population and an already-loaded M1 bar array. The caller is responsible
for binding the exact dataset and entry-artifact hashes to its research record.
"""

from dataclasses import dataclass
import copy
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Sequence

from .m1_integrity import m1_gap_detected


class V3ExitEngineError(ValueError):
    """Raised when an in-memory V3 exit research session is invalid."""


def _iso(timestamp: int | None) -> str | None:
    return (
        datetime.fromtimestamp(int(timestamp), timezone.utc).isoformat()
        if timestamp is not None
        else None
    )


def replay_trade(
    candidate: dict[str, Any],
    bars: Sequence[Any],
    rr: float,
    activation_points: float | None,
    distance_points: float | None,
    mt5_point: float,
    contract_size: float,
    *,
    volume: float,
) -> dict[str, Any]:
    """Replay one frozen V3 entry against M1 OHLC bars.

    Semantics intentionally match the controlled Discovery Matrix:
    - the entry bar is excluded from exit replay;
    - an M1 gap while open is unresolved/ambiguous;
    - same-bar SL and TP is ambiguous;
    - trailing updates made from a completed bar apply only to the next bar;
    - a proposed stop beyond the bar close is deferred;
    - no spread, slippage, or commission is inferred.
    """
    entry_idx = int(candidate["entry_idx"])
    entry = float(candidate["theoretical_entry"])
    risk = float(candidate["risk"])
    direction = str(candidate["direction"])
    initial_sl = float(candidate["sl"])
    if direction not in {"BUY", "SELL"}:
        raise V3ExitEngineError("candidate direction must be BUY or SELL")
    if not 0 <= entry_idx < len(bars):
        raise V3ExitEngineError("candidate entry_idx is outside the loaded M1 bars")
    if rr <= 0 or mt5_point <= 0 or contract_size <= 0 or volume <= 0:
        raise V3ExitEngineError("RR, MT5 point, contract size, and volume must be positive")
    if risk <= 0:
        raise V3ExitEngineError("candidate risk must be positive")
    if (activation_points is None) != (distance_points is None):
        raise V3ExitEngineError("activation and distance must both be set or both be None")
    if activation_points is not None and (activation_points <= 0 or distance_points <= 0):
        raise V3ExitEngineError("trailing activation and distance must be positive")

    initial_tp = entry + rr * risk if direction == "BUY" else entry - rr * risk
    trailing_enabled = activation_points is not None and distance_points is not None
    activation_price = activation_points * mt5_point if trailing_enabled else 0.0
    distance_price = distance_points * mt5_point if trailing_enabled else 0.0

    current_sl = initial_sl
    activated = False
    activation_time = None
    activation_bar_index = None
    trailing_updates = 0
    deferred_trailing_updates = 0
    max_fav = 0.0
    max_adverse = 0.0
    exit_price = None
    exit_time = None
    reason = "OPEN_OR_UNRESOLVED"
    ambiguous = False

    previous_bar_time = int(bars[entry_idx]["time"])
    for k in range(entry_idx + 1, len(bars)):
        bar = bars[k]
        current_bar_time = int(bar["time"])
        if m1_gap_detected(previous_bar_time, current_bar_time):
            ambiguous = True
            reason = "M1_GAP_WHILE_OPEN"
            exit_time = current_bar_time
            break
        previous_bar_time = current_bar_time
        high = float(bar["high"])
        low = float(bar["low"])
        close = float(bar["close"])

        if direction == "BUY":
            favorable = high - entry
            adverse = entry - low
            max_fav = max(max_fav, favorable)
            max_adverse = max(max_adverse, adverse)
            hit_sl = low <= current_sl
            hit_tp = high >= initial_tp

            if hit_sl and hit_tp:
                ambiguous = True
                reason = "SL_AND_TP_SAME_BAR"
                exit_time = current_bar_time
                break
            if hit_sl:
                exit_price = current_sl
                reason = "TRAIL_SL" if activated and current_sl > initial_sl else "SL"
                exit_time = current_bar_time
                break
            if hit_tp:
                exit_price = initial_tp
                reason = "TP"
                exit_time = current_bar_time
                break

            if trailing_enabled and not activated and favorable >= activation_price:
                activated = True
                activation_time = current_bar_time
                activation_bar_index = k
            if activated:
                candidate_sl = high - distance_price
                if candidate_sl < close:
                    new_sl = max(current_sl, candidate_sl)
                    if new_sl > current_sl:
                        trailing_updates += 1
                    current_sl = new_sl
                else:
                    deferred_trailing_updates += 1
        else:
            favorable = entry - low
            adverse = high - entry
            max_fav = max(max_fav, favorable)
            max_adverse = max(max_adverse, adverse)
            hit_sl = high >= current_sl
            hit_tp = low <= initial_tp

            if hit_sl and hit_tp:
                ambiguous = True
                reason = "SL_AND_TP_SAME_BAR"
                exit_time = current_bar_time
                break
            if hit_sl:
                exit_price = current_sl
                reason = "TRAIL_SL" if activated and current_sl < initial_sl else "SL"
                exit_time = current_bar_time
                break
            if hit_tp:
                exit_price = initial_tp
                reason = "TP"
                exit_time = current_bar_time
                break

            if trailing_enabled and not activated and favorable >= activation_price:
                activated = True
                activation_time = current_bar_time
                activation_bar_index = k
            if activated:
                candidate_sl = low + distance_price
                if candidate_sl > close:
                    new_sl = min(current_sl, candidate_sl)
                    if new_sl < current_sl:
                        trailing_updates += 1
                    current_sl = new_sl
                else:
                    deferred_trailing_updates += 1

    realized_price = None
    realized_r = None
    realized_usd = None
    risk_usd = risk * volume * contract_size
    if exit_price is not None:
        realized_price = (
            exit_price - entry if direction == "BUY" else entry - exit_price
        )
        realized_r = realized_price / risk
        realized_usd = realized_price * volume * contract_size

    return {
        "direction": direction,
        "trigger_time": candidate["trigger_time"],
        "signal_time_utc": candidate["signal_time_utc"],
        "theoretical_entry": entry,
        "risk": risk,
        "initial_sl": initial_sl,
        "initial_tp": initial_tp,
        "rr": rr,
        "activation_points": activation_points,
        "activation_price": activation_price,
        "distance_points": distance_points,
        "distance_price": distance_price,
        "trailing_enabled": trailing_enabled,
        "trailing_activated": activated,
        "activation_time_utc": _iso(activation_time),
        "activation_bar_index": activation_bar_index,
        "entry_bar_excluded_from_exit_replay": True,
        "trailing_updates": trailing_updates,
        "deferred_trailing_updates": deferred_trailing_updates,
        "exit_after_activation_bars": (
            (int(exit_time) - int(activation_time)) // 60
            if exit_time is not None and activation_time is not None
            else None
        ),
        "final_sl": current_sl,
        "max_favorable_price": max_fav,
        "max_adverse_price": max_adverse,
        "exit_time_utc": _iso(exit_time),
        "exit_price": exit_price,
        "reason": reason,
        "ambiguous": ambiguous,
        "realized_price": realized_price,
        "realized_R": realized_r,
        "risk_usd": risk_usd,
        "realized_usd": realized_usd,
    }


def summarize(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    decisive = [row for row in rows if not row["ambiguous"] and row["realized_R"] is not None]
    wins = [row for row in decisive if row["realized_R"] > 0]
    losses = [row for row in decisive if row["realized_R"] < 0]
    gross_profit_r = sum(row["realized_R"] for row in wins)
    gross_loss_r = abs(sum(row["realized_R"] for row in losses))
    net_r = sum(row["realized_R"] for row in decisive)
    gross_profit_usd = sum(row["realized_usd"] for row in wins)
    gross_loss_usd = abs(sum(row["realized_usd"] for row in losses))
    net_usd = sum(row["realized_usd"] for row in decisive)

    equity = peak = max_dd = 0.0
    losing_streak = max_losing_streak = 0
    for row in sorted(decisive, key=lambda item: item["trigger_time"]):
        equity += row["realized_R"]
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
        if row["realized_R"] < 0:
            losing_streak += 1
            max_losing_streak = max(max_losing_streak, losing_streak)
        else:
            losing_streak = 0

    activated = sum(1 for row in rows if row["trailing_activated"])
    trail_exits = sum(1 for row in decisive if row["reason"] == "TRAIL_SL")
    tp_exits = sum(1 for row in decisive if row["reason"] == "TP")
    sl_exits = sum(1 for row in decisive if row["reason"] == "SL")
    return {
        "signals": len(rows),
        "decisive": len(decisive),
        "wins": len(wins),
        "losses": len(losses),
        "ambiguous": len(rows) - len(decisive),
        "gap_exposed": sum(1 for row in rows if row["reason"] == "M1_GAP_WHILE_OPEN"),
        "win_rate_decisive_pct": 100.0 * len(wins) / len(decisive) if decisive else None,
        "net_R": net_r,
        "profit_factor": gross_profit_r / gross_loss_r if gross_loss_r else None,
        "max_drawdown_R": max_dd,
        "max_losing_streak": max_losing_streak,
        "gross_profit_usd": gross_profit_usd,
        "gross_loss_usd": gross_loss_usd,
        "net_profit_usd": net_usd,
        "avg_R_per_decisive": net_r / len(decisive) if decisive else None,
        "avg_usd_per_decisive": net_usd / len(decisive) if decisive else None,
        "activation_pct": 100.0 * activated / len(rows) if rows else None,
        "trail_exits": trail_exits,
        "tp_exits": tp_exits,
        "original_sl_exits": sl_exits,
    }


@dataclass(frozen=True)
class V3ExitVariant:
    session_fingerprint: str
    name: str
    rr: float
    activation_points: float | None
    distance_points: float | None
    summary: dict[str, Any]
    trades: tuple[dict[str, Any], ...]


class V3ExitReplayEngine:
    """Reusable in-memory replay over one fixed M1 dataset and entry population.

    The cache is session-local and keyed by exact parameters. It does not persist
    evidence or promote variants. The caller owns dataset/provenance binding.
    """

    def __init__(
        self,
        *,
        bars: Sequence[Any],
        population: Sequence[dict[str, Any]],
        mt5_point: float,
        contract_size: float,
        volume: float,
        engine_revision: str,
        dataset_sha256: str,
        entry_population_sha256: str,
    ) -> None:
        if len(bars) == 0 or len(population) == 0:
            raise V3ExitEngineError("bars and frozen entry population must be non-empty")
        if mt5_point <= 0 or contract_size <= 0 or volume <= 0:
            raise V3ExitEngineError("MT5 point, contract size, and volume must be positive")
        if not engine_revision:
            raise V3ExitEngineError("engine_revision is required")
        for label, digest in (
            ("dataset_sha256", dataset_sha256),
            ("entry_population_sha256", entry_population_sha256),
        ):
            if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest.lower()):
                raise V3ExitEngineError(f"{label} must be a SHA-256 hex digest")
        timestamps = [int(bar["time"]) for bar in bars]
        if any(left >= right for left, right in zip(timestamps, timestamps[1:])):
            raise V3ExitEngineError("M1 bars must be strictly chronological")
        for candidate in population:
            index = int(candidate["entry_idx"])
            if index < 0 or index >= len(bars):
                raise V3ExitEngineError("frozen population contains an invalid entry_idx")
        self._bars = bars
        self._population = tuple(dict(candidate) for candidate in population)
        self._mt5_point = float(mt5_point)
        self._contract_size = float(contract_size)
        self._volume = float(volume)
        self._engine_revision = engine_revision
        identity = {
            "engine_revision": engine_revision,
            "dataset_sha256": dataset_sha256.lower(),
            "entry_population_sha256": entry_population_sha256.lower(),
            "mt5_point": float(mt5_point),
            "contract_size": float(contract_size),
            "volume": float(volume),
        }
        self.session_fingerprint = hashlib.sha256(
            json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        self._cache: dict[tuple[float, float | None, float | None], V3ExitVariant] = {}

    @property
    def cache_entries(self) -> int:
        return len(self._cache)

    @property
    def population_size(self) -> int:
        return len(self._population)

    def evaluate(
        self,
        *,
        rr: float,
        activation_points: float | None,
        distance_points: float | None,
    ) -> V3ExitVariant:
        if rr <= 0:
            raise V3ExitEngineError("RR must be positive")
        if (activation_points is None) != (distance_points is None):
            raise V3ExitEngineError("activation and distance must both be set or both be None")
        if activation_points is not None and (activation_points <= 0 or distance_points <= 0):
            raise V3ExitEngineError("trailing activation and distance must be positive")
        key = (float(rr), None if activation_points is None else float(activation_points),
               None if distance_points is None else float(distance_points))
        cached = self._cache.get(key)
        if cached is not None:
            return copy.deepcopy(cached)
        name = (
            f"RR{key[0]:g}_NO_TRAIL"
            if key[1] is None
            else f"RR{key[0]:g}_ACT{key[1]:g}_D{key[2]:g}"
        )
        trades = []
        for candidate in self._population:
            row = replay_trade(
                candidate,
                self._bars,
                key[0],
                key[1],
                key[2],
                self._mt5_point,
                self._contract_size,
                volume=self._volume,
            )
            row["variant"] = name
            trades.append(row)
        result = V3ExitVariant(
            session_fingerprint=self.session_fingerprint,
            name=name,
            rr=key[0],
            activation_points=key[1],
            distance_points=key[2],
            summary=summarize(trades),
            trades=tuple(trades),
        )
        self._cache[key] = result
        return copy.deepcopy(result)

    def compare(self, left: V3ExitVariant, right: V3ExitVariant) -> dict[str, Any]:
        """Compare paired outcomes by frozen-population order and identity."""
        if left.session_fingerprint != self.session_fingerprint or right.session_fingerprint != self.session_fingerprint:
            raise V3ExitEngineError("variants do not belong to this exact research session")
        if len(left.trades) != len(right.trades) or len(left.trades) != len(self._population):
            raise V3ExitEngineError("variants do not share this engine's frozen population")
        paired = []
        for index, (a, b, candidate) in enumerate(zip(left.trades, right.trades, self._population)):
            expected_identity = (
                int(candidate["trigger_time"]),
                str(candidate["direction"]),
                float(candidate["theoretical_entry"]),
                float(candidate["sl"]),
                float(candidate["risk"]),
            )
            left_identity = (
                int(a["trigger_time"]),
                str(a["direction"]),
                float(a["theoretical_entry"]),
                float(a["initial_sl"]),
                float(a["risk"]),
            )
            right_identity = (
                int(b["trigger_time"]),
                str(b["direction"]),
                float(b["theoretical_entry"]),
                float(b["initial_sl"]),
                float(b["risk"]),
            )
            if left_identity != expected_identity or right_identity != expected_identity:
                raise V3ExitEngineError("frozen trade identity mismatch")
            identity = expected_identity
            a_r = a["realized_R"]
            b_r = b["realized_R"]
            paired.append({
                "population_index": index,
                "trigger_time": identity[0],
                "direction": identity[1],
                "left_variant": left.name,
                "right_variant": right.name,
                "left_reason": a["reason"],
                "right_reason": b["reason"],
                "left_ambiguous": a["ambiguous"],
                "right_ambiguous": b["ambiguous"],
                "left_realized_R": a_r,
                "right_realized_R": b_r,
                "delta_R": (b_r - a_r) if a_r is not None and b_r is not None else None,
                "outcome_changed": (
                    a["reason"] != b["reason"]
                    or a["ambiguous"] != b["ambiguous"]
                    or a_r != b_r
                ),
            })
        return {
            "left_variant": left.name,
            "right_variant": right.name,
            "paired_trade_count": len(paired),
            "changed_outcome_count": sum(1 for row in paired if row["outcome_changed"]),
            "paired_trades": paired,
        }
