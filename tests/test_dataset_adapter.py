import pytest

from strategy_factory.data import DatasetIngestionError, HistoricalDatasetAdapter
from strategy_factory.datasets import DatasetRegistry
from strategy_factory.test_contract import DatasetRole, TestDataset


PAYLOAD = b"timestamp,open,high,low,close\\n2026-01-01T00:00:00Z,1,2,0,1.5\\n"


def make_dataset(**kwargs):
    values = {
        "dataset_id": "XAU-SYNTH-001",
        "role": DatasetRole.DEVELOPMENT,
        "data_revision": "R1",
        "start": "2026-01-01",
        "end": "2026-02-01",
        "source": "SYNTHETIC",
    }
    values.update(kwargs)
    return TestDataset(**values)


def test_ingestion_is_deterministic_and_registers_artifact():
    registry = DatasetRegistry()
    adapter = HistoricalDatasetAdapter(registry)

    first = adapter.ingest(
        make_dataset(), PAYLOAD,
        artifact_id="ART-1", location="fixtures/xau.csv", format="CSV"
    )
    second = adapter.ingest(
        make_dataset(), PAYLOAD,
        artifact_id="ART-1", location="fixtures/xau.csv", format="CSV"
    )

    assert first.content_sha256 == second.content_sha256
    assert first.fingerprint == second.fingerprint
    assert first.byte_size == len(PAYLOAD)
    assert registry.get("XAU-SYNTH-001").artifact == first.artifact


def test_ingestion_rejects_non_bytes_payload():
    with pytest.raises(DatasetIngestionError):
        HistoricalDatasetAdapter(DatasetRegistry()).ingest(
            make_dataset(), "not-bytes",
            artifact_id="ART-1", location="x", format="CSV"
        )


def test_ingestion_rejects_changed_bytes_for_existing_identity():
    registry = DatasetRegistry()
    adapter = HistoricalDatasetAdapter(registry)
    adapter.ingest(
        make_dataset(), PAYLOAD,
        artifact_id="ART-1", location="fixtures/xau.csv", format="CSV"
    )

    with pytest.raises(DatasetIngestionError):
        adapter.ingest(
            make_dataset(), PAYLOAD + b"changed",
            artifact_id="ART-1", location="fixtures/xau.csv", format="CSV"
        )


def test_validation_holdout_must_be_immutable():
    registry = DatasetRegistry()
    adapter = HistoricalDatasetAdapter(registry)
    with pytest.raises(ValueError):
        adapter.ingest(
            make_dataset(role=DatasetRole.UNTOUCHED_VALIDATION, immutable=False),
            PAYLOAD,
            artifact_id="ART-VAL", location="fixtures/validation.csv", format="CSV"
        )


def test_holdout_is_locked_at_registration():
    registry = DatasetRegistry()
    adapter = HistoricalDatasetAdapter(registry)
    loaded = adapter.ingest(
        make_dataset(
            dataset_id="HOLDOUT-1",
            role=DatasetRole.FRESH_HOLDOUT,
            immutable=True,
        ),
        PAYLOAD,
        artifact_id="ART-HOLDOUT",
        location="fixtures/holdout.csv",
        format="CSV",
    )
    assert registry.get(loaded.dataset.dataset_id).locked is True


def test_verify_requires_registered_identity():
    adapter = HistoricalDatasetAdapter(DatasetRegistry())
    with pytest.raises(DatasetIngestionError):
        adapter.verify(make_dataset(), PAYLOAD)


def test_verify_rejects_payload_mismatch():
    registry = DatasetRegistry()
    adapter = HistoricalDatasetAdapter(registry)
    adapter.ingest(
        make_dataset(), PAYLOAD,
        artifact_id="ART-1", location="fixtures/xau.csv", format="CSV"
    )

    with pytest.raises(DatasetIngestionError):
        adapter.verify(make_dataset(), PAYLOAD + b"changed")


def test_verify_accepts_exact_registered_payload():
    registry = DatasetRegistry()
    adapter = HistoricalDatasetAdapter(registry)
    loaded = adapter.ingest(
        make_dataset(), PAYLOAD,
        artifact_id="ART-1", location="fixtures/xau.csv", format="CSV"
    )
    verified = adapter.verify(make_dataset(), PAYLOAD)

    assert verified.fingerprint == loaded.fingerprint
    assert verified.artifact == loaded.artifact
    assert verified.payload == PAYLOAD


def test_ingestion_does_not_transform_payload():
    registry = DatasetRegistry()
    adapter = HistoricalDatasetAdapter(registry)
    loaded = adapter.ingest(
        make_dataset(), PAYLOAD,
        artifact_id="ART-1", location="fixtures/xau.csv", format="CSV"
    )
    assert loaded.payload == PAYLOAD


def test_different_payload_produces_different_identity():
    registry = DatasetRegistry()
    adapter = HistoricalDatasetAdapter(registry)
    first = adapter.ingest(
        make_dataset(dataset_id="D1"), PAYLOAD,
        artifact_id="A1", location="x1", format="CSV"
    )
    second = adapter.ingest(
        make_dataset(dataset_id="D2"), PAYLOAD + b"2",
        artifact_id="A2", location="x2", format="CSV"
    )
    assert first.content_sha256 != second.content_sha256
    assert first.fingerprint != second.fingerprint
