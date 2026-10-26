import pytest

from strategy_factory.dataset_manifest import (
    DatasetManifest,
    DatasetManifestError,
    DatasetManifestRegistry,
)


HASH_A = "a" * 64
HASH_B = "b" * 64


def manifest(**overrides):
    values = {
        "manifest_revision": "DATASET-MANIFEST-1",
        "dataset_id": "HOLDOUT-001",
        "dataset_role": "FRESH_HOLDOUT",
        "data_revision": "DATA-REV-001",
        "dataset_fingerprint": HASH_A,
        "immutable": True,
    }
    values.update(overrides)
    return DatasetManifest.create(**values)


def test_manifest_fingerprint_is_deterministic_and_validated():
    first = manifest()
    second = manifest()
    assert first == second
    assert len(first.fingerprint) == 64
    first.validate()


def test_registry_requires_exact_external_pin():
    item = manifest()
    registry = DatasetManifestRegistry({item.dataset_id: item.fingerprint})
    assert registry.register(item) == item

    wrong_pin = DatasetManifestRegistry({item.dataset_id: HASH_B})
    with pytest.raises(DatasetManifestError, match="external trusted pin"):
        wrong_pin.register(item)


def test_mapping_only_registry_does_not_claim_authenticated_external_trust():
    item = manifest()
    registry = DatasetManifestRegistry({item.dataset_id: item.fingerprint})
    assert registry.has_authenticated_external_trust_root is False


def test_registry_blocks_unpinned_manifest():
    item = manifest()
    with pytest.raises(DatasetManifestError, match="no external trusted pin"):
        DatasetManifestRegistry({}).register(item)


def test_manifest_tampering_is_detected():
    item = manifest()
    changed = DatasetManifest(
        **{**item.payload(), "fingerprint": item.fingerprint}
    )
    changed = DatasetManifest(
        **{**changed.payload(), "dataset_fingerprint": HASH_B, "fingerprint": changed.fingerprint}
    )
    with pytest.raises(DatasetManifestError, match="fingerprint mismatch"):
        changed.validate()


def test_holdout_record_must_match_pinned_manifest_identity():
    item = manifest()
    registry = DatasetManifestRegistry({item.dataset_id: item.fingerprint})
    registry.register(item)

    class Record:
        dataset_id = item.dataset_id
        dataset_role = "FRESH_HOLDOUT"
        data_revision = item.data_revision
        dataset_fingerprint = item.dataset_fingerprint

    registry.validate_record(Record(), "FRESH_HOLDOUT")

    with pytest.raises(DatasetManifestError, match="role mismatch"):
        registry.validate_record(Record(), "UNTOUCHED_VALIDATION")

    class ChangedDatasetRecord(Record):
        dataset_fingerprint = HASH_B

    with pytest.raises(DatasetManifestError, match="fingerprint does not match"):
        registry.validate_record(ChangedDatasetRecord(), "FRESH_HOLDOUT")

    class ChangedRevisionRecord(Record):
        data_revision = "DATA-REV-OTHER"

    with pytest.raises(DatasetManifestError, match="revision does not match"):
        registry.validate_record(ChangedRevisionRecord(), "FRESH_HOLDOUT")


def test_registry_rejects_replacement_of_registered_manifest():
    first = manifest()
    registry = DatasetManifestRegistry({first.dataset_id: first.fingerprint})
    registry.register(first)
    second = manifest(data_revision="DATA-REV-OTHER")
    registry._trusted_pins[second.dataset_id] = second.fingerprint
    with pytest.raises(DatasetManifestError, match="immutable"):
        registry.register(second)


def test_manifest_rejects_empty_dataset_fingerprint():
    with pytest.raises(DatasetManifestError, match="dataset_fingerprint must be a SHA-256 hex digest"):
        manifest(dataset_fingerprint="")

