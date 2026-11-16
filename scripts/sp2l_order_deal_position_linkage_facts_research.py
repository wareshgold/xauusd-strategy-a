"""Source-aligned MT5 linkage facts for offline research fixtures.

This module preserves documented MT5 identifiers as separate raw fields.
It does not reconcile broker objects, infer ticket equivalence, query history,
or define execution/fill semantics. Pure Python only.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PositionFact:
    """One observed position snapshot; ticket and lifecycle ID stay distinct."""

    symbol: str
    position_ticket: int
    position_identifier: int


@dataclass(frozen=True)
class OrderFact:
    """Raw order linkage fields; order ticket and position ID are not aliases."""

    order_ticket: int
    order_position_id: Optional[int] = None
    state: Optional[str] = None
    filling_policy: Optional[str] = None
    volume_initial: Optional[float] = None
    volume_current: Optional[float] = None


@dataclass(frozen=True)
class DealFact:
    """Raw deal linkage fields; DEAL_ORDER points to an order ticket."""

    deal_ticket: int
    deal_order: int
    deal_position_id: int
    entry: Optional[str] = None
    volume: Optional[float] = None


@dataclass(frozen=True)
class CloseByFact:
    """Separate primary and opposite-position identifier references."""

    order_position_id: int
    order_position_by_id: int


def same_position_lifecycle(left: PositionFact, right: PositionFact) -> bool:
    """Compare only the documented stable POSITION_IDENTIFIER field.

    This is a pure comparison of supplied facts, not broker reconciliation.
    It deliberately does not compare POSITION_TICKET or symbol.
    """
    return left.position_identifier == right.position_identifier
