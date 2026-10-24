import csv
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.audit_mt5_m1_snapshot_readonly import audit

class Mt5M1SnapshotAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.csv_path = self.root / "bars.csv"
        self.manifest_path = self.root / "manifest.json"
        self.rows = [
            {"time_epoch_seconds": str(int(datetime(2026, 9, 21, 0, 53, 20, tzinfo=timezone.utc).timestamp())), "time_utc_iso": "2026-09-21T00:53:20+00:00",
             "open": "2500", "high": "2502", "low": "2499", "close": "2501",
             "tick_volume": "12", "spread": "20", "real_volume": "0"},
            {"time_epoch_seconds": str(int(datetime(2026, 9, 21, 0, 54, 20, tzinfo=timezone.utc).timestamp())), "time_utc_iso": "2026-09-21T00:54:20+00:00",
             "open": "2501", "high": "2503", "low": "2500", "close": "2502",
             "tick_volume": "13", "spread": "20", "real_volume": "0"},
        ]
        self.write_rows(self.rows)

    def write_rows(self, rows):
        fields = list(rows[0])
        with self.csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        digest = hashlib.sha256(self.csv_path.read_bytes()).hexdigest()
        self.manifest_path.write_text(json.dumps({
            "csv_sha256": digest, "symbol": "XAUUSD.ecn", "timeframe": "M1",
            "returned_bars": len(rows), "requested_start_utc": "2026-09-21T00:53:20+00:00",
            "requested_end_utc": "2026-09-21T00:54:20+00:00",
            "actual_first_bar_utc": rows[0]["time_utc_iso"],
            "actual_last_bar_utc": rows[-1]["time_utc_iso"],
        }), encoding="utf-8")

    def test_valid_snapshot_hash_and_bar_count(self):
        report = audit(self.csv_path, self.manifest_path)
        self.assertTrue(report["csv_hash_matches_manifest"])
        self.assertTrue(report["bar_count_matches_manifest"])
        self.assertEqual(report["data_quality_gate"], "PASS_STRUCTURAL_ONLY")

    def test_hash_mismatch_requires_review(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        manifest["csv_sha256"] = "wrong"
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        report = audit(self.csv_path, self.manifest_path)
        self.assertFalse(report["csv_hash_matches_manifest"])
        self.assertEqual(report["data_quality_gate"], "REVIEW_REQUIRED")

    def test_duplicate_timestamp_is_detected(self):
        duplicate = dict(self.rows[1])
        duplicate["close"] = "2502.5"
        self.write_rows([self.rows[0], self.rows[1], duplicate])
        report = audit(self.csv_path, self.manifest_path)
        self.assertEqual(report["duplicate_timestamp_count"], 1)
        self.assertEqual(report["data_quality_gate"], "REVIEW_REQUIRED")

    def test_bad_ohlc_row_is_retained_as_rejection(self):
        bad = dict(self.rows[1])
        bad["high"] = "2490"
        self.write_rows([self.rows[0], bad])
        report = audit(self.csv_path, self.manifest_path)
        self.assertEqual(len(report["rejected_rows"]), 1)
        self.assertEqual(report["data_quality_gate"], "REVIEW_REQUIRED")

    def test_gap_is_reported_not_filled(self):
        second = dict(self.rows[1])
        second["time_epoch_seconds"] = str(int(second["time_epoch_seconds"]) + 180)
        from datetime import datetime, timezone
        second["time_utc_iso"] = datetime.fromtimestamp(int(second["time_epoch_seconds"]), timezone.utc).isoformat()
        self.write_rows([self.rows[0], second])
        report = audit(self.csv_path, self.manifest_path)
        self.assertEqual(report["gap_segment_count"], 1)
        self.assertEqual(report["missing_minute_slots_between_observed_bars"], 3)
        self.assertIn("UNCLASSIFIED", report["gap_segments"][0]["classification"])

    def test_non_chronological_rows_are_detected(self):
        self.write_rows(list(reversed(self.rows)))
        report = audit(self.csv_path, self.manifest_path)
        self.assertFalse(report["timestamps_chronological"])
        self.assertEqual(report["data_quality_gate"], "REVIEW_REQUIRED")

if __name__ == "__main__":
    unittest.main()
