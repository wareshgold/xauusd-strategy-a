from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping, Sequence

from .research_record import ResearchRecord
from .research_evidence_bundle import ResearchEvidenceBundle, validate_research_evidence_bundle
from .statistical_evidence import StatisticalEvidence
from .stability_evidence import StabilityEvidence


class RobustnessMatrixError(ValueError):
    """Raised when robustness-matrix members are not provenance-compatible."""


def _canonical_parameters(parameters: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    if not isinstance(parameters, Mapping):
        raise RobustnessMatrixError("parameter_identity must be a mapping")
    return tuple(
        (str(key), json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        for key, value in sorted(parameters.items(), key=lambda item: str(item[0]))
    )


@dataclass(frozen=True)
class RobustnessMember:
    """Immutable provenance identity and descriptive result for one matrix member."""

    member_id: str
    parameter_identity: tuple[tuple[str, str], ...]
    run_id: str
    run_fingerprint: str
    research_record_fingerprint: str
    bundle_fingerprint: str
    strategy_id: str
    strategy_revision: str
    manifest_revision: str
    dataset_id: str
    dataset_role: str
    data_revision: str
    dataset_fingerprint: str
    execution_semantics: str
    sample_size: int
    win_rate: float
    mean_r: float | None
    stability_min_mean_r: float | None
    stability_max_mean_r: float | None

    def validate(self) -> None:
        if not all((
            self.member_id, self.run_id, self.run_fingerprint,
            self.research_record_fingerprint, self.bundle_fingerprint,
            self.strategy_id, self.strategy_revision, self.manifest_revision,
            self.dataset_id, self.dataset_role, self.data_revision,
            self.dataset_fingerprint, self.execution_semantics,
        )):
            raise RobustnessMatrixError("robustness member identity is incomplete")
        if not isinstance(self.parameter_identity, tuple):
            raise RobustnessMatrixError("parameter_identity must be canonicalized")
        if not isinstance(self.sample_size, int) or isinstance(self.sample_size, bool) or self.sample_size < 0:
            raise RobustnessMatrixError("robustness sample_size must be a non-negative integer")
        if not 0.0 <= self.win_rate <= 1.0:
            raise RobustnessMatrixError("robustness win_rate must be between 0 and 1")
        for value in (self.mean_r, self.stability_min_mean_r, self.stability_max_mean_r):
            if value is not None and not isinstance(value, (int, float)):
                raise RobustnessMatrixError("robustness descriptive values must be numeric")

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "member_id": self.member_id,
            "parameter_identity": [[key, value] for key, value in self.parameter_identity],
            "run_id": self.run_id,
            "run_fingerprint": self.run_fingerprint,
            "research_record_fingerprint": self.research_record_fingerprint,
            "bundle_fingerprint": self.bundle_fingerprint,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "manifest_revision": self.manifest_revision,
            "dataset_id": self.dataset_id,
            "dataset_role": self.dataset_role,
            "data_revision": self.data_revision,
            "dataset_fingerprint": self.dataset_fingerprint,
            "execution_semantics": self.execution_semantics,
            "sample_size": self.sample_size,
            "win_rate": self.win_rate,
            "mean_r": self.mean_r,
            "stability_min_mean_r": self.stability_min_mean_r,
            "stability_max_mean_r": self.stability_max_mean_r,
        }


@dataclass(frozen=True)
class RobustnessMatrix:
    """Immutable descriptive matrix; it never chooses a winner or promotes a strategy."""

    matrix_revision: str
    strategy_id: str
    strategy_revision: str
    manifest_revision: str
    dataset_role: str
    execution_semantics: str
    members: tuple[RobustnessMember, ...]
    member_count: int
    mean_r_min: float | None
    mean_r_max: float | None
    mean_r_range: float | None
    win_rate_min: float
    win_rate_max: float
    win_rate_range: float
    stability_min_mean_r: float | None
    stability_max_mean_r: float | None
    fingerprint: str

    @staticmethod
    def _payload(values: dict[str, Any]) -> bytes:
        return json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

    def _fingerprint_payload(self) -> dict[str, Any]:
        return {
            "matrix_revision": self.matrix_revision,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "manifest_revision": self.manifest_revision,
            "dataset_role": self.dataset_role,
            "execution_semantics": self.execution_semantics,
            "members": [member.as_dict() for member in self.members],
            "member_count": self.member_count,
            "mean_r_min": self.mean_r_min,
            "mean_r_max": self.mean_r_max,
            "mean_r_range": self.mean_r_range,
            "win_rate_min": self.win_rate_min,
            "win_rate_max": self.win_rate_max,
            "win_rate_range": self.win_rate_range,
            "stability_min_mean_r": self.stability_min_mean_r,
            "stability_max_mean_r": self.stability_max_mean_r,
        }

    def validate(self) -> None:
        if len(self.members) < 2:
            raise RobustnessMatrixError("robustness matrix requires at least two members")
        if self.member_count != len(self.members):
            raise RobustnessMatrixError("member_count does not match members")
        if len({member.member_id for member in self.members}) != len(self.members):
            raise RobustnessMatrixError("robustness member_id values must be unique")
        if len({member.run_id for member in self.members}) != len(self.members):
            raise RobustnessMatrixError("robustness run_id values must be unique")
        for member in self.members:
            member.validate()
        expected = hashlib.sha256(self._payload(self._fingerprint_payload())).hexdigest()
        if self.fingerprint != expected:
            raise RobustnessMatrixError("robustness matrix fingerprint mismatch")

    def as_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        self.validate()
        data = self._fingerprint_payload()
        if include_fingerprint:
            data["fingerprint"] = self.fingerprint
        return data


def _build_member(
    record: ResearchRecord,
    statistical: StatisticalEvidence,
    stability: StabilityEvidence,
    bundle: ResearchEvidenceBundle,
    *,
    member_id: str,
    parameter_identity: Mapping[str, Any],
) -> RobustnessMember:
    validate_research_evidence_bundle(bundle, record, statistical, stability)
    result = statistical.statistical_result
    profile = stability.stability_profile
    result.validate()
    profile.validate()
    return RobustnessMember(
        member_id=member_id,
        parameter_identity=_canonical_parameters(parameter_identity),
        run_id=record.run_id,
        run_fingerprint=record.run_fingerprint,
        research_record_fingerprint=record.fingerprint,
        bundle_fingerprint=bundle.fingerprint,
        strategy_id=record.strategy_id,
        strategy_revision=record.strategy_revision,
        manifest_revision=record.manifest_revision,
        dataset_id=record.dataset_id,
        dataset_role=record.dataset_role,
        data_revision=record.data_revision,
        dataset_fingerprint=record.dataset_fingerprint,
        execution_semantics=record.execution_semantics,
        sample_size=result.sample_size,
        win_rate=result.win_rate.estimate,
        mean_r=None if result.mean_r is None else result.mean_r.estimate,
        stability_min_mean_r=profile.min_mean_r,
        stability_max_mean_r=profile.max_mean_r,
    )


def build_robustness_matrix(
    members: Sequence[
        tuple[ResearchRecord, StatisticalEvidence, StabilityEvidence, ResearchEvidenceBundle, str, Mapping[str, Any]]
    ],
    *,
    matrix_revision: str = "ROBUSTNESS-MATRIX-1",
) -> RobustnessMatrix:
    """Build a provenance-safe descriptive matrix from distinct research runs.

    A matrix is deliberately single-role and single-execution-semantics. Separate
    matrices must be used for Development, Untouched Validation, or Fresh Holdout,
    and for different execution semantics. This prevents accidental mixing of
    evidence classes while leaving all promotion decisions outside this contract.
    """
    if len(members) < 2:
        raise RobustnessMatrixError("robustness matrix requires at least two members")

    built: list[RobustnessMember] = []
    for record, statistical, stability, bundle, member_id, parameter_identity in members:
        built.append(_build_member(
            record, statistical, stability, bundle,
            member_id=member_id, parameter_identity=parameter_identity,
        ))

    baseline = built[0]
    for member in built[1:]:
        if member.strategy_id != baseline.strategy_id or member.strategy_revision != baseline.strategy_revision:
            raise RobustnessMatrixError("robustness strategy identity does not match")
        if member.manifest_revision != baseline.manifest_revision:
            raise RobustnessMatrixError("robustness manifest revision does not match")
        if member.dataset_role != baseline.dataset_role:
            raise RobustnessMatrixError("robustness dataset roles must not be mixed")
        if member.execution_semantics != baseline.execution_semantics:
            raise RobustnessMatrixError("robustness execution semantics must not be mixed")

    mean_values = [member.mean_r for member in built if member.mean_r is not None]
    stability_values = [
        value
        for member in built
        for value in (member.stability_min_mean_r, member.stability_max_mean_r)
        if value is not None
    ]
    mean_min = min(mean_values) if mean_values else None
    mean_max = max(mean_values) if mean_values else None

    matrix = RobustnessMatrix(
        matrix_revision=matrix_revision,
        strategy_id=baseline.strategy_id,
        strategy_revision=baseline.strategy_revision,
        manifest_revision=baseline.manifest_revision,
        dataset_role=baseline.dataset_role,
        execution_semantics=baseline.execution_semantics,
        members=tuple(built),
        member_count=len(built),
        mean_r_min=mean_min,
        mean_r_max=mean_max,
        mean_r_range=None if mean_min is None else mean_max - mean_min,
        win_rate_min=min(member.win_rate for member in built),
        win_rate_max=max(member.win_rate for member in built),
        win_rate_range=max(member.win_rate for member in built) - min(member.win_rate for member in built),
        stability_min_mean_r=min(stability_values) if stability_values else None,
        stability_max_mean_r=max(stability_values) if stability_values else None,
        fingerprint="",
    )
    fingerprint = hashlib.sha256(matrix._payload(matrix._fingerprint_payload())).hexdigest()
    return RobustnessMatrix(**{**matrix.__dict__, "fingerprint": fingerprint})
