"""Provider-neutral market-data quality primitives.

No Strategy A geometry or trading decision is implemented here.
"""
from dataclasses import dataclass
from enum import Enum


class QualityState(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class QualityReport:
    state: QualityState
    duplicate_timestamps: int = 0
    invalid_ohlc: int = 0
    missing_intervals: int = 0


def audit_ohlc(rows: list[dict]) -> QualityReport:
    duplicates = 0
    invalid = 0
    seen = set()
    for row in rows:
        ts = row["timestamp"]
        if ts in seen:
            duplicates += 1
        seen.add(ts)
        o, h, l, c = row["open"], row["high"], row["low"], row["close"]
        if h < max(o, c) or l > min(o, c) or h < l:
            invalid += 1
    state = QualityState.BLOCKED if duplicates or invalid else QualityState.PASS
    return QualityReport(state, duplicates, invalid, 0)


def aggregate_fixed_bucket(rows: list[dict]) -> dict:
    """Aggregate an already UTC-aligned bucket deterministically."""
    if not rows:
        raise ValueError("cannot aggregate an empty bucket")
    return {
        "timestamp": rows[0]["timestamp"],
        "open": rows[0]["open"],
        "high": max(r["high"] for r in rows),
        "low": min(r["low"] for r in rows),
        "close": rows[-1]["close"],
    }
