"""Observed-deal arithmetic for research fixtures; never asserts history completeness."""
from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Iterable


class LedgerStatus(str, Enum):
    OBSERVED_ONLY = "OBSERVED_ONLY"
    INCOMPLETE_FIELDS = "INCOMPLETE_FIELDS"
    INVALID_RECORD = "INVALID_RECORD"
    EMPTY_LEDGER = "EMPTY_LEDGER"


@dataclass(frozen=True)
class EconomicDeal:
    ticket: int
    volume: float | None
    profit: float | None
    commission: float | None
    swap: float | None
    fee: float | None


@dataclass(frozen=True)
class DealLedgerSummary:
    status: LedgerStatus
    deal_tickets: tuple[int, ...]
    observed_deal_count: int
    observed_volume_sum: float | None
    gross_profit_sum: float | None
    commission_sum: float | None
    swap_sum: float | None
    fee_sum: float | None
    net_result_sum: float | None
    issues: tuple[str, ...]


def summarize_observed_deals(deals: Iterable[EconomicDeal]) -> DealLedgerSummary:
    """Sum only explicitly supplied finite values; missing components block net total.

    The result describes the supplied rows only. It does not assert that all
    broker deals are present, that volumes are fully filled, or that netting/
    hedging position accounting is resolved.
    """
    rows = tuple(deals)
    if not rows:
        return DealLedgerSummary(LedgerStatus.EMPTY_LEDGER, (), 0, None, None,
                                 None, None, None, None, ("NO_DEAL_ROWS_SUPPLIED",))
    issues: list[str] = []
    seen: dict[int, int] = {}
    for row in rows:
        seen[row.ticket] = seen.get(row.ticket, 0) + 1
    if any(row.ticket <= 0 for row in rows):
        issues.append("INVALID_DEAL_TICKET")
    if any(count > 1 for count in seen.values()):
        issues.append("DUPLICATE_DEAL_TICKET")
    numeric_fields = ("volume", "profit", "commission", "swap", "fee")
    for row in rows:
        for field in numeric_fields:
            value = getattr(row, field)
            if value is not None and not isfinite(value):
                issues.append("NONFINITE_" + field.upper())
    invalid = bool(issues)
    if invalid:
        return DealLedgerSummary(LedgerStatus.INVALID_RECORD,
            tuple(row.ticket for row in rows), len(rows), None, None, None,
            None, None, None, tuple(dict.fromkeys(issues)))

    volumes = [row.volume for row in rows]
    profits = [row.profit for row in rows]
    commissions = [row.commission for row in rows]
    swaps = [row.swap for row in rows]
    fees = [row.fee for row in rows]
    observed_volume = sum(volumes) if all(v is not None for v in volumes) else None
    gross = sum(profits) if all(v is not None for v in profits) else None
    commission_sum = sum(commissions) if all(v is not None for v in commissions) else None
    swap_sum = sum(swaps) if all(v is not None for v in swaps) else None
    fee_sum = sum(fees) if all(v is not None for v in fees) else None
    if any(value is None for value in (observed_volume, gross, commission_sum, swap_sum, fee_sum)):
        issues.append("REQUIRED_ECONOMIC_FIELD_MISSING")
        status = LedgerStatus.INCOMPLETE_FIELDS
        net = None
    else:
        status = LedgerStatus.OBSERVED_ONLY
        net = gross + commission_sum + swap_sum + fee_sum
    return DealLedgerSummary(status, tuple(row.ticket for row in rows), len(rows),
        observed_volume, gross, commission_sum, swap_sum, fee_sum, net, tuple(issues))
