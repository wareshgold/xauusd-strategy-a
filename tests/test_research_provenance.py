from dataclasses import replace

import pytest

from strategy_factory.audit import bind_research_audit
from strategy_factory.dataset_provenance import (
    DatasetProvenanceStatus,
    evaluate_dataset_provenance,
)
from strategy_factory.datasets import DatasetRegistry
from strategy_factory.evidence import EvidenceBundle
from strategy_factory.execution import ExecutionReceipt
from strategy_factory.jobs import ResearchJobSpec
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.models import StrategyPassport
from strategy_factory.research_provenance import (
    ResearchProvenanceStatus,
    evaluate_research_provenance,
    serialize_research_provenance_decision,
    serialize_provenance_input_artifact,
    deserialize_provenance_input_artifact,
)
from strategy_factory.runs import ResearchRunIdentity
from strategy_factory.snapshot import build_readiness_snapshot
from strategy_factory.sp2l_manifest import build_sp2l_research_manifest
from strategy_factory.source_ledger import SourceResolutionLedger
from strategy_factory.test_contract import (
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
)


CONTENT_SHA = "a" * 64


def make_spec(role=DatasetRole.DEVELOPMENT, revision="DATA-001"):
    return HistoricalTestSpec(
        test_id="TEST-001",
        strategy_id="SP2L-A",
        strategy_revision="RESEARCH-001",
        dataset=TestDataset(
            dataset_id="DS-001",
            role=role,
            data_revision=revision,
            start="2026-01-01T00:00:00Z",
            end="2026-02-01T00:00:00Z",
            source="synthetic",
            immutable=role is not DatasetRole.DEVELOPMENT,
        ),
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
    )


def make_chain():
    manifest = build_sp2l_research_manifest()
    passport = StrategyPassport(
        strategy_id=manifest.strategy_id,
        source_revision=manifest.revision,
        geometry_revision="GEOMETRY-PENDING",
        code_revision="CODE-PENDING",
        data_revision="DATA-PENDING",
        execution_model="BAR_CLOSE_RESEARCH",
        parameter_set={"canonical": False},
    )
    snapshot = build_readiness_snapshot(manifest, passport, SourceResolutionLedger())

    spec = make_spec()
    registry = DatasetRegistry()
    identity = registry.register(spec.dataset, CONTENT_SHA)
    dataset_provenance = evaluate_dataset_provenance(spec, registry, CONTENT_SHA)
    assert dataset_provenance.status is DatasetProvenanceStatus.PASS

    job = ResearchJobSpec.from_test_spec(
        spec,
        manifest_revision=manifest.revision,
        dataset_fingerprint=identity.fingerprint,
        job_id="JOB-001",
    )
    run = ResearchRunIdentity(
        run_id=job.job_id,
        strategy_id=job.strategy_id,
        strategy_revision=job.strategy_revision,
        manifest_revision=job.manifest_revision,
        dataset_id=job.dataset_id,
        dataset_role=spec.dataset.role.value,
        data_revision=job.data_revision,
        dataset_fingerprint=job.dataset_fingerprint,
        artifact_id=None,
        execution_semantics=job.execution_semantics,
        parameters=dict(job.parameters),
    )
    metrics = ResearchMetrics(
        trades=2,
        decisive_trades=2,
        wins=1,
        losses=1,
        ambiguous=0,
        win_rate=0.5,
        net_r=0.0,
        profit_factor=1.0,
        max_drawdown_r=1.0,
        gross_profit_r=1.0,
        gross_loss_r=-1.0,
    )
    receipt = ExecutionReceipt(
        execution_id="EXEC-001",
        test_id=spec.test_id,
        strategy_revision=spec.strategy_revision,
        execution_semantics=spec.execution_semantics,
        engine_revision="ENGINE-001",
        input_fingerprint="b" * 64,
        completed=True,
        metrics=metrics,
    )
    evidence = EvidenceBundle(
        evidence_id="EVIDENCE-001",
        run_id=run.run_id,
        run_fingerprint=run.fingerprint,
        result_revision="RESULT-001",
        metrics=metrics,
        result={"execution_id": receipt.execution_id},
    )
    audit = bind_research_audit(run, snapshot, evidence)
    return {
        "spec": spec,
        "job": job,
        "run": run,
        "receipt": receipt,
        "evidence": evidence,
        "audit": audit,
        "snapshot": snapshot,
        "dataset_provenance": dataset_provenance,
    }


def test_exact_chain_passes():
    chain = make_chain()
    result = evaluate_research_provenance(**chain)

    assert result.status is ResearchProvenanceStatus.PASS
    assert result.reasons == ()
    result.validate()
    assert dict(result.input_fingerprints)["research_run"] == __import__(
        "hashlib"
    ).sha256(__import__("json").dumps(
        chain["run"].as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")).hexdigest()
    assert len(result.decision_fingerprint) == 64


@pytest.mark.parametrize(
    "field",
    [
        "strategy_revision",
        "manifest_revision",
        "dataset_id",
        "data_revision",
        "dataset_fingerprint",
    ],
)
def test_run_identity_tampering_fails(field):
    chain = make_chain()
    original = chain["run"]
    replacement = "x" * 64 if field == "dataset_fingerprint" else "TAMPERED"
    chain["run"] = replace(original, **{field: replacement})

    result = evaluate_research_provenance(**chain)

    assert result.status is ResearchProvenanceStatus.FAIL
    assert result.reasons


def test_dataset_provenance_block_is_blocked():
    chain = make_chain()
    chain["dataset_provenance"] = replace(
        chain["dataset_provenance"],
        status=DatasetProvenanceStatus.BLOCKED,
        reasons=("dataset is not registered",),
    )

    result = evaluate_research_provenance(**chain)

    assert result.status is ResearchProvenanceStatus.BLOCKED
    assert "DATASET_PROVENANCE_BLOCKED" in result.reasons


def test_evidence_from_different_run_fails():
    chain = make_chain()
    chain["evidence"] = replace(chain["evidence"], run_id="OTHER-RUN")

    result = evaluate_research_provenance(**chain)

    assert result.status is ResearchProvenanceStatus.FAIL
    assert "EVIDENCE_RUN_ID" in result.reasons


def test_audit_from_different_snapshot_fails():
    chain = make_chain()
    chain["audit"] = replace(chain["audit"], snapshot_fingerprint="c" * 64)

    result = evaluate_research_provenance(**chain)

    assert result.status is ResearchProvenanceStatus.FAIL
    assert "AUDIT_SNAPSHOT_FINGERPRINT" in result.reasons


def test_snapshot_mismatch_fails():
    chain = make_chain()
    manifest = build_sp2l_research_manifest()
    passport = StrategyPassport(
        strategy_id=manifest.strategy_id,
        source_revision=manifest.revision,
        geometry_revision="OTHER",
        code_revision="CODE-PENDING",
        data_revision="DATA-PENDING",
        execution_model="BAR_CLOSE_RESEARCH",
        parameter_set={"canonical": False},
    )
    chain["snapshot"] = build_readiness_snapshot(
        manifest, passport, SourceResolutionLedger()
    )

    result = evaluate_research_provenance(**chain)

    assert result.status is ResearchProvenanceStatus.FAIL
    assert "AUDIT_SNAPSHOT_FINGERPRINT" in result.reasons


def test_receipt_semantics_mismatch_fails():
    chain = make_chain()
    chain["receipt"] = replace(
        chain["receipt"],
        execution_semantics=ExecutionSemantics.TICK_FEASIBLE,
    )

    result = evaluate_research_provenance(**chain)

    assert result.status is ResearchProvenanceStatus.FAIL
    assert any(reason.startswith("EXECUTION_BINDING:") for reason in result.reasons)

def test_provenance_decision_fingerprint_detects_tampering():
    result = evaluate_research_provenance(**make_chain())
    altered = replace(result, reasons=("MANUALLY_CHANGED",))
    with pytest.raises(ValueError, match="decision fingerprint mismatch"):
        altered.validate()


def test_provenance_decision_binds_execution_receipt_and_dataset_provenance():
    chain = make_chain()
    result = evaluate_research_provenance(**chain)
    bound = dict(result.input_fingerprints)
    assert bound["execution_receipt"]
    assert bound["dataset_provenance"]
    changed = dict(chain)
    changed["receipt"] = replace(
        chain["receipt"], execution_id="EXEC-OTHER"
    )
    replay = evaluate_research_provenance(**changed)
    assert replay.status is ResearchProvenanceStatus.FAIL
    assert replay.decision_fingerprint != result.decision_fingerprint



def test_provenance_decision_archive_bytes_are_canonical_and_repeatable():
    chain = make_chain()
    first = evaluate_research_provenance(**chain)
    second = evaluate_research_provenance(**chain)
    first_bytes = serialize_research_provenance_decision(first)
    assert first_bytes == serialize_research_provenance_decision(second)
    assert first_bytes.decode("utf-8") == __import__("json").dumps(
        first.as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    assert first.decision_fingerprint.encode() in first_bytes


def test_provenance_decision_archive_serialization_rejects_tampering():
    result = evaluate_research_provenance(**make_chain())
    altered = replace(result, reasons=("MANUALLY_CHANGED",))
    with pytest.raises(ValueError, match="decision fingerprint mismatch"):
        serialize_research_provenance_decision(altered)



def test_all_provenance_inputs_have_explicit_role_and_schema_serialization():
    chain = make_chain()
    role_to_key = {
        "test_spec": "spec",
        "research_job": "job",
        "research_run": "run",
        "execution_receipt": "receipt",
        "evidence_bundle": "evidence",
        "research_audit": "audit",
        "readiness_snapshot": "snapshot",
        "dataset_provenance": "dataset_provenance",
    }
    for role, key in role_to_key.items():
        value = chain[key]
        first = serialize_provenance_input_artifact(
            role, value, schema_revision="owner-fixture-schema@1"
        )
        second = serialize_provenance_input_artifact(
            role, value, schema_revision="owner-fixture-schema@1"
        )
        assert first == second
        envelope = __import__("json").loads(first)
        assert envelope["artifact_role"] == role
        assert envelope["schema_revision"] == "owner-fixture-schema@1"
        assert envelope["payload"] == value.as_dict()


def test_provenance_input_serialization_rejects_unknown_role_wrong_type_and_missing_schema():
    chain = make_chain()
    with pytest.raises(ValueError, match="unsupported provenance input role"):
        serialize_provenance_input_artifact(
            "unknown", chain["spec"], schema_revision="schema@1"
        )
    with pytest.raises(TypeError, match="requires ResearchJobSpec"):
        serialize_provenance_input_artifact(
            "research_job", chain["spec"], schema_revision="schema@1"
        )
    with pytest.raises(ValueError, match="schema_revision is required"):
        serialize_provenance_input_artifact("test_spec", chain["spec"], schema_revision=" ")



def test_test_spec_artifact_round_trip_uses_explicit_versioned_decoder():
    spec = make_spec()
    schema = "HISTORICAL-TEST-SPEC-1"
    encoded = serialize_provenance_input_artifact(
        "test_spec", spec, schema_revision=schema
    )
    decoded = deserialize_provenance_input_artifact(
        encoded, expected_role="test_spec", expected_schema_revision=schema
    )
    assert type(decoded) is HistoricalTestSpec
    assert decoded.as_dict() == spec.as_dict()
    assert serialize_provenance_input_artifact(
        "test_spec", decoded, schema_revision=schema
    ) == encoded


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda env: {**env, "artifact_role": "research_job"}, "role mismatch"),
        (lambda env: {**env, "schema_revision": "HISTORICAL-TEST-SPEC-2"},
         "schema revision mismatch"),
        (lambda env: {**env, "payload": {**env["payload"], "unexpected": True}},
         "payload keys are invalid"),
        (lambda env: {**env, "payload": {
            **env["payload"], "execution_semantics": "GUESSED_EXECUTION"
        }}, "contract validation"),
    ],
    ids=("role-drift", "schema-drift", "extra-payload-field", "invalid-enum"),
)
def test_test_spec_decoder_rejects_tampered_or_incompatible_artifacts(mutate, message):
    schema = "HISTORICAL-TEST-SPEC-1"
    encoded = serialize_provenance_input_artifact(
        "test_spec", make_spec(), schema_revision=schema
    )
    envelope = __import__("json").loads(encoded)
    changed = __import__("json").dumps(
        mutate(envelope), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    with pytest.raises(ValueError, match=message):
        deserialize_provenance_input_artifact(
            changed, expected_role="test_spec", expected_schema_revision=schema
        )


def test_test_spec_decoder_blocks_unimplemented_roles_and_schema_revisions():
    with pytest.raises(ValueError, match="no versioned decoder"):
        deserialize_provenance_input_artifact(
            b"{}", expected_role="research_job", expected_schema_revision="RESEARCH-JOB-1"
        )
    with pytest.raises(ValueError, match="does not match the implemented decoder"):
        deserialize_provenance_input_artifact(
            b"{}", expected_role="test_spec", expected_schema_revision="HISTORICAL-TEST-SPEC-2"
        )


def test_research_job_artifact_round_trip_uses_explicit_versioned_decoder():
    job = make_chain()["job"]
    schema = "RESEARCH-JOB-SPEC-1"
    encoded = serialize_provenance_input_artifact(
        "research_job", job, schema_revision=schema
    )
    decoded = deserialize_provenance_input_artifact(
        encoded, expected_role="research_job", expected_schema_revision=schema
    )
    assert type(decoded) is ResearchJobSpec
    assert decoded.as_dict() == job.as_dict()
    assert serialize_provenance_input_artifact(
        "research_job", decoded, schema_revision=schema
    ) == encoded


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda env: {**env, "artifact_role": "test_spec"}, "role mismatch"),
        (lambda env: {**env, "schema_revision": "RESEARCH-JOB-SPEC-2"},
         "schema revision mismatch"),
        (lambda env: {**env, "payload": {**env["payload"], "extra": True}},
         "payload keys are invalid"),
        (lambda env: {**env, "payload": {
            **env["payload"], "execution_semantics": "UNKNOWN_SEMANTICS"
        }}, "contract validation"),
        (lambda env: {**env, "payload": {
            **env["payload"], "dataset_fingerprint": "not-a-sha256"
        }}, "contract validation"),
    ],
    ids=("role-drift", "schema-drift", "extra-field", "invalid-enum", "bad-dataset-fingerprint"),
)
def test_research_job_decoder_rejects_tampered_or_incompatible_artifacts(mutate, message):
    schema = "RESEARCH-JOB-SPEC-1"
    encoded = serialize_provenance_input_artifact(
        "research_job", make_chain()["job"], schema_revision=schema
    )
    envelope = __import__("json").loads(encoded)
    changed = __import__("json").dumps(
        mutate(envelope), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    with pytest.raises(ValueError, match=message):
        deserialize_provenance_input_artifact(
            changed, expected_role="research_job", expected_schema_revision=schema
        )

def test_research_run_artifact_round_trip_uses_explicit_versioned_decoder():
    run = make_chain()["run"]
    schema = "RESEARCH-RUN-IDENTITY-1"
    encoded = serialize_provenance_input_artifact("research_run", run, schema_revision=schema)
    decoded = deserialize_provenance_input_artifact(encoded, expected_role="research_run", expected_schema_revision=schema)
    from strategy_factory.runs import ResearchRunIdentity
    assert type(decoded) is ResearchRunIdentity
    assert decoded.as_dict() == run.as_dict()
    assert serialize_provenance_input_artifact("research_run", decoded, schema_revision=schema) == encoded


@pytest.mark.parametrize(("mutate", "message"), [
    (lambda env: {**env, "artifact_role": "research_job"}, "role mismatch"),
    (lambda env: {**env, "schema_revision": "RESEARCH-RUN-IDENTITY-2"}, "schema revision mismatch"),
    (lambda env: {**env, "payload": {**env["payload"], "unexpected": True}}, "payload keys are invalid"),
    (lambda env: {**env, "payload": {**env["payload"], "execution_semantics": "UNKNOWN_SEMANTICS"}}, "contract validation"),
    (lambda env: {**env, "payload": {**env["payload"], "artifact_id": 7}}, "artifact_id must be a string or null"),
], ids=("role-drift", "schema-drift", "extra-field", "invalid-enum", "bad-artifact-id"))
def test_research_run_decoder_rejects_tampered_or_incompatible_artifacts(mutate, message):
    schema = "RESEARCH-RUN-IDENTITY-1"
    encoded = serialize_provenance_input_artifact("research_run", make_chain()["run"], schema_revision=schema)
    envelope = __import__("json").loads(encoded)
    changed = __import__("json").dumps(mutate(envelope), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    with pytest.raises(ValueError, match=message):
        deserialize_provenance_input_artifact(changed, expected_role="research_run", expected_schema_revision=schema)