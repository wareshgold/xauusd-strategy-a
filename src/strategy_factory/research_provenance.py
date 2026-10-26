from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from enum import Enum
from typing import Any

from .audit import ResearchAuditRecord
from .dataset_provenance import DatasetProvenanceResult, DatasetProvenanceStatus
from .evidence import EvidenceBundle
from .execution import ExecutionReceipt, validate_execution_binding
from .jobs import ResearchJobSpec, validate_job_matches_test_spec
from .runs import ResearchRunIdentity
from .snapshot import ReadinessSnapshot
from .test_contract import DatasetRole, ExecutionSemantics, HistoricalTestSpec, TestDataset


class ResearchProvenanceStatus(str, Enum):
    PASS = "PASS"
    BLOCKED = "BLOCKED"
    FAIL = "FAIL"


@dataclass(frozen=True)
class ResearchProvenanceResult:
    """Immutable end-to-end provenance decision for one research result."""

    status: ResearchProvenanceStatus
    reasons: tuple[str, ...]
    input_fingerprints: tuple[tuple[str, str], ...] = ()
    decision_fingerprint: str = ""

    @staticmethod
    def _decision_payload(
        status: ResearchProvenanceStatus,
        reasons: tuple[str, ...],
        input_fingerprints: tuple[tuple[str, str], ...],
    ) -> dict[str, Any]:
        return {
            "schema_revision": "RESEARCH-PROVENANCE-DECISION-1",
            "status": status.value,
            "reasons": list(reasons),
            "input_fingerprints": {key: value for key, value in input_fingerprints},
        }

    def validate(self) -> None:
        if self.status is ResearchProvenanceStatus.PASS and not self.input_fingerprints:
            raise ValueError("PASS provenance decision requires bound input fingerprints")
        expected = hashlib.sha256(json.dumps(
            self._decision_payload(self.status, self.reasons, self.input_fingerprints),
            sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        ).encode("utf-8")).hexdigest()
        if self.decision_fingerprint != expected:
            raise ValueError("provenance decision fingerprint mismatch")

    def as_dict(self) -> dict[str, Any]:
        return self._decision_payload(self.status, self.reasons, self.input_fingerprints) | {
            "decision_fingerprint": self.decision_fingerprint,
        }


def _object_fingerprint(value: Any) -> str:
    payload = value.as_dict()
    return hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("utf-8")).hexdigest()


def _decision_result(
    status: ResearchProvenanceStatus,
    reasons: tuple[str, ...],
    *,
    inputs: dict[str, Any] | None = None,
) -> ResearchProvenanceResult:
    fingerprints: tuple[tuple[str, str], ...] = ()
    if inputs is not None:
        fingerprints = tuple(sorted(
            (name, _object_fingerprint(value)) for name, value in inputs.items()
        ))
    payload = ResearchProvenanceResult._decision_payload(status, reasons, fingerprints)
    digest = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("utf-8")).hexdigest()
    return ResearchProvenanceResult(status, reasons, fingerprints, digest)


def evaluate_research_provenance(
    *,
    spec: HistoricalTestSpec,
    job: ResearchJobSpec,
    run: ResearchRunIdentity,
    receipt: ExecutionReceipt,
    evidence: EvidenceBundle,
    audit: ResearchAuditRecord,
    snapshot: ReadinessSnapshot,
    dataset_provenance: DatasetProvenanceResult,
) -> ResearchProvenanceResult:
    """Require one exact provenance chain from TestSpec through Audit.

    PASS means identities bind together. It does not mean the strategy is
    profitable, canonical, or production-ready.

    BLOCKED is reserved for unavailable/unregistered dataset provenance.
    Contradictions or tampering in an otherwise present chain are FAIL.
    """
    reasons: list[str] = []

    if dataset_provenance.status is DatasetProvenanceStatus.BLOCKED:
        reasons.append("DATASET_PROVENANCE_BLOCKED")
    elif dataset_provenance.status is DatasetProvenanceStatus.FAIL:
        reasons.append("DATASET_PROVENANCE_FAIL")

    try:
        spec.validate()
        job.validate()
        validate_job_matches_test_spec(
            job,
            spec,
            dataset_fingerprint=job.dataset_fingerprint,
        )
    except Exception as exc:
        reasons.append(f"JOB_SPEC_MISMATCH:{exc}")

    try:
        run.validate()
    except Exception as exc:
        reasons.append(f"RUN_INVALID:{exc}")
    else:
        checks = (
            ("RUN_JOB_ID", run.run_id == job.job_id),
            ("RUN_STRATEGY_ID", run.strategy_id == job.strategy_id),
            ("RUN_STRATEGY_REVISION", run.strategy_revision == job.strategy_revision),
            ("RUN_MANIFEST_REVISION", run.manifest_revision == job.manifest_revision),
            ("RUN_DATASET_ID", run.dataset_id == job.dataset_id),
            ("RUN_DATA_REVISION", run.data_revision == job.data_revision),
            (
                "RUN_DATASET_FINGERPRINT",
                run.dataset_fingerprint == dataset_provenance.registered_fingerprint,
            ),
            ("RUN_EXECUTION_SEMANTICS", run.execution_semantics is job.execution_semantics),
        )
        reasons.extend(name for name, ok in checks if not ok)

    try:
        validate_execution_binding(spec=spec, run=run, receipt=receipt)
    except Exception as exc:
        reasons.append(f"EXECUTION_BINDING:{exc}")

    try:
        evidence.validate()
        evidence_checks = (
            ("EVIDENCE_RUN_ID", evidence.run_id == run.run_id),
            ("EVIDENCE_RUN_FINGERPRINT", evidence.run_fingerprint == run.fingerprint),
            ("EVIDENCE_METRICS", evidence.metrics == receipt.metrics),
        )
        reasons.extend(name for name, ok in evidence_checks if not ok)
    except Exception as exc:
        reasons.append(f"EVIDENCE_INVALID:{exc}")

    try:
        snapshot.validate()
        snapshot_checks = (
            ("SNAPSHOT_STRATEGY_ID", snapshot.strategy_id == run.strategy_id),
            ("SNAPSHOT_MANIFEST_REVISION", snapshot.manifest_revision == run.manifest_revision),
        )
        reasons.extend(name for name, ok in snapshot_checks if not ok)
    except Exception as exc:
        reasons.append(f"SNAPSHOT_INVALID:{exc}")

    # Compare the audit's bound fields before validating its own fingerprint.
    # This preserves the most useful provenance diagnosis when a single audit
    # field is tampered with: identity mismatch is FAIL, while an internally
    # corrupted audit record remains AUDIT_INVALID.
    audit_checks = (
        ("AUDIT_RUN_ID", audit.run_id == run.run_id),
        ("AUDIT_RUN_FINGERPRINT", audit.run_fingerprint == run.fingerprint),
        ("AUDIT_SNAPSHOT_FINGERPRINT", audit.snapshot_fingerprint == snapshot.fingerprint),
        ("AUDIT_STRATEGY_ID", audit.strategy_id == run.strategy_id),
        ("AUDIT_STRATEGY_REVISION", audit.strategy_revision == run.strategy_revision),
        ("AUDIT_MANIFEST_REVISION", audit.manifest_revision == run.manifest_revision),
        ("AUDIT_DATASET_ID", audit.dataset_id == run.dataset_id),
        ("AUDIT_DATASET_ROLE", audit.dataset_role == run.dataset_role),
        ("AUDIT_DATA_REVISION", audit.data_revision == run.data_revision),
        ("AUDIT_DATASET_FINGERPRINT", audit.dataset_fingerprint == run.dataset_fingerprint),
        ("AUDIT_EXECUTION_SEMANTICS", audit.execution_semantics == run.execution_semantics.value),
        ("AUDIT_EVIDENCE_ID", audit.evidence_id == evidence.evidence_id),
        ("AUDIT_EVIDENCE_FINGERPRINT", audit.evidence_fingerprint == evidence.fingerprint),
    )
    reasons.extend(name for name, ok in audit_checks if not ok)
    try:
        audit.validate()
    except Exception as exc:
        if not any(reason.startswith("AUDIT_") for reason in reasons):
            reasons.append(f"AUDIT_INVALID:{exc}")

    if reasons:
        status = (
            ResearchProvenanceStatus.BLOCKED
            if "DATASET_PROVENANCE_BLOCKED" in reasons
            else ResearchProvenanceStatus.FAIL
        )
        return _decision_result(status, tuple(reasons))

    return _decision_result(
        ResearchProvenanceStatus.PASS,
        (),
        inputs={
            "test_spec": spec,
            "research_job": job,
            "research_run": run,
            "execution_receipt": receipt,
            "evidence_bundle": evidence,
            "research_audit": audit,
            "readiness_snapshot": snapshot,
            "dataset_provenance": dataset_provenance,
        },
    )


def serialize_research_provenance_decision(result: ResearchProvenanceResult) -> bytes:
    """Return canonical UTF-8 bytes for a validated provenance decision.

    This binds serialized bytes to the declared decision fingerprint. It does
    not authenticate the issuer or independently replay the upstream chain.
    """
    result.validate()
    return json.dumps(
        result.as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("utf-8")


_PROVENANCE_INPUT_TYPES = {
    "test_spec": HistoricalTestSpec,
    "research_job": ResearchJobSpec,
    "research_run": ResearchRunIdentity,
    "execution_receipt": ExecutionReceipt,
    "evidence_bundle": EvidenceBundle,
    "research_audit": ResearchAuditRecord,
    "readiness_snapshot": ReadinessSnapshot,
    "dataset_provenance": DatasetProvenanceResult,
}


def serialize_provenance_input_artifact(
    role: str, value: object, *, schema_revision: str
) -> bytes:
    """Serialize one allowlisted provenance input as canonical JSON bytes.

    Schema revision is mandatory and caller/owner-declared; this helper does
    not infer or certify a schema revision. It provides no deserializer and
    does not authenticate the caller, evaluator, or archive.
    """
    expected_type = _PROVENANCE_INPUT_TYPES.get(role)
    if expected_type is None:
        raise ValueError(f"unsupported provenance input role: {role}")
    if type(value) is not expected_type:
        raise TypeError(f"role {role!r} requires {expected_type.__name__}")
    if not isinstance(schema_revision, str) or not schema_revision.strip():
        raise ValueError("explicit schema_revision is required")
    validate = getattr(value, "validate", None)
    if callable(validate):
        validate()
    as_dict = getattr(value, "as_dict", None)
    if not callable(as_dict):
        raise TypeError(f"{expected_type.__name__} has no as_dict contract")
    payload = as_dict()
    if not isinstance(payload, dict):
        raise TypeError("provenance as_dict() must return a dictionary")
    envelope = {
        "artifact_role": role,
        "schema_revision": schema_revision,
        "payload": payload,
    }
    try:
        return json.dumps(
            envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("provenance input is not canonical-JSON serializable") from exc


PROVENANCE_INPUT_SCHEMA_REVISIONS = {
    "test_spec": "HISTORICAL-TEST-SPEC-1",
    "research_job": "RESEARCH-JOB-SPEC-1",
    "research_run": "RESEARCH-RUN-IDENTITY-1",
}


def deserialize_provenance_input_artifact(
    data: bytes, *, expected_role: str, expected_schema_revision: str
) -> object:
    """Reconstruct the first explicitly versioned provenance input contract.

    Only roles with an implemented versioned decoder are accepted. This decoder
    validates the envelope, role, schema revision, exact payload keys, enum
    values, and the reconstructed object. It is not an authenticated archive.
    """
    if not isinstance(data, bytes):
        raise TypeError("artifact data must be bytes")
    if expected_role not in PROVENANCE_INPUT_SCHEMA_REVISIONS:
        raise ValueError(f"no versioned decoder for provenance role: {expected_role}")
    if not expected_schema_revision or expected_schema_revision != PROVENANCE_INPUT_SCHEMA_REVISIONS[expected_role]:
        raise ValueError("expected schema revision does not match the implemented decoder")
    try:
        envelope = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("artifact is not valid UTF-8 JSON") from exc
    if not isinstance(envelope, dict) or set(envelope) != {
        "artifact_role", "schema_revision", "payload"
    }:
        raise ValueError("provenance artifact envelope keys are invalid")
    if envelope["artifact_role"] != expected_role:
        raise ValueError("provenance artifact role mismatch")
    if envelope["schema_revision"] != expected_schema_revision:
        raise ValueError("provenance artifact schema revision mismatch")
    payload = envelope["payload"]
    if not isinstance(payload, dict):
        raise ValueError("provenance artifact payload must be an object")
    if expected_role == "research_run":
        required = {"run_id", "strategy_id", "strategy_revision", "manifest_revision", "dataset_id", "dataset_role", "data_revision", "dataset_fingerprint", "artifact_id", "execution_semantics", "parameters", "objective", "purpose"}
        if set(payload) != required:
            raise ValueError("research run payload keys are invalid")
        if not isinstance(payload["parameters"], dict):
            raise ValueError("research run parameters must be an object")
        if payload["artifact_id"] is not None and not isinstance(payload["artifact_id"], str):
            raise ValueError("research run artifact_id must be a string or null")
        try:
            run = ResearchRunIdentity(run_id=payload["run_id"], strategy_id=payload["strategy_id"], strategy_revision=payload["strategy_revision"], manifest_revision=payload["manifest_revision"], dataset_id=payload["dataset_id"], dataset_role=payload["dataset_role"], data_revision=payload["data_revision"], dataset_fingerprint=payload["dataset_fingerprint"], artifact_id=payload["artifact_id"], execution_semantics=ExecutionSemantics(payload["execution_semantics"]), parameters=payload["parameters"], objective=payload["objective"], purpose=payload["purpose"])
            run.validate()
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("research run artifact failed contract validation") from exc
        if serialize_provenance_input_artifact("research_run", run, schema_revision=expected_schema_revision) != data:
            raise ValueError("research run artifact is not canonical JSON")
        return run
    if expected_role == "research_job":
        required = {
            "job_id", "strategy_id", "strategy_revision", "manifest_revision",
            "test_id", "dataset_id", "data_revision", "dataset_fingerprint",
            "execution_semantics", "parameters", "objective",
        }
        if set(payload) != required:
            raise ValueError("research job payload keys are invalid")
        if not isinstance(payload["parameters"], dict):
            raise ValueError("research job parameters must be an object")
        try:
            job = ResearchJobSpec(
                job_id=payload["job_id"],
                strategy_id=payload["strategy_id"],
                strategy_revision=payload["strategy_revision"],
                manifest_revision=payload["manifest_revision"],
                test_id=payload["test_id"],
                dataset_id=payload["dataset_id"],
                data_revision=payload["data_revision"],
                dataset_fingerprint=payload["dataset_fingerprint"],
                execution_semantics=ExecutionSemantics(payload["execution_semantics"]),
                parameters=payload["parameters"],
                objective=payload["objective"],
            )
            job.validate()
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("research job artifact failed contract validation") from exc
        if serialize_provenance_input_artifact(
            "research_job", job, schema_revision=expected_schema_revision
        ) != data:
            raise ValueError("research job artifact is not canonical JSON")
        return job
    if expected_role == "test_spec":
        required = {
            "test_id", "strategy_id", "strategy_revision", "dataset",
            "execution_semantics", "parameters", "objective",
        }
        if set(payload) != required:
            raise ValueError("test spec payload keys are invalid")
        dataset = payload["dataset"]
        if not isinstance(dataset, dict) or set(dataset) != {
            "dataset_id", "role", "data_revision", "start", "end", "source", "immutable"
        }:
            raise ValueError("test spec dataset keys are invalid")
        if not isinstance(payload["parameters"], dict):
            raise ValueError("test spec parameters must be an object")
        if not isinstance(dataset["immutable"], bool):
            raise ValueError("test spec dataset immutable must be boolean")
        try:
            spec = HistoricalTestSpec(
                test_id=payload["test_id"],
                strategy_id=payload["strategy_id"],
                strategy_revision=payload["strategy_revision"],
                dataset=TestDataset(
                    dataset_id=dataset["dataset_id"],
                    role=DatasetRole(dataset["role"]),
                    data_revision=dataset["data_revision"],
                    start=dataset["start"],
                    end=dataset["end"],
                    source=dataset["source"],
                    immutable=dataset["immutable"],
                ),
                execution_semantics=ExecutionSemantics(payload["execution_semantics"]),
                parameters=payload["parameters"],
                objective=payload["objective"],
            )
            spec.validate()
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("test spec artifact failed contract validation") from exc
        if serialize_provenance_input_artifact(
            "test_spec", spec, schema_revision=expected_schema_revision
        ) != data:
            raise ValueError("test spec artifact is not canonical JSON")
        return spec
    raise ValueError(f"no versioned decoder for provenance role: {expected_role}")
