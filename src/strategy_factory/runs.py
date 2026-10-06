from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Mapping

from .datasets import DatasetArtifact, DatasetRegistry, DatasetRegistryError
from .test_contract import HistoricalTestSpec, ExecutionSemantics
from .usage import DatasetUsage, DatasetUsageLedger


class ResearchRunError(DatasetRegistryError):
    """Raised when a research run cannot establish complete provenance."""


def _canonical(value: Mapping[str, Any]) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as exc:
        raise ResearchRunError("run parameters must be JSON-serializable") from exc


@dataclass(frozen=True)
class ResearchRunIdentity:
    run_id: str
    strategy_id: str
    strategy_revision: str
    manifest_revision: str
    dataset_id: str
    dataset_role: str
    data_revision: str
    dataset_fingerprint: str
    artifact_id: str | None
    execution_semantics: ExecutionSemantics
    parameters: Mapping[str, Any] = field(default_factory=dict)
    objective: str = "DESCRIPTIVE_METRICS_ONLY"
    purpose: str = "HISTORICAL_TEST"

    def validate(self) -> None:
        required = (
            self.run_id, self.strategy_id, self.strategy_revision,
            self.manifest_revision, self.dataset_id, self.dataset_role,
            self.data_revision, self.dataset_fingerprint, self.objective, self.purpose,
        )
        if any(not value for value in required):
            raise ResearchRunError("research run identity is incomplete")
        _canonical(self.parameters)

    @property
    def fingerprint(self) -> str:
        self.validate()
        payload = self.as_dict()
        return hashlib.sha256(_canonical(payload).encode()).hexdigest()

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "manifest_revision": self.manifest_revision,
            "dataset_id": self.dataset_id,
            "dataset_role": self.dataset_role,
            "data_revision": self.data_revision,
            "dataset_fingerprint": self.dataset_fingerprint,
            "artifact_id": self.artifact_id,
            "execution_semantics": self.execution_semantics.value,
            "parameters": dict(self.parameters),
            "objective": self.objective,
            "purpose": self.purpose,
        }


class ResearchRunLedger:
    """Immutable in-memory ledger for research-run provenance."""

    def __init__(self, registry: DatasetRegistry, usage_ledger: DatasetUsageLedger) -> None:
        self.registry = registry
        self.usage_ledger = usage_ledger
        self._records: dict[str, ResearchRunIdentity] = {}

    def create(
        self,
        spec: HistoricalTestSpec,
        *,
        manifest_revision: str,
        run_id: str,
        observed_fingerprint: str,
        purpose: str = "HISTORICAL_TEST",
        artifact: DatasetArtifact | None = None,
    ) -> ResearchRunIdentity:
        if not manifest_revision or not run_id:
            raise ResearchRunError("run_id and manifest_revision are required")
        spec.validate()
        usage = self.usage_ledger.record(
            spec, observed_fingerprint, purpose=purpose, artifact=artifact
        )
        identity = self._from_usage(spec, usage, manifest_revision, run_id)
        existing = self._records.get(run_id)
        if existing is not None and existing != identity:
            raise ResearchRunError("run_id already exists with different provenance")
        if existing is not None:
            return existing
        self._records[run_id] = identity
        return identity

    @staticmethod
    def _from_usage(
        spec: HistoricalTestSpec,
        usage: DatasetUsage,
        manifest_revision: str,
        run_id: str,
    ) -> ResearchRunIdentity:
        return ResearchRunIdentity(
            run_id=run_id,
            strategy_id=spec.strategy_id,
            strategy_revision=spec.strategy_revision,
            manifest_revision=manifest_revision,
            dataset_id=usage.dataset_id,
            dataset_role=usage.dataset_role.value,
            data_revision=usage.data_revision,
            dataset_fingerprint=usage.registered_fingerprint,
            artifact_id=usage.artifact_id,
            execution_semantics=spec.execution_semantics,
            parameters=dict(spec.parameters),
            objective=spec.objective,
            purpose=usage.purpose,
        )

    def get(self, run_id: str) -> ResearchRunIdentity:
        try:
            return self._records[run_id]
        except KeyError as exc:
            raise ResearchRunError(f"research run {run_id!r} is not registered") from exc

    def entries(self) -> tuple[ResearchRunIdentity, ...]:
        return tuple(self._records.values())

    def as_dict(self) -> list[dict[str, Any]]:
        return [entry.as_dict() | {"run_fingerprint": entry.fingerprint} for entry in self.entries()]
