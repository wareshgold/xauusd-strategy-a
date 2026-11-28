"""Fail-closed inventory classification for the V3.1 entry guard.

Operational safety only: this module does not define SP2L geometry or signals.
"""

from __future__ import annotations


def inspect_owned_exposure(*, symbol: str, magic: int, orders, positions) -> dict:
    """Classify active broker inventory for one V3.1 symbol/magic.

    None means MT5 query failure and is never treated as an empty result.
    Every returned broker record must expose a valid symbol, magic and ticket;
    incomplete records are ambiguous and fail closed.
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

    target_symbol = str(symbol).strip()
    if not target_symbol:
        raise ValueError("target symbol must be non-empty")
    try:
        target_magic = int(magic)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("target magic must be an integer") from exc

    def matching_tickets(items, kind):
        tickets = []
        for index, item in enumerate(items):
            item_symbol_raw = getattr(item, "symbol", None)
            item_magic_raw = getattr(item, "magic", None)
            ticket_raw = getattr(item, "ticket", None)
            if not isinstance(item_symbol_raw, str) or not item_symbol_raw.strip():
                raise ValueError(f"broker inventory {kind}[{index}] missing/invalid symbol")
            if item_magic_raw is None:
                raise ValueError(f"broker inventory {kind}[{index}] missing magic")
            if ticket_raw is None:
                raise ValueError(f"broker inventory {kind}[{index}] missing ticket")
            try:
                item_magic = int(item_magic_raw)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError("malformed broker inventory magic") from exc
            try:
                ticket = int(ticket_raw)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError("malformed broker inventory ticket") from exc
            if ticket <= 0:
                raise ValueError("malformed broker inventory ticket: must be positive")
            if item_symbol_raw != target_symbol or item_magic != target_magic:
                continue
            tickets.append(ticket)

        if len(tickets) != len(set(tickets)):
            raise ValueError(f"duplicate owned {kind} ticket in broker inventory")
        return sorted(tickets)

    order_tickets = matching_tickets(orders, "orders")
    position_tickets = matching_tickets(positions, "positions")
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
