"""Evidence-gated research brain policy; never defines canonical SP2L rules.

The module deterministically routes claims based on provenance and observed
evidence. It cannot turn backtest performance into source authority or approve
production rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class EvidenceRole(str, Enum):
    SOURCE = "SOURCE"
    DATA = "DATA"
    TEST = "TEST"
    EXECUTION = "EXECUTION"
    STATISTICAL_VALIDATION = "STATISTICAL_VALIDATION"


class EvidenceOutcome(str, Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    INCONCLUSIVE = "INCONCLUSIVE"


class ClaimDisposition(str, Enum):
    UNRESOLVED = "UNRESOLVED"
    BLOCKED_CONTRADICTION = "BLOCKED_CONTRADICTION"
    BLOCKED_TEST_FAILURE = "BLOCKED_TEST_FAILURE"
    RESEARCH_SUPPORTED = "RESEARCH_SUPPORTED"
    HUMAN_SOURCE_REVIEW_REQUIRED = "HUMAN_SOURCE_REVIEW_REQUIRED"


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    role: EvidenceRole
    reference: str
    content_sha256: str
    outcome: EvidenceOutcome
    test_passed: bool | None = None

    def validate(self) -> None:
        if not self.evidence_id or not self.reference:
            raise ValueError("evidence_id and reference are required")
        digest = self.content_sha256.lower()
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("content_sha256 must be a 64-character hexadecimal digest")
        if self.role is EvidenceRole.TEST and self.test_passed is None:
            raise ValueError("TEST evidence must explicitly record test_passed")
        if self.role is not EvidenceRole.TEST and self.test_passed is not None:
            raise ValueError("test_passed is only valid for TEST evidence")


@dataclass(frozen=True)
class ResearchHypothesis:
    hypothesis_id: str
    statement: str
    required_roles: tuple[EvidenceRole, ...]
    asks_to_change_canonical_rule: bool = False

    def validate(self) -> None:
        if not self.hypothesis_id or not self.statement.strip():
            raise ValueError("hypothesis identity and statement are required")
        if not self.required_roles:
            raise ValueError("required evidence roles must be explicit")
        if len(set(self.required_roles)) != len(self.required_roles):
            raise ValueError("required evidence roles cannot repeat")


@dataclass(frozen=True)
class ResearchDecision:
    hypothesis_id: str
    disposition: ClaimDisposition
    observed_evidence_ids: tuple[str, ...]
    missing_roles: tuple[EvidenceRole, ...]
    contradiction_ids: tuple[str, ...]
    failed_test_ids: tuple[str, ...]
    next_actions: tuple[str, ...]
    canonical_authorized: bool = False
    production_decision_authorized: bool = False


def evaluate_hypothesis(
    hypothesis: ResearchHypothesis,
    evidence: Iterable[EvidenceItem],
) -> ResearchDecision:
    """Evaluate only supplied evidence; missing facts remain missing.

    Source evidence is required to consider a rule change, but even a complete
    supporting evidence set routes to human source review. Neither this module
    nor a statistical score can canonize geometry or issue trading decisions.
    """
    hypothesis.validate()
    rows = tuple(evidence)
    for item in rows:
        item.validate()
    ids = [item.evidence_id for item in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("evidence_id values must be unique within an evaluation")

    observed_roles = {item.role for item in rows if item.outcome is EvidenceOutcome.SUPPORTS}
    missing = tuple(role for role in hypothesis.required_roles if role not in observed_roles)
    contradictions = tuple(item.evidence_id for item in rows
                           if item.outcome is EvidenceOutcome.CONTRADICTS)
    failed_tests = tuple(item.evidence_id for item in rows
                         if item.role is EvidenceRole.TEST and item.test_passed is False)
    inconclusive = any(item.outcome is EvidenceOutcome.INCONCLUSIVE for item in rows)

    actions: list[str] = []
    if contradictions:
        disposition = ClaimDisposition.BLOCKED_CONTRADICTION
        actions.append("RECONCILE_CONTRADICTORY_EVIDENCE")
    elif failed_tests:
        disposition = ClaimDisposition.BLOCKED_TEST_FAILURE
        actions.append("FIX_OR_REJECT_HYPOTHESIS; DO_NOT_PROMOTE")
    elif missing or inconclusive:
        disposition = ClaimDisposition.UNRESOLVED
        actions.extend(f"COLLECT_OR_RESOLVE_{role.value}_EVIDENCE" for role in missing)
        if inconclusive:
            actions.append("DESIGN_DISCRIMINATING_TEST_WITH_FROZEN_INPUTS")
    elif hypothesis.asks_to_change_canonical_rule:
        disposition = ClaimDisposition.HUMAN_SOURCE_REVIEW_REQUIRED
        actions.append("HUMAN_REVIEW_OF_SOURCE_AND_RULE_DIFF_REQUIRED")
    else:
        disposition = ClaimDisposition.RESEARCH_SUPPORTED
        actions.append("RECORD_RESULT; DO_NOT_INFER_CANONICAL_AUTHORITY")

    return ResearchDecision(
        hypothesis_id=hypothesis.hypothesis_id,
        disposition=disposition,
        observed_evidence_ids=tuple(ids),
        missing_roles=missing,
        contradiction_ids=contradictions,
        failed_test_ids=failed_tests,
        next_actions=tuple(actions),
        canonical_authorized=False,
        production_decision_authorized=False,
    )
