from .fresh_holdout_result_boundary import (
    FreshHoldoutResultDecision,
    FreshHoldoutResultInput,
    decide_fresh_holdout_result,
)


def test_g200_g208_full_identity_passes():
    value = FreshHoldoutResultInput("FRESH_HOLDOUT_01", "d1", "d1", "r1", "r1")
    assert decide_fresh_holdout_result(value) is FreshHoldoutResultDecision.PASS


def test_g200_g208_any_dataset_change_blocks():
    value = FreshHoldoutResultInput("FRESH_HOLDOUT_01", "d2", "d1", "r1", "r1")
    assert decide_fresh_holdout_result(value) is FreshHoldoutResultDecision.BLOCK


def test_g200_g208_any_result_change_blocks():
    value = FreshHoldoutResultInput("FRESH_HOLDOUT_01", "d1", "d1", "r2", "r1")
    assert decide_fresh_holdout_result(value) is FreshHoldoutResultDecision.BLOCK


def test_g200_g208_optimization_is_never_accepted():
    value = FreshHoldoutResultInput("FRESH_HOLDOUT_01", "d1", "d1", "r1", "r1", True)
    assert decide_fresh_holdout_result(value) is FreshHoldoutResultDecision.BLOCK


def test_g200_g208_missing_window_is_unknown():
    value = FreshHoldoutResultInput("", "d1", "d1", "r1", "r1")
    assert decide_fresh_holdout_result(value) is FreshHoldoutResultDecision.UNKNOWN
