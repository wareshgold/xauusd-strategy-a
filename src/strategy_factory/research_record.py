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
    dataset_content_sha256: str | None = None
    dataset_artifact_id: str | None = None
    dataset_byte_size: int | None = None
    execution_receipt_fingerprint: str | None = None
    dataset_binding_fingerprint: str | None = None
    output_artifact_id: str | None = None
    output_artifact_role: str | None = None
    output_artifact_path: str | None = None
    output_artifact_sha256: str | None = None
    output_artifact_byte_size: int | None = None
    output_artifact_binding_fingerprint: str | None = None

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
        if self.record_revision == "RESEARCH-RECORD-2":
            data.update({
                "dataset_content_sha256": self.dataset_content_sha256,
                "dataset_artifact_id": self.dataset_artifact_id,
                "dataset_byte_size": self.dataset_byte_size,
                "execution_receipt_fingerprint": self.execution_receipt_fingerprint,
                "dataset_binding_fingerprint": self.dataset_binding_fingerprint,
            })
            if self.output_artifact_id is not None:
                data.update({
                    "output_artifact_id": self.output_artifact_id,
                    "output_artifact_role": self.output_artifact_role,
                    "output_artifact_path": self.output_artifact_path,
                    "output_artifact_sha256": self.output_artifact_sha256,
                    "output_artifact_byte_size": self.output_artifact_byte_size,
                    "output_artifact_binding_fingerprint": self.output_artifact_binding_fingerprint,
                })
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
        if self.record_revision == "RESEARCH-RECORD-2":
            required = (
                self.dataset_content_sha256,
                self.dataset_artifact_id,
                self.execution_receipt_fingerprint,
                self.dataset_binding_fingerprint,
            )
            if any(not value for value in required) or self.dataset_byte_size is None:
                raise ResearchRecordError("research record v2 dataset binding is incomplete")
            if (not isinstance(self.dataset_content_sha256, str) or
                    len(self.dataset_content_sha256) != 64 or
                    any(ch not in "0123456789abcdef" for ch in self.dataset_content_sha256)):
                raise ResearchRecordError("research record v2 dataset SHA-256 is invalid")
            if not isinstance(self.dataset_artifact_id, str) or not self.dataset_artifact_id:
                raise ResearchRecordError("research record v2 DatasetArtifact ID is invalid")
            if (isinstance(self.dataset_byte_size, bool) or
                    not isinstance(self.dataset_byte_size, int) or self.dataset_byte_size < 0):
                raise ResearchRecordError("research record v2 dataset byte size is invalid")
            for value in (self.execution_receipt_fingerprint, self.dataset_binding_fingerprint):
                if (not isinstance(value, str) or len(value) != 64 or
                        any(ch not in "0123456789abcdef" for ch in value)):
                    raise ResearchRecordError("research record v2 binding fingerprint is invalid")
            binding_payload = {
                "binding_revision": "DATASET-BINDING-1",
                "dataset_id": self.dataset_id,
                "dataset_role": self.dataset_role,
                "data_revision": self.data_revision,
                "dataset_fingerprint": self.dataset_fingerprint,
                "artifact_id": self.dataset_artifact_id,
                "content_sha256": self.dataset_content_sha256,
                "byte_size": self.dataset_byte_size,
            }
            expected_binding = hashlib.sha256(self._payload(binding_payload)).hexdigest()
            if self.dataset_binding_fingerprint != expected_binding:
                raise ResearchRecordError("dataset binding fingerprint mismatch")
            output_values = (
                self.output_artifact_id, self.output_artifact_role, self.output_artifact_path,
                self.output_artifact_sha256, self.output_artifact_byte_size,
                self.output_artifact_binding_fingerprint,
            )
            if any(value is not None for value in output_values):
                if any(value is None for value in output_values):
                    raise ResearchRecordError("research record output artifact binding is incomplete")
                if not all(isinstance(value, str) and value for value in output_values[:3]):
                    raise ResearchRecordError("research record output artifact identity is invalid")
                if (not isinstance(self.output_artifact_sha256, str) or
                        len(self.output_artifact_sha256) != 64 or
                        any(ch not in "0123456789abcdef" for ch in self.output_artifact_sha256)):
                    raise ResearchRecordError("research record output artifact SHA-256 is invalid")
                if (isinstance(self.output_artifact_byte_size, bool) or
                        not isinstance(self.output_artifact_byte_size, int) or self.output_artifact_byte_size < 0):
                    raise ResearchRecordError("research record output artifact byte size is invalid")
                if (not isinstance(self.output_artifact_binding_fingerprint, str) or
                        len(self.output_artifact_binding_fingerprint) != 64 or
                        any(ch not in "0123456789abcdef" for ch in self.output_artifact_binding_fingerprint)):
                    raise ResearchRecordError("research record output artifact binding fingerprint is invalid")
                output_payload = {
                    "binding_revision": "OUTPUT-ARTIFACT-BINDING-1",
                    "artifact_id": self.output_artifact_id,
                    "artifact_role": self.output_artifact_role,
                    "local_path": self.output_artifact_path,
                    "content_sha256": self.output_artifact_sha256,
                    "byte_size": self.output_artifact_byte_size,
                    "dataset_binding_fingerprint": self.dataset_binding_fingerprint,
                }
                expected_output_binding = hashlib.sha256(self._payload(output_payload)).hexdigest()
                if self.output_artifact_binding_fingerprint != expected_output_binding:
                    raise ResearchRecordError("output artifact binding fingerprint mismatch")
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
        record_revision: str | None = None,
        receipt=None,
        observed_artifact=None,
        observed_content_sha256: str | None = None,
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

        binding_values = (receipt, observed_artifact, observed_content_sha256)
        if any(value is not None for value in binding_values) and not all(
            value is not None for value in binding_values
        ):
            raise ResearchRecordError("dataset binding requires receipt, observed artifact, and observed SHA")

        dataset_binding_fingerprint = None
        receipt_fingerprint = None
        artifact_id = None
        byte_size = None
        content_sha256 = None
        output_artifact = None
        output_artifact_binding_fingerprint = None
        if not all(value is not None for value in binding_values) and evidence.result.get("output_artifact") is not None:
            raise ResearchRecordError("output artifact requires a complete observed dataset binding")
        if all(value is not None for value in binding_values):
            from .datasets import DatasetArtifact
            from .execution import ExecutionReceipt
            if not isinstance(observed_artifact, DatasetArtifact):
                raise ResearchRecordError("dataset binding requires a registered DatasetArtifact")
            if not isinstance(receipt, ExecutionReceipt):
                raise ResearchRecordError("dataset binding requires an ExecutionReceipt")
            try:
                observed_artifact.validate()
                receipt.validate()
            except Exception as exc:
                raise ResearchRecordError("dataset binding inputs are invalid") from exc
            if run.artifact_id != observed_artifact.artifact_id:
                raise ResearchRecordError("dataset binding artifact does not match research run")
            if observed_artifact.content_sha256 != observed_content_sha256:
                raise ResearchRecordError("dataset binding SHA does not match observed artifact")
            if receipt.receipt_schema_version != 2 or receipt.dataset_content_sha256 != observed_content_sha256:
                raise ResearchRecordError("dataset binding receipt does not match observed SHA-256")
            if (receipt.strategy_revision != run.strategy_revision or
                    receipt.execution_semantics is not run.execution_semantics):
                raise ResearchRecordError("dataset binding receipt does not match research run")
            if evidence.result.get("execution_id") != receipt.execution_id:
                raise ResearchRecordError("dataset binding receipt does not match research evidence")
            if evidence.result.get("dataset_content_sha256") != observed_content_sha256:
                raise ResearchRecordError("dataset binding SHA does not match research evidence")
            if evidence.result.get("receipt_schema_version") != receipt.receipt_schema_version:
                raise ResearchRecordError("dataset binding receipt schema does not match research evidence")
            output_artifact = receipt.output_artifact
            evidence_output = evidence.result.get("output_artifact")
            if output_artifact is not None:
                output_payload = output_artifact.as_dict()
                if evidence_output != output_payload:
                    raise ResearchRecordError("output artifact receipt does not match research evidence")
                output_binding_payload = {
                    "binding_revision": "OUTPUT-ARTIFACT-BINDING-1",
                    "artifact_id": output_artifact.artifact_id,
                    "artifact_role": output_artifact.artifact_role,
                    "local_path": output_artifact.local_path,
                    "content_sha256": output_artifact.content_sha256,
                    "byte_size": output_artifact.byte_size,
                    "dataset_binding_fingerprint": dataset_binding_fingerprint,
                }
                output_artifact_binding_fingerprint = hashlib.sha256(
                    cls._payload(output_binding_payload)
                ).hexdigest()
            elif evidence_output is not None:
                raise ResearchRecordError("research evidence declares an unreceipted output artifact")
            artifact_id = observed_artifact.artifact_id
            byte_size = observed_artifact.byte_size
            content_sha256 = observed_content_sha256
            receipt_fingerprint = hashlib.sha256(
                cls._payload(receipt.as_dict())
            ).hexdigest()
            binding_payload = {
                "binding_revision": "DATASET-BINDING-1",
                "dataset_id": run.dataset_id,
                "dataset_role": run.dataset_role,
                "data_revision": run.data_revision,
                "dataset_fingerprint": run.dataset_fingerprint,
                "artifact_id": artifact_id,
                "content_sha256": content_sha256,
                "byte_size": byte_size,
            }
            dataset_binding_fingerprint = hashlib.sha256(
                cls._payload(binding_payload)
            ).hexdigest()

        if dataset_binding_fingerprint and record_revision not in (None, "RESEARCH-RECORD-2"):
            raise ResearchRecordError("dataset-bound records require RESEARCH-RECORD-2")
        if not dataset_binding_fingerprint and record_revision == "RESEARCH-RECORD-2":
            raise ResearchRecordError("RESEARCH-RECORD-2 requires a complete dataset binding")

        record = cls(
            record_revision=record_revision or ("RESEARCH-RECORD-2" if dataset_binding_fingerprint else "RESEARCH-RECORD-1"),
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
            dataset_content_sha256=content_sha256,
            dataset_artifact_id=artifact_id,
            dataset_byte_size=byte_size,
            execution_receipt_fingerprint=receipt_fingerprint,
            dataset_binding_fingerprint=dataset_binding_fingerprint,
            output_artifact_id=output_artifact.artifact_id if output_artifact is not None else None,
            output_artifact_role=output_artifact.artifact_role if output_artifact is not None else None,
            output_artifact_path=output_artifact.local_path if output_artifact is not None else None,
            output_artifact_sha256=output_artifact.content_sha256 if output_artifact is not None else None,
            output_artifact_byte_size=output_artifact.byte_size if output_artifact is not None else None,
            output_artifact_binding_fingerprint=output_artifact_binding_fingerprint,
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
