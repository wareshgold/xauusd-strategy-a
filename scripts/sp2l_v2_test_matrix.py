"""Deterministic research matrix for SP2L Strategy A V2."""

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


SYMBOLS = (
    "XAUUSD",
    "USDJPY",
    "EURJPY",
    "GBPUSD",
    "GBPJPY",
    "EURUSD",
    "USDCHF",
    "USDCAD",
)
TIMEFRAMES = ("M1", "M5", "M15")
WINDOWS = (
    ("W0", None, None),
    ("W1", "07:00", "17:00"),
    ("W2", "08:00", "17:00"),
    ("W3", "13:00", "17:00"),
)


def weekly_ranges(start: date, end: date):
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
    """Return deterministic XAUUSD/FX weekly research cases."""
    cases: list[MatrixCase] = []
    weeks = list(weekly_ranges(start, end))

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

        for symbol in SYMBOLS:
            if symbol == primary_symbol:
                continue
            cases.append(
                MatrixCase(
                    case_id=f"FX-{symbol}-{week_start.isoformat()}",
                    symbol=symbol,
                    timeframe="M1",
                    window_start_utc=ws,
                    window_end_utc=we,
                    session_start_utc=None,
                    session_end_utc=None,
                    population="FX_M1",
                )
            )

    return cases


if __name__ == "__main__":
    cases = build_matrix()
    print(f"cases={len(cases)}")
    print("primary=", sum(c.population == "PRIMARY" for c in cases))
    print("fx_m1=", sum(c.population == "FX_M1" for c in cases))
