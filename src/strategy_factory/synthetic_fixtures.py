"""Deterministic, research-only synthetic fixture primitives.

These helpers validate evidence handling. They do not detect SP2L setups, create
trades, model broker fills, or promote any strategy rule to canonical status.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Sequence


class FixtureStatus(str, Enum):
    DETERMINISTIC = "DETERMINISTIC"
    ORDER_SENSITIVE = "ORDER_SENSITIVE"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class TickQuote:
    """One source row; source_row is the stable original-file row ordinal."""

    time_msc: int
    source_row: int
    bid: float
    ask: float

    def validate(self) -> None:
        if self.time_msc < 0:
            raise ValueError("time_msc must be non-negative")
        if self.source_row < 0:
            raise ValueError("source_row must be non-negative")
        if self.bid <= 0 or self.ask <= 0:
            raise ValueError("bid and ask must be positive")
        if self.bid > self.ask:
            raise ValueError("crossed quote is not accepted by this fixture")


def preserve_source_order(quotes: Iterable[TickQuote]) -> tuple[TickQuote, ...]:
    """Validate and retain supplied order; never sort or deduplicate quotes."""
    rows = tuple(quotes)
    previous_row = -1
    previous_time = -1
    for quote in rows:
        quote.validate()
        if quote.source_row <= previous_row:
            raise ValueError("source_row must be strictly increasing")
        if quote.time_msc < previous_time:
            raise ValueError("timestamps moved backwards in source order")
        previous_row = quote.source_row
        previous_time = quote.time_msc
    return rows


def classify_outcome_sensitivity(outcomes: Sequence[str]) -> FixtureStatus:
    """Flag a fixture whose plausible orderings produce different outcomes."""
    if not outcomes:
        return FixtureStatus.UNRESOLVED
    if any(not outcome for outcome in outcomes):
        return FixtureStatus.UNRESOLVED
    return (
        FixtureStatus.DETERMINISTIC
        if len(set(outcomes)) == 1
        else FixtureStatus.ORDER_SENSITIVE
    )


def resolve_sl_tp_order(
    ordered_hits: Sequence[str] | None,
    *,
    ohlc_touches_both: bool = False,
) -> tuple[FixtureStatus, str | None]:
    """Resolve SL/TP only with an explicit ordered event sequence.

    An OHLC bar that touches both levels does not establish which came first.
    The accepted hit vocabulary is exactly SL or TP.
    """
    if ordered_hits is None:
        if ohlc_touches_both:
            return FixtureStatus.AMBIGUOUS, None
        return FixtureStatus.UNRESOLVED, None
    if not ordered_hits:
        return FixtureStatus.UNRESOLVED, None
    if any(hit not in {"SL", "TP"} for hit in ordered_hits):
        return FixtureStatus.UNRESOLVED, None
    return FixtureStatus.DETERMINISTIC, ordered_hits[0]


def select_completed_bar(
    bars: Sequence[dict[str, object]],
) -> dict[str, object] | None:
    """Return the latest bar only when its completion is explicitly asserted."""
    if not bars:
        return None
    latest = bars[-1]
    if latest.get("completed") is not True:
        return None
    return latest
