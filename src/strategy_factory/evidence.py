from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping

from .metrics import ResearchMetrics
from .runs import ResearchRunError, ResearchRunIdentity


def _canonical(value: Mapping[str, Any]) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as exc:
        raise ResearchRunError("evidence payload must be JSON-serializable") from exc


@dataclass(frozen=True)
class EvidenceBundle:
    """Research result tied immutably to one fully identified research run."""

    evidence_id: str
    run_id: str
    run_fingerprint: str
    result_revision: str
    metrics: ResearchMetrics
    result: Mapping[str, Any]

    def validate(self) -> None:
        if not self.evidence_id or not self.run_id or not self.run_fingerprint or not self.result_revision:
            raise ResearchRunError("evidence provenance is incomplete")
        if len(self.run_fingerprint) != 64:
            raise ResearchRunError("run_fingerprint must be a SHA-256 hex digest")
        self.metrics.validate()
        _canonical(self.result)

    @property
    def fingerprint(self) -> str:
        self.validate()
        payload = self.as_dict()
        return hashlib.sha256(_canonical(payload).encode()).hexdigest()

    def as_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "run_id": self.run_id,
            "run_fingerprint": self.run_fingerprint,
            "result_revision": self.result_revision,
            "metrics": self.metrics.as_dict(),
            "result": dict(self.result),
        }


class EvidenceLedger:
    """Immutable attachment ledger: evidence must match a registered run exactly."""

    def __init__(self, runs: "ResearchRunLedger") -> None:
        self.runs = runs
        self._records: dict[str, EvidenceBundle] = {}

    def record(self, evidence: EvidenceBundle) -> EvidenceBundle:
        evidence.validate()
        run = self.runs.get(evidence.run_id)
        if evidence.run_fingerprint != run.fingerprint:
            raise ResearchRunError("evidence run fingerprint does not match registered run")
        existing = self._records.get(evidence.evidence_id)
        if existing is not None and existing != evidence:
            raise ResearchRunError("evidence_id already exists with different evidence")
        if existing is not None:
            return existing
        self._records[evidence.evidence_id] = evidence
        return evidence

    def get(self, evidence_id: str) -> EvidenceBundle:
        try:
            return self._records[evidence_id]
        except KeyError as exc:
            raise ResearchRunError(f"evidence {evidence_id!r} is not registered") from exc

    def entries(self) -> tuple[EvidenceBundle, ...]:
        return tuple(self._records.values())

    def as_dict(self) -> list[dict[str, Any]]:
        return [
            entry.as_dict() | {"evidence_fingerprint": entry.fingerprint}
            for entry in self.entries()
        ]
