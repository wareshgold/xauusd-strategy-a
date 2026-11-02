"""Fail-closed startup reconciliation of V3.1-owned live broker objects.

This module classifies only currently active objects by exact symbol + magic.
It deliberately does not infer strategy geometry, replay historical signals,
or send/cancel/modify broker orders.
"""
from __future__ import annotations


class BrokerInventoryRecoveryError(RuntimeError):
    """Raised when startup broker inventory is incomplete or ambiguous."""


def recover_owned_broker_inventory(
    state: dict,
    *,
    symbol: str,
    magic: int,
    orders,
    positions,
    buy_limit_type: int,
    sell_limit_type: int,
) -> dict:
    """Add this runner's active limit orders and positions to tracking state.

    MT5's None means query failure, while an empty tuple/list is a valid
    empty inventory. Validate the complete snapshot before mutating state.
    Same-symbol/same-magic orders of an unexpected type fail closed.
    """
    if orders is None:
        raise BrokerInventoryRecoveryError(
            f"active order inventory unavailable for {symbol}"
        )
    if positions is None:
        raise BrokerInventoryRecoveryError(
            f"active position inventory unavailable for {symbol}"
        )

    owned_orders: set[int] = set()
    owned_positions: set[int] = set()
    allowed_order_types = {int(buy_limit_type), int(sell_limit_type)}

    for order in orders:
        order_symbol = str(getattr(order, "symbol", "") or "")
        order_magic = int(getattr(order, "magic", 0) or 0)
        if order_symbol != symbol or order_magic != int(magic):
            continue
        ticket = int(getattr(order, "ticket", 0) or 0)
        order_type = int(getattr(order, "type", -1))
        if ticket <= 0:
            raise BrokerInventoryRecoveryError(
                f"owned active order has invalid ticket for {symbol}"
            )
        if order_type not in allowed_order_types:
            raise BrokerInventoryRecoveryError(
                f"owned active order has unsupported type: ticket={ticket}"
            )
        owned_orders.add(ticket)

    for position in positions:
        position_symbol = str(getattr(position, "symbol", "") or "")
        position_magic = int(getattr(position, "magic", 0) or 0)
        if position_symbol != symbol or position_magic != int(magic):
            continue
        ticket = int(getattr(position, "ticket", 0) or 0)
        if ticket <= 0:
            raise BrokerInventoryRecoveryError(
                f"owned active position has invalid ticket for {symbol}"
            )
        owned_positions.add(ticket)

    state.setdefault("orders", set()).update(owned_orders)
    state.setdefault("positions", set()).update(owned_positions)
    return {
        "symbol": symbol,
        "magic": int(magic),
        "orders_recovered": len(owned_orders),
        "positions_recovered": len(owned_positions),
    }
