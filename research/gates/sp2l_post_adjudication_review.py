"""Source-safe post-adjudication frozen-geometry readiness review.

This module evaluates governance records only. It does not define or compute
Strategy A geometry and cannot authorize execution.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class GeometryDimension(str, Enum):
    P_GAP = "p_gap"
    ENTRY_ANCHOR = "entry_anchor"
    LEG2_START = "leg2_start"
    STRUCTURAL_INVALIDATION = "structural_invalidation"
    PENDING_REFRESH = "pending_refresh"
    TRIGGER_CLASSIFIER = "trigger_classifier"
    ABCD_ANCHORS = "abcd_anchors"
    ABCD_TOLERANCE = "abcd_tolerance"
    TARGETS_2X = "targets_2x"
    BEARISH_MIRROR = "bearish_mirror"


class ReviewStatus(str, Enum):
    BLOCKED = "BLOCKED"
    READY_FOR_FREEZE_REVIEW = "READY_FOR_FREEZE_REVIEW"


@dataclass(frozen=True)
class AdjudicationReviewRecord:
    dimension: GeometryDimension
    candidate_id: str
    source_discriminated: bool
    reproducible: bool
    invention_required: bool
    provenance_complete: bool

    def qualifies(self) -> bool:
        return (
            bool(self.candidate_id.strip())
            and self.source_discriminated
            and self.reproducible
            and not self.invention_required
            and self.provenance_complete
        )


@dataclass(frozen=True)
class FrozenGeometryReadinessReview:
    status: ReviewStatus
    qualifying_dimensions: frozenset[GeometryDimension]
    blocked_dimensions: frozenset[GeometryDimension]


def review(records: Iterable[AdjudicationReviewRecord]) -> FrozenGeometryReadinessReview:
    """Return readiness only when every dimension has a qualifying human record."""
    by_dimension: dict[GeometryDimension, AdjudicationReviewRecord] = {}
    for record in records:
        by_dimension[record.dimension] = record

    all_dimensions = frozenset(GeometryDimension)
    qualifying = frozenset(
        dimension for dimension in all_dimensions
        if dimension in by_dimension and by_dimension[dimension].qualifies()
    )
    blocked = all_dimensions - qualifying
    status = (
        ReviewStatus.READY_FOR_FREEZE_REVIEW
        if not blocked
        else ReviewStatus.BLOCKED
    )
    return FrozenGeometryReadinessReview(status, qualifying, blocked)
