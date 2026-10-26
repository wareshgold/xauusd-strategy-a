import json

import pytest

from strategy_factory.dataset_manifest import DatasetManifest
from strategy_factory.dataset_manifest_pin_ledger import (
    DatasetManifestPinLedger,
    DatasetManifestPinLedgerError,
)


def make_manifest(dataset_id, fingerprint_char):
    return DatasetManifest.create(
        manifest_revision="DATASET-MANIFEST-1",
        dataset_id=dataset_id,
        dataset_role="FRESH_HOLDOUT",
        data_revision="DATA-REV-001",
        dataset_fingerprint=fingerprint_char * 64,
        immutable=True,
    )


def test_serialized_ledger_round_trips_against_external_tip():
    ledger = DatasetManifestPinLedger()
    ledger.append(make_manifest("HOLDOUT-A", "a"))
    ledger.append(make_manifest("HOLDOUT-B", "b"))

    restored = DatasetManifestPinLedger.from_json(
        ledger.to_json(),
        expected_external_tip_fingerprint=ledger.tip_fingerprint,
    )
    assert restored.to_json() == ledger.to_json()
    assert len(restored.pins) == 2


def test_ledger_rejects_wrong_external_tip():
    ledger = DatasetManifestPinLedger()
    ledger.append(make_manifest("HOLDOUT-A", "a"))
    with pytest.raises(DatasetManifestPinLedgerError, match="externally trusted tip"):
        DatasetManifestPinLedger.from_json(
            ledger.to_json(),
            expected_external_tip_fingerprint="f" * 64,
        )


def test_ledger_detects_record_tampering_even_if_serialized_tip_is_unchanged():
    ledger = DatasetManifestPinLedger()
    ledger.append(make_manifest("HOLDOUT-A", "a"))
    data = json.loads(ledger.to_json())
    data["pins"][0]["dataset_id"] = "ALTERED"
    with pytest.raises(DatasetManifestPinLedgerError):
        DatasetManifestPinLedger.from_json(
            json.dumps(data),
            expected_external_tip_fingerprint=ledger.tip_fingerprint,
        )


def test_ledger_detects_truncation_against_external_tip():
    ledger = DatasetManifestPinLedger()
    ledger.append(make_manifest("HOLDOUT-A", "a"))
    ledger.append(make_manifest("HOLDOUT-B", "b"))
    data = json.loads(ledger.to_json())
    data["pins"] = data["pins"][:1]
    with pytest.raises(DatasetManifestPinLedgerError):
        DatasetManifestPinLedger.from_json(
            json.dumps(data),
            expected_external_tip_fingerprint=ledger.tip_fingerprint,
        )


def test_ledger_is_append_only_per_dataset_id():
    ledger = DatasetManifestPinLedger()
    ledger.append(make_manifest("HOLDOUT-A", "a"))
    with pytest.raises(DatasetManifestPinLedgerError, match="append-only"):
        ledger.append(make_manifest("HOLDOUT-A", "b"))


def test_ledger_rejects_noncontiguous_or_reordered_sequence():
    ledger = DatasetManifestPinLedger()
    ledger.append(make_manifest("HOLDOUT-A", "a"))
    ledger.append(make_manifest("HOLDOUT-B", "b"))
    data = json.loads(ledger.to_json())
    data["pins"] = list(reversed(data["pins"]))
    with pytest.raises(DatasetManifestPinLedgerError):
        DatasetManifestPinLedger.from_json(
            json.dumps(data),
            expected_external_tip_fingerprint=ledger.tip_fingerprint,
        )
