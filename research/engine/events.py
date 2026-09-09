from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional

from .models import Candle, Order, OrderStatus, OrderType, Side, Trade


class IntrabarPolicy(str, Enum):
    OHLC_PATH = "OHLC_PATH"
    OLHC_PATH = "OLHC_PATH"
    UNRESOLVED = "UNRESOLVED"


class EventType(str, Enum):
    BAR = "BAR"
    FILL = "FILL"
    STOP = "STOP"
    TARGET = "TARGET"
    CANCEL = "CANCEL"
    EXPIRE = "EXPIRE"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class ExecutionEvent:
    timestamp: object
    event_type: EventType
    order_id: Optional[str] = None
    price: Optional[float] = None
    reason: Optional[str] = None


@dataclass(frozen=True)
class ExecutionConfig:
    intrabar_policy: IntrabarPolicy = IntrabarPolicy.UNRESOLVED
    expire_after_bars: Optional[int] = None


def _path(candle: Candle, policy: IntrabarPolicy) -> tuple[float, ...]:
    if policy is IntrabarPolicy.OHLC_PATH:
        return (candle.open, candle.high, candle.low, candle.close)
    if policy is IntrabarPolicy.OLHC_PATH:
        return (candle.open, candle.low, candle.high, candle.close)
    raise ValueError("intrabar path is unresolved")


def _crossed(a: float, b: float, level: float) -> bool:
    return min(a, b) <= level <= max(a, b)


def _first_cross(path: tuple[float, ...], levels: Iterable[float]) -> Optional[float]:
    levels = tuple(levels)
    for start, end in zip(path, path[1:]):
        hits = [level for level in levels if _crossed(start, end, level)]
        if hits:
            return min(hits, key=lambda level: abs(level - start))
    return None


def _tail_from_level(path: tuple[float, ...], level: float) -> tuple[float, ...]:
    """Return the price path starting at the first occurrence of level."""
    for index, (start, end) in enumerate(zip(path, path[1:])):
        if _crossed(start, end, level):
            return (level,) + path[index + 1 :]
    return (level,)


class SyntheticExecutionRunner:
    """Strategy-neutral OHLC event runner.

    Same-bar outcomes are only resolved when an explicit intrabar path policy
    is supplied. With UNRESOLVED, a touched pending order emits an ambiguity
    event instead of manufacturing an execution result.
    """

    def __init__(self, config: ExecutionConfig = ExecutionConfig()) -> None:
        self.config = config

    def run(self, candles: Iterable[Candle], orders: Iterable[Order]) -> tuple[list[ExecutionEvent], list[Trade]]:
        bars = list(candles)
        pending = {order.order_id: order for order in orders if order.status is OrderStatus.PENDING}
        events: list[ExecutionEvent] = []
        trades: list[Trade] = []
        age = {order_id: 0 for order_id in pending}

        for candle in bars:
            events.append(ExecutionEvent(candle.timestamp, EventType.BAR))
            for order_id in list(pending):
                order = pending[order_id]
                age[order_id] += 1

                if self.config.expire_after_bars is not None and age[order_id] > self.config.expire_after_bars:
                    order.status = OrderStatus.EXPIRED
                    events.append(ExecutionEvent(candle.timestamp, EventType.EXPIRE, order_id, reason="bar_age"))
                    del pending[order_id]
                    continue

                if order.order_type is not OrderType.LIMIT or order.price is None:
                    continue

                if self.config.intrabar_policy is IntrabarPolicy.UNRESOLVED:
                    if candle.low <= order.price <= candle.high:
                        events.append(ExecutionEvent(candle.timestamp, EventType.UNRESOLVED, order_id, order.price, "intrabar_ordering"))
                    continue

                path = _path(candle, self.config.intrabar_policy)
                fill = _first_cross(path, (order.price,))
                if fill is None:
                    continue

                order.status = OrderStatus.FILLED
                events.append(ExecutionEvent(candle.timestamp, EventType.FILL, order_id, fill))
                pending.pop(order_id)
                trade = Trade(order_id, order.side, candle.timestamp, fill, order.quantity,
                              order.stop_loss, order.take_profit, setup_id=order.setup_id,
                              metadata={"intrabar_policy": self.config.intrabar_policy.value})
                trades.append(trade)

                exit_levels = []
                if order.stop_loss is not None:
                    exit_levels.append((order.stop_loss, EventType.STOP))
                if order.take_profit is not None:
                    exit_levels.append((order.take_profit, EventType.TARGET))
                if not exit_levels:
                    continue

                post_fill_path = _tail_from_level(path, fill)
                hit = _first_cross(post_fill_path, (level for level, _ in exit_levels if level != fill))
                if hit is None:
                    continue
                event_type = next(kind for level, kind in exit_levels if level == hit)
                trade.exit_time = candle.timestamp
                trade.exit_price = hit
                trade.exit_reason = event_type.value
                events.append(ExecutionEvent(candle.timestamp, event_type, order_id, hit))

        return events, trades
