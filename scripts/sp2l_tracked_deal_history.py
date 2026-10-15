"""Fetch lifecycle deals through runner-owned MT5 position IDs.

MT5's history_deals_get(ticket=...) selects a DEAL ticket, not an order ticket.
Resolve tracked order IDs through history_orders_get(ticket=...), then query
history_deals_get(position=...) for each linked position. A failed query is not
equivalent to a valid empty result. No host-UTC time window is used.
"""
from __future__ import annotations


class DealHistoryQueryError(RuntimeError):
    """An MT5 history query failed or returned None instead of a result."""

    def __init__(self, query: str, target: int, detail: str):
        self.query = query
        self.target = int(target)
        self.detail = detail
        super().__init__(f"{query}({target}) failed: {detail}")


def _last_error_text(last_error) -> str:
    if not callable(last_error):
        return "last_error unavailable"
    try:
        return repr(last_error())
    except Exception as exc:
        return f"last_error raised {type(exc).__name__}: {exc}"


def _history_result(function, query: str, target: int, *, last_error=None, **kwargs):
    if not callable(function):
        raise DealHistoryQueryError(query, target, "query function unavailable")
    try:
        result = function(**kwargs)
    except Exception as exc:
        detail = f"{type(exc).__name__}: {exc}; mt5_last_error={_last_error_text(last_error)}"
        raise DealHistoryQueryError(query, target, detail) from exc
    if result is None:
        detail = f"MT5 returned None; mt5_last_error={_last_error_text(last_error)}"
        raise DealHistoryQueryError(query, target, detail)
    return result


def collect_tracked_deals(
    *,
    history_deals_get,
    history_orders_get,
    symbol,
    tracked_orders,
    tracked_positions,
    last_error=None,
):
    orders = {int(x) for x in tracked_orders if int(x) > 0}
    positions = {int(x) for x in tracked_positions if int(x) > 0}
    found = {}

    # Resolve order -> position using the order-history API. Do not pass an
    # order ID to history_deals_get(ticket=...), whose ticket argument denotes
    # a deal ticket and can trigger a misleading repeated query failure.
    if orders and not callable(history_orders_get):
        target = min(orders)
        raise DealHistoryQueryError(
            "history_orders_get(ticket)", target, "query function unavailable"
        )

    for order_id in sorted(orders):
        historical_orders = _history_result(
            history_orders_get,
            "history_orders_get(ticket)",
            order_id,
            last_error=last_error,
            ticket=order_id,
        )
        for order in historical_orders:
            if str(getattr(order, "symbol", symbol) or symbol) != symbol:
                continue
            if int(getattr(order, "ticket", 0) or 0) != order_id:
                continue
            position_id = int(getattr(order, "position_id", 0) or 0)
            if position_id > 0:
                positions.add(position_id)

    for position_id in sorted(positions):
        position_deals = _history_result(
            history_deals_get,
            "history_deals_get(position)",
            position_id,
            last_error=last_error,
            position=position_id,
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
