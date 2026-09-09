"""F26 final source pass: semantic freeze candidates without invented geometry.

The fixture records what the source supports and keeps unresolved executable
geometry explicitly unresolved. It is intentionally unsuitable as a live
signal detector until the remaining geometry blockers are independently
resolved.
"""
from dataclasses import dataclass
from enum import Enum


class Resolution(str, Enum):
    CONFIRMED = "confirmed"
    CANDIDATE = "candidate"
    UNRESOLVED = "unresolved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class SourceDecision:
    item: str
    semantic: Resolution
    executable_geometry: Resolution
    note: str


def final_source_decisions() -> tuple[SourceDecision, ...]:
    return (
        SourceDecision(
            "P-Gap",
            Resolution.CONFIRMED,
            Resolution.UNRESOLVED,
            "First-class source concept; exact OHLC boundaries are not frozen.",
        ),
        SourceDecision(
            "Pending Limit",
            Resolution.CONFIRMED,
            Resolution.CANDIDATE,
            "Pending-limit mechanism is explicit; exact universal anchor remains open.",
        ),
        SourceDecision(
            "Structural invalidation",
            Resolution.CONFIRMED,
            Resolution.UNRESOLVED,
            "Stop is structural, but wick/body/pivot/buffer is not selected.",
        ),
        SourceDecision(
            "Trigger family",
            Resolution.CONFIRMED,
            Resolution.UNRESOLVED,
            "1/2/3-candle and key-bar examples exist; acceptance timing is open.",
        ),
        SourceDecision(
            "AB=CD",
            Resolution.CONFIRMED,
            Resolution.UNRESOLVED,
            "Magnitude relationship is explicit; A/B/C/D anchors and tolerance are open.",
        ),
        SourceDecision(
            "Leg 1 / Leg 2",
            Resolution.CONFIRMED,
            Resolution.UNRESOLVED,
            "Second-leg continuation and approximate equality are source concepts.",
        ),
        SourceDecision(
            "TP1",
            Resolution.CANDIDATE,
            Resolution.UNRESOLVED,
            "Source preference is observable; executable target formula is not frozen.",
        ),
        SourceDecision(
            "Bearish mirror",
            Resolution.CONFIRMED,
            Resolution.UNRESOLVED,
            "Directional mirror is supported; exact bearish OHLC anchors remain open.",
        ),
    )


def generic_fvg_is_source_equivalent_to_pgap() -> bool:
    return False


def market_close_reclaim_can_replace_pending_limit() -> bool:
    return False


def risk_budget_can_define_structural_stop() -> bool:
    return False


def production_freeze_is_allowed() -> bool:
    return False
