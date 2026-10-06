from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .datasets import DatasetArtifact, DatasetRegistry, DatasetRegistryError
from .test_contract import DatasetRole, HistoricalTestSpec


class DatasetUsageError(DatasetRegistryError):
    """Raised when a dataset use violates role-isolation policy."""


class UsageDisposition(str, Enum):
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class DatasetUsage:
    test_id: str
    strategy_id: str
    strategy_revision: str
    dataset_id: str
    dataset_role: DatasetRole
    data_revision: str
    registered_fingerprint: str
    observed_fingerprint: str
    artifact_id: str | None
    disposition: UsageDisposition
    purpose: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "test_id": self.test_id,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "dataset_id": self.dataset_id,
            "dataset_role": self.dataset_role.value,
            "data_revision": self.data_revision,
            "registered_fingerprint": self.registered_fingerprint,
            "observed_fingerprint": self.observed_fingerprint,
            "artifact_id": self.artifact_id,
            "disposition": self.disposition.value,
            "purpose": self.purpose,
        }


class DatasetUsageLedger:
    """Deterministic in-memory audit ledger for dataset consumption."""

    def __init__(self, registry: DatasetRegistry) -> None:
        self.registry = registry
        self._entries: list[DatasetUsage] = []

    def record(
        self,
        spec: HistoricalTestSpec,
        observed_fingerprint: str,
        *,
        purpose: str = "HISTORICAL_TEST",
        artifact: DatasetArtifact | None = None,
    ) -> DatasetUsage:
        spec.validate()
        if not purpose:
            raise DatasetUsageError("usage purpose is required")
        identity = self.registry.get(spec.dataset.dataset_id)
        if identity.role is not spec.dataset.role:
            raise DatasetUsageError("dataset role does not match registered identity")
        self.registry.validate_spec(spec, observed_fingerprint)
        if artifact is not None:
            artifact.validate()
            if artifact.content_sha256 != observed_fingerprint.lower():
                raise DatasetUsageError("observed artifact hash does not match observed fingerprint")
            if identity.artifact is None or artifact != identity.artifact:
                raise DatasetUsageError("observed artifact does not match registered artifact")

        if identity.role in (DatasetRole.UNTOUCHED_VALIDATION, DatasetRole.FRESH_HOLDOUT):
            if purpose in {"DEVELOPMENT", "OPTIMIZATION", "PARAMETER_FIT"}:
                raise DatasetUsageError(
                    f"{identity.role.value} dataset cannot be used for {purpose}"
                )

        entry = DatasetUsage(
            test_id=spec.test_id,
            strategy_id=spec.strategy_id,
            strategy_revision=spec.strategy_revision,
            dataset_id=identity.dataset_id,
            dataset_role=identity.role,
            data_revision=identity.data_revision,
            registered_fingerprint=identity.fingerprint,
            observed_fingerprint=self._fingerprint(spec, observed_fingerprint),
            artifact_id=None if artifact is None else artifact.artifact_id,
            disposition=UsageDisposition.ALLOWED,
            purpose=purpose,
        )
        self._entries.append(entry)
        return entry

    @staticmethod
    def _fingerprint(spec: HistoricalTestSpec, content: str) -> str:
        from .datasets import fingerprint_dataset
        return fingerprint_dataset(spec.dataset, content)

    def entries(self) -> tuple[DatasetUsage, ...]:
        return tuple(self._entries)

    def assert_clean(self) -> None:
        blocked = [e for e in self._entries if e.disposition is UsageDisposition.BLOCKED]
        if blocked:
            raise DatasetUsageError("usage ledger contains blocked entries")

    def as_dict(self) -> list[dict[str, Any]]:
        return [entry.as_dict() for entry in self._entries]
