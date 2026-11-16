"""Repeated-observation stability comparison for history evidence.

This module compares externally fingerprinted snapshots. It does not define a
row serialization/hash algorithm, call MT5, or infer archive completeness.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re

from scripts.sp2l_history_completeness_evidence_research import (
    HistoryCompletenessEvidence,
    HistoryEvidenceDisposition,
    classify_history_completeness_evidence,
)


class HistoryStabilityDisposition(str, Enum):
    INVALID_OBSERVATION = "invalid_observation"
    INSUFFICIENT_DISTINCT_OBSERVATIONS = "insufficient_distinct_observations"
    SCOPE_MISMATCH = "scope_mismatch"
    FINGERPRINT_METHOD_MISMATCH = "fingerprint_method_mismatch"
    CHANGED_BETWEEN_OBSERVATIONS = "changed_between_observations"
    STABLE_ACROSS_OBSERVATIONS = "stable_across_observations"


@dataclass(frozen=True)
class HistoryObservationFingerprint:
    observation_id: str
    evidence: HistoryCompletenessEvidence
    fingerprint_algorithm_id: str
    orders_payload_sha256: str
    deals_payload_sha256: str


_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_fingerprint(item: object) -> bool:
    if not isinstance(item, HistoryObservationFingerprint):
        return False
    return (
        _nonblank(item.observation_id)
        and _nonblank(item.fingerprint_algorithm_id)
        and isinstance(item.orders_payload_sha256, str)
        and bool(_SHA256_RE.fullmatch(item.orders_payload_sha256))
        and isinstance(item.deals_payload_sha256, str)
        and bool(_SHA256_RE.fullmatch(item.deals_payload_sha256))
    )


def _scope_key(evidence: HistoryCompletenessEvidence) -> tuple[object, ...]:
    scope = evidence.scope
    # Intentionally exclude observation timestamp and per-observation manifest
    # hash; retain every field defining account/session and query scope.
    return (
        scope.account_identity_verified,
        scope.account_identity_ref,
        scope.terminal_session_ref,
        scope.server_name,
        scope.date_from,
        scope.date_to,
        scope.time_basis,
        scope.time_basis_source,
        scope.package_version,
        scope.terminal_build,
    )


def compare_history_observation_stability(
    first: HistoryObservationFingerprint,
    second: HistoryObservationFingerprint,
) -> HistoryStabilityDisposition:
    """Compare two independently captured observations for one fixed scope.

    A stable result means only that the supplied fingerprints and counts match
    across two distinct observations. It is not a completeness attestation.
    """
    if not _valid_fingerprint(first) or not _valid_fingerprint(second):
        return HistoryStabilityDisposition.INVALID_OBSERVATION

    for item in (first, second):
        if not isinstance(item.evidence, HistoryCompletenessEvidence):
            return HistoryStabilityDisposition.INVALID_OBSERVATION
        if (
            classify_history_completeness_evidence(item.evidence)
            is not HistoryEvidenceDisposition.OBSERVED_CONSISTENT_FOR_SCOPE
        ):
            return HistoryStabilityDisposition.INVALID_OBSERVATION

    if first.observation_id == second.observation_id:
        return HistoryStabilityDisposition.INSUFFICIENT_DISTINCT_OBSERVATIONS
    if first.evidence.scope.observed_at == second.evidence.scope.observed_at:
        return HistoryStabilityDisposition.INSUFFICIENT_DISTINCT_OBSERVATIONS

    if _scope_key(first.evidence) != _scope_key(second.evidence):
        return HistoryStabilityDisposition.SCOPE_MISMATCH

    if first.fingerprint_algorithm_id != second.fingerprint_algorithm_id:
        return HistoryStabilityDisposition.FINGERPRINT_METHOD_MISMATCH

    first_counts = (
        first.evidence.orders.reported_total,
        first.evidence.deals.reported_total,
    )
    second_counts = (
        second.evidence.orders.reported_total,
        second.evidence.deals.reported_total,
    )
    first_hashes = (
        first.orders_payload_sha256.lower(),
        first.deals_payload_sha256.lower(),
    )
    second_hashes = (
        second.orders_payload_sha256.lower(),
        second.deals_payload_sha256.lower(),
    )

    if first_counts != second_counts or first_hashes != second_hashes:
        return HistoryStabilityDisposition.CHANGED_BETWEEN_OBSERVATIONS

    return HistoryStabilityDisposition.STABLE_ACROSS_OBSERVATIONS


def stability_proves_history_completeness(
    first: HistoryObservationFingerprint,
    second: HistoryObservationFingerprint,
) -> bool:
    """Repeated stability never proves absolute history completeness."""
    compare_history_observation_stability(first, second)
    return False
