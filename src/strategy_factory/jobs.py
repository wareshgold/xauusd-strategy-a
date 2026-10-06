from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Mapping

from .runs import ResearchRunError
from .test_contract import ExecutionSemantics, HistoricalTestSpec


class ResearchJobError(ValueError):
    """Raised when a portable research job specification is invalid."""


def _canonical(value: Mapping[str, Any]) -> str:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        )
    except (TypeError, ValueError) as exc:
        raise ResearchJobError("job parameters must be JSON-serializable") from exc


@dataclass(frozen=True)
class ResearchJobSpec:
    """Deployment-neutral, deterministic description of one research job.

    A job contains identity and inputs only. It does not contain strategy
    geometry, execution logic, optimization policy, or production decisions.
    """

    job_id: str
    strategy_id: str
    strategy_revision: str
    manifest_revision: str
    test_id: str
    dataset_id: str
    data_revision: str
    dataset_fingerprint: str
    execution_semantics: ExecutionSemantics
    parameters: Mapping[str, Any] = field(default_factory=dict)
    objective: str = "DESCRIPTIVE_METRICS_ONLY"

    @classmethod
    def from_test_spec(
        cls,
        spec: HistoricalTestSpec,
        *,
        manifest_revision: str,
        dataset_fingerprint: str,
        job_id: str,
    ) -> "ResearchJobSpec":
        spec.validate()
        if not manifest_revision or not dataset_fingerprint or not job_id:
            raise ResearchJobError(
                "job_id, manifest_revision, and dataset_fingerprint are required"
            )
        return cls(
            job_id=job_id,
            strategy_id=spec.strategy_id,
            strategy_revision=spec.strategy_revision,
            manifest_revision=manifest_revision,
            test_id=spec.test_id,
            dataset_id=spec.dataset.dataset_id,
            data_revision=spec.dataset.data_revision,
            dataset_fingerprint=dataset_fingerprint.lower(),
            execution_semantics=spec.execution_semantics,
            parameters=dict(spec.parameters),
            objective=spec.objective,
        )

    def validate(self) -> None:
        required = (
            self.job_id,
            self.strategy_id,
            self.strategy_revision,
            self.manifest_revision,
            self.test_id,
            self.dataset_id,
            self.data_revision,
            self.dataset_fingerprint,
            self.objective,
        )
        if any(not value for value in required):
            raise ResearchJobError("research job identity is incomplete")
        if len(self.dataset_fingerprint) != 64 or any(
            c not in "0123456789abcdef" for c in self.dataset_fingerprint.lower()
        ):
            raise ResearchJobError(
                "dataset_fingerprint must be a 64-character hexadecimal SHA-256"
            )
        if not isinstance(self.execution_semantics, ExecutionSemantics):
            raise ResearchJobError("execution_semantics must be explicit")
        _canonical(self.parameters)

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "job_id": self.job_id,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "manifest_revision": self.manifest_revision,
            "test_id": self.test_id,
            "dataset_id": self.dataset_id,
            "data_revision": self.data_revision,
            "dataset_fingerprint": self.dataset_fingerprint,
            "execution_semantics": self.execution_semantics.value,
            "parameters": dict(self.parameters),
            "objective": self.objective,
        }

    @property
    def fingerprint(self) -> str:
        self.validate()
        return hashlib.sha256(
            _canonical(self.as_dict()).encode("utf-8")
        ).hexdigest()


def validate_job_matches_test_spec(
    job: ResearchJobSpec,
    spec: HistoricalTestSpec,
    *,
    dataset_fingerprint: str,
) -> None:
    """Require a portable job to represent its source test exactly."""
    job.validate()
    spec.validate()

    expected = ResearchJobSpec.from_test_spec(
        spec,
        manifest_revision=job.manifest_revision,
        dataset_fingerprint=dataset_fingerprint,
        job_id=job.job_id,
    )

    if job.as_dict() != expected.as_dict():
        raise ResearchJobError(
            "research job does not exactly match its historical test specification"
        )
