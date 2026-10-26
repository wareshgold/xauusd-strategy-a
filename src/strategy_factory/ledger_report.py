"""Read-only ledger verification report; never promotes evidence or authority."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from strategy_factory.research_ledger import (
    EvidenceStatus,
    ExperimentRecord,
    ExperimentStatus,
    verify_ledger,
)


@dataclass(frozen=True)
class LedgerReport:
    verified: bool
    record_count: int
    tip_sha256: str
    status_counts: tuple[tuple[str, int], ...]
    evidence_status_counts: tuple[tuple[str, int], ...]
    failure_record_ids: tuple[str, ...]
    inconclusive_record_ids: tuple[str, ...]
    blocked_record_ids: tuple[str, ...]
    planned_record_ids: tuple[str, ...]
    counterexample_refs: tuple[str, ...]
    missing_evidence_record_ids: tuple[str, ...]
    source_review_required_record_ids: tuple[str, ...]
    contradicted_record_ids: tuple[str, ...]
    canonical_authorized: bool = False
    production_decision_authorized: bool = False


def build_ledger_report(
    records: Iterable[ExperimentRecord],
    *,
    expected_tip_sha256: str,
    expected_record_count: int,
) -> LedgerReport:
    """Verify against externally pinned tip/count, then summarize without mutation."""
    rows = tuple(records)
    if expected_tip_sha256 is None or not expected_tip_sha256.strip():
        raise ValueError("an externally pinned expected_tip_sha256 is required")
    if expected_record_count is None:
        raise ValueError("an externally pinned expected_record_count is required")
    tip = verify_ledger(
        rows,
        expected_tip_sha256=expected_tip_sha256,
        expected_record_count=expected_record_count,
    )
    status_counts = Counter(row.status.value for row in rows)
    evidence_counts = Counter(row.evidence_status.value for row in rows)
    return LedgerReport(
        verified=True,
        record_count=len(rows),
        tip_sha256=tip,
        status_counts=tuple(sorted(status_counts.items())),
        evidence_status_counts=tuple(sorted(evidence_counts.items())),
        failure_record_ids=tuple(row.record_id for row in rows if row.status is ExperimentStatus.FAIL),
        inconclusive_record_ids=tuple(row.record_id for row in rows if row.status is ExperimentStatus.INCONCLUSIVE),
        blocked_record_ids=tuple(row.record_id for row in rows if row.status is ExperimentStatus.BLOCKED),
        planned_record_ids=tuple(row.record_id for row in rows if row.status is ExperimentStatus.PLANNED),
        counterexample_refs=tuple(ref for row in rows for ref in row.counterexample_refs),
        missing_evidence_record_ids=tuple(
            row.record_id for row in rows
            if row.evidence_status is EvidenceStatus.EVIDENCE_INCOMPLETE or not row.evidence_refs
        ),
        source_review_required_record_ids=tuple(
            row.record_id for row in rows
            if row.evidence_status is EvidenceStatus.SOURCE_REVIEW_REQUIRED
        ),
        contradicted_record_ids=tuple(
            row.record_id for row in rows if row.evidence_status is EvidenceStatus.CONTRADICTED
        ),
    )
