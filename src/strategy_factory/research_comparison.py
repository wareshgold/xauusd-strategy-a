from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Sequence

from .research_record import ResearchRecord
from .research_evidence_bundle import ResearchEvidenceBundle, validate_research_evidence_bundle
from .statistical_evidence import StatisticalEvidence
from .stability_evidence import StabilityEvidence


class ResearchComparisonError(ValueError):
    """Raised when research comparison inputs are not provenance-compatible."""


@dataclass(frozen=True)
class ComparisonObservation:
    """Descriptive metrics for one provenance-valid research run."""

    run_id: str
    research_record_fingerprint: str
    bundle_fingerprint: str
    sample_size: int
    win_rate: float
    mean_r: float | None
    max_drawdown_r: float | None
    stability_min_mean_r: float | None
    stability_max_mean_r: float | None

    def validate(self) -> None:
        if not self.run_id or not self.research_record_fingerprint or not self.bundle_fingerprint:
            raise ResearchComparisonError("comparison observation identity is incomplete")
        if not isinstance(self.sample_size, int) or isinstance(self.sample_size, bool) or self.sample_size < 0:
            raise ResearchComparisonError("comparison sample_size must be a non-negative integer")
        values = (self.win_rate, self.mean_r, self.max_drawdown_r,
                  self.stability_min_mean_r, self.stability_max_mean_r)
        if any(v is not None and not isinstance(v, (int, float)) for v in values):
            raise ResearchComparisonError("comparison values must be numeric")
        if not 0.0 <= self.win_rate <= 1.0:
            raise ResearchComparisonError("comparison win_rate must be between 0 and 1")

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "run_id": self.run_id,
            "research_record_fingerprint": self.research_record_fingerprint,
            "bundle_fingerprint": self.bundle_fingerprint,
            "sample_size": self.sample_size,
            "win_rate": self.win_rate,
            "mean_r": self.mean_r,
            "max_drawdown_r": self.max_drawdown_r,
            "stability_min_mean_r": self.stability_min_mean_r,
            "stability_max_mean_r": self.stability_max_mean_r,
        }


@dataclass(frozen=True)
class ResearchComparison:
    """Immutable descriptive comparison; never selects a winner or promotes a strategy."""

    comparison_revision: str
    strategy_id: str
    strategy_revision: str
    dataset_role: str
    baseline: ComparisonObservation
    candidates: tuple[ComparisonObservation, ...]
    comparison_count: int
    candidate_mean_r_delta: tuple[float | None, ...]
    candidate_win_rate_delta: tuple[float, ...]
    candidate_drawdown_delta: tuple[float | None, ...]
    fingerprint: str

    @staticmethod
    def _payload(values: dict[str, Any]) -> bytes:
        return json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

    def _fingerprint_payload(self) -> dict[str, Any]:
        return {
            "comparison_revision": self.comparison_revision,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "dataset_role": self.dataset_role,
            "baseline": self.baseline.as_dict(),
            "candidates": [candidate.as_dict() for candidate in self.candidates],
            "comparison_count": self.comparison_count,
            "candidate_mean_r_delta": list(self.candidate_mean_r_delta),
            "candidate_win_rate_delta": list(self.candidate_win_rate_delta),
            "candidate_drawdown_delta": list(self.candidate_drawdown_delta),
        }

    def validate(self) -> None:
        self.baseline.validate()
        for candidate in self.candidates:
            candidate.validate()
        if not self.candidates:
            raise ResearchComparisonError("comparison requires at least one candidate")
        if len(self.candidates) != len(self.candidate_mean_r_delta) or len(self.candidates) != len(self.candidate_win_rate_delta) or len(self.candidates) != len(self.candidate_drawdown_delta):
            raise ResearchComparisonError("comparison delta lengths do not match candidates")
        if self.comparison_count != len(self.candidates):
            raise ResearchComparisonError("comparison_count does not match candidates")
        expected = hashlib.sha256(self._payload(self._fingerprint_payload())).hexdigest()
        if self.fingerprint != expected:
            raise ResearchComparisonError("research comparison fingerprint mismatch")

    def as_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        self.validate()
        data = self._fingerprint_payload()
        if include_fingerprint:
            data["fingerprint"] = self.fingerprint
        return data


def _observation(record: ResearchRecord, bundle: ResearchEvidenceBundle,
                 statistical: StatisticalEvidence, stability: StabilityEvidence) -> ComparisonObservation:
    result = statistical.statistical_result
    profile = stability.stability_profile
    result.validate()
    profile.validate()
    return ComparisonObservation(
        run_id=record.run_id,
        research_record_fingerprint=record.fingerprint,
        bundle_fingerprint=bundle.fingerprint,
        sample_size=result.sample_size,
        win_rate=result.win_rate.estimate,
        mean_r=None if result.mean_r is None else result.mean_r.estimate,
        max_drawdown_r=None,
        stability_min_mean_r=profile.min_mean_r,
        stability_max_mean_r=profile.max_mean_r,
    )


def build_research_comparison(
    baseline: tuple[ResearchRecord, StatisticalEvidence, StabilityEvidence, ResearchEvidenceBundle],
    candidates: Sequence[tuple[ResearchRecord, StatisticalEvidence, StabilityEvidence, ResearchEvidenceBundle]],
    *,
    comparison_revision: str = "RESEARCH-COMPARISON-1",
) -> ResearchComparison:
    """Compare provenance-valid runs descriptively; no winner selection."""
    if not candidates:
        raise ResearchComparisonError("at least one candidate is required")

    b_record, b_stat, b_stability, b_bundle = baseline
    validate_research_evidence_bundle(b_bundle, b_record, b_stat, b_stability)
    b_obs = _observation(b_record, b_bundle, b_stat, b_stability)

    observations: list[ComparisonObservation] = []
    for candidate in candidates:
        record, stat, stability, bundle = candidate
        validate_research_evidence_bundle(bundle, record, stat, stability)
        obs = _observation(record, bundle, stat, stability)
        if obs.run_id == b_obs.run_id:
            raise ResearchComparisonError("baseline and candidate run_id must be distinct")
        if record.strategy_id != b_record.strategy_id or record.strategy_revision != b_record.strategy_revision:
            raise ResearchComparisonError("comparison strategy identity does not match baseline")
        if record.dataset_role != b_record.dataset_role:
            raise ResearchComparisonError("comparison dataset roles do not match baseline")
        observations.append(obs)

    mean_deltas = tuple(
        None if b_obs.mean_r is None or obs.mean_r is None else obs.mean_r - b_obs.mean_r
        for obs in observations
    )
    win_deltas = tuple(obs.win_rate - b_obs.win_rate for obs in observations)
    drawdown_deltas = tuple(
        None if b_obs.max_drawdown_r is None or obs.max_drawdown_r is None
        else obs.max_drawdown_r - b_obs.max_drawdown_r
        for obs in observations
    )

    comparison = ResearchComparison(
        comparison_revision=comparison_revision,
        strategy_id=b_record.strategy_id,
        strategy_revision=b_record.strategy_revision,
        dataset_role=b_record.dataset_role,
        baseline=b_obs,
        candidates=tuple(observations),
        comparison_count=len(observations),
        candidate_mean_r_delta=mean_deltas,
        candidate_win_rate_delta=win_deltas,
        candidate_drawdown_delta=drawdown_deltas,
        fingerprint="",
    )
    fingerprint = hashlib.sha256(comparison._payload(comparison._fingerprint_payload())).hexdigest()
    return ResearchComparison(**{**comparison.__dict__, "fingerprint": fingerprint})
