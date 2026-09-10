from .validation_ledger import LedgerDecision, ValidationLedgerInput, decide_ledger


def base(**overrides):
    value = dict(
        source_version="source-v1",
        dataset_fingerprint="dataset-sha",
        specification_version="spec-v1",
        fixture_fingerprint="fixture-sha",
        dev_result_fingerprint="dev-sha",
        validation_result_fingerprint="val-sha",
        holdout_untouched=True,
    )
    value.update(overrides)
    return ValidationLedgerInput(**value)


def test_complete_ledger_passes():
    assert decide_ledger(base()) is LedgerDecision.PASS


def test_missing_ledger_field_is_unknown():
    assert decide_ledger(base(dataset_fingerprint="")) is LedgerDecision.UNKNOWN


def test_touched_holdout_blocks():
    assert decide_ledger(base(holdout_untouched=False)) is LedgerDecision.BLOCK


def test_missing_source_is_unknown():
    assert decide_ledger(base(source_version="")) is LedgerDecision.UNKNOWN


def test_missing_validation_result_is_unknown():
    assert decide_ledger(base(validation_result_fingerprint="")) is LedgerDecision.UNKNOWN
