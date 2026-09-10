from .demo_batch_quality_gate import BatchQualityDecision, BatchQualityInput, decide_batch_quality
from .demo_batch_replay_boundary import ReplayBoundaryDecision, ReplayBoundaryInput, decide_replay_boundary


def test_g119_g127_valid_batch_passes_quality():
    value = BatchQualityInput(True, True, True, True, 3)
    assert decide_batch_quality(value) is BatchQualityDecision.PASS


def test_g119_g127_empty_batch_is_unknown():
    value = BatchQualityInput(True, True, True, True, 0)
    assert decide_batch_quality(value) is BatchQualityDecision.UNKNOWN


def test_g119_g127_invalid_journal_blocks():
    value = BatchQualityInput(False, True, True, True, 3)
    assert decide_batch_quality(value) is BatchQualityDecision.BLOCK


def test_g119_g127_unstable_recovery_blocks():
    value = BatchQualityInput(True, True, False, True, 3)
    assert decide_batch_quality(value) is BatchQualityDecision.BLOCK


def test_g119_g127_sequence_gap_blocks_replay():
    value = ReplayBoundaryInput(False, True, True, True)
    assert decide_replay_boundary(value) is ReplayBoundaryDecision.BLOCK


def test_g119_g127_uncertain_replay_requires_review():
    value = ReplayBoundaryInput(True, False, True, True)
    assert decide_replay_boundary(value) is ReplayBoundaryDecision.REQUIRE_REVIEW


def test_g119_g127_valid_replay_passes():
    value = ReplayBoundaryInput(True, True, True, True)
    assert decide_replay_boundary(value) is ReplayBoundaryDecision.PASS
