from __future__ import annotations

from .evidence import EvidenceBundle
from .models import GateResult, GateStatus, Stage
from .runs import ResearchRunIdentity


def provenance_gate(
    *, run: ResearchRunIdentity | None, evidence: EvidenceBundle | None
) -> GateResult:
    if run is None or evidence is None:
        return GateResult(
            name="PROVENANCE",
            status=GateStatus.BLOCKED,
            evidence="Complete research-run and evidence provenance is required.",
            details={"run_present": run is not None, "evidence_present": evidence is not None},
        )
    try:
        run.validate()
        evidence.validate()
    except Exception as exc:
        return GateResult(
            name="PROVENANCE",
            status=GateStatus.BLOCKED,
            evidence="Research provenance is invalid.",
            details={"error": str(exc)},
        )
    if evidence.run_id != run.run_id or evidence.run_fingerprint != run.fingerprint:
        return GateResult(
            name="PROVENANCE",
            status=GateStatus.FAIL,
            evidence="Evidence does not match the identified research run.",
            details={
                "run_id": run.run_id,
                "evidence_run_id": evidence.run_id,
                "run_fingerprint": run.fingerprint,
                "evidence_run_fingerprint": evidence.run_fingerprint,
            },
        )
    return GateResult(
        name="PROVENANCE",
        status=GateStatus.PASS,
        evidence="Research result has complete and matching provenance.",
        details={"run_id": run.run_id, "evidence_id": evidence.evidence_id},
    )
