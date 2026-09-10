from .research_hygiene_gate import HygieneDecision, HygieneInput, decide_hygiene


def test_complete_hygiene_passes():
    assert decide_hygiene(HygieneInput(True, True, True, True)) is HygieneDecision.PASS


def test_unfrozen_spec_is_unknown():
    assert decide_hygiene(HygieneInput(True, True, False, True)) is HygieneDecision.UNKNOWN


def test_missing_source_version_blocks():
    assert decide_hygiene(HygieneInput(False, True, True, True)) is HygieneDecision.BLOCK


def test_missing_dataset_version_blocks():
    assert decide_hygiene(HygieneInput(True, False, True, True)) is HygieneDecision.BLOCK


def test_validation_isolation_failure_blocks():
    assert decide_hygiene(HygieneInput(True, True, True, False)) is HygieneDecision.BLOCK


def test_live_authorization_never_passes():
    assert decide_hygiene(HygieneInput(True, True, True, True, True)) is HygieneDecision.BLOCK
