import pytest

from research.gates.sp2l_frozen_geometry_readiness import (
    EXECUTABLE_DIMENSIONS,
    GeometryStatus,
    readiness_status,
)


def test_missing_dimension_is_rejected() -> None:
    statuses = {name: GeometryStatus.BLOCKED for name in EXECUTABLE_DIMENSIONS[:-1]}
    with pytest.raises(ValueError):
        readiness_status(statuses)


def test_all_blocked_is_not_ready() -> None:
    statuses = {name: GeometryStatus.BLOCKED for name in EXECUTABLE_DIMENSIONS}
    assert readiness_status(statuses) == "NOT_READY_SOURCE_GEOMETRY_BLOCKED"


def test_source_discriminated_but_unadjudicated_is_not_ready() -> None:
    statuses = {
        name: GeometryStatus.SOURCE_DISCRIMINATED
        for name in EXECUTABLE_DIMENSIONS
    }
    assert readiness_status(statuses) == "NOT_READY_SOURCE_GEOMETRY_BLOCKED"


def test_full_manual_adjudication_is_the_only_ready_state() -> None:
    statuses = {
        name: GeometryStatus.MANUALLY_ADJUDICATED
        for name in EXECUTABLE_DIMENSIONS
    }
    assert readiness_status(statuses) == "READY_FOR_FREEZE_REVIEW"
