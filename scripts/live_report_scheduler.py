"""Deterministic report scheduler for daily/weekly/monthly SP2L reports.

Reporting/infrastructure only: decides WHEN a report is due; it does not
generate signals and does not touch strategy geometry.

Timezone/session policy (docs/research/SESSION_TIMEZONE_CORRECTION_2026-09-05.md):
- canonical journal timestamps are UTC;
- the New York session is evaluated in `America/New_York` via the IANA
  timezone database (DST-aware), never via fixed offsets;
- the NY close time is an explicit configuration input
  (REPORT_NY_CLOSE_HHMM, default "17:00" America/New_York = 5 PM ET).
  This module does NOT invent a broker-timezone conversion.

Unresolved-data contract:
- If NY-close scheduling depends on data that cannot be resolved here
  (e.g. broker-declared session close or an early-close/holiday calendar),
  callers must set REPORT_PERIOD_BASIS to an explicit marker
  (e.g. UNRESOLVED_NY_CLOSE_CALENDAR) and this module marks the due
  decision as UNRESOLVED rather than guessing.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_SESSION_TZ = "America/New_York"
DEFAULT_NY_CLOSE_HHMM = "17:00"  # 5 PM ET, America/New_York, DST via IANA db

UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class ScheduleConfig:
    session_timezone: str = DEFAULT_SESSION_TZ
    ny_close_hhmm: str = DEFAULT_NY_CLOSE_HHMM
    period_basis: str = "EXPLICIT_PERIOD_BOUNDS"
    # REPORT_SCHEDULE_BASIS documents where the close boundary comes from.
    # EXPLICIT_NY_CLOSE_1700_ET -> the explicit 17:00 America/New_York input.
    # UNRESOLVED_* -> scheduling is marked UNRESOLVED and reports must not fire.
    schedule_basis: str = "EXPLICIT_NY_CLOSE_1700_ET"


def load_schedule_config(env: dict | None = None) -> ScheduleConfig:
    source = os.environ if env is None else env
    return ScheduleConfig(
        session_timezone=(source.get("REPORT_SESSION_TIMEZONE") or DEFAULT_SESSION_TZ).strip(),
        ny_close_hhmm=(source.get("REPORT_NY_CLOSE_HHMM") or DEFAULT_NY_CLOSE_HHMM).strip(),
        period_basis=(source.get("REPORT_PERIOD_BASIS") or "EXPLICIT_PERIOD_BOUNDS").strip(),
        schedule_basis=(source.get("REPORT_SCHEDULE_BASIS") or "EXPLICIT_NY_CLOSE_1700_ET").strip(),
    )


def _zone(name: str) -> ZoneInfo:
    return ZoneInfo(name)


def _try_zone(name: str) -> ZoneInfo | None:
    """IANA zone or None. Never substitutes a fixed offset for a missing db."""
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, OSError, ValueError):
        return None


def _parse_hhmm(value: str) -> tuple[int, int]:
    parts = value.split(":")
    if len(parts) != 2:
        raise ValueError(f"invalid HH:MM value: {value!r}")
    hour, minute = int(parts[0]), int(parts[1])
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"invalid HH:MM value: {value!r}")
    return hour, minute


def _now_from_reference(now_utc: datetime) -> datetime:
    if now_utc.tzinfo is None:
        return now_utc.replace(tzinfo=timezone.utc)
    return now_utc.astimezone(timezone.utc)


def ny_close_utc(day: datetime, config: ScheduleConfig) -> datetime:
    """NY close for the given local day, DST-correct via the IANA database."""
    zone = _zone(config.session_timezone)
    if day.tzinfo is None:
        local_day = day.replace(tzinfo=zone)
    else:
        local_day = day.astimezone(zone)
    hour, minute = _parse_hhmm(config.ny_close_hhmm)
    return local_day.replace(hour=hour, minute=minute, second=0, microsecond=0).astimezone(timezone.utc)


def _day_bounds_local(day: datetime, config: ScheduleConfig) -> tuple[datetime, datetime]:
    zone = _zone(config.session_timezone)
    if day.tzinfo is None:
        local_day = day.replace(tzinfo=zone)
    else:
        local_day = day.astimezone(zone)
    start_local = local_day.replace(hour=0, minute=0, second=0, microsecond=0)
    hour, minute = _parse_hhmm(config.ny_close_hhmm)
    end_local = local_day.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return start_local, end_local


def daily_report_bounds(day: datetime, config: ScheduleConfig) -> tuple[datetime, datetime]:
    """UTC bounds of one trading day: local midnight -> configured NY close."""
    start_local, end_local = _day_bounds_local(day, config)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def _week_anchor_days_back(now_local: datetime) -> int:
    """Signed days from `now_local` to its trading week's Friday close.

    Mon-Fri -> the upcoming Friday of the current week (non-positive).
    Sat/Sun -> the Friday that just ended (1 or 2 days back).
    """
    weekday = now_local.weekday()
    if weekday <= 4:
        return weekday - 4
    return (weekday - 4) % 7


def weekly_report_bounds(now_utc: datetime, config: ScheduleConfig) -> tuple[datetime, datetime]:
    """UTC bounds of the trading week containing `now_utc`.

    Half-open window [previous Friday close, this week's Friday close).
    """
    zone = _zone(config.session_timezone)
    now_local = _now_from_reference(now_utc).astimezone(zone)
    friday = now_local - timedelta(days=_week_anchor_days_back(now_local))
    _, end_local = _day_bounds_local(friday, config)
    _, prev_end_local = _day_bounds_local(friday - timedelta(days=7), config)
    return prev_end_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def monthly_report_bounds(now_utc: datetime, config: ScheduleConfig) -> tuple[datetime, datetime]:
    """UTC bounds of the calendar month containing `now_utc`."""
    zone = _zone(config.session_timezone)
    now_local = _now_from_reference(now_utc).astimezone(zone)
    start_local = now_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now_local.month == 12:
        next_month = now_local.replace(year=now_local.year + 1, month=1, day=1)
    else:
        next_month = now_local.replace(month=now_local.month + 1, day=1)
    end_local = next_month.replace(hour=0, minute=0, second=0, microsecond=0)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def _is_last_trading_day_of_month(now_utc: datetime, config: ScheduleConfig) -> bool:
    """Deterministic weekday-based proxy: the last Mon-Fri local day of the month.

    Uses the IANA session timezone only; it does not consult a broker holiday
    calendar. When holiday awareness is required, callers must mark
    REPORT_PERIOD_BASIS=UNRESOLVED_* (see module docstring).
    """
    zone = _zone(config.session_timezone)
    now_local = _now_from_reference(now_utc).astimezone(zone)
    if now_local.month == 12:
        next_month = now_local.replace(year=now_local.year + 1, month=1, day=1)
    else:
        next_month = now_local.replace(month=now_local.month + 1, day=1)
    # Walk back from the first day of the next month to the last weekday.
    cursor = next_month - timedelta(days=1)
    while cursor.weekday() >= 5:  # 5=Saturday, 6=Sunday
        cursor -= timedelta(days=1)
    return cursor.date() == now_local.date()


def is_due(
    report_type: str,
    now_utc: datetime,
    config: ScheduleConfig | None = None,
    *,
    last_sent_utc: datetime | None = None,
    reference_close: datetime | None = None,
) -> tuple[bool, str]:
    """Decide whether a report type is due at `now_utc`.

    Returns (due, reason). Reasons are deterministic labels, e.g.:
    - AFTER_NY_CLOSE (daily)
    - AFTER_FRIDAY_CLOSE (weekly)
    - LAST_TRADING_DAY_AFTER_CLOSE (monthly)
    - BEFORE_CLOSE / WRONG_WEEKDAY / ALREADY_SENT / UNRESOLVED_*

    `reference_close` lets callers pin the close instant (e.g. an explicit
    broker-provided close); when omitted, the configured explicit NY close
    is used.
    """
    config = config or ScheduleConfig()

    if config.schedule_basis.upper().startswith("UNRESOLVED") or config.period_basis.upper().startswith("UNRESOLVED"):
        return False, f"UNRESOLVED:{config.schedule_basis}:{config.period_basis}"

    if _try_zone(config.session_timezone) is None:
        # No IANA database: mark unresolved instead of inventing a conversion.
        return False, f"UNRESOLVED:ZONEINFO_UNAVAILABLE:{config.session_timezone}"

    now = _now_from_reference(now_utc)
    zone = _zone(config.session_timezone)
    now_local = now.astimezone(zone)

    if last_sent_utc is not None:
        last_sent = _now_from_reference(last_sent_utc)
        if report_type == "daily" and last_sent.date() == now.date():
            return False, "ALREADY_SENT"
        if report_type == "weekly":
            last_local = last_sent.astimezone(zone)
            if _week_anchor_days_back(last_local) == _week_anchor_days_back(now_local) and (
                (last_local - timedelta(days=_week_anchor_days_back(last_local))).date()
                == (now_local - timedelta(days=_week_anchor_days_back(now_local))).date()
            ):
                return False, "ALREADY_SENT"
        if report_type == "monthly" and last_sent.astimezone(zone).strftime("%Y-%m") == now_local.strftime("%Y-%m"):
            return False, "ALREADY_SENT"

    if report_type == "daily":
        close = reference_close or ny_close_utc(now_local, config)
        if now >= close:
            return True, "AFTER_NY_CLOSE"
        return False, "BEFORE_CLOSE"

    if report_type == "weekly":
        if now_local.weekday() != 4:  # Friday
            return False, "WRONG_WEEKDAY"
        close = reference_close or ny_close_utc(now_local, config)
        if now >= close:
            return True, "AFTER_FRIDAY_CLOSE"
        return False, "BEFORE_CLOSE"

    if report_type == "monthly":
        if not _is_last_trading_day_of_month(now, config):
            return False, "NOT_LAST_TRADING_DAY"
        close = reference_close or ny_close_utc(now_local, config)
        if now >= close:
            return True, "LAST_TRADING_DAY_AFTER_CLOSE"
        return False, "BEFORE_CLOSE"

    return False, f"UNKNOWN_REPORT_TYPE:{report_type}"
