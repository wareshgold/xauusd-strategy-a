from .candidates_g55 import CANDIDATES, CandidateStatus, candidate_ids, execution_allowed


def test_candidate_registry_is_explicit_and_unique():
    ids = candidate_ids()
    assert len(ids) == len(set(ids))
    assert len(ids) == len(CANDIDATES)
    assert all(candidate.status is CandidateStatus.HYPOTHESIS for candidate in CANDIDATES)


def test_candidates_never_authorize_execution():
    assert all(not execution_allowed(candidate) for candidate in CANDIDATES)


def test_market_reclaim_is_not_registered_as_trigger_candidate():
    assert not any("reclaim" in candidate.description.lower() for candidate in CANDIDATES)
