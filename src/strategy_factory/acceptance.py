from __future__ import annotations

from .dataset_provenance import DatasetProvenanceResult, DatasetProvenanceStatus
from .evidence import EvidenceBundle
from .execution import ExecutionReceipt, validate_execution_binding
from .models import GateResult, GateStatus
from .provenance import metrics_gate, provenance_gate
from .runs import ResearchRunError, ResearchRunIdentity
from .test_contract import DatasetRole, HistoricalTestSpec


def _validate_receipt_dataset_identity(
    *,
    spec: HistoricalTestSpec,
    receipt: ExecutionReceipt,
    dataset_provenance: DatasetProvenanceResult | None,
    adapter: object | None,
    purpose: str | None,
) -> None:
    if receipt.receipt_schema_version != 2:
        return

    if dataset_provenance is None or adapter is None or purpose is None:
        raise ResearchRunError(
            "schema-v2 acceptance requires independent dataset provenance, adapter identity, and purpose"
        )
    if dataset_provenance.status is not DatasetProvenanceStatus.PASS:
        raise ResearchRunError("dataset provenance is not PASS")
    if dataset_provenance.dataset_id != spec.dataset.dataset_id:
        raise ResearchRunError("dataset provenance dataset_id does not match test specification")

    from .synthetic import SyntheticExecutionAdapter

    if type(adapter) is SyntheticExecutionAdapter:
        if purpose != "SYNTHETIC_INFRASTRUCTURE_TEST":
            raise ResearchRunError("synthetic adapter requires SYNTHETIC_INFRASTRUCTURE_TEST purpose")
        if spec.dataset.role is not DatasetRole.DEVELOPMENT:
            raise ResearchRunError("synthetic adapter is restricted to DEVELOPMENT datasets")
        if receipt.dataset_content_sha256 is not None:
            raise ResearchRunError("trusted synthetic receipt must declare dataset_content_sha256 as null")
        return

    registered = dataset_provenance.registered_content_sha256
    observed = dataset_provenance.observed_content_sha256
    if not registered or not observed:
        raise ResearchRunError("dataset provenance is missing independent raw content SHA-256 values")
    if receipt.dataset_content_sha256 is None:
        raise ResearchRunError("dataset-backed schema-v2 receipt cannot have a null dataset_content_sha256")
    if receipt.dataset_content_sha256 != registered or receipt.dataset_content_sha256 != observed:
        raise ResearchRunError("execution receipt dataset_content_sha256 does not match registered and observed dataset bytes")


def validate_evidence_acceptance(
    *,
    spec: HistoricalTestSpec,
    run: ResearchRunIdentity,
    receipt: ExecutionReceipt,
    evidence: EvidenceBundle,
    dataset_provenance: DatasetProvenanceResult | None = None,
    adapter: object | None = None,
    purpose: str | None = None,
) -> None:
    """Require one evidence bundle to match its test, run, execution, and metrics."""
    spec.validate()
    run.validate()
    receipt.validate()
    evidence.validate()

    validate_execution_binding(spec=spec, run=run, receipt=receipt)
    _validate_receipt_dataset_identity(
        spec=spec,
        receipt=receipt,
        dataset_provenance=dataset_provenance,
        adapter=adapter,
        purpose=purpose,
    )

    if evidence.run_id != run.run_id:
        raise ResearchRunError("evidence run_id does not match registered research run")
    if evidence.run_fingerprint != run.fingerprint:
        raise ResearchRunError("evidence run fingerprint does not match research run")
    if receipt.metrics != evidence.metrics:
        raise ResearchRunError("execution receipt metrics do not match evidence metrics")
    if receipt.receipt_schema_version == 2:
        if evidence.result_revision != "RECEIPT_METRICS_V2":
            raise ResearchRunError("schema-v2 receipt requires RECEIPT_METRICS_V2 evidence")
        if evidence.result.get("receipt_schema_version") != 2:
            raise ResearchRunError("evidence receipt_schema_version does not match execution receipt")
        if "dataset_content_sha256" not in evidence.result:
            raise ResearchRunError("schema-v2 evidence is missing dataset_content_sha256")
        if evidence.result.get("dataset_content_sha256") != receipt.dataset_content_sha256:
            raise ResearchRunError("evidence dataset_content_sha256 does not match execution receipt")


def evidence_acceptance_gate(
    *,
    spec: HistoricalTestSpec | None,
    run: ResearchRunIdentity | None,
    receipt: ExecutionReceipt | None,
    evidence: EvidenceBundle | None,
    dataset_provenance: DatasetProvenanceResult | None = None,
    adapter: object | None = None,
    purpose: str | None = None,
) -> GateResult:
    """Accept evidence only when provenance, execution, and metrics all agree.

    This is a research-evidence acceptance boundary. It does not judge
    performance, optimize parameters, establish statistical significance, or
    authorize production decisions.
    """
    if any(value is None for value in (spec, run, receipt, evidence)):
        return GateResult(
            name="EVIDENCE_ACCEPTANCE",
            status=GateStatus.BLOCKED,
            evidence="Complete test, run, execution receipt, and evidence bundle are required.",
            details={
                "spec_present": spec is not None,
                "run_present": run is not None,
                "receipt_present": receipt is not None,
                "evidence_present": evidence is not None,
            },
        )

    provenance = provenance_gate(run=run, evidence=evidence)
    metrics = metrics_gate(evidence=evidence)
    if provenance.status is not GateStatus.PASS:
        return GateResult(
            name="EVIDENCE_ACCEPTANCE",
            status=provenance.status,
            evidence="Evidence provenance is not acceptable.",
            details={"failed_gate": "PROVENANCE", **provenance.details},
        )
    if metrics.status is not GateStatus.PASS:
        return GateResult(
            name="EVIDENCE_ACCEPTANCE",
            status=metrics.status,
            evidence="Evidence metrics are not acceptable.",
            details={"failed_gate": "METRICS_COMPLETENESS", **metrics.details},
        )

    try:
        validate_evidence_acceptance(
            spec=spec,
            run=run,
            receipt=receipt,
            evidence=evidence,
            dataset_provenance=dataset_provenance,
            adapter=adapter,
            purpose=purpose,
        )
    except (ResearchRunError, ValueError) as exc:
        return GateResult(
            name="EVIDENCE_ACCEPTANCE",
            status=GateStatus.FAIL,
            evidence="Evidence does not match its declared execution contract.",
            details={"error": str(exc)},
        )

    return GateResult(
        name="EVIDENCE_ACCEPTANCE",
        status=GateStatus.PASS,
        evidence="Evidence has matching provenance, execution semantics, and descriptive metrics.",
        details={
            "test_id": spec.test_id,
            "run_id": run.run_id,
            "execution_id": receipt.execution_id,
            "evidence_id": evidence.evidence_id,
            "execution_semantics": receipt.execution_semantics.value,
            "dataset_verified": receipt.receipt_schema_version == 2 and receipt.dataset_content_sha256 is not None,
        },
    )
