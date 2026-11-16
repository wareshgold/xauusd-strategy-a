"""Offline model for scoped MT5 history count/collection evidence.

This module consumes already captured observations. It does not call MT5,
validate broker archive completeness, or authorize recovery.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


class HistoryEvidenceQueryKind(str, Enum):
    ORDERS = "orders"
    DEALS = "deals"


class HistoryEvidenceDisposition(str, Enum):
    INVALID_SCOPE = "invalid_scope"
    QUERY_FAILED = "query_failed"
    COUNT_MISMATCH = "count_mismatch"
    OBSERVED_CONSISTENT_FOR_SCOPE = "observed_consistent_for_scope"
    COMPLETENESS_UNPROVEN = "completeness_unproven"


@dataclass(frozen=True)
class HistoryEvidenceScope:
    account_identity_verified: bool
    account_identity_ref: str
    terminal_session_ref: str
    server_name: str
    date_from: str
    date_to: str
    time_basis: str
    time_basis_source: str
    observed_at: str
    package_version: str
    terminal_build: str
    manifest_sha256: str


@dataclass(frozen=True)
class HistoryKindEvidence:
    """One query kind's independent total and collection observations.

    total_error/get_error are opaque source payloads. None means no captured
    error; a non-None value means that observation failed. A successful empty
    collection is represented by records=(), never records=None.
    """

    query_kind: HistoryEvidenceQueryKind
    reported_total: int | None
    records: tuple[object, ...] | None
    total_error: object | None = None
    get_error: object | None = None


@dataclass(frozen=True)
class HistoryCompletenessEvidence:
    scope: HistoryEvidenceScope
    orders: HistoryKindEvidence
    deals: HistoryKindEvidence


_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_scope(scope: object) -> bool:
    if not isinstance(scope, HistoryEvidenceScope):
        return False
    if scope.account_identity_verified is not True:
        return False
    required_text = (
        scope.account_identity_ref,
        scope.terminal_session_ref,
        scope.server_name,
        scope.date_from,
        scope.date_to,
        scope.time_basis,
        scope.time_basis_source,
        scope.observed_at,
        scope.package_version,
        scope.terminal_build,
    )
    if not all(_nonblank(value) for value in required_text):
        return False
    if scope.date_from == scope.date_to:
        return False
    return bool(
        isinstance(scope.manifest_sha256, str)
        and _SHA256_RE.fullmatch(scope.manifest_sha256)
    )


def _valid_kind(evidence: object, expected: HistoryEvidenceQueryKind) -> bool:
    if not isinstance(evidence, HistoryKindEvidence):
        return False
    if evidence.query_kind is not expected:
        return False
    if evidence.total_error is not None or evidence.get_error is not None:
        return False
    if isinstance(evidence.reported_total, bool) or not isinstance(
        evidence.reported_total, int
    ):
        return False
    if evidence.reported_total < 0:
        return False
    if not isinstance(evidence.records, tuple):
        return False
    return True


def classify_history_completeness_evidence(
    evidence: HistoryCompletenessEvidence,
) -> HistoryEvidenceDisposition:
    """Classify API observations without asserting absolute completeness."""
    if not isinstance(evidence, HistoryCompletenessEvidence):
        return HistoryEvidenceDisposition.INVALID_SCOPE
    if not _valid_scope(evidence.scope):
        return HistoryEvidenceDisposition.INVALID_SCOPE

    if not _valid_kind(evidence.orders, HistoryEvidenceQueryKind.ORDERS):
        return HistoryEvidenceDisposition.QUERY_FAILED
    if not _valid_kind(evidence.deals, HistoryEvidenceQueryKind.DEALS):
        return HistoryEvidenceDisposition.QUERY_FAILED

    if (
        evidence.orders.reported_total != len(evidence.orders.records)
        or evidence.deals.reported_total != len(evidence.deals.records)
    ):
        return HistoryEvidenceDisposition.COUNT_MISMATCH

    # Count agreement is only an API-level consistency observation for this
    # scope. It is deliberately not a completeness attestation.
    return HistoryEvidenceDisposition.OBSERVED_CONSISTENT_FOR_SCOPE


def history_completeness_is_proven(
    evidence: HistoryCompletenessEvidence,
) -> bool:
    """Absolute completeness remains unproven by this API-only model."""
    # Keep the evidence useful for diagnostics without allowing this model to
    # manufacture the independent assertion required by the recovery gate.
    classify_history_completeness_evidence(evidence)
    return False
