from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CandidateStatus(str, Enum):
    HYPOTHESIS = "HYPOTHESIS"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class CandidateGeometry:
    candidate_id: str
    description: str
    status: CandidateStatus = CandidateStatus.HYPOTHESIS


CANDIDATES = (
    CandidateGeometry("B1-PGAP-V1", "P-Gap candidate: breakout plus follow-through with adjacent range separation."),
    CandidateGeometry("B1-PGAP-V2", "P-Gap candidate: breakout plus follow-through with alternative boundary interpretation."),
    CandidateGeometry("B2-ENTRY-STRUCTURAL", "Entry candidate: pending Limit at a relevant completed structural low/high."),
    CandidateGeometry("B2-ENTRY-LATEST", "Entry candidate: pending Limit at the latest completed higher-low/lower-high."),
    CandidateGeometry("B3-SL-STRUCTURAL", "Stop candidate: structural invalidation beyond the relevant structural low/high."),
    CandidateGeometry("B4-TRIGGER-1C", "Trigger candidate: one-candle form."),
    CandidateGeometry("B4-TRIGGER-2C", "Trigger candidate: two-candle form."),
    CandidateGeometry("B4-TRIGGER-3C", "Trigger candidate: three-candle form."),
    CandidateGeometry("B4-TRIGGER-KEYBAR", "Trigger candidate: key-bar form."),
    CandidateGeometry("B5-ABCD-WICK", "AB=CD candidate: wick-based endpoints."),
    CandidateGeometry("B5-ABCD-BODY", "AB=CD candidate: body-based endpoints."),
    CandidateGeometry("B5-ABCD-PIVOT", "AB=CD candidate: structural-pivot endpoints."),
    CandidateGeometry("B5-ABCD-MIXED", "AB=CD candidate: mixed endpoint model."),
    CandidateGeometry("B6-LEG2-MAGNITUDE", "Leg2 candidate: continuation linked to Leg1 magnitude by AB=CD."),
)


def candidate_ids() -> tuple[str, ...]:
    return tuple(candidate.candidate_id for candidate in CANDIDATES)


def execution_allowed(candidate: CandidateGeometry) -> bool:
    """G55 candidates never authorize production execution."""
    return False
