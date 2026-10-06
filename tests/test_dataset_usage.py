import pytest

from strategy_factory.datasets import DatasetArtifact, DatasetRegistry, DatasetRegistryError
from strategy_factory.test_contract import DatasetRole, ExecutionSemantics, HistoricalTestSpec, TestDataset
from strategy_factory.usage import DatasetUsageError, DatasetUsageLedger, UsageDisposition


def dataset(role=DatasetRole.DEVELOPMENT, dataset_id="DATA-001", immutable=False):
    return TestDataset(
        dataset_id=dataset_id,
        role=role,
        data_revision="R1",
        start="2026-01-01T00:00:00Z",
        end="2026-02-01T00:00:00Z",
        source="RESEARCH_FIXTURE",
        immutable=immutable,
    )


def spec(d):
    return HistoricalTestSpec(
        test_id="TEST-001",
        strategy_id="SP2L-A",
        strategy_revision="STRAT-001",
        dataset=d,
        execution_semantics=ExecutionSemantics.TICK_FEASIBLE,
    )


def test_development_usage_is_recorded():
    registry = DatasetRegistry()
    d = dataset()
    identity = registry.register(d, "CONTENT-ABC")
    ledger = DatasetUsageLedger(registry)

    entry = ledger.record(spec(d), "CONTENT-ABC", purpose="DEVELOPMENT")

    assert entry.disposition is UsageDisposition.ALLOWED
    assert entry.registered_fingerprint == identity.fingerprint
    assert entry.observed_fingerprint == identity.fingerprint
    assert entry.dataset_role is DatasetRole.DEVELOPMENT


@pytest.mark.parametrize("role", [DatasetRole.UNTOUCHED_VALIDATION, DatasetRole.FRESH_HOLDOUT])
@pytest.mark.parametrize("purpose", ["DEVELOPMENT", "OPTIMIZATION", "PARAMETER_FIT"])
def test_validation_and_holdout_cannot_be_used_for_fitting(role, purpose):
    registry = DatasetRegistry()
    d = dataset(role=role, immutable=True)
    registry.register(d, "CONTENT-ABC")
    ledger = DatasetUsageLedger(registry)

    with pytest.raises(DatasetUsageError):
        ledger.record(spec(d), "CONTENT-ABC", purpose=purpose)

    assert ledger.entries() == ()


def test_fresh_holdout_is_allowed_for_final_holdout_test():
    registry = DatasetRegistry()
    d = dataset(role=DatasetRole.FRESH_HOLDOUT, immutable=True)
    registry.register(d, "CONTENT-ABC")
    ledger = DatasetUsageLedger(registry)

    entry = ledger.record(spec(d), "CONTENT-ABC", purpose="FRESH_HOLDOUT_TEST")

    assert entry.disposition is UsageDisposition.ALLOWED


def test_observed_content_must_match_registered_identity():
    registry = DatasetRegistry()
    d = dataset(role=DatasetRole.FRESH_HOLDOUT, immutable=True)
    registry.register(d, "CONTENT-ABC")
    ledger = DatasetUsageLedger(registry)

    with pytest.raises(DatasetRegistryError):
        ledger.record(spec(d), "CONTENT-CHANGED")


def test_observed_artifact_must_match_registered_artifact():
    registry = DatasetRegistry()
    d = dataset(role=DatasetRole.FRESH_HOLDOUT, immutable=True)
    artifact = DatasetArtifact("ART-001", "data/holdout.csv", "a" * 64, 10, "CSV")
    registry.register(d, "a" * 64, artifact=artifact)
    ledger = DatasetUsageLedger(registry)

    with pytest.raises(DatasetUsageError):
        ledger.record(
            spec(d),
            "a" * 64,
            artifact=DatasetArtifact("ART-002", "data/other.csv", "a" * 64, 10, "CSV"),
            purpose="FRESH_HOLDOUT_TEST",
        )


def test_ledger_is_deterministic_and_serializable():
    registry = DatasetRegistry()
    d = dataset()
    registry.register(d, "CONTENT-ABC")
    ledger = DatasetUsageLedger(registry)

    ledger.record(spec(d), "CONTENT-ABC", purpose="DEVELOPMENT")

    assert len(ledger.entries()) == 1
    assert ledger.as_dict()[0]["purpose"] == "DEVELOPMENT"
    ledger.assert_clean()
