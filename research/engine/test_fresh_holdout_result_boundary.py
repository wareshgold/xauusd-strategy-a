from .fresh_holdout_result_boundary import (
    FreshHoldoutResultDecision,
    FreshHoldoutResultInput,
    decide_fresh_holdout_result,
)


def test_valid_result_passes():
    value = FreshHoldoutResultInput("FRESH_HOLDOUT_01", "r1", "r1")
    assert decide_fresh_holdout_result(value) is FreshHoldoutResultDecision.PASS


def test_result_mismatch_blocks():
    value = FreshHoldoutResultInput("FRESH_HOLDOUT_01", "r1", "r2")
    assert decide_fresh_holdout_result(value) is FreshHoldoutResultDecision.BLOCK


def test_optimization_blocks():
    value = FreshHoldoutResultInput("FRESH_HOLDOUT_01", "r1", "r1", True)
    assert decide_fresh_holdout_result(value) is FreshHoldoutResultDecision.BLOCK


def test_missing_result_identity_is_unknown():
    value = FreshHoldoutResultInput("FRESH_HOLDOUT_01", "", "r1")
    assert decide_fresh_holdout_result(value) is FreshHoldoutResultDecision.UNKNOWN
