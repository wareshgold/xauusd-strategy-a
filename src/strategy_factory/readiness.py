from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .manifest import StrategyManifest
from .source_gate import SourceGateResult, SourceGateStatus, evaluate_source_gate
from .source_ledger import SourceResolutionLedger


@dataclass(frozen=True)
class SourceReadiness:
    """Deterministic source-readiness summary.

    This is a research governance result only. It never promotes rules to
    canonical status and never uses performance to resolve source questions.
    """

    strategy_id: str
    manifest_revision: str
    gate: SourceGateResult
    total_questions: int
    confirmed_questions: int
    unresolved_questions: int
    missing_questions: int
    frozen_geometry_blocked: bool
    canonical_strategy_eligible: bool
    production_eligible: bool

    @property
    def status(self) -> SourceGateStatus:
        return self.gate.status

    def validate(self) -> None:
        if self.total_questions < 0:
            raise ValueError("total_questions must be non-negative")
        if self.confirmed_questions < 0:
            raise ValueError("confirmed_questions must be non-negative")
        if self.unresolved_questions < 0:
            raise ValueError("unresolved_questions must be non-negative")
        if self.missing_questions < 0:
            raise ValueError("missing_questions must be non-negative")
        if self.confirmed_questions + self.unresolved_questions != self.total_questions:
            # A question is either present/confirmed or present/unresolved;
            # missing questions are counted separately from the manifest total.
            if self.confirmed_questions + self.unresolved_questions + self.missing_questions != self.total_questions:
                raise ValueError("readiness counts do not reconcile")
        if self.production_eligible and not self.canonical_strategy_eligible:
            raise ValueError("production cannot be eligible before canonical eligibility")
        if self.canonical_strategy_eligible and self.frozen_geometry_blocked:
            raise ValueError("canonical strategy cannot be eligible while geometry is blocked")

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "strategy_id": self.strategy_id,
            "manifest_revision": self.manifest_revision,
            "status": self.status.value,
            "gate": self.gate.as_dict(),
            "total_questions": self.total_questions,
            "confirmed_questions": self.confirmed_questions,
            "unresolved_questions": self.unresolved_questions,
            "missing_questions": self.missing_questions,
            "frozen_geometry_blocked": self.frozen_geometry_blocked,
            "canonical_strategy_eligible": self.canonical_strategy_eligible,
            "production_eligible": self.production_eligible,
        }


def evaluate_source_readiness(
    manifest: StrategyManifest,
    ledger: SourceResolutionLedger,
) -> SourceReadiness:
    """Evaluate manifest source readiness without resolving any question."""

    questions = tuple(manifest.unresolved)
    gate = evaluate_source_gate(questions, ledger)

    confirmed = sum(
        1
        for question in questions
        if any(
            record.question_id == question.question_id
            and record.status.value == "CONFIRMED"
            for record in ledger.records
        )
    )
    missing = len(gate.missing_questions)
    unresolved = len(gate.unresolved_questions)

    frozen_geometry_blocked = gate.status is not SourceGateStatus.PASS
    canonical_strategy_eligible = (
        not frozen_geometry_blocked
        and manifest.canonical_ready
    )
    production_eligible = False

    result = SourceReadiness(
        strategy_id=manifest.strategy_id,
        manifest_revision=manifest.revision,
        gate=gate,
        total_questions=len(questions),
        confirmed_questions=confirmed,
        unresolved_questions=unresolved,
        missing_questions=missing,
        frozen_geometry_blocked=frozen_geometry_blocked,
        canonical_strategy_eligible=canonical_strategy_eligible,
        production_eligible=production_eligible,
    )
    result.validate()
    return result
