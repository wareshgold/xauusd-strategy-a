import pytest

from strategy_factory.datasets import DatasetRegistry, DatasetRegistryError, fingerprint_dataset
from strategy_factory.test_contract import DatasetRole, TestDataset


def dataset(role=DatasetRole.DEVELOPMENT, dataset_id="DATA-001", immutable=False, revision="R1"):
    return TestDataset(
        dataset_id=dataset_id, role=role, data_revision=revision,
        start="2026-01-01T00:00:00Z", end="2026-02-01T00:00:00Z",
        source="RESEARCH_FIXTURE", immutable=immutable,
    )


def test_fingerprint_is_deterministic():
    d = dataset()
    assert fingerprint_dataset(d, "CONTENT-ABC") == fingerprint_dataset(d, "CONTENT-ABC")
    assert fingerprint_dataset(d, "CONTENT-ABC") != fingerprint_dataset(d, "CONTENT-XYZ")


def test_registry_returns_same_identity_for_same_registration():
    registry = DatasetRegistry()
    first = registry.register(dataset(), "CONTENT-ABC")
    second = registry.register(dataset(), "CONTENT-ABC")
    assert first == second


def test_revision_or_content_change_cannot_mutate_registered_identity():
    registry = DatasetRegistry()
    registry.register(dataset(), "CONTENT-ABC")
    with pytest.raises(DatasetRegistryError):
        registry.register(dataset(revision="R2"), "CONTENT-ABC")
    with pytest.raises(DatasetRegistryError):
        registry.register(dataset(), "CONTENT-XYZ")


@pytest.mark.parametrize("role", [DatasetRole.UNTOUCHED_VALIDATION, DatasetRole.FRESH_HOLDOUT])
def test_non_development_dataset_is_locked_and_immutable(role):
    registry = DatasetRegistry()
    identity = registry.register(dataset(role=role, immutable=True), "CONTENT-ABC")
    assert identity.immutable is True
    assert identity.locked is True


def test_holdout_fingerprint_cannot_be_reused_under_another_id():
    registry = DatasetRegistry()
    registry.register(dataset(role=DatasetRole.FRESH_HOLDOUT, immutable=True), "CONTENT-ABC")
    with pytest.raises(DatasetRegistryError):
        registry.assert_no_holdout_reuse(
            dataset(role=DatasetRole.FRESH_HOLDOUT, dataset_id="OTHER", immutable=True),
            "CONTENT-ABC",
        )


def test_holdout_cannot_be_registered_as_development_with_same_fingerprint():
    registry = DatasetRegistry()
    registry.register(dataset(role=DatasetRole.FRESH_HOLDOUT, immutable=True), "CONTENT-ABC")
    with pytest.raises(DatasetRegistryError):
        registry.register(dataset(role=DatasetRole.DEVELOPMENT, dataset_id="DEV"), "CONTENT-ABC")
