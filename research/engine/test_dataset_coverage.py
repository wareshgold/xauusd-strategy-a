from datetime import date

import pytest

from research.engine.dataset_coverage import (
    CoverageWindow,
    plan_windows,
    validate_non_overlapping,
)


def test_plan_windows_is_deterministic_and_covers_requested_range():
    expected = (
        CoverageWindow("2026-01-01", "2026-01-03"),
        CoverageWindow("2026-01-04", "2026-01-06"),
        CoverageWindow("2026-01-07", "2026-01-07"),
    )
    first = plan_windows(date(2026, 1, 1), date(2026, 1, 7), days_per_window=3)
    second = plan_windows(date(2026, 1, 1), date(2026, 1, 7), days_per_window=3)
    assert first == expected
    assert second == first


def test_single_day_range_produces_one_window():
    assert plan_windows(date(2026, 1, 5), date(2026, 1, 5)) == (
        CoverageWindow("2026-01-05", "2026-01-05"),
    )


def test_invalid_range_and_window_size_are_rejected():
    with pytest.raises(ValueError, match="end date"):
        plan_windows(date(2026, 1, 2), date(2026, 1, 1))
    with pytest.raises(ValueError, match="days_per_window"):
        plan_windows(date(2026, 1, 1), date(2026, 1, 1), days_per_window=0)


def test_non_overlapping_validation_accepts_adjacent_windows():
    validate_non_overlapping(
        (
            CoverageWindow("2026-01-01", "2026-01-03"),
            CoverageWindow("2026-01-04", "2026-01-06"),
        )
    )


def test_non_overlapping_validation_rejects_overlap():
    with pytest.raises(ValueError, match="overlap"):
        validate_non_overlapping(
            (
                CoverageWindow("2026-01-01", "2026-01-03"),
                CoverageWindow("2026-01-03", "2026-01-05"),
            )
        )
