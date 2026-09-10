from .demo_recovery_guard import RecoveryGuardDecision, RecoveryGuardInput, guard_recovery


def test_g101_valid_recovery_can_continue():
    value = RecoveryGuardInput(True, True, True, True)
    assert guard_recovery(value) is RecoveryGuardDecision.CONTINUE


def test_g102_integrity_failure_blocks():
    assert guard_recovery(RecoveryGuardInput(False, True, True, True)) is RecoveryGuardDecision.BLOCK
    assert guard_recovery(RecoveryGuardInput(True, False, True, True)) is RecoveryGuardDecision.BLOCK


def test_g103_uncertain_recovery_requires_review():
    assert guard_recovery(RecoveryGuardInput(True, True, False, True)) is RecoveryGuardDecision.REQUIRE_REVIEW
    assert guard_recovery(RecoveryGuardInput(True, True, True, False)) is RecoveryGuardDecision.REQUIRE_REVIEW
