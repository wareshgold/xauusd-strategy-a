"""Offline linkage checks between a manifest record and history observations.

This validates declared metadata relationships only. It does not read artifacts,
verify hashes, authenticate provenance, or prove history completeness.
"""
from __future__ import annotations

from enum import Enum
import re

from scripts.sp2l_evidence_manifest_research import (
    EvidenceManifestRecord,
    validate_evidence_manifest,
    EvidenceManifestDisposition,
)
from scripts.sp2l_history_completeness_evidence_research import (
    HistoryEvidenceDisposition,
    classify_history_completeness_evidence,
)
from scripts.sp2l_history_stability_research import HistoryObservationFingerprint


class EvidenceManifestLinkageDisposition(str, Enum):
    INVALID_MANIFEST = "invalid_manifest"
    INVALID_OBSERVATION = "invalid_observation"
    OBSERVATION_NOT_LISTED = "observation_not_listed"
    SCOPE_MISMATCH = "scope_mismatch"
    LINKED_FOR_DECLARED_SCOPE = "linked_for_declared_scope"


_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _observation_is_valid(item: object) -> bool:
    if not isinstance(item, HistoryObservationFingerprint):
        return False
    if not isinstance(item.observation_id, str) or not item.observation_id.strip():
        return False
    if not isinstance(item.fingerprint_algorithm_id, str) or not item.fingerprint_algorithm_id.strip():
        return False
    if not isinstance(item.orders_payload_sha256, str) or not _SHA256_RE.fullmatch(item.orders_payload_sha256):
        return False
    if not isinstance(item.deals_payload_sha256, str) or not _SHA256_RE.fullmatch(item.deals_payload_sha256):
        return False
    return (
        classify_history_completeness_evidence(item.evidence)
        is HistoryEvidenceDisposition.OBSERVED_CONSISTENT_FOR_SCOPE
    )


def _scope_matches(manifest: EvidenceManifestRecord, observation: HistoryObservationFingerprint) -> bool:
    scope = observation.evidence.scope
    return (
        manifest.account_identity_ref == scope.account_identity_ref
        and manifest.terminal_session_ref == scope.terminal_session_ref
        and manifest.server_name == scope.server_name
        and manifest.date_from == scope.date_from
        and manifest.date_to == scope.date_to
        and manifest.time_basis == scope.time_basis
        and manifest.time_basis_source == scope.time_basis_source
        and manifest.package_version == scope.package_version
        and manifest.terminal_build == scope.terminal_build
    )


def link_manifest_to_history_observations(
    manifest: EvidenceManifestRecord,
    observations: tuple[HistoryObservationFingerprint, ...],
) -> EvidenceManifestLinkageDisposition:
    """Check that supplied observation IDs and declared scopes match a manifest."""
    if validate_evidence_manifest(manifest) is not EvidenceManifestDisposition.VALID_MANIFEST_RECORD:
        return EvidenceManifestLinkageDisposition.INVALID_MANIFEST
    if not isinstance(observations, tuple) or not observations:
        return EvidenceManifestLinkageDisposition.INVALID_OBSERVATION

    for observation in observations:
        if not _observation_is_valid(observation):
            return EvidenceManifestLinkageDisposition.INVALID_OBSERVATION
    if len({item.observation_id for item in observations}) != len(observations):
        return EvidenceManifestLinkageDisposition.INVALID_OBSERVATION

    listed = set(manifest.observation_ids)
    supplied = {item.observation_id for item in observations}
    if not supplied.issubset(listed):
        return EvidenceManifestLinkageDisposition.OBSERVATION_NOT_LISTED

    if not all(_scope_matches(manifest, item) for item in observations):
        return EvidenceManifestLinkageDisposition.SCOPE_MISMATCH

    return EvidenceManifestLinkageDisposition.LINKED_FOR_DECLARED_SCOPE
