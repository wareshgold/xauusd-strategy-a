from __future__ import annotations

from dataclasses import dataclass
import hashlib

from .datasets import DatasetArtifact, DatasetRegistry, DatasetRegistryError
from .test_contract import TestDataset


class DatasetIngestionError(ValueError):
    """Raised when a historical dataset cannot be ingested deterministically."""


@dataclass(frozen=True)
class LoadedDataset:
    """Immutable raw dataset payload plus its registered artifact identity.

    The ingestion boundary deliberately does not parse, resample, timezone-shift,
    or otherwise transform market data. The raw bytes are the content identity.
    """

    dataset: TestDataset
    artifact: DatasetArtifact
    content_sha256: str
    byte_size: int
    payload: bytes

    def validate(self) -> None:
        self.dataset.validate()
        self.artifact.validate()
        actual = hashlib.sha256(self.payload).hexdigest()
        if actual != self.content_sha256:
            raise DatasetIngestionError("loaded payload SHA-256 does not match identity")
        if self.byte_size != len(self.payload):
            raise DatasetIngestionError("loaded payload byte size does not match identity")
        if self.artifact.content_sha256 != self.content_sha256:
            raise DatasetIngestionError("artifact SHA-256 does not match loaded payload")
        if self.artifact.byte_size != self.byte_size:
            raise DatasetIngestionError("artifact byte size does not match loaded payload")

    @property
    def fingerprint(self) -> str:
        self.validate()
        from .datasets import fingerprint_dataset
        return fingerprint_dataset(self.dataset, self.content_sha256)


class HistoricalDatasetAdapter:
    """Deterministic boundary for registering and loading raw historical artifacts."""

    def __init__(self, registry: DatasetRegistry) -> None:
        self.registry = registry

    @staticmethod
    def content_identity(payload: bytes) -> tuple[str, int]:
        if not isinstance(payload, bytes):
            raise DatasetIngestionError("historical dataset payload must be bytes")
        return hashlib.sha256(payload).hexdigest(), len(payload)

    def ingest(
        self,
        dataset: TestDataset,
        payload: bytes,
        *,
        artifact_id: str,
        location: str,
        format: str,
        lock: bool = False,
    ) -> LoadedDataset:
        dataset.validate()
        content_sha256, byte_size = self.content_identity(payload)
        artifact = DatasetArtifact(
            artifact_id=artifact_id,
            location=location,
            content_sha256=content_sha256,
            byte_size=byte_size,
            format=format,
        )
        try:
            self.registry.register(
                dataset,
                content_sha256,
                lock=lock,
                artifact=artifact,
            )
        except DatasetRegistryError as exc:
            raise DatasetIngestionError("historical dataset failed registry validation") from exc

        loaded = LoadedDataset(
            dataset=dataset,
            artifact=artifact,
            content_sha256=content_sha256,
            byte_size=byte_size,
            payload=payload,
        )
        loaded.validate()
        return loaded

    def verify(
        self,
        dataset: TestDataset,
        payload: bytes,
    ) -> LoadedDataset:
        """Verify bytes against the already-registered dataset identity."""
        dataset.validate()
        content_sha256, byte_size = self.content_identity(payload)
        try:
            identity = self.registry.get(dataset.dataset_id)
            self.registry.validate_spec(dataset_spec := _dataset_spec_placeholder(dataset), content_sha256)
        except DatasetRegistryError as exc:
            raise DatasetIngestionError("historical dataset failed identity verification") from exc

        if identity.artifact is None:
            artifact = DatasetArtifact(
                artifact_id=f"UNSPECIFIED-{dataset.dataset_id}",
                location="UNSPECIFIED",
                content_sha256=content_sha256,
                byte_size=byte_size,
                format="UNKNOWN",
            )
        else:
            artifact = identity.artifact
            if artifact.content_sha256 != content_sha256 or artifact.byte_size != byte_size:
                raise DatasetIngestionError("payload does not match registered artifact")

        loaded = LoadedDataset(dataset, artifact, content_sha256, byte_size, payload)
        loaded.validate()
        return loaded


def _dataset_spec_placeholder(dataset: TestDataset):
    from .test_contract import HistoricalTestSpec, ExecutionSemantics
    return HistoricalTestSpec(
        test_id=f"DATASET-VERIFY-{dataset.dataset_id}",
        strategy_id="DATASET_ADAPTER",
        strategy_revision=dataset.data_revision,
        dataset=dataset,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
    )
