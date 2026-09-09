from datetime import datetime

import pytest

from .coverage import CoverageChunk, plan_chunks, validate_chunk_boundaries


def test_plan_chunks_is_deterministic_and_non_overlapping():
    chunks = plan_chunks(
        "2026-01-01T00:00:00+00:00",
        "2026-01-01T10:00:00+00:00",
        interval="1min",
        max_points=5,
    )
    assert len(chunks) == 121
    assert chunks[0].start_utc == "2026-01-01T00:00:00+00:00"
    assert chunks[0].end_utc == "2026-01-01T00:04:00+00:00"
    assert chunks[1].start_utc == "2026-01-01T00:05:00+00:00"
    assert chunks[-1].end_utc == "2026-01-01T10:00:00+00:00"
    validate_chunk_boundaries(chunks, interval="1min")
    assert chunks == plan_chunks(
        "2026-01-01T00:00:00+00:00",
        "2026-01-01T10:00:00+00:00",
        interval="1min",
        max_points=5,
    )


def test_invalid_boundary_is_rejected():
    chunks = (
        CoverageChunk(0, "2026-01-01T00:00:00+00:00", "2026-01-01T00:04:00+00:00"),
        CoverageChunk(1, "2026-01-01T00:04:00+00:00", "2026-01-01T00:08:00+00:00"),
    )
    with pytest.raises(ValueError, match="overlapping or non-contiguous"):
        validate_chunk_boundaries(chunks, interval="1min")


def test_naive_boundaries_are_rejected():
    with pytest.raises(ValueError, match="must include timezone"):
        plan_chunks("2026-01-01T00:00:00", "2026-01-01T01:00:00+00:00", interval="1min")


def test_invalid_range_and_limits_are_rejected():
    with pytest.raises(ValueError, match="start_utc"):
        plan_chunks("2026-01-02T00:00:00+00:00", "2026-01-01T00:00:00+00:00", interval="1min")
    with pytest.raises(ValueError, match="max_points"):
        plan_chunks("2026-01-01T00:00:00+00:00", "2026-01-01T00:01:00+00:00", interval="1min", max_points=0)
