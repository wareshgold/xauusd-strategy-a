"""Offline exact-byte verification for operator-resolved evidence artifacts.

The caller supplies artifact_id -> local path mappings. Manifest locator strings
are deliberately not interpreted: URI, relative-path, root, and traversal
semantics remain outside this verifier until explicitly specified.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import hashlib
import os
from pathlib import Path
import stat

from scripts.sp2l_evidence_manifest_research import (
    EvidenceManifestDisposition,
    EvidenceManifestRecord,
    validate_evidence_manifest,
)


class EvidenceArtifactVerificationDisposition(str, Enum):
    VERIFIED_EXACT_BYTES = "verified_exact_bytes"
    PATH_NOT_SUPPLIED = "path_not_supplied"
    MISSING_PATH = "missing_path"
    NOT_REGULAR_FILE = "not_regular_file"
    READ_ERROR = "read_error"
    FILE_CHANGED_DURING_READ = "file_changed_during_read"
    BYTE_LENGTH_MISMATCH = "byte_length_mismatch"
    SHA256_MISMATCH = "sha256_mismatch"


class EvidenceArtifactVerificationReportDisposition(str, Enum):
    INVALID_MANIFEST = "invalid_manifest"
    INVALID_PATH_MAPPING = "invalid_path_mapping"
    ARTIFACTS_NOT_ALL_VERIFIED = "artifacts_not_all_verified"
    ALL_ARTIFACTS_VERIFIED = "all_artifacts_verified"


@dataclass(frozen=True)
class EvidenceArtifactVerificationResult:
    artifact_id: str
    disposition: EvidenceArtifactVerificationDisposition
    observed_byte_length: int | None = None
    observed_sha256: str | None = None


@dataclass(frozen=True)
class EvidenceArtifactVerificationReport:
    disposition: EvidenceArtifactVerificationReportDisposition
    artifact_results: tuple[EvidenceArtifactVerificationResult, ...]


def _is_path_value(value: object) -> bool:
    if isinstance(value, bytes):
        return False
    if not isinstance(value, (str, os.PathLike)):
        return False
    try:
        raw = os.fspath(value)
    except (TypeError, ValueError):
        return False
    return isinstance(raw, str) and bool(raw.strip())


def _file_identity(info: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        int(info.st_dev),
        int(info.st_ino),
        int(info.st_size),
        int(info.st_mtime_ns),
        int(info.st_ctime_ns),
    )


def _verify_one(artifact, path_value: object) -> EvidenceArtifactVerificationResult:
    if path_value is None:
        return EvidenceArtifactVerificationResult(
            artifact.artifact_id,
            EvidenceArtifactVerificationDisposition.PATH_NOT_SUPPLIED,
        )

    try:
        path = Path(os.fspath(path_value))
        # Check the path before opening it: on Windows, opening a directory
        # as "rb" can fail with PermissionError before fstat is reachable.
        path_info = path.stat()
        if not stat.S_ISREG(path_info.st_mode):
            return EvidenceArtifactVerificationResult(
                artifact.artifact_id,
                EvidenceArtifactVerificationDisposition.NOT_REGULAR_FILE,
            )

        with path.open("rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):
                return EvidenceArtifactVerificationResult(
                    artifact.artifact_id,
                    EvidenceArtifactVerificationDisposition.NOT_REGULAR_FILE,
                )

            digest = hashlib.sha256()
            byte_length = 0
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                byte_length += len(chunk)
                digest.update(chunk)

            after = os.fstat(stream.fileno())
    except FileNotFoundError:
        return EvidenceArtifactVerificationResult(
            artifact.artifact_id,
            EvidenceArtifactVerificationDisposition.MISSING_PATH,
        )
    except OSError:
        return EvidenceArtifactVerificationResult(
            artifact.artifact_id,
            EvidenceArtifactVerificationDisposition.READ_ERROR,
        )
    except (TypeError, ValueError):
        return EvidenceArtifactVerificationResult(
            artifact.artifact_id,
            EvidenceArtifactVerificationDisposition.READ_ERROR,
        )

    observed_sha256 = digest.hexdigest()
    if _file_identity(before) != _file_identity(after):
        disposition = EvidenceArtifactVerificationDisposition.FILE_CHANGED_DURING_READ
    elif byte_length != artifact.byte_length:
        disposition = EvidenceArtifactVerificationDisposition.BYTE_LENGTH_MISMATCH
    elif observed_sha256.lower() != artifact.byte_sha256.lower():
        disposition = EvidenceArtifactVerificationDisposition.SHA256_MISMATCH
    else:
        disposition = EvidenceArtifactVerificationDisposition.VERIFIED_EXACT_BYTES

    return EvidenceArtifactVerificationResult(
        artifact.artifact_id,
        disposition,
        byte_length,
        observed_sha256,
    )


def verify_evidence_artifacts(
    manifest: EvidenceManifestRecord,
    resolved_paths: Mapping[str, str | os.PathLike[str]],
) -> EvidenceArtifactVerificationReport:
    """Verify exact file bytes using explicit artifact-ID-to-path resolution.

    The manifest locator is never parsed or joined to a root. Every manifest
    artifact receives an independent result. A report passes only when every
    artifact is verified against both declared byte length and SHA-256.
    """
    if (
        validate_evidence_manifest(manifest)
        is not EvidenceManifestDisposition.VALID_MANIFEST_RECORD
    ):
        return EvidenceArtifactVerificationReport(
            EvidenceArtifactVerificationReportDisposition.INVALID_MANIFEST,
            (),
        )

    if not isinstance(resolved_paths, Mapping):
        return EvidenceArtifactVerificationReport(
            EvidenceArtifactVerificationReportDisposition.INVALID_PATH_MAPPING,
            (),
        )

    artifact_ids = {item.artifact_id for item in manifest.artifacts}
    if any(not isinstance(key, str) for key in resolved_paths):
        return EvidenceArtifactVerificationReport(
            EvidenceArtifactVerificationReportDisposition.INVALID_PATH_MAPPING,
            (),
        )
    if any(key not in artifact_ids for key in resolved_paths):
        return EvidenceArtifactVerificationReport(
            EvidenceArtifactVerificationReportDisposition.INVALID_PATH_MAPPING,
            (),
        )
    if any(not _is_path_value(value) for value in resolved_paths.values()):
        return EvidenceArtifactVerificationReport(
            EvidenceArtifactVerificationReportDisposition.INVALID_PATH_MAPPING,
            (),
        )

    results = tuple(
        _verify_one(artifact, resolved_paths.get(artifact.artifact_id))
        for artifact in manifest.artifacts
    )
    all_verified = all(
        item.disposition
        is EvidenceArtifactVerificationDisposition.VERIFIED_EXACT_BYTES
        for item in results
    )
    report_disposition = (
        EvidenceArtifactVerificationReportDisposition.ALL_ARTIFACTS_VERIFIED
        if all_verified
        else EvidenceArtifactVerificationReportDisposition.ARTIFACTS_NOT_ALL_VERIFIED
    )
    return EvidenceArtifactVerificationReport(report_disposition, results)
