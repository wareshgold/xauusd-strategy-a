from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional

from .models import Candle, Fill, Order, OrderStatus, OrderType, Side, Trade


class IntrabarPolicy(str, Enum):
    """Explicit policy for OHLC bars that touch multiple executable levels."""

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
    for start, end in zip(path, path[1:]):
        hits = [level for level in levels if _crossed(start, end, level)]
        if hits:
            return min(hits, key=lambda level: abs(level - start))
    return None


class SyntheticExecutionRunner:
    """Strategy-neutral OHLC event runner.

    It deliberately refuses to resolve same-bar ambiguity unless an explicit
    intrabar policy is supplied. It does not create or infer Strategy A setups.
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
                    # A LIMIT fill can be inferred from a simple touch, but once
                    # post-fill SL/TP outcomes can also be touched in the same bar,
                    # the ordering is not knowable from OHLC alone.
                    if not (candle.low <= order.price <= candle.high):
                        continue
                    events.append(ExecutionEvent(candle.timestamp, EventType.UNRESOLVED, order_id, order.price, "intrabar_ordering"))
                    continue

                path = _path(candle, self.config.intrabar_policy)
                fill = _first_cross(path, (order.price,))
                if fill is None:
                    continue

                order.status = OrderStatus.FILLED
                events.append(ExecutionEvent(candle.timestamp, EventType.FILL, order_id, fill))
                pending.pop(order_id)
                trades.append(Trade(order_id, order.side, candle.timestamp, fill, order.quantity,
                                    order.stop_loss, order.take_profit, setup_id=order.setup_id,
                                    metadata={"intrabar_policy": self.config.intrabar_policy.value}))

                exit_levels = []
                if order.stop_loss is not None:
                    exit_levels.append((order.stop_loss, EventType.STOP))
                if order.take_profit is not None:
                    exit_levels.append((order.take_profit, EventType.TARGET))
                if not exit_levels:
                    continue

                hit = _first_cross(path, (level for level, _ in exit_levels if level != fill))
                if hit is None:
                    continue
                event_type = next(kind for level, kind in exit_levels if level == hit)
                trade = trades[-1]
                trade.exit_time = candle.timestamp
                trade.exit_price = hit
                trade.exit_reason = event_type.value
                events.append(ExecutionEvent(candle.timestamp, event_type, order_id, hit))

        return events, trades
