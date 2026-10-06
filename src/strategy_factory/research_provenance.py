from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .audit import ResearchAuditRecord
from .dataset_provenance import DatasetProvenanceResult, DatasetProvenanceStatus
from .evidence import EvidenceBundle
from .execution import ExecutionReceipt, validate_execution_binding
from .jobs import ResearchJobSpec, validate_job_matches_test_spec
from .runs import ResearchRunIdentity
from .snapshot import ReadinessSnapshot
from .test_contract import HistoricalTestSpec


class ResearchProvenanceStatus(str, Enum):
    PASS = "PASS"
    BLOCKED = "BLOCKED"
    FAIL = "FAIL"


@dataclass(frozen=True)
class ResearchProvenanceResult:
    """Immutable end-to-end provenance decision for one research result."""

    status: ResearchProvenanceStatus
    reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "reasons": list(self.reasons),
        }


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
            ("RUN_DATASET_FINGERPRINT", run.dataset_fingerprint == job.dataset_fingerprint),
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
        return ResearchProvenanceResult(status, tuple(reasons))

    return ResearchProvenanceResult(ResearchProvenanceStatus.PASS, ())
