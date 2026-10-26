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
    PROVENANCE_ARCHIVE_REQUIRED_ROLES,
    validate_provenance_archive_manifest,
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
        evaluator_revision="evaluator@pinned", required_input_schemas={"input": "input@1"},
        decision_schema_revision="decision@1", evaluator=lambda inputs: decision_bytes if inputs["input"] == input_bytes else b"wrong",
    )
    assert result.status is ReplayStatus.MATCH
    mismatch = replay_archived_decision(
        manifest, store, required_input_roles=("input",), decision_role="decision",
        evaluator_revision="evaluator@pinned", required_input_schemas={"input": "input@1"},
        decision_schema_revision="decision@1", evaluator=lambda inputs: b'{"decision":"FAIL"}',
    )
    assert mismatch.status is ReplayStatus.MISMATCH


def test_replay_harness_blocks_missing_inputs_and_missing_evaluator():
    manifest, input_bytes, decision_bytes = build_replay_manifest()
    missing = replay_archived_decision(
        manifest, FakeStore(), required_input_roles=("input",), decision_role="decision",
        evaluator_revision="evaluator@pinned", required_input_schemas={"input": "input@1"},
        decision_schema_revision="decision@1", evaluator=lambda inputs: decision_bytes,
    )
    assert missing.status is ReplayStatus.BLOCKED_ARTIFACT_UNAVAILABLE
    unavailable = replay_archived_decision(
        manifest, FakeStore({manifest.artifacts[0].locator: input_bytes, manifest.artifacts[1].locator: decision_bytes}),
        required_input_roles=("input",), decision_role="decision", evaluator=None,
        evaluator_revision="evaluator@pinned", required_input_schemas={"input": "input@1"},
        decision_schema_revision="decision@1",
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
        evaluator_revision="evaluator@pinned", required_input_schemas={"input": "input@1"},
        decision_schema_revision="decision@1", evaluator=lambda inputs: 17,
    )
    assert failed.status is ReplayStatus.BLOCKED_EVALUATOR_ERROR
    invalid = replay_archived_decision(
        manifest, store, required_input_roles=("decision",), decision_role="decision",
        evaluator_revision="evaluator@pinned", required_input_schemas={"decision": "decision@1"},
        decision_schema_revision="decision@1", evaluator=lambda inputs: decision_bytes,
    )
    assert invalid.status is ReplayStatus.MANIFEST_INVALID



def test_replay_harness_blocks_revision_mismatch_and_schema_mismatch():
    manifest, input_bytes, decision_bytes = build_replay_manifest()
    store = FakeStore({
        manifest.artifacts[0].locator: input_bytes,
        manifest.artifacts[1].locator: decision_bytes,
    })
    kwargs = dict(
        manifest=manifest, store=store, required_input_roles=("input",),
        decision_role="decision", evaluator=lambda inputs: decision_bytes,
        evaluator_revision="evaluator@wrong",
        required_input_schemas={"input": "input@1"}, decision_schema_revision="decision@1",
    )
    assert replay_archived_decision(**kwargs).status is ReplayStatus.BLOCKED_EVALUATOR_REVISION_MISMATCH
    kwargs["evaluator_revision"] = "evaluator@pinned"
    kwargs["required_input_schemas"] = {"input": "input@wrong"}
    assert replay_archived_decision(**kwargs).status is ReplayStatus.MANIFEST_INVALID


def test_replay_harness_requires_verified_archived_decision_artifact():
    manifest, input_bytes, decision_bytes = build_replay_manifest()
    store = FakeStore({manifest.artifacts[0].locator: input_bytes})
    result = replay_archived_decision(
        manifest, store, required_input_roles=("input",), decision_role="decision",
        evaluator=lambda inputs: decision_bytes, evaluator_revision="evaluator@pinned",
        required_input_schemas={"input": "input@1"}, decision_schema_revision="decision@1",
    )
    assert result.status is ReplayStatus.BLOCKED_ARTIFACT_UNAVAILABLE
    assert result.blocked_role == "decision"



@pytest.mark.parametrize(
    ("store_factory", "expected_status"),
    [
        (lambda manifest, input_bytes, decision_bytes: FakeStore(unavailable=True),
         ReplayStatus.BLOCKED_ARTIFACT_UNAVAILABLE),
        (lambda manifest, input_bytes, decision_bytes: FakeStore({
            manifest.artifacts[0].locator: b"tampered",
            manifest.artifacts[1].locator: decision_bytes,
        }), ReplayStatus.BLOCKED_ARTIFACT_UNAVAILABLE),
        (lambda manifest, input_bytes, decision_bytes: FakeStore({
            manifest.artifacts[0].locator: input_bytes,
        }), ReplayStatus.BLOCKED_ARTIFACT_UNAVAILABLE),
    ],
    ids=("archive-unavailable", "input-digest-mismatch", "reference-decision-missing"),
)
def test_replay_failure_matrix_never_returns_match(store_factory, expected_status):
    manifest, input_bytes, decision_bytes = build_replay_manifest()
    store = store_factory(manifest, input_bytes, decision_bytes)
    invoked = []
    result = replay_archived_decision(
        manifest, store, required_input_roles=("input",), decision_role="decision",
        evaluator_revision="evaluator@pinned",
        required_input_schemas={"input": "input@1"},
        decision_schema_revision="decision@1",
        evaluator=lambda inputs: invoked.append(True) or decision_bytes,
    )
    assert result.status is expected_status
    assert result.status is not ReplayStatus.MATCH
    assert result.blocked_role is not None
    assert invoked == []


@pytest.mark.parametrize(
    ("kwargs_update", "expected_status"),
    [
        ({"decision_schema_revision": "decision@wrong"}, ReplayStatus.MANIFEST_INVALID),
        ({"required_input_roles": ("input", "input"),
          "required_input_schemas": {"input": "input@1"}}, ReplayStatus.MANIFEST_INVALID),
        ({"evaluator_revision": ""}, ReplayStatus.BLOCKED_EVALUATOR_REVISION_MISMATCH),
    ],
    ids=("decision-schema-drift", "duplicate-required-role", "empty-evaluator-revision"),
)
def test_replay_contract_matrix_blocks_invalid_contracts(kwargs_update, expected_status):
    manifest, input_bytes, decision_bytes = build_replay_manifest()
    store = FakeStore({
        manifest.artifacts[0].locator: input_bytes,
        manifest.artifacts[1].locator: decision_bytes,
    })
    kwargs = dict(
        manifest=manifest, store=store, required_input_roles=("input",),
        decision_role="decision", evaluator=lambda inputs: decision_bytes,
        evaluator_revision="evaluator@pinned",
        required_input_schemas={"input": "input@1"}, decision_schema_revision="decision@1",
    )
    kwargs.update(kwargs_update)
    result = replay_archived_decision(**kwargs)
    assert result.status is expected_status
    assert result.status is not ReplayStatus.MATCH


def test_replay_evaluator_exception_is_blocked_not_a_decision():
    manifest, input_bytes, decision_bytes = build_replay_manifest()
    store = FakeStore({
        manifest.artifacts[0].locator: input_bytes,
        manifest.artifacts[1].locator: decision_bytes,
    })

    def fail(_inputs):
        raise RuntimeError("deterministic fixture failure")

    result = replay_archived_decision(
        manifest, store, required_input_roles=("input",), decision_role="decision",
        evaluator=fail, evaluator_revision="evaluator@pinned",
        required_input_schemas={"input": "input@1"}, decision_schema_revision="decision@1",
    )
    assert result.status is ReplayStatus.BLOCKED_EVALUATOR_ERROR
    assert result.observed_decision_digest is None



def test_replay_failure_matrix_does_not_accept_evaluator_exception_or_non_bytes():
    manifest, input_bytes, decision_bytes = build_replay_manifest()
    store = FakeStore({
        manifest.artifacts[0].locator: input_bytes,
        manifest.artifacts[1].locator: decision_bytes,
    })

    def raising(_inputs):
        raise RuntimeError("fixture error")

    for evaluator in (raising, lambda _inputs: {"decision": "PASS"}):
        result = replay_archived_decision(
            manifest, store, required_input_roles=("input",), decision_role="decision",
            evaluator=evaluator, evaluator_revision="evaluator@pinned",
            required_input_schemas={"input": "input@1"}, decision_schema_revision="decision@1",
        )
        assert result.status is ReplayStatus.BLOCKED_EVALUATOR_ERROR
        assert result.status is not ReplayStatus.MATCH


def test_provenance_archive_role_contract_reports_every_missing_role():
    manifest, _ = build_manifest()
    reasons = validate_provenance_archive_manifest(manifest)
    assert reasons == tuple(
        f"REQUIRED_ROLE_MISSING:{role}"
        for role in PROVENANCE_ARCHIVE_REQUIRED_ROLES
        if role != "provenance_decision"
    )


def test_provenance_archive_role_contract_accepts_complete_explicit_role_set():
    artifacts = []
    payloads = {}
    for role in PROVENANCE_ARCHIVE_REQUIRED_ROLES:
        data = ("fixture:" + role).encode()
        digest = hashlib.sha256(data).hexdigest()
        artifacts.append(ArtifactDescriptor(
            role=role,
            schema_revision="explicit-fixture-schema@1",
            digest_sha256=digest,
            byte_length=len(data),
            locator=f"sha256:{digest}",
        ))
        payloads[f"sha256:{digest}"] = data
    manifest = EvidenceArchiveManifest(
        archive_record_id="PROVENANCE-ROLE-COVERAGE-001",
        evaluator_revision="explicit-fixture-evaluator@1",
        policy_revision="explicit-fixture-policy@1",
        artifacts=tuple(artifacts),
    )
    assert validate_provenance_archive_manifest(manifest) == ()
    # This is only role coverage: the fixture schema is intentionally not
    # represented as a claim about the production schema of any artifact.
    assert len(payloads) == len(PROVENANCE_ARCHIVE_REQUIRED_ROLES)


def test_provenance_archive_role_contract_does_not_infer_missing_schema_semantics():
    manifest, data = build_manifest()
    result = replace(
        manifest,
        artifacts=(replace(manifest.artifacts[0], schema_revision="owner-defined-schema@future"),),
    )
    assert validate_provenance_archive_manifest(result) == tuple(
        f"REQUIRED_ROLE_MISSING:{role}"
        for role in PROVENANCE_ARCHIVE_REQUIRED_ROLES
        if role != "provenance_decision"
    )
