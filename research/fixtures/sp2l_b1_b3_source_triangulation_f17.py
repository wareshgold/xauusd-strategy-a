"""F17 research fixture for P-Gap, Entry and structural SL discrimination.

This module deliberately represents competing source-plausible geometries without
promoting any of them to production rules.
"""
from dataclasses import dataclass
from enum import Enum


class Candidate(str, Enum):
    PGAP_GENERIC_THREE_CANDLE = "pgap_generic_three_candle"
    PGAP_SOURCE_MARKED_STRUCTURE = "pgap_source_marked_structure"
    ENTRY_FIRST_RELEVANT_LOW_HIGH = "entry_first_relevant_low_high"
    ENTRY_LATEST_COMPLETED_HL_LH = "entry_latest_completed_hl_lh"
    ENTRY_LEG2_START = "entry_leg2_start"
    SL_WICK_EXTREME = "sl_wick_extreme"
    SL_BODY_EDGE = "sl_body_edge"
    SL_STRUCTURAL_PIVOT = "sl_structural_pivot"


@dataclass(frozen=True)
class GeometryEvidence:
    candidate: Candidate
    source_supported: bool
    source_uniquely_determined: bool


def f17_evidence():
    return (
        GeometryEvidence(Candidate.PGAP_GENERIC_THREE_CANDLE, False, False),
        GeometryEvidence(Candidate.PGAP_SOURCE_MARKED_STRUCTURE, True, False),
        GeometryEvidence(Candidate.ENTRY_FIRST_RELEVANT_LOW_HIGH, True, False),
        GeometryEvidence(Candidate.ENTRY_LATEST_COMPLETED_HL_LH, True, False),
        GeometryEvidence(Candidate.ENTRY_LEG2_START, False, False),
        GeometryEvidence(Candidate.SL_WICK_EXTREME, True, False),
        GeometryEvidence(Candidate.SL_BODY_EDGE, True, False),
        GeometryEvidence(Candidate.SL_STRUCTURAL_PIVOT, True, False),
    )


def frozen_candidates():
    """Return only candidates that are uniquely source-determined."""
    return tuple(e.candidate for e in f17_evidence() if e.source_uniquely_determined)
