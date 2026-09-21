"""Deterministic scheduler tests (offline, no market data).

Validates the explicit-configuration NY-close logic, DST handling via the
IANA database, weekly/monthly windows, and the unresolved-marking contract.
"""

from datetime import datetime, timezone

import pytest

from scripts.live_report_scheduler import (
    ScheduleConfig,
    daily_report_bounds,
    is_due,
    load_schedule_config,
    monthly_report_bounds,
    ny_close_utc,
    weekly_report_bounds,
)

CONFIG = ScheduleConfig()


def test_ny_close_is_dst_correct_via_iana():
    # July = EDT (UTC-4): 17:00 local -> 21:00 UTC.
    july = ny_close_utc(datetime(2026, 7, 15, 12, 0), CONFIG)
    assert july.utcoffset() == timezone.utc.utcoffset(None)
    assert july.hour == 21 and july.minute == 0
    # December = EST (UTC-5): 17:00 local -> 22:00 UTC.
    december = ny_close_utc(datetime(2026, 12, 15, 12, 0), CONFIG)
    assert december.hour == 22 and december.minute == 0


def test_daily_due_only_after_close():
    before = datetime(2026, 9, 16, 20, 0, tzinfo=timezone.utc)  # 16:00 ET
    after = datetime(2026, 9, 16, 22, 0, tzinfo=timezone.utc)   # 18:00 ET
    assert is_due("daily", before, CONFIG) == (False, "BEFORE_CLOSE")
    assert is_due("daily", after, CONFIG) == (True, "AFTER_NY_CLOSE")


def test_daily_not_due_twice_same_day():
    after = datetime(2026, 9, 16, 22, 0, tzinfo=timezone.utc)
    sent_same_day = datetime(2026, 9, 16, 22, 5, tzinfo=timezone.utc)
    assert is_due("daily", after, CONFIG, last_sent_utc=sent_same_day) == (False, "ALREADY_SENT")


def test_weekly_due_only_on_friday_after_close():
    thursday = datetime(2026, 9, 17, 22, 0, tzinfo=timezone.utc)
    friday_after = datetime(2026, 9, 18, 22, 0, tzinfo=timezone.utc)
    friday_before = datetime(2026, 9, 18, 20, 0, tzinfo=timezone.utc)
    assert is_due("weekly", thursday, CONFIG) == (False, "WRONG_WEEKDAY")
    assert is_due("weekly", friday_before, CONFIG) == (False, "BEFORE_CLOSE")
    assert is_due("weekly", friday_after, CONFIG) == (True, "AFTER_FRIDAY_CLOSE")


def test_monthly_due_on_last_weekday_after_close():
    # September 2026: Sep 30 is the last Wednesday (last weekday).
    mid_month = datetime(2026, 9, 15, 22, 0, tzinfo=timezone.utc)
    last_day_before = datetime(2026, 9, 30, 20, 0, tzinfo=timezone.utc)
    last_day_after = datetime(2026, 9, 30, 22, 0, tzinfo=timezone.utc)
    assert is_due("monthly", mid_month, CONFIG) == (False, "NOT_LAST_TRADING_DAY")
    assert is_due("monthly", last_day_before, CONFIG) == (False, "BEFORE_CLOSE")
    assert is_due("monthly", last_day_after, CONFIG) == (True, "LAST_TRADING_DAY_AFTER_CLOSE")


def test_monthly_not_due_twice_same_month():
    last_day_after = datetime(2026, 9, 30, 22, 0, tzinfo=timezone.utc)
    sent = datetime(2026, 9, 30, 22, 5, tzinfo=timezone.utc)
    assert is_due("monthly", last_day_after, CONFIG, last_sent_utc=sent) == (False, "ALREADY_SENT")


def test_unresolved_schedule_basis_blocks_reports():
    config = ScheduleConfig(schedule_basis="UNRESOLVED_NY_CLOSE_CALENDAR")
    assert is_due("daily", datetime(2026, 9, 16, 22, 0, tzinfo=timezone.utc), config)[0] is False
    assert is_due("daily", datetime(2026, 9, 16, 22, 0, tzinfo=timezone.utc), config)[1].startswith("UNRESOLVED")


def test_period_bounds_cover_expected_windows():
    # Trading day Wed 2026-09-16: 04:00 UTC (midnight EDT) -> 21:00 UTC (close).
    start, end = daily_report_bounds(datetime(2026, 9, 16, 12, 0, tzinfo=timezone.utc), CONFIG)
    assert start.hour == 4 and end.hour == 21
    # Trading week ending Friday 2026-09-18: prev Friday 04:00 UTC -> 21:00 UTC.
    w_start, w_end = weekly_report_bounds(datetime(2026, 9, 16, 12, 0, tzinfo=timezone.utc), CONFIG)
    assert w_start.day == 11 and w_end.day == 18
    # September 2026: 2026-09-01 04:00 UTC -> 2026-10-01 04:00 UTC.
    m_start, m_end = monthly_report_bounds(datetime(2026, 9, 16, 12, 0, tzinfo=timezone.utc), CONFIG)
    assert (m_start.month, m_start.day) == (9, 1)
    assert (m_end.month, m_end.day) == (10, 1)


def test_config_comes_from_environment_not_hardcode():
    config = load_schedule_config({
        "REPORT_SESSION_TIMEZONE": "Europe/London",
        "REPORT_NY_CLOSE_HHMM": "16:30",
    })
    assert config.session_timezone == "Europe/London"
    assert config.ny_close_hhmm == "16:30"
    close = ny_close_utc(datetime(2026, 7, 15, 12, 0), config)
    assert close.hour == 15 and close.minute == 30  # 16:30 BST == 15:30 UTC


def test_invalid_close_time_is_rejected():
    with pytest.raises(ValueError):
        ny_close_utc(datetime(2026, 9, 16, 12, 0), ScheduleConfig(ny_close_hhmm="25:00"))
