import pytest

from .g69_baseline_stability import summarize_returns


def test_summary_is_deterministic():
    result = summarize_returns([0.01, -0.02, 0.03, 0.00])
    assert result.observations == 4
    assert result.mean_return == pytest.approx(0.005)
    assert result.median_return == pytest.approx(0.005)
    assert result.min_return == -0.02
    assert result.max_return == 0.03


def test_empty_returns_are_rejected():
    with pytest.raises(ValueError):
        summarize_returns([])
