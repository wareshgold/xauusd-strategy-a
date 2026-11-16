"""Synthetic tests for manifest-to-history metadata linkage."""
from __future__ import annotations

import unittest
from dataclasses import replace

from scripts.sp2l_evidence_manifest_research import EvidenceArtifactRecord, EvidenceManifestRecord
from scripts.sp2l_evidence_manifest_linkage_research import (
    EvidenceManifestLinkageDisposition,
    link_manifest_to_history_observations,
)
from scripts.sp2l_history_completeness_evidence_research import (
    HistoryCompletenessEvidence,
    HistoryEvidenceQueryKind,
    HistoryEvidenceScope,
    HistoryKindEvidence,
)
from scripts.sp2l_history_stability_research import HistoryObservationFingerprint


def make_scope(**changes):
    values = dict(
        account_identity_verified=True,
        account_identity_ref="acct-ref-01",
        terminal_session_ref="session-01",
        server_name="Broker-Demo",
        date_from="2026-11-01T00:00:00",
        date_to="2026-11-16T00:00:00",
        time_basis="broker_server_time",
        time_basis_source="source-record-01",
        observed_at="2026-11-16T10:00:00+03:30",
        package_version="5.0.6180",
        terminal_build="build-01",
        manifest_sha256="a" * 64,
    )
    values.update(changes)
    return HistoryEvidenceScope(**values)


def make_observation(observation_id="obs-1", **scope_changes):
    scope = make_scope(**scope_changes)
    evidence = HistoryCompletenessEvidence(
        scope,
        HistoryKindEvidence(HistoryEvidenceQueryKind.ORDERS, 1, (object(),)),
        HistoryKindEvidence(HistoryEvidenceQueryKind.DEALS, 1, (object(),)),
    )
    return HistoryObservationFingerprint(
        observation_id, evidence, "external-v1", "b" * 64, "c" * 64
    )


def make_manifest(**changes):
    values = dict(
        manifest_id="manifest-1",
        recorded_at="2026-11-16T10:10:00+03:30",
        account_identity_ref="acct-ref-01",
        terminal_session_ref="session-01",
        server_name="Broker-Demo",
        date_from="2026-11-01T00:00:00",
        date_to="2026-11-16T00:00:00",
        time_basis="broker_server_time",
        time_basis_source="source-record-01",
        package_version="5.0.6180",
        terminal_build="build-01",
        capture_method_id="capture-v1",
        capture_tool_version="tool-1",
        observation_ids=("obs-1", "obs-2"),
        artifacts=(
            EvidenceArtifactRecord("a1", "declared", "artifact-a", 1, "d" * 64),
        ),
    )
    values.update(changes)
    return EvidenceManifestRecord(**values)


class TestEvidenceManifestLinkageResearch(unittest.TestCase):
    def test_matching_manifest_and_observation_link(self):
        self.assertEqual(
            link_manifest_to_history_observations(make_manifest(), (make_observation(),)),
            EvidenceManifestLinkageDisposition.LINKED_FOR_DECLARED_SCOPE,
        )

    def test_two_listed_observations_link(self):
        self.assertEqual(
            link_manifest_to_history_observations(
                make_manifest(),
                (make_observation("obs-1"), make_observation("obs-2", observed_at="2026-11-16T10:05:00+03:30")),
            ),
            EvidenceManifestLinkageDisposition.LINKED_FOR_DECLARED_SCOPE,
        )

    def test_invalid_manifest_is_rejected(self):
        self.assertEqual(
            link_manifest_to_history_observations(make_manifest(server_name=" "), (make_observation(),)),
            EvidenceManifestLinkageDisposition.INVALID_MANIFEST,
        )

    def test_empty_observations_are_rejected(self):
        self.assertEqual(
            link_manifest_to_history_observations(make_manifest(), ()),
            EvidenceManifestLinkageDisposition.INVALID_OBSERVATION,
        )

    def test_non_tuple_observations_are_rejected(self):
        self.assertEqual(
            link_manifest_to_history_observations(make_manifest(), [make_observation()]),
            EvidenceManifestLinkageDisposition.INVALID_OBSERVATION,
        )

    def test_unlisted_observation_id_is_rejected(self):
        self.assertEqual(
            link_manifest_to_history_observations(make_manifest(), (make_observation("not-listed"),)),
            EvidenceManifestLinkageDisposition.OBSERVATION_NOT_LISTED,
        )

    def test_account_scope_mismatch_is_rejected(self):
        self.assertEqual(
            link_manifest_to_history_observations(
                make_manifest(), (make_observation(account_identity_ref="other"),)
            ),
            EvidenceManifestLinkageDisposition.SCOPE_MISMATCH,
        )

    def test_session_scope_mismatch_is_rejected(self):
        self.assertEqual(
            link_manifest_to_history_observations(
                make_manifest(), (make_observation(terminal_session_ref="other"),)
            ),
            EvidenceManifestLinkageDisposition.SCOPE_MISMATCH,
        )

    def test_server_scope_mismatch_is_rejected(self):
        self.assertEqual(
            link_manifest_to_history_observations(
                make_manifest(), (make_observation(server_name="other"),)
            ),
            EvidenceManifestLinkageDisposition.SCOPE_MISMATCH,
        )

    def test_interval_mismatch_is_rejected(self):
        self.assertEqual(
            link_manifest_to_history_observations(
                make_manifest(), (make_observation(date_to="2026-11-17T00:00:00"),)
            ),
            EvidenceManifestLinkageDisposition.SCOPE_MISMATCH,
        )

    def test_time_basis_mismatch_is_rejected(self):
        self.assertEqual(
            link_manifest_to_history_observations(
                make_manifest(), (make_observation(time_basis="unknown"),)
            ),
            EvidenceManifestLinkageDisposition.SCOPE_MISMATCH,
        )

    def test_package_version_mismatch_is_rejected(self):
        self.assertEqual(
            link_manifest_to_history_observations(
                make_manifest(), (make_observation(package_version="other"),)
            ),
            EvidenceManifestLinkageDisposition.SCOPE_MISMATCH,
        )

    def test_invalid_history_evidence_is_rejected(self):
        bad = make_observation()
        evidence = replace(
            bad.evidence,
            orders=HistoryKindEvidence(HistoryEvidenceQueryKind.ORDERS, 9, ()),
        )
        self.assertEqual(
            link_manifest_to_history_observations(
                make_manifest(), (replace(bad, evidence=evidence),)
            ),
            EvidenceManifestLinkageDisposition.INVALID_OBSERVATION,
        )

    def test_duplicate_observation_ids_are_rejected(self):
        self.assertEqual(
            link_manifest_to_history_observations(
                make_manifest(), (make_observation(), make_observation())
            ),
            EvidenceManifestLinkageDisposition.INVALID_OBSERVATION,
        )


if __name__ == "__main__":
    unittest.main()
