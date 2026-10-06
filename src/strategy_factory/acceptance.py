from __future__ import annotations

from .evidence import EvidenceBundle
from .execution import ExecutionReceipt, validate_execution_binding
from .models import GateResult, GateStatus
from .provenance import metrics_gate, provenance_gate
from .runs import ResearchRunError, ResearchRunIdentity
from .test_contract import HistoricalTestSpec


def validate_evidence_acceptance(
    *,
    spec: HistoricalTestSpec,
    run: ResearchRunIdentity,
    receipt: ExecutionReceipt,
    evidence: EvidenceBundle,
) -> None:
    """Require one evidence bundle to match its test, run, execution, and metrics."""
    spec.validate()
    run.validate()
    receipt.validate()
    evidence.validate()

    validate_execution_binding(spec=spec, run=run, receipt=receipt)

    if evidence.run_id != run.run_id:
        raise ResearchRunError("evidence run_id does not match registered research run")
    if evidence.run_fingerprint != run.fingerprint:
        raise ResearchRunError("evidence run fingerprint does not match research run")
    if receipt.metrics != evidence.metrics:
        raise ResearchRunError("execution receipt metrics do not match evidence metrics")


def evidence_acceptance_gate(
    *,
    spec: HistoricalTestSpec | None,
    run: ResearchRunIdentity | None,
    receipt: ExecutionReceipt | None,
    evidence: EvidenceBundle | None,
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
        },
    )
