import hashlib
from dataclasses import replace

import pytest

from strategy_factory.evidence_archive import (
    ARCHIVE_ASSURANCE_SCOPE,
    ARCHIVE_MANIFEST_SCHEMA_REVISION,
    ArchiveUnavailable,
    ArtifactDescriptor,
    ArtifactNotFound,
    ArtifactVerificationStatus,
    EvidenceArchiveError,
    EvidenceArchiveManifest,
    retrieve_verified_artifact,
)


class FakeStore:
    def __init__(self, items=None, *, unavailable=False):
        self.items = items or {}
        self.unavailable = unavailable

    def get(self, locator):
        if self.unavailable:
            raise ArchiveUnavailable("adapter unavailable")
        if locator not in self.items:
            raise ArtifactNotFound("locator absent")
        return self.items[locator]


def build_manifest(data=b'{"decision":"PASS"}'):
    digest = hashlib.sha256(data).hexdigest()
    artifact = ArtifactDescriptor(
        role="provenance_decision",
        schema_revision="RESEARCH-PROVENANCE-DECISION-1",
        digest_sha256=digest,
        byte_length=len(data),
        locator=f"sha256:{digest}",
    )
    manifest = EvidenceArchiveManifest(
        archive_record_id="ARCHIVE-001",
        evaluator_revision="evaluator@abc123",
        policy_revision="policy@1",
        artifacts=(artifact,),
    )
    return manifest, data


def test_archive_manifest_fingerprint_and_serialization_are_deterministic():
    manifest, _ = build_manifest()
    reordered = replace(manifest, artifacts=tuple(reversed(manifest.artifacts)))
    assert manifest.fingerprint() == reordered.fingerprint()
    assert manifest.as_dict()["manifest_fingerprint"] == manifest.fingerprint()
    assert manifest.as_dict()["assurance_scope"] == ARCHIVE_ASSURANCE_SCOPE


def test_verified_retrieval_returns_exact_bytes():
    manifest, data = build_manifest()
    result, returned = retrieve_verified_artifact(
        manifest, "provenance_decision", FakeStore({manifest.artifacts[0].locator: data})
    )
    assert result.status is ArtifactVerificationStatus.VERIFIED
    assert returned == data


def test_missing_artifact_is_not_conflated_with_unavailable_archive():
    manifest, _ = build_manifest()
    missing, data = retrieve_verified_artifact(manifest, "provenance_decision", FakeStore())
    unavailable, other_data = retrieve_verified_artifact(
        manifest, "provenance_decision", FakeStore(unavailable=True)
    )
    assert missing.status is ArtifactVerificationStatus.ARTIFACT_NOT_FOUND
    assert unavailable.status is ArtifactVerificationStatus.ARCHIVE_UNAVAILABLE
    assert data is None and other_data is None


def test_digest_mismatch_returns_no_unverified_bytes():
    manifest, _ = build_manifest()
    wrong = b'{"decision":"FAIL"}'
    result, returned = retrieve_verified_artifact(
        manifest, "provenance_decision", FakeStore({manifest.artifacts[0].locator: wrong})
    )
    assert result.status is ArtifactVerificationStatus.DIGEST_MISMATCH
    assert returned is None


def test_length_mismatch_is_explicit():
    manifest, _ = build_manifest()
    shorter = b"x"
    result, returned = retrieve_verified_artifact(
        manifest, "provenance_decision", FakeStore({manifest.artifacts[0].locator: shorter})
    )
    assert result.status is ArtifactVerificationStatus.LENGTH_MISMATCH
    assert returned is None


def test_undeclared_role_and_duplicate_roles_are_blocked():
    manifest, _ = build_manifest()
    result, returned = retrieve_verified_artifact(manifest, "missing_role", FakeStore())
    assert result.status is ArtifactVerificationStatus.MANIFEST_INVALID
    assert returned is None

    duplicate = replace(manifest, artifacts=(manifest.artifacts[0], manifest.artifacts[0]))
    result, returned = retrieve_verified_artifact(duplicate, "provenance_decision", FakeStore())
    assert result.status is ArtifactVerificationStatus.MANIFEST_INVALID
    assert returned is None


def test_manifest_rejects_unsupported_schema_and_forged_assurance_scope():
    manifest, _ = build_manifest()
    unsupported = replace(manifest, schema_revision="FUTURE-SCHEMA")
    result, _ = retrieve_verified_artifact(unsupported, "provenance_decision", FakeStore())
    assert result.status is ArtifactVerificationStatus.MANIFEST_INVALID

    forged = replace(manifest, assurance_scope="AUTHENTICATED")
    with pytest.raises(EvidenceArchiveError, match="cannot claim durable or authenticated"):
        forged.validate()


def test_manifest_rejects_invalid_digest_and_negative_length():
    manifest, _ = build_manifest()
    bad_digest = replace(manifest.artifacts[0], digest_sha256="g" * 64)
    with pytest.raises(EvidenceArchiveError, match="SHA-256"):
        replace(manifest, artifacts=(bad_digest,)).validate()
    bad_length = replace(manifest.artifacts[0], byte_length=-1)
    with pytest.raises(EvidenceArchiveError, match="cannot be negative"):
        replace(manifest, artifacts=(bad_length,)).validate()
