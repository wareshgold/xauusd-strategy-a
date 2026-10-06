from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .evidence import EvidenceBundle
from .runs import ResearchRunIdentity
from .snapshot import ReadinessSnapshot


class AuditBindingError(ValueError):
    """Raised when a research audit record has inconsistent provenance."""


@dataclass(frozen=True)
class ResearchAuditRecord:
    """Immutable provenance binding for one research result."""

    audit_revision: str
    run_id: str
    run_fingerprint: str
    snapshot_fingerprint: str
    strategy_id: str
    strategy_revision: str
    manifest_revision: str
    dataset_id: str
    dataset_role: str
    data_revision: str
    dataset_fingerprint: str
    execution_semantics: str
    evidence_id: str
    evidence_fingerprint: str
    fingerprint: str

    @staticmethod
    def _payload(values: dict[str, Any]) -> bytes:
        return json.dumps(
            values, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")

    def validate(self) -> None:
        payload = self.as_dict(include_fingerprint=False)
        expected = hashlib.sha256(self._payload(payload)).hexdigest()
        if self.fingerprint != expected:
            raise AuditBindingError("research audit fingerprint mismatch")

    def as_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        data = {
            "audit_revision": self.audit_revision,
            "run_id": self.run_id,
            "run_fingerprint": self.run_fingerprint,
            "snapshot_fingerprint": self.snapshot_fingerprint,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "manifest_revision": self.manifest_revision,
            "dataset_id": self.dataset_id,
            "dataset_role": self.dataset_role,
            "data_revision": self.data_revision,
            "dataset_fingerprint": self.dataset_fingerprint,
            "execution_semantics": self.execution_semantics,
            "evidence_id": self.evidence_id,
            "evidence_fingerprint": self.evidence_fingerprint,
        }
        if include_fingerprint:
            data["fingerprint"] = self.fingerprint
        return data


def bind_research_audit(
    run: ResearchRunIdentity,
    snapshot: ReadinessSnapshot,
    evidence: EvidenceBundle,
    *,
    audit_revision: str = "RESEARCH-AUDIT-1",
) -> ResearchAuditRecord:
    run.validate()
    snapshot.validate()
    evidence.validate()

    if run.strategy_id != snapshot.strategy_id:
        raise AuditBindingError("run strategy_id does not match readiness snapshot")
    if run.manifest_revision != snapshot.manifest_revision:
        raise AuditBindingError("run manifest_revision does not match readiness snapshot")
    if evidence.run_id != run.run_id:
        raise AuditBindingError("evidence run_id does not match research run")
    if evidence.run_fingerprint != run.fingerprint:
        raise AuditBindingError("evidence run_fingerprint does not match research run")

    record = ResearchAuditRecord(
        audit_revision=audit_revision,
        run_id=run.run_id,
        run_fingerprint=run.fingerprint,
        snapshot_fingerprint=snapshot.fingerprint,
        strategy_id=run.strategy_id,
        strategy_revision=run.strategy_revision,
        manifest_revision=run.manifest_revision,
        dataset_id=run.dataset_id,
        dataset_role=run.dataset_role,
        data_revision=run.data_revision,
        dataset_fingerprint=run.dataset_fingerprint,
        execution_semantics=run.execution_semantics.value,
        evidence_id=evidence.evidence_id,
        evidence_fingerprint=evidence.fingerprint,
        fingerprint="",
    )
    fingerprint = hashlib.sha256(
        record._payload(record.as_dict(include_fingerprint=False))
    ).hexdigest()
    return ResearchAuditRecord(
        **record.as_dict(include_fingerprint=False),
        fingerprint=fingerprint,
    )
