from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .datasets import DatasetArtifact, DatasetRegistry, DatasetRegistryError, fingerprint_dataset
from .test_contract import HistoricalTestSpec


class DatasetProvenanceStatus(str, Enum):
    PASS = "PASS"
    BLOCKED = "BLOCKED"
    FAIL = "FAIL"


@dataclass(frozen=True)
class DatasetProvenanceResult:
    status: DatasetProvenanceStatus
    dataset_id: str
    registered_fingerprint: str | None
    observed_fingerprint: str | None
    registered_artifact_id: str | None
    observed_artifact_id: str | None
    reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "dataset_id": self.dataset_id,
            "registered_fingerprint": self.registered_fingerprint,
            "observed_fingerprint": self.observed_fingerprint,
            "registered_artifact_id": self.registered_artifact_id,
            "observed_artifact_id": self.observed_artifact_id,
            "reasons": list(self.reasons),
        }


def evaluate_dataset_provenance(
    spec: HistoricalTestSpec,
    registry: DatasetRegistry,
    observed_content_sha256: str,
    *,
    observed_artifact: DatasetArtifact | None = None,
) -> DatasetProvenanceResult:
    """Verify exact registered dataset/artifact identity.

    Provenance-only: no market-data interpretation, strategy geometry,
    performance, optimization, or production eligibility.
    """
    try:
        spec.validate()
        identity = registry.get(spec.dataset.dataset_id)
    except (DatasetRegistryError, ValueError) as exc:
        return DatasetProvenanceResult(
            DatasetProvenanceStatus.BLOCKED,
            spec.dataset.dataset_id,
            None,
            None,
            None,
            None if observed_artifact is None else observed_artifact.artifact_id,
            (str(exc),),
        )

    observed = observed_content_sha256.lower()
    try:
        computed = fingerprint_dataset(spec.dataset, observed)
    except DatasetRegistryError as exc:
        return DatasetProvenanceResult(
            DatasetProvenanceStatus.BLOCKED,
            identity.dataset_id,
            identity.fingerprint,
            None,
            None if identity.artifact is None else identity.artifact.artifact_id,
            None if observed_artifact is None else observed_artifact.artifact_id,
            (str(exc),),
        )

    reasons: list[str] = []
    if computed != identity.fingerprint:
        reasons.append("DATASET_FINGERPRINT_MISMATCH")
    if spec.dataset.role is not identity.role:
        reasons.append("DATASET_ROLE_MISMATCH")
    if spec.dataset.data_revision != identity.data_revision:
        reasons.append("DATA_REVISION_MISMATCH")

    if observed_artifact is not None:
        try:
            observed_artifact.validate()
        except DatasetRegistryError as exc:
            reasons.append(str(exc))
        else:
            if observed_artifact.content_sha256 != observed:
                reasons.append("OBSERVED_ARTIFACT_HASH_MISMATCH")
            if identity.artifact is None:
                reasons.append("REGISTERED_ARTIFACT_MISSING")
            elif observed_artifact != identity.artifact:
                reasons.append("ARTIFACT_IDENTITY_MISMATCH")
    elif identity.artifact is not None:
        reasons.append("OBSERVED_ARTIFACT_REQUIRED")

    if reasons:
        return DatasetProvenanceResult(
            DatasetProvenanceStatus.FAIL,
            identity.dataset_id,
            identity.fingerprint,
            computed,
            None if identity.artifact is None else identity.artifact.artifact_id,
            None if observed_artifact is None else observed_artifact.artifact_id,
            tuple(reasons),
        )

    return DatasetProvenanceResult(
        DatasetProvenanceStatus.PASS,
        identity.dataset_id,
        identity.fingerprint,
        computed,
        None if identity.artifact is None else identity.artifact.artifact_id,
        None if observed_artifact is None else observed_artifact.artifact_id,
        (),
    )
