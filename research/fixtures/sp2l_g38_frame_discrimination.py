"""Source-neutral discrimination fixtures for SP2L G38.

These tests model only logical source constraints. They do not claim to encode
canonical Strategy A OHLC geometry.
"""
from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    CONFIRMED = "CONFIRMED"
    UNRESOLVED = "UNRESOLVED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class Candidate:
    name: str
    satisfies_source_constraints: bool


def classify_candidates(candidates: list[Candidate]) -> Decision:
    valid = [c for c in candidates if c.satisfies_source_constraints]
    if len(valid) == 1:
        return Decision.CONFIRMED
    if len(valid) == 0:
        return Decision.REJECTED
    return Decision.UNRESOLVED


def p_gap_candidates() -> list[Candidate]:
    # Generic FVG cannot be treated as canonical merely because it resembles
    # some source drawings; multiple source-consistent constructions remain.
    return [
        Candidate("breakout_followthrough_separation", True),
        Candidate("generic_three_candle_fvg", False),
        Candidate("alternate_source_gap_construction", True),
    ]


def entry_candidates() -> list[Candidate]:
    return [
        Candidate("relevant_structural_pivot", True),
        Candidate("fixed_original_spike_extreme", True),
    ]


def abcd_candidates() -> list[Candidate]:
    return [
        Candidate("wick_anchor", True),
        Candidate("body_anchor", True),
        Candidate("structural_pivot_anchor", True),
    ]
