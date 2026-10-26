from hashlib import sha256

import pytest

from strategy_factory.research_brain import (
    ClaimDisposition,
    EvidenceItem,
    EvidenceOutcome,
    EvidenceRole,
    ResearchHypothesis,
    evaluate_hypothesis,
)


def item(eid, role, outcome=EvidenceOutcome.SUPPORTS, test_passed=None):
    return EvidenceItem(eid, role, f"fixture://{eid}", sha256(eid.encode()).hexdigest(),
                        outcome, test_passed)


def hypothesis(canonical=False, roles=None):
    return ResearchHypothesis("H-001", "A testable research claim",
        tuple(roles or (EvidenceRole.SOURCE, EvidenceRole.DATA, EvidenceRole.TEST)),
        asks_to_change_canonical_rule=canonical)


def test_missing_source_evidence_stays_unresolved_even_with_good_results():
    result = evaluate_hypothesis(hypothesis(), [
        item("data", EvidenceRole.DATA), item("test", EvidenceRole.TEST, test_passed=True)
    ])
    assert result.disposition is ClaimDisposition.UNRESOLVED
    assert result.missing_roles == (EvidenceRole.SOURCE,)
    assert result.canonical_authorized is False


def test_backtest_or_test_evidence_cannot_replace_source_authority():
    result = evaluate_hypothesis(hypothesis(roles=(EvidenceRole.SOURCE, EvidenceRole.TEST)), [
        item("test", EvidenceRole.TEST, test_passed=True)
    ])
    assert result.disposition is ClaimDisposition.UNRESOLVED
    assert result.canonical_authorized is False


def test_any_explicit_contradiction_blocks_claim():
    result = evaluate_hypothesis(hypothesis(), [
        item("source", EvidenceRole.SOURCE),
        item("data", EvidenceRole.DATA),
        item("test", EvidenceRole.TEST, test_passed=True),
        item("counterexample", EvidenceRole.DATA, EvidenceOutcome.CONTRADICTS),
    ])
    assert result.disposition is ClaimDisposition.BLOCKED_CONTRADICTION
    assert result.contradiction_ids == ("counterexample",)


def test_failed_test_blocks_claim_even_if_other_evidence_supports_it():
    result = evaluate_hypothesis(hypothesis(), [
        item("source", EvidenceRole.SOURCE),
        item("data", EvidenceRole.DATA),
        item("test", EvidenceRole.TEST, test_passed=False),
    ])
    assert result.disposition is ClaimDisposition.BLOCKED_TEST_FAILURE
    assert result.failed_test_ids == ("test",)


def test_complete_evidence_for_rule_change_routes_to_human_source_review():
    result = evaluate_hypothesis(hypothesis(canonical=True), [
        item("source", EvidenceRole.SOURCE),
        item("data", EvidenceRole.DATA),
        item("test", EvidenceRole.TEST, test_passed=True),
    ])
    assert result.disposition is ClaimDisposition.HUMAN_SOURCE_REVIEW_REQUIRED
    assert result.canonical_authorized is False
    assert result.production_decision_authorized is False


def test_inconclusive_evidence_requests_discriminating_test():
    result = evaluate_hypothesis(hypothesis(roles=(EvidenceRole.SOURCE,)), [
        item("source", EvidenceRole.SOURCE, EvidenceOutcome.INCONCLUSIVE)
    ])
    assert result.disposition is ClaimDisposition.UNRESOLVED
    assert "DESIGN_DISCRIMINATING_TEST_WITH_FROZEN_INPUTS" in result.next_actions


def test_duplicate_evidence_ids_fail_closed():
    with pytest.raises(ValueError, match="unique"):
        evaluate_hypothesis(hypothesis(roles=(EvidenceRole.SOURCE,)), [
            item("same", EvidenceRole.SOURCE), item("same", EvidenceRole.SOURCE)
        ])


def test_invalid_evidence_digest_is_rejected():
    bad = EvidenceItem("bad", EvidenceRole.SOURCE, "fixture://bad", "not-a-digest",
                       EvidenceOutcome.SUPPORTS)
    with pytest.raises(ValueError, match="content_sha256"):
        evaluate_hypothesis(hypothesis(roles=(EvidenceRole.SOURCE,)), [bad])


def test_research_supported_never_authorizes_production_decisions():
    result = evaluate_hypothesis(hypothesis(roles=(EvidenceRole.SOURCE, EvidenceRole.TEST)), [
        item("source", EvidenceRole.SOURCE), item("test", EvidenceRole.TEST, test_passed=True)
    ])
    assert result.disposition is ClaimDisposition.RESEARCH_SUPPORTED
    assert result.canonical_authorized is False
    assert result.production_decision_authorized is False
