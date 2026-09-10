from .fresh_holdout_result_boundary import (
    FreshHoldoutResultDecision,
    FreshHoldoutResultInput,
    decide_fresh_holdout_result,
)


def valid():
    return FreshHoldoutResultInput("FRESH_HOLDOUT_01", "data-1", "data-1", "r1", "r1")


def test_g200_g208_valid_result_passes():
    assert decide_fresh_holdout_result(valid()) is FreshHoldoutResultDecision.PASS


def test_g200_g208_dataset_mismatch_blocks():
    value = FreshHoldoutResultInput("FRESH_HOLDOUT_01", "data-2", "data-1", "r1", "r1")
    assert decide_fresh_holdout_result(value) is FreshHoldoutResultDecision.BLOCK


def test_g200_g208_result_mismatch_blocks():
    value = FreshHoldoutResultInput("FRESH_HOLDOUT_01", "data-1", "data-1", "r1", "r2")
    assert decide_fresh_holdout_result(value) is FreshHoldoutResultDecision.BLOCK


def test_g200_g208_optimization_blocks():
    value = FreshHoldoutResultInput("FRESH_HOLDOUT_01", "data-1", "data-1", "r1", "r1", True)
    assert decide_fresh_holdout_result(value) is FreshHoldoutResultDecision.BLOCK


def test_g200_g208_missing_identity_is_unknown():
    value = FreshHoldoutResultInput("", "data-1", "data-1", "r1", "r1")
    assert decide_fresh_holdout_result(value) is FreshHoldoutResultDecision.UNKNOWN
