import pytest

from .unresolved_geometry import (
    GeometryDecision,
    GeometryState,
    production_allowed,
    require_resolved_for_production,
)


def test_only_source_resolved_geometry_can_enter_production():
    assert production_allowed(
        GeometryDecision("example", GeometryState.RESOLVED_SOURCE_GEOMETRY, "source uniquely specifies it")
    )
    for state in (
        GeometryState.CANDIDATE_RESEARCH_GEOMETRY,
        GeometryState.UNRESOLVED_SOURCE_GEOMETRY,
        GeometryState.BLOCKED_PRODUCTION,
    ):
        assert not production_allowed(GeometryDecision("example", state, "not source-unique"))


def test_unresolved_geometry_fails_closed():
    decision = GeometryDecision(
        "B1-PGAP",
        GeometryState.UNRESOLVED_SOURCE_GEOMETRY,
        "participating candle boundary is not source-unique",
    )
    with pytest.raises(RuntimeError, match="Production blocked"):
        require_resolved_for_production(decision)


def test_candidate_geometry_also_fails_closed():
    decision = GeometryDecision(
        "B5-ABCD",
        GeometryState.CANDIDATE_RESEARCH_GEOMETRY,
        "endpoint model is a research hypothesis",
    )
    with pytest.raises(RuntimeError, match="Production blocked"):
        require_resolved_for_production(decision)
