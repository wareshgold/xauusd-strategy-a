from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from typing import Any

from .audit import ResearchAuditRecord
from .evidence import EvidenceBundle
from .research_provenance import ResearchProvenanceResult, ResearchProvenanceStatus
from .runs import ResearchRunIdentity
from .snapshot import ReadinessSnapshot


class ResearchRecordError(ValueError):
    """Raised when an immutable research record is inconsistent."""


@dataclass(frozen=True)
class ResearchRecord:
    """Immutable, deterministic record of one accepted research result."""

    record_revision: str
    run_id: str
    run_fingerprint: str
    evidence_id: str
    evidence_fingerprint: str
    snapshot_fingerprint: str
    audit_fingerprint: str
    strategy_id: str
    strategy_revision: str
    manifest_revision: str
    dataset_id: str
    dataset_role: str
    data_revision: str
    dataset_fingerprint: str
    execution_semantics: str
    provenance_status: ResearchProvenanceStatus
    provenance_reasons: tuple[str, ...]
    fingerprint: str

    @staticmethod
    def _payload(values: dict[str, Any]) -> bytes:
        return json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

    def as_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        data = {
            "record_revision": self.record_revision,
            "run_id": self.run_id,
            "run_fingerprint": self.run_fingerprint,
            "evidence_id": self.evidence_id,
            "evidence_fingerprint": self.evidence_fingerprint,
            "snapshot_fingerprint": self.snapshot_fingerprint,
            "audit_fingerprint": self.audit_fingerprint,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "manifest_revision": self.manifest_revision,
            "dataset_id": self.dataset_id,
            "dataset_role": self.dataset_role,
            "data_revision": self.data_revision,
            "dataset_fingerprint": self.dataset_fingerprint,
            "execution_semantics": self.execution_semantics,
            "provenance_status": self.provenance_status.value,
            "provenance_reasons": list(self.provenance_reasons),
        }
        if include_fingerprint:
            data["fingerprint"] = self.fingerprint
        return data

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> "ResearchRecord":
        """Reconstruct and validate a record from its serialized representation."""
        try:
            data = dict(values)
            data["provenance_status"] = ResearchProvenanceStatus(data["provenance_status"])
            data["provenance_reasons"] = tuple(data["provenance_reasons"])
            record = cls(**data)
        except (KeyError, TypeError, ValueError) as exc:
            raise ResearchRecordError("invalid serialized research record") from exc
        record.validate()
        return record

    def validate(self) -> None:
        if not self.run_id or not self.strategy_id or not self.strategy_revision:
            raise ResearchRecordError("research record identity is incomplete")
        if not isinstance(self.provenance_status, ResearchProvenanceStatus):
            raise ResearchRecordError("research record provenance status must be explicit")
        if self.provenance_status.value != ResearchProvenanceStatus.PASS.value:
            raise ResearchRecordError("research record requires PASS provenance status")
        expected = hashlib.sha256(self._payload(self.as_dict(include_fingerprint=False))).hexdigest()
        if self.fingerprint != expected:
            raise ResearchRecordError("research record fingerprint mismatch")

    @classmethod
    def from_components(
        cls,
        run: ResearchRunIdentity,
        evidence: EvidenceBundle,
        snapshot: ReadinessSnapshot,
        audit: ResearchAuditRecord,
        provenance: ResearchProvenanceResult,
        *,
        record_revision: str = "RESEARCH-RECORD-1",
    ) -> "ResearchRecord":
        run.validate()
        evidence.validate()
        snapshot.validate()
        audit.validate()
        if provenance.status.value != ResearchProvenanceStatus.PASS.value:
            raise ResearchRecordError("cannot record non-PASS provenance")
        if evidence.run_id != run.run_id or evidence.run_fingerprint != run.fingerprint:
            raise ResearchRecordError("evidence is not bound to research run")
        if audit.run_fingerprint != run.fingerprint:
            raise ResearchRecordError("audit is not bound to research run")
        if audit.snapshot_fingerprint != snapshot.fingerprint:
            raise ResearchRecordError("audit is not bound to readiness snapshot")
        if audit.evidence_fingerprint != evidence.fingerprint:
            raise ResearchRecordError("audit is not bound to evidence")

        record = cls(
            record_revision=record_revision,
            run_id=run.run_id,
            run_fingerprint=run.fingerprint,
            evidence_id=evidence.evidence_id,
            evidence_fingerprint=evidence.fingerprint,
            snapshot_fingerprint=snapshot.fingerprint,
            audit_fingerprint=audit.fingerprint,
            strategy_id=run.strategy_id,
            strategy_revision=run.strategy_revision,
            manifest_revision=run.manifest_revision,
            dataset_id=run.dataset_id,
            dataset_role=run.dataset_role,
            data_revision=run.data_revision,
            dataset_fingerprint=run.dataset_fingerprint,
            execution_semantics=run.execution_semantics.value,
            provenance_status=provenance.status,
            provenance_reasons=provenance.reasons,
            fingerprint="",
        )
        fingerprint = hashlib.sha256(record._payload(record.as_dict(include_fingerprint=False))).hexdigest()
        final = replace(record, fingerprint=fingerprint)
        final.validate()
        return final


class ResearchRecordLedger:
    """Append-only in-memory registry for immutable research records."""

    def __init__(self) -> None:
        self._records: dict[str, ResearchRecord] = {}

    def record(self, record: ResearchRecord) -> ResearchRecord:
        existing = self._records.get(record.run_id)
        if existing is not None and existing != record:
            raise ResearchRecordError("run_id already exists with a different immutable research record")
        record.validate()
        if existing is not None:
            return existing
        self._records[record.run_id] = record
        return record

    def get(self, run_id: str) -> ResearchRecord:
        try:
            return self._records[run_id]
        except KeyError as exc:
            raise ResearchRecordError(f"research record {run_id!r} is not registered") from exc

    def entries(self) -> tuple[ResearchRecord, ...]:
        return tuple(self._records.values())

    def as_dict(self) -> list[dict[str, Any]]:
        return [record.as_dict() for record in self.entries()]
