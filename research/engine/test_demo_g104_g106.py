from .demo_recovery_fingerprint import RecoveryFingerprint, fingerprint


def test_g104_same_recovered_state_has_same_fingerprint():
    value = RecoveryFingerprint("o1", "FILLED", 7)
    assert fingerprint(value) == fingerprint(value)


def test_g105_fingerprint_changes_when_state_changes():
    a = fingerprint(RecoveryFingerprint("o1", "FILLED", 7))
    b = fingerprint(RecoveryFingerprint("o1", "CANCELLED", 7))
    assert a != b


def test_g106_fingerprint_changes_when_sequence_changes():
    a = fingerprint(RecoveryFingerprint("o1", "FILLED", 7))
    b = fingerprint(RecoveryFingerprint("o1", "FILLED", 8))
    assert a != b
