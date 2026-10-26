from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Callable, Mapping, Protocol


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

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> "EvidenceArchiveManifest":
        """Parse and verify a serialized manifest without trusting its fingerprint."""
        try:
            if not isinstance(raw, dict):
                raise EvidenceArchiveError("serialized archive manifest must be an object")
            raw_artifacts = raw["artifacts"]
            if not isinstance(raw_artifacts, list):
                raise EvidenceArchiveError("serialized artifacts must be a list")
            artifacts: list[ArtifactDescriptor] = []
            for item in raw_artifacts:
                if not isinstance(item, dict):
                    raise EvidenceArchiveError("serialized artifact descriptor must be an object")
                if item.get("digest_algorithm") != "sha256":
                    raise EvidenceArchiveError("unsupported artifact digest algorithm")
                artifacts.append(ArtifactDescriptor(
                    role=str(item["role"]),
                    schema_revision=str(item["schema_revision"]),
                    digest_sha256=str(item["digest_sha256"]),
                    byte_length=int(item["byte_length"]),
                    locator=str(item["locator"]),
                ))
            manifest = cls(
                archive_record_id=str(raw["archive_record_id"]),
                evaluator_revision=str(raw["evaluator_revision"]),
                policy_revision=str(raw["policy_revision"]),
                artifacts=tuple(artifacts),
                dataset_manifest_fingerprint=(
                    str(raw["dataset_manifest_fingerprint"])
                    if raw.get("dataset_manifest_fingerprint") is not None else None
                ),
                dataset_role=str(raw["dataset_role"]) if raw.get("dataset_role") is not None else None,
                assurance_scope=str(raw["assurance_scope"]),
                schema_revision=str(raw["schema_revision"]),
            )
            manifest.validate()
            declared_fingerprint = raw.get("manifest_fingerprint")
            if not isinstance(declared_fingerprint, str) or declared_fingerprint != manifest.fingerprint():
                raise EvidenceArchiveError("serialized manifest fingerprint mismatch")
            return manifest
        except EvidenceArchiveError:
            raise
        except (KeyError, TypeError, ValueError) as exc:
            raise EvidenceArchiveError(f"malformed serialized archive manifest: {exc}") from exc

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


class ManifestCommitStatus(str, Enum):
    STORED_AND_VERIFIED = "STORED_AND_VERIFIED"
    ALREADY_PRESENT_MATCHING_DIGEST = "ALREADY_PRESENT_MATCHING_DIGEST"
    CONFLICTING_MANIFEST = "CONFLICTING_MANIFEST"
    MANIFEST_NOT_FOUND = "MANIFEST_NOT_FOUND"
    MANIFEST_INVALID = "MANIFEST_INVALID"
    ARCHIVE_UNAVAILABLE = "ARCHIVE_UNAVAILABLE"


def _safe_record_id(record_id: str) -> str:
    if not record_id or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-" for ch in record_id):
        raise EvidenceArchiveError("archive record ID contains unsupported characters")
    if record_id in {".", ".."}:
        raise EvidenceArchiveError("archive record ID contains unsupported characters")
    return record_id



class FileSystemContentAddressedStore:
    """Local content-addressed adapter with create-if-absent writes.

    This adapter detects accidental corruption and avoids overwriting an
    existing digest path. It does not provide WORM guarantees, issuer
    authentication, backup, or protection from a privileged local actor.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    @staticmethod
    def _digest_from_locator(locator: str) -> str:
        prefix = "sha256:"
        digest = locator[len(prefix):] if locator.startswith(prefix) else ""
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise EvidenceArchiveError("unsupported content-addressed locator")
        return digest

    def _path_for_digest(self, digest: str) -> Path:
        return self.root / "sha256" / digest[:2] / digest

    def put(self, data: bytes) -> str:
        """Persist bytes under their digest; repeat writes are idempotent."""
        if not isinstance(data, bytes):
            raise TypeError("artifact content must be bytes")
        digest = hashlib.sha256(data).hexdigest()
        target = self._path_for_digest(digest)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="wb", prefix=".artifact-", dir=target.parent, delete=False
            ) as handle:
                temporary = Path(handle.name)
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            try:
                # Same-directory hard link makes publication create-if-absent:
                # readers see either no final path or the complete file.
                os.link(temporary, target)
            except FileExistsError:
                existing = target.read_bytes()
                if hashlib.sha256(existing).hexdigest() != digest or existing != data:
                    raise EvidenceArchiveError(
                        "existing content-addressed object does not match its locator"
                    )
            finally:
                temporary.unlink(missing_ok=True)
        except EvidenceArchiveError:
            raise
        except OSError as exc:
            raise ArchiveUnavailable(f"local artifact store write failed: {exc}") from exc
        return f"sha256:{digest}"

    def commit_manifest(self, manifest: EvidenceArchiveManifest) -> ManifestCommitStatus:
        """Atomically create an immutable record manifest, rejecting conflicts."""
        try:
            serialized = manifest.as_dict()
            record_id = _safe_record_id(manifest.archive_record_id)
        except EvidenceArchiveError:
            return ManifestCommitStatus.MANIFEST_INVALID
        # A committed record must not advertise artifacts that are absent or corrupt.
        for artifact in manifest.artifacts:
            try:
                stored = self.get(artifact.locator)
            except ArtifactNotFound:
                return ManifestCommitStatus.MANIFEST_INVALID
            except (ArchiveUnavailable, EvidenceArchiveError):
                return ManifestCommitStatus.ARCHIVE_UNAVAILABLE
            if len(stored) != artifact.byte_length or hashlib.sha256(stored).hexdigest() != artifact.digest_sha256:
                return ManifestCommitStatus.MANIFEST_INVALID
        target = self.root / "manifests" / f"{record_id}.json"
        data = json.dumps(serialized, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="wb", prefix=".manifest-", dir=target.parent, delete=False
            ) as handle:
                temporary = Path(handle.name)
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(temporary, target)
            except FileExistsError:
                try:
                    existing_raw = json.loads(target.read_text(encoding="utf-8"))
                    existing = EvidenceArchiveManifest.from_dict(existing_raw)
                except (OSError, json.JSONDecodeError, EvidenceArchiveError):
                    return ManifestCommitStatus.ARCHIVE_UNAVAILABLE
                if existing.fingerprint() != manifest.fingerprint():
                    return ManifestCommitStatus.CONFLICTING_MANIFEST
                return ManifestCommitStatus.ALREADY_PRESENT_MATCHING_DIGEST
            finally:
                temporary.unlink(missing_ok=True)
            try:
                verified = EvidenceArchiveManifest.from_dict(json.loads(target.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError, EvidenceArchiveError):
                return ManifestCommitStatus.ARCHIVE_UNAVAILABLE
            if verified.fingerprint() != manifest.fingerprint():
                return ManifestCommitStatus.ARCHIVE_UNAVAILABLE
            return ManifestCommitStatus.STORED_AND_VERIFIED
        except OSError:
            return ManifestCommitStatus.ARCHIVE_UNAVAILABLE

    def get_manifest(self, record_id: str) -> EvidenceArchiveManifest:
        """Load a committed manifest and verify its self-consistency."""
        safe_id = _safe_record_id(record_id)
        path = self.root / "manifests" / f"{safe_id}.json"
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise ArtifactNotFound(f"archive manifest not found: {record_id}") from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise ArchiveUnavailable(f"archive manifest read failed: {exc}") from exc
        try:
            return EvidenceArchiveManifest.from_dict(raw)
        except EvidenceArchiveError as exc:
            raise ArchiveUnavailable(f"archive manifest failed verification: {exc}") from exc

    def get(self, locator: str) -> bytes:
        digest = self._digest_from_locator(locator)
        path = self._path_for_digest(digest)
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise ArtifactNotFound(f"content-addressed artifact not found: {locator}") from exc
        except OSError as exc:
            raise ArchiveUnavailable(f"local artifact store read failed: {exc}") from exc
        if hashlib.sha256(data).hexdigest() != digest:
            raise EvidenceArchiveError("stored bytes do not match content-addressed locator")
        return data


@dataclass(frozen=True)
class ArtifactVerificationResult:
    status: ArtifactVerificationStatus
    role: str
    expected_digest: str | None = None
    observed_digest: str | None = None
    expected_length: int | None = None
    observed_length: int | None = None
    detail: str = ""


class ReplayStatus(str, Enum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    BLOCKED_ARTIFACT_UNAVAILABLE = "BLOCKED_ARTIFACT_UNAVAILABLE"
    BLOCKED_EVALUATOR_UNAVAILABLE = "BLOCKED_EVALUATOR_UNAVAILABLE"
    BLOCKED_EVALUATOR_ERROR = "BLOCKED_EVALUATOR_ERROR"
    MANIFEST_INVALID = "MANIFEST_INVALID"


@dataclass(frozen=True)
class ReplayResult:
    status: ReplayStatus
    manifest_fingerprint: str
    expected_decision_digest: str | None = None
    observed_decision_digest: str | None = None
    blocked_role: str | None = None
    detail: str = ""


def replay_archived_decision(
    manifest: EvidenceArchiveManifest,
    store: ArtifactStore,
    *,
    required_input_roles: tuple[str, ...],
    decision_role: str,
    evaluator: Callable[[Mapping[str, bytes]], bytes] | None,
) -> ReplayResult:
    """Replay a caller-supplied evaluator over exact verified archived inputs.

    This is a deterministic harness, not a code loader or evaluator authenticator.
    The caller is responsible for supplying the exact pinned evaluator revision;
    missing inputs or evaluator failures never become a decision.
    """
    try:
        manifest.validate()
    except EvidenceArchiveError as exc:
        return ReplayResult(ReplayStatus.MANIFEST_INVALID, "", detail=str(exc))
    manifest_fp = manifest.fingerprint()
    descriptor = next((item for item in manifest.artifacts if item.role == decision_role), None)
    if descriptor is None or decision_role in required_input_roles or len(set(required_input_roles)) != len(required_input_roles):
        return ReplayResult(ReplayStatus.MANIFEST_INVALID, manifest_fp, detail="decision role or input roles are invalid")
    if evaluator is None:
        return ReplayResult(
            ReplayStatus.BLOCKED_EVALUATOR_UNAVAILABLE, manifest_fp,
            expected_decision_digest=descriptor.digest_sha256,
            detail="pinned evaluator implementation was not supplied",
        )
    inputs: dict[str, bytes] = {}
    for role in required_input_roles:
        result, data = retrieve_verified_artifact(manifest, role, store)
        if result.status is not ArtifactVerificationStatus.VERIFIED or data is None:
            return ReplayResult(
                ReplayStatus.BLOCKED_ARTIFACT_UNAVAILABLE, manifest_fp,
                expected_decision_digest=descriptor.digest_sha256,
                blocked_role=role,
                detail=f"{result.status.value}: {result.detail}",
            )
        inputs[role] = data
    try:
        observed = evaluator(inputs)
        if not isinstance(observed, bytes):
            raise TypeError("evaluator must return serialized decision bytes")
    except Exception as exc:
        return ReplayResult(
            ReplayStatus.BLOCKED_EVALUATOR_ERROR, manifest_fp,
            expected_decision_digest=descriptor.digest_sha256,
            detail=f"evaluator failed: {type(exc).__name__}: {exc}",
        )
    observed_digest = hashlib.sha256(observed).hexdigest()
    expected_length = descriptor.byte_length
    if len(observed) != expected_length or observed_digest != descriptor.digest_sha256:
        return ReplayResult(
            ReplayStatus.MISMATCH, manifest_fp, descriptor.digest_sha256,
            observed_digest, detail=f"replayed decision length {len(observed)}; expected {expected_length}",
        )
    return ReplayResult(
        ReplayStatus.MATCH, manifest_fp, descriptor.digest_sha256, observed_digest,
    )




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
    except EvidenceArchiveError as exc:
        return ArtifactVerificationResult(
            ArtifactVerificationStatus.DIGEST_MISMATCH, role,
            descriptor.digest_sha256, expected_length=descriptor.byte_length,
            detail=f"storage adapter integrity check failed: {exc}",
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
