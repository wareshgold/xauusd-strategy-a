"""Fail-closed inventory classification for the V3.1 entry guard.

Operational safety only: this module does not define SP2L geometry or signals.
"""

from __future__ import annotations


def inspect_owned_exposure(*, symbol: str, magic: int, orders, positions) -> dict:
    """Classify active broker inventory for one V3.1 symbol/magic.

    None means MT5 query failure and is never treated as an empty result.
    The caller must pass the direct results of orders_get/positions_get.
    """
    if orders is None or positions is None:
        missing = []
        if orders is None:
            missing.append("orders")
        if positions is None:
            missing.append("positions")
        return {
            "ok": False,
            "active": False,
            "reason": "BROKER_INVENTORY_UNAVAILABLE",
            "failed_queries": missing,
            "order_tickets": [],
            "position_tickets": [],
        }

    target_symbol = str(symbol)
    target_magic = int(magic)

    def matching_tickets(items):
        tickets = []
        for item in items:
            item_symbol = str(getattr(item, "symbol", target_symbol) or target_symbol)
            if item_symbol != target_symbol:
                continue
            try:
                item_magic = int(getattr(item, "magic", 0) or 0)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError("malformed broker inventory magic") from exc
            if item_magic != target_magic:
                continue
            try:
                ticket = int(getattr(item, "ticket", 0) or 0)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError("malformed broker inventory ticket") from exc
            tickets.append(ticket)

        return sorted(tickets)

    order_tickets = matching_tickets(orders)
    position_tickets = matching_tickets(positions)
    active = bool(order_tickets or position_tickets)
    if order_tickets and position_tickets:
        reason = "OWN_ORDER_AND_POSITION_ACTIVE"
    elif order_tickets:
        reason = "OWN_PENDING_ORDER_ACTIVE"
    elif position_tickets:
        reason = "OWN_POSITION_ACTIVE"
    else:
        reason = "NO_OWN_EXPOSURE"

    return {
        "ok": True,
        "active": active,
        "reason": reason,
        "failed_queries": [],
        "order_tickets": order_tickets,
        "position_tickets": position_tickets,
    }
