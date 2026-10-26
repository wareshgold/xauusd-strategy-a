import hashlib
from pathlib import Path
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
    FileSystemContentAddressedStore,
    ManifestCommitStatus,
    ReplayStatus,
    replay_archived_decision,
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



def test_filesystem_store_put_is_idempotent_and_survives_reopen(tmp_path):
    data = b"evidence payload"
    store = FileSystemContentAddressedStore(tmp_path / "archive")
    locator = store.put(data)
    assert locator == store.put(data)
    reopened = FileSystemContentAddressedStore(tmp_path / "archive")
    assert reopened.get(locator) == data


def test_filesystem_store_missing_and_corrupted_objects_fail_closed(tmp_path):
    store = FileSystemContentAddressedStore(tmp_path / "archive")
    with pytest.raises(ArtifactNotFound):
        store.get("sha256:" + "a" * 64)

    locator = store.put(b"original")
    digest = locator.removeprefix("sha256:")
    path = Path(tmp_path / "archive" / "sha256" / digest[:2] / digest)
    path.write_bytes(b"tampered")
    with pytest.raises(EvidenceArchiveError, match="do not match"):
        store.get(locator)


def test_filesystem_store_rejects_non_sha256_locator(tmp_path):
    store = FileSystemContentAddressedStore(tmp_path / "archive")
    with pytest.raises(EvidenceArchiveError, match="unsupported content-addressed"):
        store.get("../../outside")



def test_manifest_round_trip_and_fingerprint_tampering_rejected():
    manifest, _ = build_manifest()
    serialized = manifest.as_dict()
    restored = EvidenceArchiveManifest.from_dict(serialized)
    assert restored.as_dict() == serialized

    tampered = dict(serialized)
    tampered["policy_revision"] = "policy@changed"
    with pytest.raises(EvidenceArchiveError, match="fingerprint mismatch"):
        EvidenceArchiveManifest.from_dict(tampered)


def test_manifest_parser_rejects_unknown_digest_algorithm():
    manifest, _ = build_manifest()
    serialized = manifest.as_dict()
    serialized["artifacts"][0]["digest_algorithm"] = "sha512"
    with pytest.raises(EvidenceArchiveError, match="digest algorithm"):
        EvidenceArchiveManifest.from_dict(serialized)



def test_retrieval_converts_local_store_corruption_to_blocked_result(tmp_path):
    store = FileSystemContentAddressedStore(tmp_path / "archive")
    locator = store.put(b"original")
    digest = locator.removeprefix("sha256:")
    path = Path(tmp_path / "archive" / "sha256" / digest[:2] / digest)
    path.write_bytes(b"tampered")
    manifest = EvidenceArchiveManifest(
        archive_record_id="ARCHIVE-CORRUPT",
        evaluator_revision="evaluator@abc123",
        policy_revision="policy@1",
        artifacts=(ArtifactDescriptor(
            role="evidence",
            schema_revision="evidence@1",
            digest_sha256=digest,
            byte_length=len(b"original"),
            locator=locator,
        ),),
    )
    result, data = retrieve_verified_artifact(manifest, "evidence", store)
    assert result.status is ArtifactVerificationStatus.DIGEST_MISMATCH
    assert data is None



def test_manifest_commit_is_idempotent_and_retrievable_after_reopen(tmp_path):
    manifest, data = build_manifest()
    root = tmp_path / "archive"
    store = FileSystemContentAddressedStore(root)
    assert store.put(data) == manifest.artifacts[0].locator
    assert store.commit_manifest(manifest) is ManifestCommitStatus.STORED_AND_VERIFIED
    reopened = FileSystemContentAddressedStore(root)
    assert reopened.commit_manifest(manifest) is ManifestCommitStatus.ALREADY_PRESENT_MATCHING_DIGEST
    assert reopened.get_manifest(manifest.archive_record_id).fingerprint() == manifest.fingerprint()


def test_manifest_commit_rejects_conflicting_content_for_same_record_id(tmp_path):
    manifest, data = build_manifest()
    other, other_data = build_manifest(b'{"decision":"FAIL"}')
    store = FileSystemContentAddressedStore(tmp_path / "archive")
    store.put(data)
    store.put(other_data)
    assert store.commit_manifest(manifest) is ManifestCommitStatus.STORED_AND_VERIFIED
    conflict = replace(other, archive_record_id=manifest.archive_record_id)
    assert store.commit_manifest(conflict) is ManifestCommitStatus.CONFLICTING_MANIFEST
    assert store.get_manifest(manifest.archive_record_id).fingerprint() == manifest.fingerprint()


def test_manifest_commit_rejects_unsafe_record_id(tmp_path):
    manifest, _ = build_manifest()
    store = FileSystemContentAddressedStore(tmp_path / "archive")
    assert store.commit_manifest(replace(manifest, archive_record_id="../escape")) is ManifestCommitStatus.MANIFEST_INVALID



def build_replay_manifest():
    input_bytes = b'{"input":1}'
    decision_bytes = b'{"decision":"PASS"}'
    input_digest = hashlib.sha256(input_bytes).hexdigest()
    decision_digest = hashlib.sha256(decision_bytes).hexdigest()
    manifest = EvidenceArchiveManifest(
        archive_record_id="REPLAY-001",
        evaluator_revision="evaluator@pinned",
        policy_revision="policy@pinned",
        artifacts=(
            ArtifactDescriptor("input", "input@1", input_digest, len(input_bytes), f"sha256:{input_digest}"),
            ArtifactDescriptor("decision", "decision@1", decision_digest, len(decision_bytes), f"sha256:{decision_digest}"),
        ),
    )
    return manifest, input_bytes, decision_bytes


def test_replay_harness_matches_only_exact_reproduced_decision():
    manifest, input_bytes, decision_bytes = build_replay_manifest()
    store = FakeStore({
        manifest.artifacts[0].locator: input_bytes,
        manifest.artifacts[1].locator: decision_bytes,
    })
    result = replay_archived_decision(
        manifest, store, required_input_roles=("input",), decision_role="decision",
        evaluator=lambda inputs: decision_bytes if inputs["input"] == input_bytes else b"wrong",
    )
    assert result.status is ReplayStatus.MATCH
    mismatch = replay_archived_decision(
        manifest, store, required_input_roles=("input",), decision_role="decision",
        evaluator=lambda inputs: b'{"decision":"FAIL"}',
    )
    assert mismatch.status is ReplayStatus.MISMATCH


def test_replay_harness_blocks_missing_inputs_and_missing_evaluator():
    manifest, input_bytes, decision_bytes = build_replay_manifest()
    missing = replay_archived_decision(
        manifest, FakeStore(), required_input_roles=("input",), decision_role="decision",
        evaluator=lambda inputs: decision_bytes,
    )
    assert missing.status is ReplayStatus.BLOCKED_ARTIFACT_UNAVAILABLE
    unavailable = replay_archived_decision(
        manifest, FakeStore({manifest.artifacts[0].locator: input_bytes, manifest.artifacts[1].locator: decision_bytes}),
        required_input_roles=("input",), decision_role="decision", evaluator=None,
    )
    assert unavailable.status is ReplayStatus.BLOCKED_EVALUATOR_UNAVAILABLE


def test_replay_harness_blocks_evaluator_errors_and_invalid_role_contract():
    manifest, input_bytes, decision_bytes = build_replay_manifest()
    store = FakeStore({
        manifest.artifacts[0].locator: input_bytes,
        manifest.artifacts[1].locator: decision_bytes,
    })
    failed = replay_archived_decision(
        manifest, store, required_input_roles=("input",), decision_role="decision",
        evaluator=lambda inputs: 17,
    )
    assert failed.status is ReplayStatus.BLOCKED_EVALUATOR_ERROR
    invalid = replay_archived_decision(
        manifest, store, required_input_roles=("decision",), decision_role="decision",
        evaluator=lambda inputs: decision_bytes,
    )
    assert invalid.status is ReplayStatus.MANIFEST_INVALID
