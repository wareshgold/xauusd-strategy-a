"""F11: pending-limit lifecycle without inventing a replacement threshold.

Research-only. KEEP/DELETE/REPLACE are explicit states; the numerical
materiality threshold remains unresolved because the source does not provide
one in the currently resolved evidence.
"""

from dataclasses import dataclass
from enum import Enum


class OrderAction(str, Enum):
    KEEP = "KEEP"
    DELETE = "DELETE"
    REPLACE = "REPLACE"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class PendingOrder:
    price: float
    structural_stop: float


def stop_distance(order: PendingOrder) -> float:
    return abs(order.price - order.structural_stop)


def compare_pending_order(old: PendingOrder, new: PendingOrder) -> OrderAction:
    """Return only what source evidence currently supports.

    The source supports that a materially changed distance may justify
    delete/re-place, but does not supply a deterministic threshold. Therefore
    a numeric comparison alone cannot authorize REPLACE.
    """
    if old == new:
        return OrderAction.KEEP
    return OrderAction.UNRESOLVED


def explicit_management_decision(materially_different: bool) -> OrderAction:
    """Represent the source-level qualitative decision without quantifying it."""
    return OrderAction.REPLACE if materially_different else OrderAction.KEEP
