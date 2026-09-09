from .multi_window_plan import HistoricalWindow, flatten_chunks, plan_windows


def test_windows_are_sorted_and_chunks_are_deterministic():
    windows = (
        HistoricalWindow("b", "2026-01-02T00:00:00+00:00", "2026-01-02T00:10:00+00:00"),
        HistoricalWindow("a", "2026-01-01T00:00:00+00:00", "2026-01-01T00:10:00+00:00"),
    )
    plans = plan_windows(windows, interval="1min", max_points=5)
    assert [p.window.name for p in plans] == ["a", "b"]
    assert len(flatten_chunks(plans)) == 22
    assert plans == plan_windows(windows, interval="1min", max_points=5)


def test_overlapping_windows_are_rejected():
    windows = (
        HistoricalWindow("a", "2026-01-01T00:00:00+00:00", "2026-01-01T01:00:00+00:00"),
        HistoricalWindow("b", "2026-01-01T01:00:00+00:00", "2026-01-01T02:00:00+00:00"),
    )
    try:
        plan_windows(windows, interval="1min")
    except ValueError as exc:
        assert "overlap" in str(exc)
    else:
        raise AssertionError("overlapping windows must be rejected")
