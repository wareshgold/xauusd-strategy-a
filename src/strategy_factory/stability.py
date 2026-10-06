from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from statistics import fmean
from typing import Any, Sequence


class StabilityContractError(ValueError):
    """Raised when robustness/stability evidence is structurally invalid."""


@dataclass(frozen=True)
class StabilitySegment:
    """One independently identified research segment; descriptive only."""

    segment_id: str
    label: str
    sample_size: int
    mean_r: float
    win_rate: float

    def validate(self) -> None:
        if not self.segment_id or not self.label:
            raise StabilityContractError("segment identity is required")
        if not isinstance(self.sample_size, int) or isinstance(self.sample_size, bool) or self.sample_size < 0:
            raise StabilityContractError("segment sample_size must be a non-negative integer")
        if not isfinite(self.mean_r):
            raise StabilityContractError("segment mean_r must be finite")
        if not 0.0 <= self.win_rate <= 1.0:
            raise StabilityContractError("segment win_rate must be between 0 and 1")

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "segment_id": self.segment_id,
            "label": self.label,
            "sample_size": self.sample_size,
            "mean_r": self.mean_r,
            "win_rate": self.win_rate,
        }


@dataclass(frozen=True)
class StabilityProfile:
    """Deterministic cross-segment description; never a promotion decision."""

    segments: tuple[StabilitySegment, ...]
    min_mean_r: float
    max_mean_r: float
    mean_r_range: float
    average_segment_mean_r: float

    @property
    def canonical_eligible(self) -> bool:
        return False

    @property
    def production_eligible(self) -> bool:
        return False

    def validate(self) -> None:
        if not self.segments:
            raise StabilityContractError("at least one stability segment is required")
        for segment in self.segments:
            segment.validate()
        means = tuple(segment.mean_r for segment in self.segments)
        expected_min = min(means)
        expected_max = max(means)
        expected_range = expected_max - expected_min
        expected_average = fmean(means)
        if self.min_mean_r != expected_min:
            raise StabilityContractError("minimum segment mean mismatch")
        if self.max_mean_r != expected_max:
            raise StabilityContractError("maximum segment mean mismatch")
        if self.mean_r_range != expected_range:
            raise StabilityContractError("segment mean range mismatch")
        if self.average_segment_mean_r != expected_average:
            raise StabilityContractError("average segment mean mismatch")

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "segments": [segment.as_dict() for segment in self.segments],
            "min_mean_r": self.min_mean_r,
            "max_mean_r": self.max_mean_r,
            "mean_r_range": self.mean_r_range,
            "average_segment_mean_r": self.average_segment_mean_r,
            "canonical_eligible": False,
            "production_eligible": False,
        }


def evaluate_stability(segments: Sequence[StabilitySegment]) -> StabilityProfile:
    """Build deterministic descriptive stability evidence from supplied segments."""
    normalized = tuple(segments)
    if not normalized:
        raise StabilityContractError("at least one stability segment is required")

    ids = [segment.segment_id for segment in normalized]
    if len(ids) != len(set(ids)):
        raise StabilityContractError("segment_id values must be unique")

    for segment in normalized:
        segment.validate()

    means = tuple(segment.mean_r for segment in normalized)
    profile = StabilityProfile(
        segments=normalized,
        min_mean_r=min(means),
        max_mean_r=max(means),
        mean_r_range=max(means) - min(means),
        average_segment_mean_r=fmean(means),
    )
    profile.validate()
    return profile
