import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_sp2l_replay_json_readonly import audit


class ReplayJsonAuditTests(unittest.TestCase):
    def write_fixture(self, root: Path, payload: dict) -> Path:
        path = root / "fixture.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_flags_unresolved_timestamp_mapping_and_count_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_fixture(root, {
                "research_only": True,
                "source": "synthetic fixture",
                "timestamp_basis": "epoch rendered as UTC; historical MT5 timestamp mapping remains unresolved",
                "requested_interval_utc": {
                    "start": "2026-09-01T00:00:00+00:00",
                    "end": "2026-09-02T00:00:00+00:00",
                },
                "actual_first_utc": "2026-09-01T01:00:00+00:00",
                "actual_last_utc": "2026-09-01T23:58:00+00:00",
                "expected_minute_span": 1441,
                "raw_returned_bars": 1441,
                "filtered_bars_in_interval": 1379,
                "raw_bars_discarded_outside_interval": 62,
                "unique_timestamps": True,
                "chronological": True,
                "gap_count": 1,
                "gaps": [{"from_utc": "2026-09-01T12:00:00+00:00",
                          "to_utc": "2026-09-01T12:02:00+00:00",
                          "missing_minutes": 1}],
                "signals": [{"index": 1}],
                "trades": [],
            })
            report = audit(path)
            self.assertTrue(report["research_only"])
            self.assertEqual(report["input_sha256"], __import__("hashlib").sha256(path.read_bytes()).hexdigest())
            self.assertTrue(any("timestamp mapping unresolved" in item for item in report["warnings"]))
            self.assertTrue(any("Signal count differs" in item for item in report["warnings"]))
            self.assertTrue(any("starts after requested interval start" in item for item in report["warnings"]))
            self.assertEqual(report["detailed_gap_items"], 1)

    def test_does_not_claim_performance_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fixture(Path(directory), {
                "requested_interval_utc": {
                    "start": "2026-09-01T00:00:00+00:00",
                    "end": "2026-09-01T00:01:00+00:00",
                },
                "actual_first_utc": "2026-09-01T00:00:00+00:00",
                "actual_last_utc": "2026-09-01T00:01:00+00:00",
                "signals": [],
                "trades": [],
                "gaps": [],
                "unique_timestamps": True,
                "chronological": True,
            })
            report = audit(path)
            self.assertIn("does not validate", report["interpretation"])
            self.assertTrue(report["research_only"])


if __name__ == "__main__":
    unittest.main()
