from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any


@dataclass(frozen=True)
class DatasetArtifact:
    """Immutable reference to the concrete stored dataset artifact."""

    artifact_id: str
    location: str
    content_sha256: str
    byte_size: int
    format: str

    def validate(self) -> None:
        if not self.artifact_id or not self.location or not self.content_sha256 or not self.format:
            raise DatasetRegistryError("artifact identity, location, hash, and format are required")
        if len(self.content_sha256) != 64 or any(c not in "0123456789abcdef" for c in self.content_sha256.lower()):
            raise DatasetRegistryError("artifact content_sha256 must be a 64-character hexadecimal SHA-256")
        if self.byte_size < 0:
            raise DatasetRegistryError("artifact byte_size cannot be negative")

    def as_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "location": self.location,
            "content_sha256": self.content_sha256,
            "byte_size": self.byte_size,
            "format": self.format,
        }

from .test_contract import ContractViolation, DatasetRole, HistoricalTestSpec, TestDataset


class DatasetRegistryError(ContractViolation):
    """Raised when a dataset violates registry identity or isolation rules."""


@dataclass(frozen=True)
class DatasetIdentity:
    dataset_id: str
    data_revision: str
    fingerprint: str
    role: DatasetRole
    immutable: bool
    locked: bool = False
    artifact: DatasetArtifact | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "data_revision": self.data_revision,
            "fingerprint": self.fingerprint,
            "role": self.role.value,
            "immutable": self.immutable,
            "locked": self.locked,
            "artifact": None if self.artifact is None else self.artifact.as_dict(),
        }


def fingerprint_dataset(dataset: TestDataset, content_fingerprint: str) -> str:
    """Return a deterministic identity for dataset metadata + source content hash.

    The registry does not inspect market-data bytes. Callers must provide a
    stable content hash produced by the dataset ingestion layer.
    """
    dataset.validate()
    if not content_fingerprint:
        raise DatasetRegistryError("content fingerprint is required")
    payload = {
        "data_revision": dataset.data_revision,
        "start": dataset.start,
        "end": dataset.end,
        "source": dataset.source,
        "content_fingerprint": content_fingerprint,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class DatasetRegistry:
    """In-memory registry enforcing dataset identity and role isolation.

    Persistence is deliberately deferred. This layer establishes the contract;
    a later persistent registry can store the same immutable identity records.
    """

    def __init__(self) -> None:
        self._records: dict[str, DatasetIdentity] = {}
        self._fingerprints: dict[str, str] = {}

    def register(\n        self,\n        dataset: TestDataset,\n        content_fingerprint: str,\n        *,\n        lock: bool = False,\n        artifact: DatasetArtifact | None = None,\n    ) -> DatasetIdentity:\n        dataset.validate()\n        if artifact is not None:\n            artifact.validate()\n            if artifact.content_sha256 != content_fingerprint.lower():\n                raise DatasetRegistryError("artifact SHA-256 does not match content_fingerprint")\n        fingerprint = fingerprint_dataset(dataset, content_fingerprint.lower())\n        existing = self._records.get(dataset.dataset_id)
        if existing is not None:
            if existing.fingerprint != fingerprint or existing.data_revision != dataset.data_revision:
                raise DatasetRegistryError(
                    f"dataset_id {dataset.dataset_id!r} already has a different identity"
                )
            if existing.role is not dataset.role:\n                raise DatasetRegistryError("dataset role cannot change after registration")\n            if artifact is not None and existing.artifact is not None and artifact != existing.artifact:\n                raise DatasetRegistryError("registered dataset artifact cannot change")\n            if artifact is not None and existing.artifact is None:\n                raise DatasetRegistryError("registered dataset cannot acquire a new artifact after identity is locked")\n            if existing.locked and not lock:
                return existing
            return existing

        owner = self._fingerprints.get(fingerprint)
        if owner is not None and owner != dataset.dataset_id:
            raise DatasetRegistryError(
                f"fingerprint already registered under dataset_id {owner!r}"
            )

        if dataset.role is not DatasetRole.DEVELOPMENT and not dataset.immutable:
            raise DatasetRegistryError("validation/holdout datasets must be immutable")

        identity = DatasetIdentity(
            dataset_id=dataset.dataset_id,
            data_revision=dataset.data_revision,
            fingerprint=fingerprint,
            role=dataset.role,
            immutable=dataset.immutable,
            locked=lock or dataset.role is not DatasetRole.DEVELOPMENT,\n            artifact=artifact,\n        )
        self._records[dataset.dataset_id] = identity
        self._fingerprints[fingerprint] = dataset.dataset_id
        return identity

    def get(self, dataset_id: str) -> DatasetIdentity:
        try:
            return self._records[dataset_id]
        except KeyError as exc:
            raise DatasetRegistryError(f"dataset {dataset_id!r} is not registered") from exc

    def validate_spec(self, spec: HistoricalTestSpec, content_fingerprint: str) -> HistoricalTestSpec:
        spec.validate()
        identity = self.get(spec.dataset.dataset_id)
        actual = fingerprint_dataset(spec.dataset, content_fingerprint)
        if actual != identity.fingerprint:
            raise DatasetRegistryError("dataset fingerprint does not match registered identity")
        if spec.dataset.role is not identity.role:
            raise DatasetRegistryError("test dataset role does not match registered identity")
        if identity.locked and spec.dataset.data_revision != identity.data_revision:
            raise DatasetRegistryError("locked dataset revision cannot change")
        return spec

    def assert_no_holdout_reuse(self, dataset: TestDataset, content_fingerprint: str) -> None:
        fingerprint = fingerprint_dataset(dataset, content_fingerprint)
        for record in self._records.values():
            if record.role in (DatasetRole.UNTOUCHED_VALIDATION, DatasetRole.FRESH_HOLDOUT):
                if record.fingerprint == fingerprint and record.dataset_id != dataset.dataset_id:
                    raise DatasetRegistryError("holdout identity cannot be reused under another dataset_id")

    def as_dict(self) -> dict[str, dict[str, Any]]:
        return {key: value.as_dict() for key, value in sorted(self._records.items())}
