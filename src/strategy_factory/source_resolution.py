from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .sp2l_discrimination import (
    DiscriminationFixture,
    FixtureDisposition,
)


class SourceVerdict(str, Enum):
    CONFIRMED = "CONFIRMED"
    UNRESOLVED = "UNRESOLVED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class SourceEvidence:
    evidence_id: str
    question_id: str
    selected_alternative: str | None
    source_reference: str
    rationale: str
    directly_supported: bool = False

    def validate(self) -> None:
        if not self.evidence_id or not self.question_id:
            raise ValueError("source evidence identity is required")
        if not self.source_reference:
            raise ValueError("source reference is required")
        if not self.rationale:
            raise ValueError("source rationale is required")

    @property
    def verdict(self) -> SourceVerdict:
        return (
            SourceVerdict.CONFIRMED
            if self.directly_supported and self.selected_alternative
            else SourceVerdict.UNRESOLVED
        )


@dataclass(frozen=True)
class SourceResolutionResult:
    fixture_id: str
    question_id: str
    verdict: SourceVerdict
    selected_alternative: str | None
    evidence_id: str | None
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "fixture_id": self.fixture_id,
            "question_id": self.question_id,
            "verdict": self.verdict.value,
            "selected_alternative": self.selected_alternative,
            "evidence_id": self.evidence_id,
            "reason": self.reason,
        }


class SourceResolutionError(ValueError):
    pass


def evaluate_source_resolution(
    fixture: DiscriminationFixture,
    evidence: SourceEvidence | None = None,
) -> SourceResolutionResult:
    fixture.validate()

    if evidence is None:
        return SourceResolutionResult(
            fixture.fixture_id,
            fixture.question_id,
            SourceVerdict.BLOCKED,
            None,
            None,
            "no source evidence was supplied",
        )

    try:
        evidence.validate()
    except ValueError as exc:
        raise SourceResolutionError(str(exc)) from exc

    if evidence.question_id != fixture.question_id:
        raise SourceResolutionError(
            "source evidence question does not match fixture"
        )

    if evidence.selected_alternative is not None and (
        evidence.selected_alternative not in fixture.alternatives
    ):
        raise SourceResolutionError(
            "source evidence selects an alternative not represented by fixture"
        )

    if not evidence.directly_supported:
        return SourceResolutionResult(
            fixture.fixture_id,
            fixture.question_id,
            SourceVerdict.UNRESOLVED,
            None,
            evidence.evidence_id,
            "source evidence does not directly discriminate the alternatives",
        )

    if evidence.selected_alternative is None:
        raise SourceResolutionError(
            "directly supported evidence must identify the supported alternative"
        )

    return SourceResolutionResult(
        fixture.fixture_id,
        fixture.question_id,
        SourceVerdict.CONFIRMED,
        evidence.selected_alternative,
        evidence.evidence_id,
        "source evidence directly discriminates the fixture alternatives",
    )


def resolve_fixture_set(
    fixtures: tuple[DiscriminationFixture, ...],
    evidence: tuple[SourceEvidence, ...] = (),
) -> tuple[SourceResolutionResult, ...]:
    evidence_by_question = {item.question_id: item for item in evidence}

    results = []
    for fixture in fixtures:
        results.append(
            evaluate_source_resolution(
                fixture,
                evidence_by_question.get(fixture.question_id),
            )
        )
    return tuple(results)
