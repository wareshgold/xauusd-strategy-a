"""F21-F25 source-first SP2L geometry discrimination fixtures.

These fixtures encode only source-safe relationships. They deliberately do not
select an unresolved P-Gap formula, Entry anchor, SL wick/body rule, pending
replacement threshold, or universal bearish geometry.
"""
from dataclasses import dataclass
from enum import Enum


class Direction(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"


class OrderAction(str, Enum):
    KEEP = "keep"
    REPLACE = "replace"
    UNRESOLVED = "unresolved"


class GapConstruction(str, Enum):
    BREAKOUT_THEN_GAP = "breakout_then_gap"
    GAP_AFTER_STRUCTURAL_SEQUENCE = "gap_after_structural_sequence"


class StopAnchor(str, Enum):
    STRUCTURAL_INVALIDATION = "structural_invalidation"
    WICK = "wick"
    BODY = "body"
    PIVOT = "pivot"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class EntryCandidate:
    direction: Direction
    mechanism: str
    anchor: str


@dataclass(frozen=True)
class BearishMirror:
    direction: Direction
    structure: str
    entry: str
    invalidation: str
    leg2: str


def source_safe_pgap_candidates() -> set[GapConstruction]:
    """Observed source constructions; no generic FVG substitution."""
    return {
        GapConstruction.BREAKOUT_THEN_GAP,
        GapConstruction.GAP_AFTER_STRUCTURAL_SEQUENCE,
    }


def generic_three_candle_imbalance_is_canonical() -> bool:
    return False


def source_safe_entry_candidates(direction: Direction) -> set[EntryCandidate]:
    if direction is Direction.BULLISH:
        return {
            EntryCandidate(direction, "pending_limit", "first_or_relevant_structural_low"),
            EntryCandidate(direction, "pending_limit", "evolving_relevant_higher_low"),
        }
    return {
        EntryCandidate(direction, "pending_limit", "first_or_relevant_structural_high"),
        EntryCandidate(direction, "pending_limit", "evolving_relevant_lower_high"),
    }


def entry_equals_leg2_start_is_canonical() -> bool:
    return False


def source_safe_stop_model() -> StopAnchor:
    return StopAnchor.STRUCTURAL_INVALIDATION


def exact_stop_ohlc_anchor_is_resolved() -> bool:
    return False


def pending_update(materially_different: bool | None) -> OrderAction:
    """Source permits replacement for material change; threshold remains unresolved."""
    if materially_different is None:
        return OrderAction.UNRESOLVED
    return OrderAction.REPLACE if materially_different else OrderAction.KEEP


def bearish_mirror_abstraction() -> BearishMirror:
    return BearishMirror(
        direction=Direction.BEARISH,
        structure="Lower Highs -> Breakout -> P-Gap -> Correction -> Leg 2",
        entry="Sell Limit at relevant structural High candidate",
        invalidation="Structural High invalidation candidate",
        leg2="Second bearish continuation leg",
    )


def bearish_geometry_is_universally_source_proven() -> bool:
    return False


def production_freeze_allowed() -> bool:
    return False
