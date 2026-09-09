from __future__ import annotations

from dataclasses import dataclass
from statistics import median


@dataclass(frozen=True)
class StabilitySummary:
    observations: int
    mean_return: float
    median_return: float
    min_return: float
    max_return: float


def summarize_returns(returns: list[float]) -> StabilitySummary:
    if not returns:
        raise ValueError("returns must not be empty")
    return StabilitySummary(
        observations=len(returns),
        mean_return=sum(returns) / len(returns),
        median_return=median(returns),
        min_return=min(returns),
        max_return=max(returns),
    )
