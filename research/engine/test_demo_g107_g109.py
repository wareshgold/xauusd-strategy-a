from .demo_recovery_fingerprint import RecoveryFingerprint
from .demo_replay_integrity import compare_recovery


def test_g107_identical_recovery_replays_deterministically():
    value = RecoveryFingerprint("o1", "FILLED", 7)
    assert compare_recovery(value, value).deterministic


def test_g108_changed_recovery_is_detected():
    a = RecoveryFingerprint("o1", "FILLED", 7)
    b = RecoveryFingerprint("o1", "CANCELLED", 7)
    assert not compare_recovery(a, b).deterministic


def test_g109_sequence_change_is_detected():
    a = RecoveryFingerprint("o1", "FILLED", 7)
    b = RecoveryFingerprint("o1", "FILLED", 8)
    assert not compare_recovery(a, b).deterministic
