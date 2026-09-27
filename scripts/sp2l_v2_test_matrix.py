"""Deterministic research matrix for SP2L Strategy A V2.

This module defines test cases only. Execution is intentionally separate so the
same matrix can be replayed against MT5 data without changing candidate logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class MatrixCase:
    case_id: str
    symbol: str
    timeframe: str
    window_start_utc: str
    window_end_utc: str
    session_start_utc: str | None
    session_end_utc: str | None
    population: str


SYMBOLS = ("XAUUSD", "BTCUSD", "USTEC", "DJ30")
TIMEFRAMES = ("M1", "M5", "M15")
WINDOWS = (
    ("W0", None, None),
    ("W1", "07:00", "17:00"),
    ("W2", "08:00", "17:00"),
    ("W3", "13:00", "17:00"),
)


def weekly_ranges(start: date, end: date):
    """Yield Monday-Sunday half-open UTC calendar-week ranges."""
    cursor = start - timedelta(days=start.weekday())
    while cursor < end:
        week_end = cursor + timedelta(days=7)
        yield cursor, week_end
        cursor = week_end


def build_matrix(
    start: date = date(2026, 1, 1),
    end: date = date(2026, 9, 26),
    primary_symbol: str = "XAUUSD",
):
    """Return deterministic cases; primary XAUUSD M1 cases come first."""
    cases: list[MatrixCase] = []
    weeks = list(weekly_ranges(start, end))

    # Primary population: XAUUSD M1, all weekly slices and session windows.
    for week_start, week_end in weeks:
        if week_end <= start or week_start >= end:
            continue
        ws = max(week_start, start).isoformat()
        we = min(week_end, end).isoformat()
        for wid, ss, se in WINDOWS:
            cases.append(
                MatrixCase(
                    case_id=f"PRIMARY-{week_start.isoformat()}-{wid}",
                    symbol=primary_symbol,
                    timeframe="M1",
                    window_start_utc=ws,
                    window_end_utc=we,
                    session_start_utc=ss,
                    session_end_utc=se,
                    population="PRIMARY",
                )
            )

    # Robustness diagnostics: one full-day weekly slice per variation.
    for symbol in SYMBOLS:
        for timeframe in TIMEFRAMES:
            if symbol == primary_symbol and timeframe == "M1":
                continue
            for week_start, week_end in weeks:
                if week_end <= start or week_start >= end:
                    continue
                cases.append(
                    MatrixCase(
                        case_id=f"ROBUST-{symbol}-{timeframe}-{week_start.isoformat()}",
                        symbol=symbol,
                        timeframe=timeframe,
                        window_start_utc=max(week_start, start).isoformat(),
                        window_end_utc=min(week_end, end).isoformat(),
                        session_start_utc=None,
                        session_end_utc=None,
                        population="ROBUSTNESS_DIAGNOSTIC",
                    )
                )
    return cases


if __name__ == "__main__":
    cases = build_matrix()
    print(f"cases={len(cases)}")
    print("primary=", sum(c.population == "PRIMARY" for c in cases))
    print("robustness=", sum(c.population == "ROBUSTNESS_DIAGNOSTIC" for c in cases))
