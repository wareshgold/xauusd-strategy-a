from .demo_integrity_boundary import IntegrityCheck, IntegrityDecision, decide_integrity


def test_g98_valid_integrity_allows_demo_progression():
    assert decide_integrity(IntegrityCheck(True, True, True)) is IntegrityDecision.ALLOW


def test_g99_invalid_journal_or_sequence_blocks():
    assert decide_integrity(IntegrityCheck(False, True, True)) is IntegrityDecision.BLOCK
    assert decide_integrity(IntegrityCheck(True, False, True)) is IntegrityDecision.BLOCK


def test_g100_unrecovered_state_is_unknown_not_success():
    assert decide_integrity(IntegrityCheck(True, True, False)) is IntegrityDecision.UNKNOWN
