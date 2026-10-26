from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Protocol


ARCHIVE_MANIFEST_SCHEMA_REVISION = "FACTORY-EVIDENCE-ARCHIVE-MANIFEST-1"
ARCHIVE_ASSURANCE_SCOPE = "CONTENT_DIGEST_ONLY_NOT_DURABLE_NOT_AUTHENTICATED"


class EvidenceArchiveError(ValueError):
    """Base error for evidence archive contract violations."""


class ArtifactNotFound(EvidenceArchiveError):
    """The requested immutable locator is absent from the store."""


class ArchiveUnavailable(EvidenceArchiveError):
    """The storage adapter cannot currently answer the retrieval request."""


class ArtifactVerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    ARTIFACT_NOT_FOUND = "ARTIFACT_NOT_FOUND"
    ARCHIVE_UNAVAILABLE = "ARCHIVE_UNAVAILABLE"
    DIGEST_MISMATCH = "DIGEST_MISMATCH"
    LENGTH_MISMATCH = "LENGTH_MISMATCH"
    MANIFEST_INVALID = "MANIFEST_INVALID"


@dataclass(frozen=True)
class ArtifactDescriptor:
    role: str
    schema_revision: str
    digest_sha256: str
    byte_length: int
    locator: str

    def as_dict(self) -> dict[str, object]:
        return {
            "role": self.role,
            "schema_revision": self.schema_revision,
            "digest_algorithm": "sha256",
            "digest_sha256": self.digest_sha256,
            "byte_length": self.byte_length,
            "locator": self.locator,
        }

    def validate(self) -> None:
        if not self.role.strip() or not self.schema_revision.strip() or not self.locator.strip():
            raise EvidenceArchiveError("artifact role, schema revision, and locator are required")
        if len(self.digest_sha256) != 64 or any(c not in "0123456789abcdef" for c in self.digest_sha256):
            raise EvidenceArchiveError("artifact SHA-256 digest must be 64 lowercase hexadecimal characters")
        if self.byte_length < 0:
            raise EvidenceArchiveError("artifact byte length cannot be negative")


@dataclass(frozen=True)
class EvidenceArchiveManifest:
    archive_record_id: str
    evaluator_revision: str
    policy_revision: str
    artifacts: tuple[ArtifactDescriptor, ...]
    dataset_manifest_fingerprint: str | None = None
    dataset_role: str | None = None
    assurance_scope: str = ARCHIVE_ASSURANCE_SCOPE
    schema_revision: str = ARCHIVE_MANIFEST_SCHEMA_REVISION

    def payload(self) -> dict[str, object]:
        return {
            "schema_revision": self.schema_revision,
            "archive_record_id": self.archive_record_id,
            "evaluator_revision": self.evaluator_revision,
            "policy_revision": self.policy_revision,
            "dataset_manifest_fingerprint": self.dataset_manifest_fingerprint,
            "dataset_role": self.dataset_role,
            "assurance_scope": self.assurance_scope,
            "artifacts": [item.as_dict() for item in sorted(self.artifacts, key=lambda item: item.role)],
        }

    def fingerprint(self) -> str:
        return hashlib.sha256(json.dumps(
            self.payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        ).encode("utf-8")).hexdigest()

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {**self.payload(), "manifest_fingerprint": self.fingerprint()}

    def validate(self) -> None:
        if self.schema_revision != ARCHIVE_MANIFEST_SCHEMA_REVISION:
            raise EvidenceArchiveError("unsupported archive manifest schema revision")
        if not self.archive_record_id.strip() or not self.evaluator_revision.strip() or not self.policy_revision.strip():
            raise EvidenceArchiveError("archive record, evaluator, and policy identities are required")
        if self.assurance_scope != ARCHIVE_ASSURANCE_SCOPE:
            raise EvidenceArchiveError("archive manifest cannot claim durable or authenticated assurance")
        if not self.artifacts:
            raise EvidenceArchiveError("archive manifest requires at least one artifact")
        roles: set[str] = set()
        for artifact in self.artifacts:
            artifact.validate()
            if artifact.role in roles:
                raise EvidenceArchiveError("archive manifest contains duplicate artifact roles")
            roles.add(artifact.role)
        if self.dataset_manifest_fingerprint is not None:
            value = self.dataset_manifest_fingerprint
            if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                raise EvidenceArchiveError("dataset manifest fingerprint must be a SHA-256 digest")


class ArtifactStore(Protocol):
    """Adapter contract only; durability and trust guarantees are implementation-specific."""

    def get(self, locator: str) -> bytes:
        """Return exact artifact bytes or raise ArtifactNotFound / ArchiveUnavailable."""
        ...


@dataclass(frozen=True)
class ArtifactVerificationResult:
    status: ArtifactVerificationStatus
    role: str
    expected_digest: str | None = None
    observed_digest: str | None = None
    expected_length: int | None = None
    observed_length: int | None = None
    detail: str = ""


def retrieve_verified_artifact(
    manifest: EvidenceArchiveManifest,
    role: str,
    store: ArtifactStore,
) -> tuple[ArtifactVerificationResult, bytes | None]:
    """Verify a retrieved artifact against its manifest before any parsing.

    This function does not persist data, authenticate an issuer, or prove that
    the supplied store is durable. The returned bytes are usable only when
    the result status is VERIFIED.
    """
    try:
        manifest.validate()
    except EvidenceArchiveError as exc:
        return ArtifactVerificationResult(
            ArtifactVerificationStatus.MANIFEST_INVALID, role, detail=str(exc)
        ), None

    descriptor = next((item for item in manifest.artifacts if item.role == role), None)
    if descriptor is None:
        return ArtifactVerificationResult(
            ArtifactVerificationStatus.MANIFEST_INVALID, role, detail="artifact role is not declared"
        ), None

    try:
        data = store.get(descriptor.locator)
    except ArtifactNotFound as exc:
        return ArtifactVerificationResult(
            ArtifactVerificationStatus.ARTIFACT_NOT_FOUND, role,
            descriptor.digest_sha256, expected_length=descriptor.byte_length, detail=str(exc),
        ), None
    except ArchiveUnavailable as exc:
        return ArtifactVerificationResult(
            ArtifactVerificationStatus.ARCHIVE_UNAVAILABLE, role,
            descriptor.digest_sha256, expected_length=descriptor.byte_length, detail=str(exc),
        ), None

    observed_length = len(data)
    observed_digest = hashlib.sha256(data).hexdigest()
    if observed_length != descriptor.byte_length:
        return ArtifactVerificationResult(
            ArtifactVerificationStatus.LENGTH_MISMATCH, role,
            descriptor.digest_sha256, observed_digest,
            descriptor.byte_length, observed_length,
            "retrieved byte length does not match manifest",
        ), None
    if observed_digest != descriptor.digest_sha256:
        return ArtifactVerificationResult(
            ArtifactVerificationStatus.DIGEST_MISMATCH, role,
            descriptor.digest_sha256, observed_digest,
            descriptor.byte_length, observed_length,
            "retrieved content digest does not match manifest",
        ), None

    return ArtifactVerificationResult(
        ArtifactVerificationStatus.VERIFIED, role,
        descriptor.digest_sha256, observed_digest,
        descriptor.byte_length, observed_length,
    ), data
