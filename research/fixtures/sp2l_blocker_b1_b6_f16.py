"""F16 source-blocker discrimination fixtures (research only)."""
from dataclasses import dataclass
from enum import Enum

class CandidateStatus(str, Enum):
    CONFIRMED_SEMANTIC = "CONFIRMED_SEMANTIC"
    CANDIDATE = "CANDIDATE"
    UNRESOLVED = "UNRESOLVED"

@dataclass(frozen=True)
class Blocker:
    id: str
    candidates: tuple[str, ...]
    status: CandidateStatus

F16_BLOCKERS = (
    Blocker("B1_PGAP", ("source_specific_gap", "generic_three_candle_imbalance"), CandidateStatus.UNRESOLVED),
    Blocker("B2_ENTRY", ("first_relevant_low_high", "latest_completed_hl_lh", "other_structural_reference"), CandidateStatus.CANDIDATE),
    Blocker("B3_SL", ("wick_extreme", "body_edge", "structural_pivot", "buffered_structural_level"), CandidateStatus.UNRESOLVED),
    Blocker("B4_TRIGGER", ("one_candle", "two_candle", "three_candle", "key_bar_confirmation"), CandidateStatus.CANDIDATE),
    Blocker("B5_ABCD", ("wick_anchors", "body_anchors", "structural_pivots", "mixed_anchors"), CandidateStatus.UNRESOLVED),
    Blocker("B6_LEG2_TP1", ("equal_magnitude_from_source_leg", "fixed_ratio_projection", "other_source_projection"), CandidateStatus.UNRESOLVED),
)

def blocker_by_id(blocker_id: str) -> Blocker:
    for blocker in F16_BLOCKERS:
        if blocker.id == blocker_id:
            return blocker
    raise KeyError(blocker_id)

def production_safe(blocker: Blocker) -> bool:
    return blocker.status is CandidateStatus.CONFIRMED_SEMANTIC and len(blocker.candidates) == 1
