from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .source_resolution import SourceResolutionResult, SourceVerdict


class ResolutionStatus(str, Enum):
    OPEN = "OPEN"
    UNRESOLVED = "UNRESOLVED"
    CONFIRMED = "CONFIRMED"


@dataclass(frozen=True)
class ResolutionRecord:
    question_id: str
    fixture_id: str
    status: ResolutionStatus
    evidence_id: str | None
    selected_alternative: str | None
    source_reference: str
    rationale: str

    def validate(self) -> None:
        if not self.question_id or not self.fixture_id:
            raise ValueError("resolution identity is required")
        if not self.source_reference:
            raise ValueError("source reference is required")
        if not self.rationale:
            raise ValueError("resolution rationale is required")
        if self.status is ResolutionStatus.CONFIRMED:
            if not self.evidence_id or not self.selected_alternative:
                raise ValueError(
                    "confirmed resolution requires evidence and selected alternative"
                )
        else:
            if self.selected_alternative is not None:
                raise ValueError(
                    "non-confirmed resolution cannot select an alternative"
                )

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "question_id": self.question_id,
            "fixture_id": self.fixture_id,
            "status": self.status.value,
            "evidence_id": self.evidence_id,
            "selected_alternative": self.selected_alternative,
            "source_reference": self.source_reference,
            "rationale": self.rationale,
        }


class SourceLedgerError(ValueError):
    pass


class SourceResolutionLedger:
    """Append-only in-memory ledger for source-resolution evidence.

    This ledger records evidence state only. It never promotes strategy
    rules to canonical status and never evaluates backtest performance.
    """

    def __init__(self) -> None:
        self._records: dict[str, ResolutionRecord] = {}

    def record(
        self,
        result: SourceResolutionResult,
        *,
        source_reference: str,
        rationale: str,
        evidence_id: str | None = None,
    ) -> ResolutionRecord:
        if not source_reference or not rationale:
            raise SourceLedgerError("source reference and rationale are required")

        if result.verdict is SourceVerdict.CONFIRMED:
            status = ResolutionStatus.CONFIRMED
            if not result.selected_alternative or not result.evidence_id:
                raise SourceLedgerError(
                    "confirmed result must contain source evidence"
                )
            resolved_evidence_id = result.evidence_id
        elif result.verdict is SourceVerdict.UNRESOLVED:
            status = ResolutionStatus.UNRESOLVED
            resolved_evidence_id = evidence_id or result.evidence_id
        else:
            status = ResolutionStatus.OPEN
            resolved_evidence_id = evidence_id

        record = ResolutionRecord(
            question_id=result.question_id,
            fixture_id=result.fixture_id,
            status=status,
            evidence_id=resolved_evidence_id,
            selected_alternative=(
                result.selected_alternative
                if status is ResolutionStatus.CONFIRMED
                else None
            ),
            source_reference=source_reference,
            rationale=rationale,
        )
        record.validate()

        existing = self._records.get(record.question_id)
        if existing is not None and existing != record:
            raise SourceLedgerError(
                f"resolution for {record.question_id} is already recorded differently"
            )
        self._records[record.question_id] = record
        return record

    def get(self, question_id: str) -> ResolutionRecord:
        try:
            return self._records[question_id]
        except KeyError as exc:
            raise SourceLedgerError(
                f"no source resolution record for {question_id}"
            ) from exc

    @property
    def records(self) -> tuple[ResolutionRecord, ...]:
        return tuple(self._records[key] for key in sorted(self._records))

    @property
    def all_confirmed(self) -> bool:
        return bool(self._records) and all(
            record.status is ResolutionStatus.CONFIRMED
            for record in self._records.values()
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "records": [record.as_dict() for record in self.records],
            "all_confirmed": self.all_confirmed,
        }
