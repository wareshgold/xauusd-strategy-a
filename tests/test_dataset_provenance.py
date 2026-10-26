from strategy_factory.dataset_provenance import (
    DatasetProvenanceStatus,
    evaluate_dataset_provenance,
)
from strategy_factory.datasets import DatasetArtifact, DatasetRegistry
from strategy_factory.test_contract import DatasetRole, HistoricalTestSpec, TestDataset


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
        execution_semantics=__import__("strategy_factory").ExecutionSemantics.BAR_CLOSE_RESEARCH,
    )


HASH_A = "a" * 64
HASH_B = "b" * 64


def artifact(h=HASH_A, artifact_id="ART-001"):
    return DatasetArtifact(artifact_id, "data/a.csv", h, 10, "csv")


def test_exact_dataset_artifact_passes():
    spec = make_spec()
    registry = DatasetRegistry()
    registry.register(spec.dataset, HASH_A, artifact=artifact())
    result = evaluate_dataset_provenance(spec, registry, HASH_A, observed_artifact=artifact())
    assert result.status is DatasetProvenanceStatus.PASS


def test_content_change_fails_even_with_same_dataset_id():
    spec = make_spec()
    registry = DatasetRegistry()
    registry.register(spec.dataset, HASH_A)
    result = evaluate_dataset_provenance(spec, registry, HASH_B)
    assert result.status is DatasetProvenanceStatus.FAIL
    assert "DATASET_FINGERPRINT_MISMATCH" in result.reasons


def test_artifact_identity_change_fails():
    spec = make_spec()
    registry = DatasetRegistry()
    registry.register(spec.dataset, HASH_A, artifact=artifact())
    result = evaluate_dataset_provenance(
        spec, registry, HASH_A,
        observed_artifact=artifact(artifact_id="ART-OTHER"),
    )
    assert result.status is DatasetProvenanceStatus.FAIL
    assert "ARTIFACT_IDENTITY_MISMATCH" in result.reasons


def test_registered_artifact_requires_observed_artifact():
    spec = make_spec()
    registry = DatasetRegistry()
    registry.register(spec.dataset, HASH_A, artifact=artifact())
    result = evaluate_dataset_provenance(spec, registry, HASH_A)
    assert result.status is DatasetProvenanceStatus.FAIL
    assert "OBSERVED_ARTIFACT_REQUIRED" in result.reasons


def test_unknown_dataset_is_blocked():
    spec = make_spec()
    result = evaluate_dataset_provenance(spec, DatasetRegistry(), HASH_A)
    assert result.status is DatasetProvenanceStatus.BLOCKED


def test_holdout_revision_change_fails():
    spec = make_spec(DatasetRole.FRESH_HOLDOUT)
    registry = DatasetRegistry()
    registry.register(spec.dataset, HASH_A, artifact=artifact())
    changed = make_spec(DatasetRole.FRESH_HOLDOUT, revision="DATA-002")
    result = evaluate_dataset_provenance(changed, registry, HASH_A, observed_artifact=artifact())
    assert result.status is DatasetProvenanceStatus.FAIL
    assert "DATA_REVISION_MISMATCH" in result.reasons
