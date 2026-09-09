from .sp2l_g59_frame_discrimination import OBSERVATIONS, Verdict, contradicted_candidates, source_unique


def test_frame_observations_are_source_consistent():
    assert OBSERVATIONS
    assert all(item.verdict is Verdict.CONSISTENT for item in OBSERVATIONS)


def test_g59_does_not_convert_consistency_into_uniqueness():
    assert contradicted_candidates() == ()
    assert source_unique() is False


def test_observations_have_candidate_traceability():
    assert all(item.timestamp and item.claim and item.candidate_ids for item in OBSERVATIONS)
