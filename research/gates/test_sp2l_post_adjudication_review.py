from research.gates.sp2l_post_adjudication_review import (
    AdjudicationReviewRecord,
    FrozenGeometryReadinessReview,
    GeometryDimension,
    ReviewStatus,
    review,
)


def record(dimension, *, good=True):
    return AdjudicationReviewRecord(
        dimension=dimension,
        candidate_id=f"candidate-{dimension.value}",
        source_discriminated=good,
        reproducible=good,
        invention_required=not good,
        provenance_complete=good,
    )


def test_partial_records_remain_blocked():
    result = review(record(d) for d in list(GeometryDimension)[:3])
    assert result.status is ReviewStatus.BLOCKED
    assert len(result.blocked_dimensions) == 7


def test_all_qualifying_records_are_ready_for_review():
    result = review(record(d) for d in GeometryDimension)
    assert result.status is ReviewStatus.READY_FOR_FREEZE_REVIEW
    assert result.blocked_dimensions == frozenset()
    assert result.qualifying_dimensions == frozenset(GeometryDimension)


def test_missing_provenance_blocks_dimension():
    records = [record(d) for d in GeometryDimension]
    records[0] = AdjudicationReviewRecord(
        dimension=GeometryDimension.P_GAP,
        candidate_id="candidate-p-gap",
        source_discriminated=True,
        reproducible=True,
        invention_required=False,
        provenance_complete=False,
    )
    result = review(records)
    assert result.status is ReviewStatus.BLOCKED
    assert GeometryDimension.P_GAP in result.blocked_dimensions


def test_invention_required_blocks_dimension():
    records = [record(d) for d in GeometryDimension]
    records[0] = record(GeometryDimension.P_GAP, good=False)
    result = review(records)
    assert result.status is ReviewStatus.BLOCKED
    assert GeometryDimension.P_GAP in result.blocked_dimensions
