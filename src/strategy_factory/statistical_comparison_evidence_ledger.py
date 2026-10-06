from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .statistical_comparison_evidence import (
    StatisticalComparisonEvidence,
    StatisticalComparisonEvidenceError,
    validate_statistical_comparison_evidence,
)


class StatisticalComparisonEvidenceLedgerError(ValueError):
    """Raised when statistical comparison evidence cannot be registered."""


@dataclass(frozen=True)
class StatisticalComparisonEvidenceLedgerEntry:
    evidence_fingerprint: str
    comparison_fingerprint: str
    adjustment_fingerprint: str
    method: str
    family_size: int
    fingerprint: str

    def _payload(self) -> dict[str, object]:
        return {
            "evidence_fingerprint": self.evidence_fingerprint,
            "comparison_fingerprint": self.comparison_fingerprint,
            "adjustment_fingerprint": self.adjustment_fingerprint,
            "method": self.method,
            "family_size": self.family_size,
        }

    def validate(self) -> None:
        if not self.evidence_fingerprint or not self.comparison_fingerprint or not self.adjustment_fingerprint:
            raise StatisticalComparisonEvidenceLedgerError("ledger entry identity is incomplete")
        expected = hashlib.sha256(json.dumps(self._payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if self.fingerprint != expected:
            raise StatisticalComparisonEvidenceLedgerError("statistical comparison ledger fingerprint mismatch")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {**self._payload(), "fingerprint": self.fingerprint}


class StatisticalComparisonEvidenceLedger:
    """Append-only in-memory registry for provenance-valid comparison evidence."""

    def __init__(self) -> None:
        self._entries: dict[str, StatisticalComparisonEvidenceLedgerEntry] = {}

    def record(self, evidence: StatisticalComparisonEvidence) -> StatisticalComparisonEvidenceLedgerEntry:
        try:
            evidence.validate()
        except StatisticalComparisonEvidenceError as exc:
            raise StatisticalComparisonEvidenceLedgerError(str(exc)) from exc
        existing = self._entries.get(evidence.fingerprint)
        if existing is not None:
            return existing
        entry = StatisticalComparisonEvidenceLedgerEntry(
            evidence_fingerprint=evidence.fingerprint,
            comparison_fingerprint=evidence.comparison_fingerprint,
            adjustment_fingerprint=evidence.adjustment_fingerprint,
            method=evidence.method,
            family_size=evidence.family_size,
            fingerprint="",
        )
        fingerprint = hashlib.sha256(json.dumps(entry._payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        entry = StatisticalComparisonEvidenceLedgerEntry(**{**entry.__dict__, "fingerprint": fingerprint})
        entry.validate()
        for prior in self._entries.values():
            if prior.comparison_fingerprint == entry.comparison_fingerprint and prior.evidence_fingerprint != entry.evidence_fingerprint:
                raise StatisticalComparisonEvidenceLedgerError("conflicting evidence already recorded for comparison")
        self._entries[evidence.fingerprint] = entry
        return entry

    def contains(self, evidence: StatisticalComparisonEvidence) -> bool:
        return evidence.fingerprint in self._entries

    def entries(self) -> tuple[StatisticalComparisonEvidenceLedgerEntry, ...]:
        return tuple(self._entries.values())

    def assert_clean(self) -> None:
        for entry in self._entries.values():
            entry.validate()

    def as_dict(self) -> list[dict[str, object]]:
        self.assert_clean()
        return [entry.as_dict() for entry in self._entries.values()]
