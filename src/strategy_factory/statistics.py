from __future__ import annotations

from dataclasses import dataclass
from math import comb, erf, isfinite, sqrt
from statistics import fmean, stdev
from typing import Sequence

from .metrics import ResearchMetrics
from .test_contract import DatasetRole


class StatisticalValidationError(ValueError):
    """Raised when a statistical validation contract is invalid."""


@dataclass(frozen=True)
class ConfidenceInterval:
    estimate: float
    lower: float
    upper: float
    confidence_level: float

    def validate(self) -> None:
        if not all(isfinite(v) for v in (self.estimate, self.lower, self.upper)):
            raise StatisticalValidationError("confidence interval values must be finite")
        if not 0.0 < self.confidence_level < 1.0:
            raise StatisticalValidationError("confidence level must be between 0 and 1")
        if self.lower > self.upper:
            raise StatisticalValidationError("confidence interval bounds are reversed")

    def as_dict(self) -> dict[str, float]:
        self.validate()
        return {"estimate": self.estimate, "lower": self.lower, "upper": self.upper, "confidence_level": self.confidence_level}


@dataclass(frozen=True)
class StatisticalValidationResult:
    """Descriptive uncertainty/stability evidence; never a promotion decision."""

    role: DatasetRole
    sample_size: int
    win_rate: ConfidenceInterval
    mean_r: ConfidenceInterval | None
    sign_test_p_value: float | None
    comparison_count: int
    adjusted_sign_test_p_value: float | None
    stability_min_mean_r: float | None
    stability_max_mean_r: float | None
    stability_range_r: float | None

    def validate(self) -> None:
        if not isinstance(self.role, DatasetRole):
            raise StatisticalValidationError("role must be a DatasetRole")
        if not isinstance(self.sample_size, int) or isinstance(self.sample_size, bool) or self.sample_size < 0:
            raise StatisticalValidationError("sample_size must be a non-negative integer")
        self.win_rate.validate()
        if self.mean_r is not None:
            self.mean_r.validate()
        if self.sign_test_p_value is not None and not 0.0 <= self.sign_test_p_value <= 1.0:
            raise StatisticalValidationError("sign_test_p_value must be between 0 and 1")
        if not isinstance(self.comparison_count, int) or isinstance(self.comparison_count, bool) or self.comparison_count < 1:
            raise StatisticalValidationError("comparison_count must be a positive integer")
        if self.adjusted_sign_test_p_value is not None and not 0.0 <= self.adjusted_sign_test_p_value <= 1.0:
            raise StatisticalValidationError("adjusted_sign_test_p_value must be between 0 and 1")
        values = (self.stability_min_mean_r, self.stability_max_mean_r, self.stability_range_r)
        if any(v is not None and not isfinite(v) for v in values):
            raise StatisticalValidationError("stability values must be finite")
        if self.stability_range_r is not None and self.stability_range_r < 0:
            raise StatisticalValidationError("stability range must be non-negative")

    @property
    def canonical_eligible(self) -> bool:
        return False

    @property
    def production_eligible(self) -> bool:
        return False

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "role": self.role.value,
            "sample_size": self.sample_size,
            "win_rate": self.win_rate.as_dict(),
            "mean_r": None if self.mean_r is None else self.mean_r.as_dict(),
            "sign_test_p_value": self.sign_test_p_value,
            "comparison_count": self.comparison_count,
            "adjusted_sign_test_p_value": self.adjusted_sign_test_p_value,
            "stability_min_mean_r": self.stability_min_mean_r,
            "stability_max_mean_r": self.stability_max_mean_r,
            "stability_range_r": self.stability_range_r,
            "canonical_eligible": False,
            "production_eligible": False,
        }


def _normal_cdf(z: float) -> float:
    return 0.5 * (1.0 + erf(z / sqrt(2.0)))


def _normal_quantile(p: float) -> float:
    if not 0.0 < p < 1.0:
        raise StatisticalValidationError("normal quantile probability must be between 0 and 1")
    lo, hi = -8.0, 8.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if _normal_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _wilson_interval(successes: int, trials: int, confidence_level: float) -> ConfidenceInterval:
    if trials == 0:
        return ConfidenceInterval(0.0, 0.0, 1.0, confidence_level)
    z = _normal_quantile(0.5 + confidence_level / 2.0)
    p = successes / trials
    denom = 1.0 + z * z / trials
    center = (p + z * z / (2.0 * trials)) / denom
    half = z * sqrt(p * (1.0 - p) / trials + z * z / (4.0 * trials * trials)) / denom
    return ConfidenceInterval(p, max(0.0, center - half), min(1.0, center + half), confidence_level)


def _mean_interval(values: Sequence[float], confidence_level: float) -> ConfidenceInterval:
    mean = fmean(values)
    if len(values) < 2:
        return ConfidenceInterval(mean, mean, mean, confidence_level)
    z = _normal_quantile(0.5 + confidence_level / 2.0)
    half = z * stdev(values) / sqrt(len(values))
    return ConfidenceInterval(mean, mean - half, mean + half, confidence_level)


def _two_sided_sign_test_p_value(values: Sequence[float]) -> float | None:
    nonzero = [v for v in values if v != 0.0]
    n = len(nonzero)
    if n == 0:
        return None
    positives = sum(v > 0.0 for v in nonzero)
    k = min(positives, n - positives)
    tail = sum(comb(n, i) for i in range(k + 1)) / (2.0 ** n)
    return min(1.0, 2.0 * tail)


def evaluate_statistical_validation(
    metrics: ResearchMetrics,
    *,
    role: DatasetRole,
    trade_returns_r: Sequence[float] | None = None,
    confidence_level: float = 0.95,
    comparison_count: int = 1,
    segment_mean_r: Sequence[float] | None = None,
) -> StatisticalValidationResult:
    """Compute deterministic descriptive uncertainty and stability statistics."""
    metrics.validate()
    if not isinstance(role, DatasetRole):
        raise StatisticalValidationError("role must be a DatasetRole")
    if not 0.0 < confidence_level < 1.0:
        raise StatisticalValidationError("confidence level must be between 0 and 1")
    if not isinstance(comparison_count, int) or isinstance(comparison_count, bool) or comparison_count < 1:
        raise StatisticalValidationError("comparison_count must be a positive integer")

    returns = None if trade_returns_r is None else tuple(float(v) for v in trade_returns_r)
    if returns is not None:
        if len(returns) != metrics.decisive_trades:
            raise StatisticalValidationError("trade_returns_r must match decisive_trades")
        if not all(isfinite(v) for v in returns):
            raise StatisticalValidationError("trade returns must be finite")

    segments = None if segment_mean_r is None else tuple(float(v) for v in segment_mean_r)
    if segments is not None and (not segments or not all(isfinite(v) for v in segments)):
        raise StatisticalValidationError("segment_mean_r must contain finite values")

    p_value = None if returns is None else _two_sided_sign_test_p_value(returns)
    adjusted = None if p_value is None else min(1.0, p_value * comparison_count)
    minimum = None if segments is None else min(segments)
    maximum = None if segments is None else max(segments)

    result = StatisticalValidationResult(
        role=role,
        sample_size=metrics.decisive_trades,
        win_rate=_wilson_interval(metrics.wins, metrics.decisive_trades, confidence_level),
        mean_r=None if returns is None else _mean_interval(returns, confidence_level),
        sign_test_p_value=p_value,
        comparison_count=comparison_count,
        adjusted_sign_test_p_value=adjusted,
        stability_min_mean_r=minimum,
        stability_max_mean_r=maximum,
        stability_range_r=None if segments is None else maximum - minimum,
    )
    result.validate()
    return result
