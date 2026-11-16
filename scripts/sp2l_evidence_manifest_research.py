"""Offline evidence-manifest record validation.

The model records provenance and externally measured byte-level artifact hashes.
It performs no filesystem I/O, serialization, hashing, MT5 calls, or completeness
attestation. Manifest serialization and self-hashing are intentionally deferred.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


class EvidenceManifestDisposition(str, Enum):
    INVALID_MANIFEST = "invalid_manifest"
    VALID_MANIFEST_RECORD = "valid_manifest_record"


@dataclass(frozen=True)
class EvidenceArtifactRecord:
    """Metadata for one exact artifact byte stream, not semantic row content."""

    artifact_id: str
    artifact_role: str
    locator: str
    byte_length: int
    byte_sha256: str


@dataclass(frozen=True)
class EvidenceManifestRecord:
    """Provenance record for a scoped observation and its evidence artifacts.

    Values are declarations supplied by the capture process/operator. This
    record does not independently verify account identity, locator existence,
    file bytes, capture time, or the truth of provenance claims.
    """

    manifest_id: str
    recorded_at: str
    account_identity_ref: str
    terminal_session_ref: str
    server_name: str
    date_from: str
    date_to: str
    time_basis: str
    time_basis_source: str
    package_version: str
    terminal_build: str
    capture_method_id: str
    capture_tool_version: str
    observation_ids: tuple[str, ...]
    artifacts: tuple[EvidenceArtifactRecord, ...]


_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_artifact(item: object) -> bool:
    if not isinstance(item, EvidenceArtifactRecord):
        return False
    if not all(
        _nonblank(value)
        for value in (
            item.artifact_id,
            item.artifact_role,
            item.locator,
            item.byte_sha256,
        )
    ):
        return False
    if isinstance(item.byte_length, bool) or not isinstance(item.byte_length, int):
        return False
    if item.byte_length < 0:
        return False
    return bool(_SHA256_RE.fullmatch(item.byte_sha256))


def validate_evidence_manifest(
    manifest: EvidenceManifestRecord,
) -> EvidenceManifestDisposition:
    """Validate record shape and required provenance without I/O or hashing."""
    if not isinstance(manifest, EvidenceManifestRecord):
        return EvidenceManifestDisposition.INVALID_MANIFEST

    required_text = (
        manifest.manifest_id,
        manifest.recorded_at,
        manifest.account_identity_ref,
        manifest.terminal_session_ref,
        manifest.server_name,
        manifest.date_from,
        manifest.date_to,
        manifest.time_basis,
        manifest.time_basis_source,
        manifest.package_version,
        manifest.terminal_build,
        manifest.capture_method_id,
        manifest.capture_tool_version,
    )
    if not all(_nonblank(value) for value in required_text):
        return EvidenceManifestDisposition.INVALID_MANIFEST
    if manifest.date_from == manifest.date_to:
        return EvidenceManifestDisposition.INVALID_MANIFEST

    if not isinstance(manifest.observation_ids, tuple) or not manifest.observation_ids:
        return EvidenceManifestDisposition.INVALID_MANIFEST
    if not all(_nonblank(value) for value in manifest.observation_ids):
        return EvidenceManifestDisposition.INVALID_MANIFEST
    if len(set(manifest.observation_ids)) != len(manifest.observation_ids):
        return EvidenceManifestDisposition.INVALID_MANIFEST

    if not isinstance(manifest.artifacts, tuple) or not manifest.artifacts:
        return EvidenceManifestDisposition.INVALID_MANIFEST
    if not all(_valid_artifact(item) for item in manifest.artifacts):
        return EvidenceManifestDisposition.INVALID_MANIFEST
    artifact_ids = tuple(item.artifact_id for item in manifest.artifacts)
    if len(set(artifact_ids)) != len(artifact_ids):
        return EvidenceManifestDisposition.INVALID_MANIFEST

    return EvidenceManifestDisposition.VALID_MANIFEST_RECORD


def evidence_manifest_record_is_valid(
    manifest: EvidenceManifestRecord,
) -> bool:
    """Convenience shape check; validity is not proof of artifact authenticity."""
    return (
        validate_evidence_manifest(manifest)
        is EvidenceManifestDisposition.VALID_MANIFEST_RECORD
    )
