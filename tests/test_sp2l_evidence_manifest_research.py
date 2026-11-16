"""Synthetic tests for the offline evidence-manifest record model."""
from __future__ import annotations

import unittest
from dataclasses import replace

from scripts.sp2l_evidence_manifest_research import (
    EvidenceArtifactRecord,
    EvidenceManifestDisposition,
    EvidenceManifestRecord,
    evidence_manifest_record_is_valid,
    validate_evidence_manifest,
)


def make_artifact(**changes):
    values = dict(
        artifact_id="artifact-orders-01",
        artifact_role="orders-history-export",
        locator="evidence/observation-01/orders.bin",
        byte_length=128,
        byte_sha256="a" * 64,
    )
    values.update(changes)
    return EvidenceArtifactRecord(**values)


def make_manifest(**changes):
    values = dict(
        manifest_id="manifest-01",
        recorded_at="2026-11-16T10:00:00+03:30",
        account_identity_ref="opaque-account-ref",
        terminal_session_ref="session-ref-01",
        server_name="Broker-Demo",
        date_from="2026-11-01T00:00:00",
        date_to="2026-11-16T00:00:00",
        time_basis="broker_server_time",
        time_basis_source="source-record-01",
        package_version="5.0.6180",
        terminal_build="build-01",
        capture_method_id="mt5-history-capture-v1",
        capture_tool_version="research-capture-0.1",
        observation_ids=("observation-01", "observation-02"),
        artifacts=(
            make_artifact(),
            make_artifact(
                artifact_id="artifact-deals-01",
                artifact_role="deals-history-export",
                locator="evidence/observation-01/deals.bin",
                byte_length=256,
                byte_sha256="b" * 64,
            ),
        ),
    )
    values.update(changes)
    return EvidenceManifestRecord(**values)


class TestEvidenceManifestResearch(unittest.TestCase):
    def test_complete_manifest_record_is_valid(self):
        self.assertEqual(
            validate_evidence_manifest(make_manifest()),
            EvidenceManifestDisposition.VALID_MANIFEST_RECORD,
        )

    def test_validity_helper_matches_disposition(self):
        self.assertTrue(evidence_manifest_record_is_valid(make_manifest()))

    def test_non_manifest_input_is_rejected(self):
        self.assertEqual(
            validate_evidence_manifest(object()),
            EvidenceManifestDisposition.INVALID_MANIFEST,
        )

    def test_blank_required_provenance_is_rejected(self):
        self.assertEqual(
            validate_evidence_manifest(make_manifest(server_name="  ")),
            EvidenceManifestDisposition.INVALID_MANIFEST,
        )

    def test_empty_observation_ids_are_rejected(self):
        self.assertEqual(
            validate_evidence_manifest(make_manifest(observation_ids=())),
            EvidenceManifestDisposition.INVALID_MANIFEST,
        )

    def test_duplicate_observation_ids_are_rejected(self):
        self.assertEqual(
            validate_evidence_manifest(
                make_manifest(observation_ids=("obs-1", "obs-1"))
            ),
            EvidenceManifestDisposition.INVALID_MANIFEST,
        )

    def test_non_tuple_observation_ids_are_rejected(self):
        self.assertEqual(
            validate_evidence_manifest(make_manifest(observation_ids=["obs-1"])),
            EvidenceManifestDisposition.INVALID_MANIFEST,
        )

    def test_empty_artifact_collection_is_rejected(self):
        self.assertEqual(
            validate_evidence_manifest(make_manifest(artifacts=())),
            EvidenceManifestDisposition.INVALID_MANIFEST,
        )

    def test_non_tuple_artifact_collection_is_rejected(self):
        self.assertEqual(
            validate_evidence_manifest(make_manifest(artifacts=[make_artifact()])),
            EvidenceManifestDisposition.INVALID_MANIFEST,
        )

    def test_duplicate_artifact_ids_are_rejected(self):
        artifact = make_artifact()
        self.assertEqual(
            validate_evidence_manifest(
                make_manifest(artifacts=(artifact, replace(artifact, locator="other.bin")))
            ),
            EvidenceManifestDisposition.INVALID_MANIFEST,
        )

    def test_invalid_artifact_sha256_is_rejected(self):
        self.assertEqual(
            validate_evidence_manifest(
                make_manifest(artifacts=(make_artifact(byte_sha256="bad"),))
            ),
            EvidenceManifestDisposition.INVALID_MANIFEST,
        )

    def test_negative_byte_length_is_rejected(self):
        self.assertEqual(
            validate_evidence_manifest(
                make_manifest(artifacts=(make_artifact(byte_length=-1),))
            ),
            EvidenceManifestDisposition.INVALID_MANIFEST,
        )

    def test_boolean_byte_length_is_rejected(self):
        self.assertEqual(
            validate_evidence_manifest(
                make_manifest(artifacts=(make_artifact(byte_length=True),))
            ),
            EvidenceManifestDisposition.INVALID_MANIFEST,
        )

    def test_zero_byte_artifact_is_valid(self):
        self.assertTrue(
            evidence_manifest_record_is_valid(
                make_manifest(artifacts=(make_artifact(byte_length=0),))
            )
        )

    def test_identical_interval_endpoints_are_rejected(self):
        self.assertEqual(
            validate_evidence_manifest(
                make_manifest(date_to="2026-11-01T00:00:00")
            ),
            EvidenceManifestDisposition.INVALID_MANIFEST,
        )

    def test_locator_and_hash_are_recorded_not_verified(self):
        # The model accepts a declared locator and digest without touching disk.
        self.assertTrue(
            evidence_manifest_record_is_valid(
                make_manifest(
                    artifacts=(
                        make_artifact(
                            locator="not-accessed://external-artifact",
                            byte_sha256="f" * 64,
                        ),
                    )
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
