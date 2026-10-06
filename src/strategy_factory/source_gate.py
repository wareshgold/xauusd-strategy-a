from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol

from .source_ledger import ResolutionStatus, SourceResolutionLedger


class SourceGateStatus(str, Enum):
    PASS = "PASS"
    BLOCKED = "BLOCKED"
    FAIL = "FAIL"


class ManifestQuestion(Protocol):
    question_id: str
    blocking: bool


@dataclass(frozen=True)
class SourceGateResult:
    status: SourceGateStatus
    blocking_questions: tuple[str, ...]
    unresolved_questions: tuple[str, ...]
    missing_questions: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "blocking_questions": list(self.blocking_questions),
            "unresolved_questions": list(self.unresolved_questions),
            "missing_questions": list(self.missing_questions),
        }


def evaluate_source_gate(
    questions: tuple[ManifestQuestion, ...],
    ledger: SourceResolutionLedger,
) -> SourceGateResult:
    blocking: list[str] = []
    unresolved: list[str] = []
    missing: list[str] = []

    for question in questions:
        try:
            record = ledger.get(question.question_id)
        except Exception:
            if question.blocking:
                missing.append(question.question_id)
            continue

        if record.status is not ResolutionStatus.CONFIRMED:
            unresolved.append(question.question_id)
            if question.blocking:
                blocking.append(question.question_id)

    status = SourceGateStatus.PASS
    if missing or blocking:
        status = SourceGateStatus.BLOCKED

    return SourceGateResult(
        status=status,
        blocking_questions=tuple(sorted(blocking)),
        unresolved_questions=tuple(sorted(unresolved)),
        missing_questions=tuple(sorted(missing)),
    )
