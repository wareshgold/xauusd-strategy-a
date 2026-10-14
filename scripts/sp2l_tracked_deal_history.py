"""Fetch lifecycle deals by runner-owned MT5 order/position IDs.

Avoid host-UTC time windows when broker timestamps use a different clock basis.
Callers must supply only IDs they own or have explicitly reconciled.
A failed MT5 history query is not equivalent to a valid empty result.
"""
from __future__ import annotations


class DealHistoryQueryError(RuntimeError):
    """An MT5 history query failed or returned None instead of a result."""

    def __init__(self, query: str, target: int, detail: str):
        self.query = query
        self.target = int(target)
        self.detail = detail
        super().__init__(f"{query}({target}) failed: {detail}")


def _history_result(function, query: str, target: int, **kwargs):
    if not callable(function):
        raise DealHistoryQueryError(query, target, "query function unavailable")
    try:
        result = function(**kwargs)
    except Exception as exc:
        raise DealHistoryQueryError(query, target, f"{type(exc).__name__}: {exc}") from exc
    if result is None:
        raise DealHistoryQueryError(query, target, "MT5 returned None")
    return result


def collect_tracked_deals(*, history_deals_get, history_orders_get, symbol, tracked_orders, tracked_positions):
    orders = {int(x) for x in tracked_orders if int(x) > 0}
    positions = {int(x) for x in tracked_positions if int(x) > 0}
    found = {}

    for order_id in sorted(orders):
        # MT5's empty tuple means no matching order; None or an exception means
        # the query failed and reconciliation must be deferred for this poll.
        if history_orders_get is not None:
            historical_orders = _history_result(
                history_orders_get, "history_orders_get", order_id, ticket=order_id
            )
            for order in historical_orders:
                if str(getattr(order, "symbol", symbol) or symbol) != symbol:
                    continue
                if int(getattr(order, "ticket", 0) or 0) != order_id:
                    continue
                position_id = int(getattr(order, "position_id", 0) or 0)
                if position_id > 0:
                    positions.add(position_id)

        order_deals = _history_result(
            history_deals_get, "history_deals_get(ticket)", order_id, ticket=order_id
        )
        for deal in order_deals:
            if str(getattr(deal, "symbol", symbol) or symbol) != symbol:
                continue
            if int(getattr(deal, "order", 0) or 0) != order_id:
                continue
            found[int(deal.ticket)] = deal
            position_id = int(getattr(deal, "position_id", 0) or 0)
            if position_id > 0:
                positions.add(position_id)

    for position_id in sorted(positions):
        position_deals = _history_result(
            history_deals_get, "history_deals_get(position)", position_id, position=position_id
        )
        for deal in position_deals:
            if str(getattr(deal, "symbol", symbol) or symbol) != symbol:
                continue
            deal_order = int(getattr(deal, "order", 0) or 0)
            deal_position = int(getattr(deal, "position_id", 0) or 0)
            if deal_order not in orders and deal_position not in positions:
                continue
            found[int(deal.ticket)] = deal

    return sorted(found.values(), key=lambda d: (int(d.time), int(d.ticket)))
