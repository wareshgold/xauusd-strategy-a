from __future__ import annotations

from enum import Enum


class GeometryStatus(str, Enum):
    BLOCKED = "BLOCKED"
    SOURCE_DISCRIMINATED = "SOURCE_DISCRIMATED"
    MANUALLY_ADJUDICATED = "MANUALLY_ADJUDICATED"


EXECUTABLE_DIMENSIONS = (
    "p_gap",
    "entry_anchor",
    "leg2_start",
    "structural_invalidation",
    "pending_refresh",
    "trigger_classifier",
    "abcd_anchors",
    "abcd_tolerance",
    "targets_2x",
    "bearish_mirror",
)


def readiness_status(statuses: dict[str, GeometryStatus]) -> str:
    missing = [name for name in EXECUTABLE_DIMENSIONS if name not in statuses]
    if missing:
        raise ValueError(f"missing executable geometry dimensions: {missing}")

    if all(statuses[name] == GeometryStatus.MANUALLY_ADJUDICATED for name in EXECUTABLE_DIMENSIONS):
        return "READY_FOR_FREEZE_REVIEW"

    return "NOT_READY_SOURCE_GEOMETRY_BLOCKED"


def assert_current_source_gate() -> None:
    statuses = {name: GeometryStatus.BLOCKED for name in EXECUTABLE_DIMENSIONS}
    result = readiness_status(statuses)
    assert result == "NOT_READY_SOURCE_GEOMETRY_BLOCKED"


def test_all_executable_geometry_dimensions_are_explicitly_blocked() -> None:
    assert_current_source_gate()


def test_partial_source_discrimination_does_not_pass_gate() -> None:
    statuses = {name: GeometryStatus.BLOCKED for name in EXECUTABLE_DIMENSIONS}
    statuses["p_gap"] = GeometryStatus.SOURCE_DISCRIMINATED
    assert readiness_status(statuses) == "NOT_READY_SOURCE_GEOMETRY_BLOCKED"


def test_only_manual_adjudication_of_every_dimension_can_pass() -> None:
    statuses = {
        name: GeometryStatus.MANUALLY_ADJUDICATED
        for name in EXECUTABLE_DIMENSIONS
    }
    assert readiness_status(statuses) == "READY_FOR_FREEZE_REVIEW"
