"""Synthetic filesystem tests for exact-byte evidence artifact verification."""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.sp2l_evidence_manifest_research import (
    EvidenceArtifactRecord,
    EvidenceManifestRecord,
)
from scripts.sp2l_evidence_artifact_verification_research import (
    EvidenceArtifactVerificationDisposition as ArtifactStatus,
    EvidenceArtifactVerificationReportDisposition as ReportStatus,
    verify_evidence_artifacts,
)


def make_manifest(artifacts=None):
    if artifacts is None:
        payload_a = b"orders\x00raw\r\n"
        payload_b = b"deals\xffraw"
        artifacts = (
            EvidenceArtifactRecord(
                "orders-01", "orders-export", "opaque://orders",
                len(payload_a), hashlib.sha256(payload_a).hexdigest(),
            ),
            EvidenceArtifactRecord(
                "deals-01", "deals-export", "opaque://deals",
                len(payload_b), hashlib.sha256(payload_b).hexdigest(),
            ),
        )
    return EvidenceManifestRecord(
        "manifest-01", "2026-11-16T10:00:00+03:30", "acct-ref",
        "session-ref", "Broker-Demo", "2026-11-01T00:00:00",
        "2026-11-16T00:00:00", "broker_server_time", "source-ref",
        "5.0.6180", "build-01", "capture-v1", "tool-1",
        ("obs-01",), tuple(artifacts),
    )


class TestEvidenceArtifactVerificationResearch(unittest.TestCase):
    def test_all_exact_bytes_verify(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            orders = b"orders\x00raw\r\n"
            deals = b"deals\xffraw"
            (root / "orders.bin").write_bytes(orders)
            (root / "deals.bin").write_bytes(deals)
            report = verify_evidence_artifacts(
                make_manifest(),
                {"orders-01": root / "orders.bin", "deals-01": root / "deals.bin"},
            )
        self.assertEqual(report.disposition, ReportStatus.ALL_ARTIFACTS_VERIFIED)
        self.assertTrue(all(x.disposition is ArtifactStatus.VERIFIED_EXACT_BYTES for x in report.artifact_results))

    def test_zero_byte_file_verifies(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.bin"
            path.write_bytes(b"")
            artifact = EvidenceArtifactRecord(
                "empty", "empty-export", "opaque://empty", 0,
                hashlib.sha256(b"").hexdigest(),
            )
            report = verify_evidence_artifacts(
                make_manifest((artifact,)), {"empty": path}
            )
        self.assertEqual(report.disposition, ReportStatus.ALL_ARTIFACTS_VERIFIED)

    def test_raw_bytes_are_hashed_without_text_normalization(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "raw.bin"
            path.write_bytes(b"a\r\nb")
            artifact = EvidenceArtifactRecord(
                "raw", "raw", "opaque://raw", 4,
                hashlib.sha256(b"a\nb").hexdigest(),
            )
            report = verify_evidence_artifacts(
                make_manifest((artifact,)), {"raw": path}
            )
        self.assertEqual(report.artifact_results[0].disposition, ArtifactStatus.SHA256_MISMATCH)

    def test_byte_length_mismatch_is_distinguished(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x.bin"
            path.write_bytes(b"abc")
            artifact = EvidenceArtifactRecord(
                "x", "raw", "opaque://x", 4, hashlib.sha256(b"abc").hexdigest()
            )
            report = verify_evidence_artifacts(make_manifest((artifact,)), {"x": path})
        self.assertEqual(report.artifact_results[0].disposition, ArtifactStatus.BYTE_LENGTH_MISMATCH)

    def test_sha256_mismatch_is_distinguished(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x.bin"
            path.write_bytes(b"abc")
            artifact = EvidenceArtifactRecord("x", "raw", "opaque://x", 3, "0" * 64)
            report = verify_evidence_artifacts(make_manifest((artifact,)), {"x": path})
        self.assertEqual(report.artifact_results[0].disposition, ArtifactStatus.SHA256_MISMATCH)

    def test_missing_path_key_is_reported_per_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orders.bin"
            path.write_bytes(b"orders\x00raw\r\n")
            report = verify_evidence_artifacts(make_manifest(), {"orders-01": path})
        self.assertEqual(report.disposition, ReportStatus.ARTIFACTS_NOT_ALL_VERIFIED)
        self.assertEqual(report.artifact_results[1].disposition, ArtifactStatus.PATH_NOT_SUPPLIED)

    def test_nonexistent_file_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.bin"
            artifact = EvidenceArtifactRecord("x", "raw", "opaque://x", 0, hashlib.sha256(b"").hexdigest())
            report = verify_evidence_artifacts(make_manifest((artifact,)), {"x": path})
        self.assertEqual(report.artifact_results[0].disposition, ArtifactStatus.MISSING_PATH)

    def test_directory_is_not_accepted_as_file(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = EvidenceArtifactRecord("x", "raw", "opaque://x", 0, hashlib.sha256(b"").hexdigest())
            report = verify_evidence_artifacts(make_manifest((artifact,)), {"x": Path(directory)})
        self.assertEqual(report.artifact_results[0].disposition, ArtifactStatus.NOT_REGULAR_FILE)

    def test_invalid_manifest_is_rejected_before_io(self):
        invalid = make_manifest((EvidenceArtifactRecord("x", "raw", "opaque", -1, "a" * 64),))
        report = verify_evidence_artifacts(invalid, {"x": "/path/not/read"})
        self.assertEqual(report.disposition, ReportStatus.INVALID_MANIFEST)
        self.assertEqual(report.artifact_results, ())

    def test_non_mapping_is_rejected(self):
        report = verify_evidence_artifacts(make_manifest(), [("orders-01", "x")])
        self.assertEqual(report.disposition, ReportStatus.INVALID_PATH_MAPPING)

    def test_unknown_artifact_key_is_rejected(self):
        report = verify_evidence_artifacts(make_manifest(), {"unknown": "x"})
        self.assertEqual(report.disposition, ReportStatus.INVALID_PATH_MAPPING)

    def test_invalid_path_value_is_rejected(self):
        report = verify_evidence_artifacts(make_manifest(), {"orders-01": b"path"})
        self.assertEqual(report.disposition, ReportStatus.INVALID_PATH_MAPPING)

    def test_manifest_locator_is_not_interpreted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "real.bin"
            payload = b"orders\x00raw\r\n"
            path.write_bytes(payload)
            artifact = EvidenceArtifactRecord(
                "orders-01", "orders-export", "not-a-local-path://unresolved",
                len(payload), hashlib.sha256(payload).hexdigest(),
            )
            report = verify_evidence_artifacts(make_manifest((artifact,)), {"orders-01": path})
        self.assertEqual(report.disposition, ReportStatus.ALL_ARTIFACTS_VERIFIED)

    def test_string_paths_are_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orders.bin"
            payload = b"orders\x00raw\r\n"
            path.write_bytes(payload)
            artifact = EvidenceArtifactRecord(
                "orders-01", "orders-export", "opaque://orders",
                len(payload), hashlib.sha256(payload).hexdigest(),
            )
            report = verify_evidence_artifacts(make_manifest((artifact,)), {"orders-01": str(path)})
        self.assertEqual(report.disposition, ReportStatus.ALL_ARTIFACTS_VERIFIED)

    def test_uppercase_declared_digest_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x.bin"
            path.write_bytes(b"abc")
            artifact = EvidenceArtifactRecord("x", "raw", "opaque://x", 3, hashlib.sha256(b"abc").hexdigest().upper())
            report = verify_evidence_artifacts(make_manifest((artifact,)), {"x": path})
        self.assertEqual(report.disposition, ReportStatus.ALL_ARTIFACTS_VERIFIED)

    def test_all_artifacts_are_reported_even_when_one_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "orders.bin").write_bytes(b"wrong")
            (root / "deals.bin").write_bytes(b"deals\xffraw")
            report = verify_evidence_artifacts(
                make_manifest(),
                {"orders-01": root / "orders.bin", "deals-01": root / "deals.bin"},
            )
        self.assertEqual(len(report.artifact_results), 2)
        self.assertEqual(report.artifact_results[0].disposition, ArtifactStatus.BYTE_LENGTH_MISMATCH)
        self.assertEqual(report.artifact_results[1].disposition, ArtifactStatus.VERIFIED_EXACT_BYTES)


if __name__ == "__main__":
    unittest.main()
