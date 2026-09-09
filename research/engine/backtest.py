from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from .models import Candle, Order, OrderStatus, OrderType, Side, Trade


@dataclass(frozen=True)
class ExecutionPolicy:
    """Explicit intrabar policy for deterministic research mechanics.

    When both protective levels are touched by one candle and tick ordering is
    unavailable, stop-first is conservative. This is an execution convention,
    not a Strategy A rule.
    """

    stop_first_on_conflict: bool = True


class BacktestEngine:
    """Strategy-neutral candle backtester.

    A strategy supplies already-resolved orders. The engine never decides
    whether a market pattern is valid and never creates a Strategy A order.
    """

    def __init__(self, policy: ExecutionPolicy | None = None) -> None:
        self.policy = policy or ExecutionPolicy()

    def run(self, candles: Iterable[Candle], orders: Iterable[Order]) -> list[Trade]:
        bars = sorted(candles, key=lambda c: c.timestamp)
        pending = [o for o in orders if o.status is OrderStatus.PENDING]
        trades: list[Trade] = []

        for bar in bars:
            still_pending: list[Order] = []
            for order in pending:
                if order.created_at > bar.timestamp:
                    still_pending.append(order)
                    continue
                fill_price = self._fill_price(order, bar)
                if fill_price is None:
                    still_pending.append(order)
                    continue
                order.status = OrderStatus.FILLED
                trade = Trade(order.order_id, order.side, bar.timestamp, fill_price, order.quantity,
                              order.stop_loss, order.take_profit, setup_id=order.setup_id,
                              metadata=dict(order.metadata))
                self._resolve_exit(trade, bar)
                trades.append(trade)
            pending = still_pending + [o for o in pending if o.status is OrderStatus.FILLED]

            # Existing trades may span multiple candles.
            for trade in trades:
                if trade.exit_time is None and trade.entry_time < bar.timestamp:
                    self._resolve_exit(trade, bar)

        return trades

    @staticmethod
    def _fill_price(order: Order, bar: Candle) -> Optional[float]:
        if order.order_type is OrderType.MARKET:
            return bar.open if order.created_at <= bar.timestamp else None
        if order.price is None:
            raise ValueError("non-market order requires price")
        if order.order_type is OrderType.LIMIT:
            if order.side is Side.BUY and bar.low <= order.price:
                return order.price
            if order.side is Side.SELL and bar.high >= order.price:
                return order.price
        elif order.order_type is OrderType.STOP:
            if order.side is Side.BUY and bar.high >= order.price:
                return order.price
            if order.side is Side.SELL and bar.low <= order.price:
                return order.price
        return None

    def _resolve_exit(self, trade: Trade, bar: Candle) -> None:
        if trade.exit_time is not None:
            return
        stop_hit = self._stop_hit(trade, bar)
        target_hit = self._target_hit(trade, bar)
        if not stop_hit and not target_hit:
            return
        if stop_hit and target_hit:
            if self.policy.stop_first_on_conflict:
                trade.exit_price, trade.exit_reason = trade.stop_loss, "STOP"
            else:
                trade.exit_price, trade.exit_reason = trade.take_profit, "TARGET"
        elif stop_hit:
            trade.exit_price, trade.exit_reason = trade.stop_loss, "STOP"
        else:
            trade.exit_price, trade.exit_reason = trade.take_profit, "TARGET"
        trade.exit_time = bar.timestamp

    @staticmethod
    def _stop_hit(trade: Trade, bar: Candle) -> bool:
        if trade.stop_loss is None:
            return False
        return bar.low <= trade.stop_loss if trade.side is Side.BUY else bar.high >= trade.stop_loss

    @staticmethod
    def _target_hit(trade: Trade, bar: Candle) -> bool:
        if trade.take_profit is None:
            return False
        return bar.high >= trade.take_profit if trade.side is Side.BUY else bar.low <= trade.take_profit
