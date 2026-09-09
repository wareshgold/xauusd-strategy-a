from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Resolution(str, Enum):
    SUPPORTED = "SUPPORTED"
    REJECTED = "REJECTED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class DiscriminationCase:
    blocker: str
    candidate_id: str
    source_evidence: str
    resolution: Resolution
    reason: str


CASES = (
    DiscriminationCase("B1", "B1-PGAP-V1", "Breakout + follow-through + P-Gap is source-confirmed.", Resolution.SUPPORTED, "Candidate remains source-consistent; exact candle boundaries are not established."),
    DiscriminationCase("B1", "B1-PGAP-V2", "P-Gap is first-class and not generic FVG.", Resolution.UNRESOLVED, "Alternative boundary interpretation cannot be selected without source-unique geometry."),
    DiscriminationCase("B2", "B2-ENTRY-STRUCTURAL", "Pending Limit is placed at a relevant structural Low/High.", Resolution.SUPPORTED, "Semantic entry anchor is supported; exact OHLC boundary remains unresolved."),
    DiscriminationCase("B2", "B2-ENTRY-LATEST", "Demonstrated examples update the pending level as completed HL/LH structures form.", Resolution.UNRESOLVED, "This is a demonstrated candidate variant, not a universal source rule."),
    DiscriminationCase("B3", "B3-SL-STRUCTURAL", "Stop is tied to structural invalidation.", Resolution.SUPPORTED, "Structural invalidation is source-confirmed; exact wick/body boundary is unresolved."),
    DiscriminationCase("B4", "B4-TRIGGER-1C", "One-candle trigger form is shown.", Resolution.SUPPORTED, "Family member is source-consistent; acceptance precedence is unresolved."),
    DiscriminationCase("B4", "B4-TRIGGER-2C", "Two-candle trigger form is shown.", Resolution.SUPPORTED, "Family member is source-consistent; acceptance precedence is unresolved."),
    DiscriminationCase("B4", "B4-TRIGGER-3C", "Three-candle trigger form is shown.", Resolution.SUPPORTED, "Family member is source-consistent; acceptance precedence is unresolved."),
    DiscriminationCase("B4", "B4-TRIGGER-KEYBAR", "Key-Bar trigger form is shown.", Resolution.SUPPORTED, "Family member is source-consistent; acceptance precedence is unresolved."),
    DiscriminationCase("B5", "B5-ABCD-WICK", "AB=CD magnitude relationship is source-confirmed.", Resolution.SUPPORTED, "Wick endpoints remain a candidate, not a canonical anchor."),
    DiscriminationCase("B5", "B5-ABCD-BODY", "AB=CD magnitude relationship is source-confirmed.", Resolution.SUPPORTED, "Body endpoints remain a candidate, not a canonical anchor."),
    DiscriminationCase("B5", "B5-ABCD-PIVOT", "AB=CD magnitude relationship is source-confirmed.", Resolution.SUPPORTED, "Structural-pivot endpoints remain a candidate, not a canonical anchor."),
    DiscriminationCase("B5", "B5-ABCD-MIXED", "AB=CD magnitude relationship is source-confirmed.", Resolution.SUPPORTED, "Mixed endpoints remain a candidate, not a canonical anchor."),
    DiscriminationCase("B6", "B6-LEG2-MAGNITUDE", "Second-leg continuation and approximate equality with Leg1 are source-confirmed.", Resolution.UNRESOLVED, "Executable projection and TP geometry remain unresolved."),
)


def unresolved_blockers() -> tuple[str, ...]:
    return tuple(sorted({case.blocker for case in CASES if case.resolution is Resolution.UNRESOLVED}))


def production_allowed() -> bool:
    """Source discrimination cannot authorize production while critical geometry is unresolved."""
    return not unresolved_blockers()
