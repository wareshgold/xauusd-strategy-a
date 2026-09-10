from .validation_boundary import ValidationDecision, ValidationInput, decide_validation


def test_valid_frozen_validation_passes():
    assert decide_validation(ValidationInput(True, True, True, True)) is ValidationDecision.PASS


def test_unfrozen_spec_is_unknown():
    assert decide_validation(ValidationInput(False, True, True, True)) is ValidationDecision.UNKNOWN


def test_fixture_failure_blocks():
    assert decide_validation(ValidationInput(True, False, True, True)) is ValidationDecision.BLOCK


def test_dev_incomplete_blocks():
    assert decide_validation(ValidationInput(True, True, False, True)) is ValidationDecision.BLOCK


def test_validation_isolation_failure_blocks():
    assert decide_validation(ValidationInput(True, True, True, False)) is ValidationDecision.BLOCK


def test_touched_holdout_blocks():
    assert decide_validation(ValidationInput(True, True, True, True, True)) is ValidationDecision.BLOCK
