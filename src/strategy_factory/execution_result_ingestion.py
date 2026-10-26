"""Controlled ingestion of explicitly captured experiment execution results.

This validates declared run metadata and hashes; it cannot authenticate the
runner, independently fetch artifacts, or claim a test ran unless a caller
supplies a captured execution report.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


from strategy_factory.research_ledger import (
    EvidenceStatus,
    ExperimentRecord,
    ExperimentStatus,
    create_record,
    validate_record,
)


@dataclass(frozen=True)
class CapturedExecution:
    run_id: str
    command: str
    exit_code: int
    output_sha256: str
    environment_sha256: str
    evidence_refs: tuple[str, ...]
    result_summary: str


def ingest_execution_result(
    *,
    plan_record: ExperimentRecord,
    captured: CapturedExecution,
    sequence: int,
    previous_record_sha256: str,
    prior_failure_refs: tuple[str, ...] = (),
    counterexample_refs: tuple[str, ...] = (),
) -> ExperimentRecord:
    """Append a result record linked to a PLANNED record; do not execute tests."""
    if plan_record.status is not ExperimentStatus.PLANNED:
        raise ValueError("execution result must reference a PLANNED record")
    validate_record(plan_record)
    if not captured.run_id.strip() or not captured.command.strip():
        raise ValueError("captured run_id and command are required")
    if sequence != plan_record.sequence + 1:
        raise ValueError("result sequence must immediately follow its plan in this single-record ingestion")
    if previous_record_sha256 != plan_record.record_sha256:
        raise ValueError("previous hash must link to the referenced plan")
    if not isinstance(captured.exit_code, int) or isinstance(captured.exit_code, bool):
        raise ValueError("captured exit_code must be an integer")
    for field_name in ("output_sha256", "environment_sha256"):
        value = getattr(captured, field_name)
        if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
            raise ValueError(f"{field_name} must be a lowercase 64-character SHA-256 digest")
    if not captured.result_summary.strip():
        raise ValueError("captured result summary is required")
    if not captured.evidence_refs or any(not ref.strip() for ref in captured.evidence_refs):
        raise ValueError("at least one non-empty captured evidence reference is required")
    if captured.exit_code == 0:
        status = ExperimentStatus.PASS
    else:
        status = ExperimentStatus.FAIL
    # create_record validates SHA-256 formatting and hashes all evidence references.
    refs = tuple(captured.evidence_refs) + (
        f"execution://{captured.run_id}",
        f"command://{captured.command}",
        f"exit-code://{captured.exit_code}",
        f"environment-sha256://{captured.environment_sha256}",
        f"output-sha256://{captured.output_sha256}",
        f"plan://{plan_record.record_id}",
    )
    if len(set(refs)) != len(refs):
        raise ValueError("captured evidence references collide with generated execution references")
    record = create_record(
        record_id=f"RESULT-{captured.run_id}",
        sequence=sequence,
        experiment_key=plan_record.experiment_key,
        hypothesis_id=plan_record.hypothesis_id,
        hypothesis_version=plan_record.hypothesis_version,
        input_sha256=plan_record.input_sha256,
        code_sha256=plan_record.code_sha256,
        status=status,
        evidence_status=EvidenceStatus.SYNTHETIC_ONLY,
        result_summary=(
            f"Captured execution metadata supplied by caller; not independently authenticated. "
            f"Run {captured.run_id}; exit code {captured.exit_code}. {captured.result_summary}"
        ),
        evidence_refs=refs,
        counterexample_refs=counterexample_refs,
        prior_failure_refs=prior_failure_refs,
        previous_record_sha256=previous_record_sha256,
    )
    return record
