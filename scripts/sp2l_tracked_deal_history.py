"""Fetch lifecycle deals by runner-owned MT5 order/position IDs.

Avoid host-UTC time windows when broker timestamps use a different clock basis.
Callers must supply only IDs they own or have explicitly reconciled.
"""
from __future__ import annotations


def collect_tracked_deals(*, history_deals_get, history_orders_get, symbol, tracked_orders, tracked_positions):
    orders = {int(x) for x in tracked_orders if int(x) > 0}
    positions = {int(x) for x in tracked_positions if int(x) > 0}
    found = {}

    for order_id in sorted(orders):
        try:
            historical_orders = history_orders_get(ticket=order_id) or []
        except Exception:
            historical_orders = []
        for order in historical_orders:
            if str(getattr(order, "symbol", symbol) or symbol) != symbol:
                continue
            if int(getattr(order, "ticket", 0) or 0) != order_id:
                continue
            position_id = int(getattr(order, "position_id", 0) or 0)
            if position_id > 0:
                positions.add(position_id)

        try:
            order_deals = history_deals_get(ticket=order_id) or []
        except Exception:
            order_deals = []
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
        try:
            position_deals = history_deals_get(position=position_id) or []
        except Exception:
            position_deals = []
        for deal in position_deals:
            if str(getattr(deal, "symbol", symbol) or symbol) != symbol:
                continue
            deal_order = int(getattr(deal, "order", 0) or 0)
            deal_position = int(getattr(deal, "position_id", 0) or 0)
            if deal_order not in orders and deal_position not in positions:
                continue
            found[int(deal.ticket)] = deal

    return sorted(found.values(), key=lambda d: (int(d.time), int(d.ticket)))
