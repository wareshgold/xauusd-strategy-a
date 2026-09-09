"""F15: test whether the source-confirmed SP2L sequence can be mirrored bearish.

Research-only. Symmetry is tested, not assumed as a production rule.
"""
from dataclasses import dataclass
from enum import Enum


class Direction(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


@dataclass(frozen=True)
class MirrorCase:
    direction: Direction
    structure: tuple[str, ...]
    pending_order: str
    invalidation_relation: str


def f15_cases():
    bullish = MirrorCase(
        Direction.BULLISH,
        ("higher_lows", "breakout", "p_gap", "correction", "leg_2"),
        "buy_limit",
        "below_structural_low",
    )
    bearish = MirrorCase(
        Direction.BEARISH,
        ("lower_highs", "breakout", "p_gap", "correction", "leg_2"),
        "sell_limit",
        "above_structural_high",
    )
    return bullish, bearish


def structural_mirror(bullish: MirrorCase, bearish: MirrorCase) -> bool:
    return (
        bullish.pending_order == "buy_limit"
        and bearish.pending_order == "sell_limit"
        and bullish.invalidation_relation == "below_structural_low"
        and bearish.invalidation_relation == "above_structural_high"
        and bullish.structure[1:] == bearish.structure[1:]
    )
