from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .research_certification import ResearchCertification, ResearchCertificationError


class ResearchCertificationLedgerError(ValueError):
    """Raised when a certification ledger entry is invalid or conflicting."""


@dataclass(frozen=True)
class ResearchCertificationLedgerEntry:
    certification_fingerprint: str
    run_id: str
    research_record_fingerprint: str
    source_snapshot_fingerprint: str
    strategy_id: str
    strategy_revision: str
    fingerprint: str

    def _fingerprint_payload(self) -> dict[str, object]:
        return {
            "certification_fingerprint": self.certification_fingerprint,
            "run_id": self.run_id,
            "research_record_fingerprint": self.research_record_fingerprint,
            "source_snapshot_fingerprint": self.source_snapshot_fingerprint,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
        }

    def validate(self) -> None:
        if not self.certification_fingerprint or not self.run_id:
            raise ResearchCertificationLedgerError("research certification ledger identity is incomplete")
        expected = hashlib.sha256(
            json.dumps(self._fingerprint_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest()
        if self.fingerprint != expected:
            raise ResearchCertificationLedgerError("research certification ledger fingerprint mismatch")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {**self._fingerprint_payload(), "fingerprint": self.fingerprint}


class ResearchCertificationLedger:
    """Append-only in-memory registry for immutable research certifications."""

    def __init__(self) -> None:
        self._entries: list[ResearchCertificationLedgerEntry] = []

    def record(self, certification: ResearchCertification, *, strategy_id: str, strategy_revision: str) -> ResearchCertificationLedgerEntry:
        try:
            certification.validate()
        except ResearchCertificationError as exc:
            raise ResearchCertificationLedgerError(str(exc)) from exc

        candidate = ResearchCertificationLedgerEntry(
            certification_fingerprint=certification.fingerprint,
            run_id=certification.run_id,
            research_record_fingerprint=certification.research_record_fingerprint,
            source_snapshot_fingerprint=certification.source_snapshot_fingerprint,
            strategy_id=strategy_id,
            strategy_revision=strategy_revision,
            fingerprint="",
        )
        fingerprint = hashlib.sha256(
            json.dumps(candidate._fingerprint_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest()
        candidate = ResearchCertificationLedgerEntry(**{**candidate.__dict__, "fingerprint": fingerprint})

        for existing in self._entries:
            if existing.run_id != candidate.run_id:
                continue
            if existing == candidate:
                return existing
            raise ResearchCertificationLedgerError("conflicting research certification already recorded for run_id")

        self._entries.append(candidate)
        return candidate

    def entries(self) -> tuple[ResearchCertificationLedgerEntry, ...]:
        return tuple(self._entries)

    def assert_clean(self) -> None:
        for entry in self._entries:
            entry.validate()

    def as_dict(self) -> list[dict[str, object]]:
        return [entry.as_dict() for entry in self._entries]
