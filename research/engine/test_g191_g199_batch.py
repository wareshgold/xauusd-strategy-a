from .fresh_holdout_integrity import FreshHoldoutDecision, FreshHoldoutIntegrityInput, decide_fresh_holdout_integrity
from .fresh_holdout_result_boundary import FreshHoldoutResultDecision, FreshHoldoutResultInput, decide_fresh_holdout_result


def test_g191_g199_complete_integrity_passes():
    assert decide_fresh_holdout_integrity(FreshHoldoutIntegrityInput("d", "d", "FRESH_HOLDOUT_01", "r", True)) is FreshHoldoutDecision.PASS


def test_g191_g199_optimization_is_blocked():
    assert decide_fresh_holdout_integrity(FreshHoldoutIntegrityInput("d", "d", "FRESH_HOLDOUT_01", "r", True, True)) is FreshHoldoutDecision.BLOCK


def test_g191_g199_result_boundary_passes():
    assert decide_fresh_holdout_result(FreshHoldoutResultInput("FRESH_HOLDOUT_01", "r", "r")) is FreshHoldoutResultDecision.PASS


def test_g191_g199_result_mismatch_blocks():
    assert decide_fresh_holdout_result(FreshHoldoutResultInput("FRESH_HOLDOUT_01", "r1", "r2")) is FreshHoldoutResultDecision.BLOCK
