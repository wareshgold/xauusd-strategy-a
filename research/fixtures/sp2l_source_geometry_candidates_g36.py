"""Explicit research-only candidate registry for unresolved SP2L geometry.

This module intentionally contains hypotheses, not canonical Strategy A rules.
A candidate must never be promoted solely because it backtests better.
"""

from dataclasses import dataclass
from enum import Enum


class Resolution(str, Enum):
    CONFIRMED = "CONFIRMED"
    UNRESOLVED = "UNRESOLVED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class GeometryCandidate:
    blocker: str
    name: str
    resolution: Resolution
    source_basis: str
    forbidden_assumption: str | None = None


CANDIDATES = (
    GeometryCandidate("B1", "adjacent-range-separation", Resolution.UNRESOLVED,
                      "source shows breakout/follow-through with P-Gap separation",
                      "must not be generalized to generic three-candle FVG"),
    GeometryCandidate("B2", "relevant-structural-extreme", Resolution.UNRESOLVED,
                      "pending Buy/Sell Limit is placed during correction at a relevant structural level",
                      "must not assume original spike extreme, Leg2 start, body edge, or wick extreme"),
    GeometryCandidate("B3", "structural-invalidation", Resolution.UNRESOLVED,
                      "source separates Entry from SL and uses structural invalidation",
                      "must not substitute fixed distance, ATR, or risk percentage"),
    GeometryCandidate("B4", "one-two-three-candle-or-key-bar-trigger", Resolution.UNRESOLVED,
                      "source explicitly demonstrates multiple trigger constructions",
                      "must not substitute market close-reclaim"),
    GeometryCandidate("B5", "abcd-magnitude", Resolution.UNRESOLVED,
                      "source explicitly states AB=CD / equal-leg relationship",
                      "must not invent anchors or tolerance"),
    GeometryCandidate("B6", "leg2-projection", Resolution.UNRESOLVED,
                      "source describes first leg, second leg, TP1/TP2 and 2X",
                      "must not invent executable projection formula"),
)


def unresolved_blockers() -> tuple[str, ...]:
    return tuple(sorted({candidate.blocker for candidate in CANDIDATES
                         if candidate.resolution is Resolution.UNRESOLVED}))
