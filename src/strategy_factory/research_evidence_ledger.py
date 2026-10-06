from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .research_evidence_bundle import ResearchEvidenceBundle, ResearchEvidenceBundleError


class ResearchEvidenceLedgerError(ValueError):
    """Raised when a research evidence ledger entry is invalid or conflicting."""


@dataclass(frozen=True)
class ResearchEvidenceLedgerEntry:
    bundle_fingerprint: str
    run_id: str
    research_record_fingerprint: str
    dataset_id: str
    dataset_role: str
    strategy_id: str
    strategy_revision: str
    fingerprint: str

    @staticmethod
    def _payload(values: dict[str, object]) -> bytes:
        return json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

    def _fingerprint_payload(self) -> dict[str, object]:
        return {
            "bundle_fingerprint": self.bundle_fingerprint,
            "run_id": self.run_id,
            "research_record_fingerprint": self.research_record_fingerprint,
            "dataset_id": self.dataset_id,
            "dataset_role": self.dataset_role,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
        }

    def validate(self) -> None:
        if not self.bundle_fingerprint or not self.run_id or not self.research_record_fingerprint:
            raise ResearchEvidenceLedgerError("research evidence ledger identity is incomplete")
        expected = hashlib.sha256(self._payload(self._fingerprint_payload())).hexdigest()
        if self.fingerprint != expected:
            raise ResearchEvidenceLedgerError("research evidence ledger fingerprint mismatch")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {**self._fingerprint_payload(), "fingerprint": self.fingerprint}


class ResearchEvidenceLedger:
    """Append-only in-memory registry preventing conflicting evidence bindings."""

    def __init__(self) -> None:
        self._entries: list[ResearchEvidenceLedgerEntry] = []

    def record(self, bundle: ResearchEvidenceBundle) -> ResearchEvidenceLedgerEntry:
        try:
            bundle.validate()
        except ResearchEvidenceBundleError as exc:
            raise ResearchEvidenceLedgerError("invalid research evidence bundle") from exc
        candidate = ResearchEvidenceLedgerEntry(
            bundle_fingerprint=bundle.fingerprint,
            run_id=bundle.run_id,
            research_record_fingerprint=bundle.research_record_fingerprint,
            dataset_id=bundle.dataset_id,
            dataset_role=bundle.dataset_role,
            strategy_id=bundle.strategy_id,
            strategy_revision=bundle.strategy_revision,
            fingerprint="",
        )
        fingerprint = hashlib.sha256(candidate._payload(candidate._fingerprint_payload())).hexdigest()
        candidate = ResearchEvidenceLedgerEntry(**{**candidate.__dict__, "fingerprint": fingerprint})

        for existing in self._entries:
            if existing.run_id != candidate.run_id:
                continue
            if existing == candidate:
                return existing
            raise ResearchEvidenceLedgerError("conflicting research evidence already recorded for run_id")

        self._entries.append(candidate)
        return candidate

    def entries(self) -> tuple[ResearchEvidenceLedgerEntry, ...]:
        return tuple(self._entries)

    def assert_clean(self) -> None:
        for entry in self._entries:
            entry.validate()

    def as_dict(self) -> list[dict[str, object]]:
        return [entry.as_dict() for entry in self._entries]
