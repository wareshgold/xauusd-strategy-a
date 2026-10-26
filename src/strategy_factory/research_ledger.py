"""Append-only, hash-chained research experiment records.

This is a provenance/integrity ledger, not a strategy evaluator. It never
promotes a hypothesis to canonical geometry or authorizes production decisions.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
import json
import re
from typing import Iterable


ZERO_HASH = "0" * 64
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ExperimentStatus(str, Enum):
    PLANNED = "PLANNED"
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"
    BLOCKED = "BLOCKED"


class EvidenceStatus(str, Enum):
    EVIDENCE_INCOMPLETE = "EVIDENCE_INCOMPLETE"
    SYNTHETIC_ONLY = "SYNTHETIC_ONLY"
    DATA_ONLY = "DATA_ONLY"
    SOURCE_CITATION_RECORDED = "SOURCE_CITATION_RECORDED"
    SOURCE_REVIEW_REQUIRED = "SOURCE_REVIEW_REQUIRED"
    CONTRADICTED = "CONTRADICTED"


@dataclass(frozen=True)
class ExperimentRecord:
    record_id: str
    sequence: int
    experiment_key: str
    hypothesis_id: str
    hypothesis_version: str
    input_sha256: str
    code_sha256: str
    status: ExperimentStatus
    evidence_status: EvidenceStatus
    result_summary: str
    evidence_refs: tuple[str, ...]
    counterexample_refs: tuple[str, ...]
    prior_failure_refs: tuple[str, ...]
    previous_record_sha256: str
    record_sha256: str
    canonical_authorized: bool = False
    production_decision_authorized: bool = False


def _payload(record: ExperimentRecord) -> dict:
    payload = asdict(record)
    payload.pop("record_sha256")
    payload.pop("canonical_authorized")
    payload.pop("production_decision_authorized")
    payload["status"] = record.status.value
    payload["evidence_status"] = record.evidence_status.value
    for key in ("evidence_refs", "counterexample_refs", "prior_failure_refs"):
        payload[key] = list(payload[key])
    return payload


def calculate_record_sha256(record: ExperimentRecord) -> str:
    canonical = json.dumps(_payload(record), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_record(record: ExperimentRecord) -> None:
    if not record.record_id.strip() or not record.experiment_key.strip():
        raise ValueError("record_id and experiment_key are required")
    if not record.hypothesis_id.strip() or not record.hypothesis_version.strip():
        raise ValueError("hypothesis_id and hypothesis_version are required")
    if record.sequence < 1:
        raise ValueError("sequence must be positive")
    for name in ("input_sha256", "code_sha256", "previous_record_sha256", "record_sha256"):
        value = getattr(record, name)
        if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
            raise ValueError(f"{name} must be a lowercase 64-character SHA-256 digest")
    if not record.result_summary.strip():
        raise ValueError("result_summary is required, including for failed or blocked runs")
    if len(set(record.evidence_refs)) != len(record.evidence_refs):
        raise ValueError("evidence_refs cannot contain duplicates")
    if len(set(record.counterexample_refs)) != len(record.counterexample_refs):
        raise ValueError("counterexample_refs cannot contain duplicates")
    if len(set(record.prior_failure_refs)) != len(record.prior_failure_refs):
        raise ValueError("prior_failure_refs cannot contain duplicates")
    if any(not ref.strip() for ref in record.evidence_refs + record.counterexample_refs + record.prior_failure_refs):
        raise ValueError("references cannot be empty")
    if record.canonical_authorized or record.production_decision_authorized:
        raise ValueError("research ledger records cannot authorize canonical or production decisions")
    if calculate_record_sha256(record) != record.record_sha256:
        raise ValueError("record_sha256 does not match canonical record payload")


def create_record(
    *,
    record_id: str,
    sequence: int,
    experiment_key: str,
    hypothesis_id: str,
    hypothesis_version: str,
    input_sha256: str,
    code_sha256: str,
    status: ExperimentStatus,
    evidence_status: EvidenceStatus,
    result_summary: str,
    evidence_refs: tuple[str, ...] = (),
    counterexample_refs: tuple[str, ...] = (),
    prior_failure_refs: tuple[str, ...] = (),
    previous_record_sha256: str = ZERO_HASH,
) -> ExperimentRecord:
    """Build a record with a deterministic content hash; no clock/random IDs."""
    record = ExperimentRecord(
        record_id=record_id,
        sequence=sequence,
        experiment_key=experiment_key,
        hypothesis_id=hypothesis_id,
        hypothesis_version=hypothesis_version,
        input_sha256=input_sha256,
        code_sha256=code_sha256,
        status=status,
        evidence_status=evidence_status,
        result_summary=result_summary,
        evidence_refs=tuple(evidence_refs),
        counterexample_refs=tuple(counterexample_refs),
        prior_failure_refs=tuple(prior_failure_refs),
        previous_record_sha256=previous_record_sha256,
        record_sha256=ZERO_HASH,
    )
    record = ExperimentRecord(**{**asdict(record), "status": status, "evidence_status": evidence_status,
                                 "record_sha256": calculate_record_sha256(record)})
    validate_record(record)
    return record


def verify_ledger(
    records: Iterable[ExperimentRecord],
    *,
    expected_tip_sha256: str | None = None,
    expected_record_count: int | None = None,
) -> str:
    """Verify chain order and prior-failure references; return verified tip.

    A caller must pin expected_tip_sha256 and/or expected_record_count outside
    the ledger to detect truncation of a valid suffix. Internal chain validity
    alone cannot prove that no later record was omitted.
    """
    rows = tuple(records)
    if expected_record_count is not None and len(rows) != expected_record_count:
        raise ValueError("ledger record count differs from pinned count")
    seen_ids: set[str] = set()
    prior_by_id: dict[str, ExperimentRecord] = {}
    previous_hash = ZERO_HASH
    for expected_sequence, record in enumerate(rows, start=1):
        validate_record(record)
        if record.sequence != expected_sequence:
            raise ValueError("ledger sequence must be contiguous and ordered")
        if record.record_id in seen_ids:
            raise ValueError("duplicate record_id")
        if record.previous_record_sha256 != previous_hash:
            raise ValueError("previous_record_sha256 breaks the append-only chain")
        for ref in record.prior_failure_refs:
            prior = prior_by_id.get(ref)
            if prior is None:
                raise ValueError("prior_failure_refs must refer to an earlier record")
            if prior.status not in (ExperimentStatus.FAIL, ExperimentStatus.INCONCLUSIVE, ExperimentStatus.BLOCKED):
                raise ValueError("prior_failure_refs must identify a prior non-success record")
        seen_ids.add(record.record_id)
        prior_by_id[record.record_id] = record
        previous_hash = record.record_sha256
    if expected_tip_sha256 is not None:
        if not _SHA256_RE.fullmatch(expected_tip_sha256):
            raise ValueError("expected_tip_sha256 must be a lowercase SHA-256 digest")
        if previous_hash != expected_tip_sha256:
            raise ValueError("ledger tip differs from pinned tip")
    return previous_hash
