"""Fetch lifecycle deals by runner-owned MT5 order/position IDs.

Avoid host-UTC time windows when broker timestamps use a different clock basis.
Callers must supply only IDs they own or have explicitly reconciled.
MT5 history_deals_get(ticket=...) selects a DEAL ticket, not an ORDER ticket.
Resolve tracked orders with history_orders_get(ticket=...), then query linked
position histories with history_deals_get(position=...).
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


def _last_error_detail(last_error) -> str | None:
    if not callable(last_error):
        return None
    try:
        value = last_error()
    except Exception as exc:
        return f"last_error unavailable: {type(exc).__name__}: {exc}"
    return str(value)


def _history_result(function, query: str, target: int, *, last_error=None, **kwargs):
    if not callable(function):
        raise DealHistoryQueryError(query, target, "query function unavailable")
    try:
        result = function(**kwargs)
    except Exception as exc:
        detail = f"{type(exc).__name__}: {exc}"
        extra = _last_error_detail(last_error)
        if extra:
            detail = f"{detail}; MT5 last_error={extra}"
        raise DealHistoryQueryError(query, target, detail) from exc
    if result is None:
        detail = "MT5 returned None"
        extra = _last_error_detail(last_error)
        if extra:
            detail = f"{detail}; MT5 last_error={extra}"
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
    """Collect only deals linked to the supplied runner-owned IDs.

    Empty MT5 results are valid. Exceptions and None are query failures and
    raise DealHistoryQueryError so callers can defer lifecycle reconciliation.
    """
    orders = {int(x) for x in tracked_orders if int(x) > 0}
    positions = {int(x) for x in tracked_positions if int(x) > 0}

    # MT5's history_deals_get(ticket=...) expects a DEAL ticket. Resolve each
    # tracked ORDER ticket first, then use its position identifier to retrieve
    # the complete lifecycle, including the closing deal.
    for order_id in sorted(orders):
        historical_orders = _history_result(
            history_orders_get,
            "history_orders_get",
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

    found = {}
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
            if deal_order not in orders and deal_position != position_id:
                continue
            found[int(deal.ticket)] = deal

    return sorted(found.values(), key=lambda d: (int(d.time), int(d.ticket)))
