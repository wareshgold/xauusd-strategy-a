from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from statistics import fmean, stdev
from typing import Sequence

from .forward_observed_evidence import ForwardObservedEvidence, ForwardObservedEvidenceError
from .statistics import ConfidenceInterval, _wilson_interval


class ForwardObservedStatisticsError(ValueError):
    """Raised when observed Forward statistics cannot be computed safely."""


@dataclass(frozen=True)
class ForwardObservedStatistics:
    """Descriptive statistics over already-observed Forward lifecycle facts.

    This contract deliberately does not use R-multiples, profitability
    thresholds, parameter selection, canonical rules, or production decisions.
    """

    evidence_fingerprint: str
    observation_count: int
    pips_measured_count: int
    pips_missing_count: int
    net_measured_count: int
    positive_pips_count: int
    negative_pips_count: int
    zero_pips_count: int
    pips_coverage: float
    positive_pips_rate: ConfidenceInterval
    mean_pips: ConfidenceInterval | None
    mean_net: ConfidenceInterval | None

    def validate(self, evidence: ForwardObservedEvidence) -> None:
        evidence.validate()
        if self.evidence_fingerprint != evidence.fingerprint:
            raise ForwardObservedStatisticsError("observed statistics are not bound to Forward evidence")
        counts = (
            self.observation_count,
            self.pips_measured_count,
            self.pips_missing_count,
            self.net_measured_count,
            self.positive_pips_count,
            self.negative_pips_count,
            self.zero_pips_count,
        )
        if any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in counts):
            raise ForwardObservedStatisticsError("observation counts must be non-negative integers")
        if self.observation_count != len(evidence.trades):
            raise ForwardObservedStatisticsError("observation count does not match Forward evidence")
        if self.pips_measured_count + self.pips_missing_count != self.observation_count:
            raise ForwardObservedStatisticsError("pips coverage counts are inconsistent")
        if self.positive_pips_count + self.negative_pips_count + self.zero_pips_count != self.pips_measured_count:
            raise ForwardObservedStatisticsError("pips sign counts are inconsistent")
        if self.net_measured_count != self.observation_count:
            raise ForwardObservedStatisticsError("net coverage does not match observed trades")
        if not isfinite(self.pips_coverage) or not 0.0 <= self.pips_coverage <= 1.0:
            raise ForwardObservedStatisticsError("pips coverage must be between 0 and 1")
        self.positive_pips_rate.validate()
        if self.mean_pips is not None:
            self.mean_pips.validate()
        if self.mean_net is not None:
            self.mean_net.validate()

    def as_dict(self) -> dict[str, object]:
        return {
            "evidence_fingerprint": self.evidence_fingerprint,
            "observation_count": self.observation_count,
            "pips_measured_count": self.pips_measured_count,
            "pips_missing_count": self.pips_missing_count,
            "net_measured_count": self.net_measured_count,
            "positive_pips_count": self.positive_pips_count,
            "negative_pips_count": self.negative_pips_count,
            "zero_pips_count": self.zero_pips_count,
            "pips_coverage": self.pips_coverage,
            "positive_pips_rate": self.positive_pips_rate.as_dict(),
            "mean_pips": None if self.mean_pips is None else self.mean_pips.as_dict(),
            "mean_net": None if self.mean_net is None else self.mean_net.as_dict(),
            "canonical_eligible": False,
            "production_eligible": False,
        }


def _mean_interval(values: Sequence[float], confidence_level: float) -> ConfidenceInterval:
    mean = fmean(values)
    if len(values) < 2:
        return ConfidenceInterval(mean, mean, mean, confidence_level)
    half = 1.96 * stdev(values) / sqrt(len(values))
    return ConfidenceInterval(mean, mean - half, mean + half, confidence_level)


def build_forward_observed_statistics(
    evidence: ForwardObservedEvidence,
    *,
    confidence_level: float = 0.95,
) -> ForwardObservedStatistics:
    evidence.validate()
    if not 0.0 < confidence_level < 1.0:
        raise ForwardObservedStatisticsError("confidence level must be between 0 and 1")

    pips = tuple(float(t.pips_result) for t in evidence.trades if t.pips_result is not None)
    net = tuple(float(t.net) for t in evidence.trades)
    if not all(isfinite(v) for v in pips + net):
        raise ForwardObservedStatisticsError("observed pips/net values must be finite")

    positive = sum(v > 0.0 for v in pips)
    negative = sum(v < 0.0 for v in pips)
    zero = sum(v == 0.0 for v in pips)
    result = ForwardObservedStatistics(
        evidence_fingerprint=evidence.fingerprint,
        observation_count=len(evidence.trades),
        pips_measured_count=len(pips),
        pips_missing_count=len(evidence.trades) - len(pips),
        net_measured_count=len(net),
        positive_pips_count=positive,
        negative_pips_count=negative,
        zero_pips_count=zero,
        pips_coverage=len(pips) / len(evidence.trades) if evidence.trades else 0.0,
        positive_pips_rate=_wilson_interval(positive, len(pips), confidence_level),
        mean_pips=None if not pips else _mean_interval(pips, confidence_level),
        mean_net=None if not net else _mean_interval(net, confidence_level),
    )
    result.validate(evidence)
    return result
