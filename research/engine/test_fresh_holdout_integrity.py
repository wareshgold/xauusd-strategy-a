from .fresh_holdout_integrity import (
    FreshHoldoutDecision,
    FreshHoldoutIntegrityInput,
    decide_fresh_holdout_integrity,
)


def valid():
    return FreshHoldoutIntegrityInput("data-1", "data-1", "FRESH_HOLDOUT_01", "result-1", True)


def test_g191_g199_valid_holdout_passes():
    assert decide_fresh_holdout_integrity(valid()) is FreshHoldoutDecision.PASS


def test_g191_g199_dataset_mismatch_blocks():
    value = FreshHoldoutIntegrityInput("data-2", "data-1", "FRESH_HOLDOUT_01", "result-1", True)
    assert decide_fresh_holdout_integrity(value) is FreshHoldoutDecision.BLOCK


def test_g191_g199_optimization_blocks():
    value = FreshHoldoutIntegrityInput("data-1", "data-1", "FRESH_HOLDOUT_01", "result-1", True, True)
    assert decide_fresh_holdout_integrity(value) is FreshHoldoutDecision.BLOCK


def test_g191_g199_missing_identity_is_unknown():
    value = FreshHoldoutIntegrityInput("", "data-1", "FRESH_HOLDOUT_01", "result-1", True)
    assert decide_fresh_holdout_integrity(value) is FreshHoldoutDecision.UNKNOWN


def test_g191_g199_unrecorded_result_is_unknown():
    value = FreshHoldoutIntegrityInput("data-1", "data-1", "FRESH_HOLDOUT_01", "", False)
    assert decide_fresh_holdout_integrity(value) is FreshHoldoutDecision.UNKNOWN


def test_g191_g199_recorded_result_without_fingerprint_blocks():
    value = FreshHoldoutIntegrityInput("data-1", "data-1", "FRESH_HOLDOUT_01", "", True)
    assert decide_fresh_holdout_integrity(value) is FreshHoldoutDecision.BLOCK
