from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EvidenceStatus(str, Enum):
    SOURCE_CONFIRMED = "SOURCE_CONFIRMED"
    PARTIALLY_RESOLVED = "PARTIALLY_RESOLVED"
    UNRESOLVED = "UNRESOLVED"
    RESEARCH_ONLY = "RESEARCH_ONLY"


class RuleAuthority(str, Enum):
    CANONICAL = "CANONICAL"
    NON_CANONICAL = "NON_CANONICAL"


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    rule_id: str
    status: EvidenceStatus
    statement: str
    source_reference: str
    notes: str = ""
    unresolved_questions: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "rule_id": self.rule_id,
            "status": self.status.value,
            "statement": self.statement,
            "source_reference": self.source_reference,
            "notes": self.notes,
            "unresolved_questions": list(self.unresolved_questions),
        }


@dataclass(frozen=True)
class UnresolvedQuestion:
    question_id: str
    rule_id: str
    question: str
    blocking: bool = True
    disposition: str = "OPEN"

    def as_dict(self) -> dict[str, Any]:
        return {
            "question_id": self.question_id,
            "rule_id": self.rule_id,
            "question": self.question,
            "blocking": self.blocking,
            "disposition": self.disposition,
        }


@dataclass(frozen=True)
class StrategyRule:
    rule_id: str
    name: str
    authority: RuleAuthority
    evidence_status: EvidenceStatus
    evidence_ids: tuple[str, ...] = ()
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "authority": self.authority.value,
            "evidence_status": self.evidence_status.value,
            "evidence_ids": list(self.evidence_ids),
            "notes": self.notes,
        }


@dataclass
class StrategyManifest:
    strategy_id: str
    revision: str
    rules: list[StrategyRule] = field(default_factory=list)
    evidence: list[EvidenceRecord] = field(default_factory=list)
    unresolved: list[UnresolvedQuestion] = field(default_factory=list)

    @property
    def canonical_ready(self) -> bool:
        if not self.rules:
            return False
        if any(rule.authority is not RuleAuthority.CANONICAL for rule in self.rules):
            return False
        return not any(
            question.blocking and question.disposition == "OPEN"
            for question in self.unresolved
        )

    def evidence_for(self, rule_id: str) -> list[EvidenceRecord]:
        return [item for item in self.evidence if item.rule_id == rule_id]

    def unresolved_for(self, rule_id: str) -> list[UnresolvedQuestion]:
        return [item for item in self.unresolved if item.rule_id == rule_id]

    def as_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "revision": self.revision,
            "canonical_ready": self.canonical_ready,
            "rules": [rule.as_dict() for rule in self.rules],
            "evidence": [item.as_dict() for item in self.evidence],
            "unresolved": [item.as_dict() for item in self.unresolved],
        }
