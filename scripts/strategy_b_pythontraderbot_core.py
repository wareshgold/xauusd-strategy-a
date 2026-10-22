"""Source-aligned, offline-only Strategy B core.

Mirrors the live PythonTraderBot SP2L_Advanced_Bot_Optimized.py logic for
setup geometry and pending-entry qualification. No MT5, network, order,
Telegram, or file side effects are permitted in this module.

Source reference (reviewed 2026-10-22):
https://github.com/AlirezaSadabadi/PythonTraderBot/blob/main/code/SP2L/SP2L_Advanced_Bot_Optimized.py
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence

Direction = Literal["BUY", "SELL"]


@dataclass(frozen=True)
class StrategyBConfig:
    spike_candle_size: float = 1.5
    p_gap_points: float = 100.0
    max_sl_distance_points: float = 1000.0
    tp_r: float = 0.9
    use_lowerlow_higherhigh_sl: bool = False
    use_ema_filter: bool = True
    ema_period: int = 60
    use_trend_filter: bool = True
    max_opposite_moves: int = 1
    use_range_filter: bool = False
    min_adx: float = 20.0
    use_adx_rising_filter: bool = False
    use_session_filter: bool = False
    session_start_hour: int = 1
    session_end_hour: int = 5


@dataclass(frozen=True)
class Setup:
    direction: Direction
    setup_time: int | str
    setup_pos: int
    sl: float
    spike_body: float


@dataclass(frozen=True)
class EntryCandidate:
    direction: Direction
    setup_time: int | str
    entry_time: int | str
    entry: float
    sl: float
    tp: float
    risk: float
    spike_body: float


def _v(candle: dict, name: str) -> float:
    return float(candle[name])


def _body(candle: dict) -> float:
    return abs(_v(candle, "close") - _v(candle, "open"))


def detect_setup(
    candles: Sequence[dict],
    *,
    broker_point: float,
    config: StrategyBConfig = StrategyBConfig(),
) -> Setup | None:
    """Detect the source live bot's current/forming-candle BUY or SELL setup.

    Input rows must be chronological and the final row is the current,
    potentially forming M1 candle. Source inequalities are kept strict.
    """
    if broker_point <= 0:
        raise ValueError("broker_point must be > 0")
    if len(candles) < 5:
        return None

    before, spike, post, current = candles[-4], candles[-3], candles[-2], candles[-1]
    p_gap = config.p_gap_points * broker_point
    buy = (
        _v(current, "low") < _v(post, "low")
        and _v(post, "close") > _v(spike, "close")
        and _v(post, "open") > _v(spike, "open")
        and _v(spike, "close") > _v(before, "close")
        and _v(spike, "open") > _v(before, "open")
        and _v(post, "close") > _v(post, "open")
        and _v(spike, "close") > _v(spike, "open")
        and _v(before, "close") > _v(before, "open")
        and _v(post, "low") > _v(before, "high") + p_gap
        and (_v(spike, "close") - _v(spike, "open"))
        > config.spike_candle_size * (_v(post, "close") - _v(post, "open"))
        and (_v(spike, "close") - _v(spike, "open"))
        > config.spike_candle_size * (_v(before, "close") - _v(before, "open"))
    )
    sell = (
        _v(current, "high") > _v(post, "high")
        and _v(post, "close") < _v(spike, "close")
        and _v(post, "open") < _v(spike, "open")
        and _v(spike, "close") < _v(before, "close")
        and _v(spike, "open") < _v(before, "open")
        and _v(post, "close") < _v(post, "open")
        and _v(spike, "close") < _v(spike, "open")
        and _v(before, "close") < _v(before, "open")
        and _v(post, "high") < _v(before, "low") - p_gap
        and (_v(spike, "open") - _v(spike, "close"))
        > config.spike_candle_size * (_v(post, "open") - _v(post, "close"))
        and (_v(spike, "open") - _v(spike, "close"))
        > config.spike_candle_size * (_v(before, "open") - _v(before, "close"))
    )
    # Source creates a pending setup only when exactly one direction is true.
    if buy == sell:
        return None

    direction: Direction = "BUY" if buy else "SELL"
    sl = (
        _find_pivot_sl(candles, direction)
        if config.use_lowerlow_higherhigh_sl
        else (_v(before, "low") if direction == "BUY" else _v(before, "high"))
    )
    if sl is None:
        return None
    stamp = current.get("time", current.get("timestamp", len(candles) - 1))
    return Setup(direction, stamp, len(candles) - 1, float(sl), _body(spike))


def _find_pivot_sl(candles: Sequence[dict], direction: Direction) -> float | None:
    # Source scans backward from the candle before the spike (-4).
    for pos in range(len(candles) - 4, 0, -1):
        if direction == "BUY":
            value = _v(candles[pos], "low")
            if value < _v(candles[pos - 1], "low") and value < _v(candles[pos + 1], "low"):
                return value
        else:
            value = _v(candles[pos], "high")
            if value > _v(candles[pos - 1], "high") and value > _v(candles[pos + 1], "high"):
                return value
    return None


def _ema(values: Sequence[float], period: int) -> list[float]:
    alpha = 2.0 / (period + 1.0)
    out: list[float] = []
    for value in values:
        out.append(value if not out else alpha * value + (1.0 - alpha) * out[-1])
    return out


def evaluate_pending_entry(
    candles: Sequence[dict],
    setup: Setup,
    *,
    broker_point: float,
    config: StrategyBConfig = StrategyBConfig(),
) -> EntryCandidate | Literal["INVALID"] | None:
    """Check source pending setup against the current/forming candle.

    None means not triggered or filtered; INVALID means source max-SL/side
    risk check clears the pending setup. It deliberately does not expire a
    setup, place an order, or infer broker fills.
    """
    if len(candles) < 2 or broker_point <= 0:
        return None
    current, previous = candles[-1], candles[-2]
    if setup.direction == "BUY":
        if _v(current, "low") >= _v(previous, "low"):
            return None
        entry = _v(current, "low")
        risk = entry - setup.sl
    else:
        if _v(current, "high") <= _v(previous, "high"):
            return None
        entry = _v(current, "high")
        risk = setup.sl - entry

    if risk <= 0:
        return None
    if risk > config.max_sl_distance_points * broker_point:
        return "INVALID"

    entry_time = current.get("time", current.get("timestamp", len(candles) - 1))
    # The source locates setup_pos_time in the current dataframe on every
    # poll. Re-find it by timestamp rather than retaining an index that can
    # drift when the rolling 500-bar window advances.
    setup_pos = next(
        (
            i for i, row in enumerate(candles)
            if row.get("time", row.get("timestamp", i)) == setup.setup_time
        ),
        None,
    )
    if setup_pos is None:
        return None

    if config.use_trend_filter:
        opposite = 0
        for pos in range(setup_pos + 1, len(candles)):
            if setup.direction == "BUY":
                favorable = _v(candles[pos], "high") > _v(candles[pos - 1], "high")
            else:
                favorable = _v(candles[pos], "low") < _v(candles[pos - 1], "low")
            opposite = 0 if favorable else opposite + 1
            if opposite > config.max_opposite_moves:
                return None

    if config.use_ema_filter:
        closes = [_v(row, "close") for row in candles]
        # The live observer supplies EMA calculated with the source bot's
        # cached/incremental semantics. Offline fixtures may omit it.
        current_ema = (
            float(candles[-1]["ema"])
            if candles[-1].get("ema") is not None
            else _ema(closes, config.ema_period)[-1]
        )
        if setup.direction == "BUY" and closes[-1] <= current_ema:
            return None
        if setup.direction == "SELL" and closes[-1] >= current_ema:
            return None

    if config.use_range_filter:
        adx = current.get("adx")
        if adx is None or float(adx) < config.min_adx:
            return None

    if config.use_adx_rising_filter:
        if len(candles) < 3:
            return None
        a, b = candles[-2].get("adx"), candles[-3].get("adx")
        if a is None or b is None or float(a) <= float(b):
            return None

    if config.use_session_filter:
        # The source localizes naive timestamps to Etc/GMT-3, then converts
        # to America/New_York. Timezone interpretation is delegated to the
        # MT5 adapter; this pure core fails closed without an explicit hour.
        session_hour = current.get("new_york_hour")
        if session_hour is None:
            return None
        hour = int(session_hour)
        if not (config.session_start_hour <= hour < config.session_end_hour):
            return None

    reward = config.tp_r * risk
    tp = entry + reward if setup.direction == "BUY" else entry - reward
    return EntryCandidate(
        direction=setup.direction,
        setup_time=setup.setup_time,
        entry_time=entry_time,
        entry=entry,
        sl=setup.sl,
        tp=tp,
        risk=risk,
        spike_body=setup.spike_body,
    )
