import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "research" / "monthly_matrix_source_audit.py"
SPEC = importlib.util.spec_from_file_location("monthly_matrix_source_audit", SCRIPT)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class MonthlyMatrixSourceAuditTests(unittest.TestCase):
    def test_timestamp_requires_timezone(self):
        with self.assertRaises(ValueError):
            AUDIT.parse_ts("2026-10-01T12:00:00")

    def test_timestamp_normalizes_to_utc(self):
        a = AUDIT.parse_ts("2026-10-01T15:30:00+03:30")
        b = AUDIT.parse_ts("2026-10-01T12:00:00Z")
        self.assertEqual(a, b)

    def test_load_segments_gap_without_synthesizing_bars(self):
        csv_text = (
            "timestamp_utc,open,high,low,close\n"
            "2026-10-01T12:00:00Z,100,101,99,100.5\n"
            "2026-10-01T12:01:00Z,100.5,102,100,101.5\n"
            "2026-10-01T12:04:00Z,101.5,103,101,102.5\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bars.csv"
            path.write_text(csv_text, encoding="utf-8")
            bars, digest, time_col = AUDIT.load(path)
        self.assertEqual(len(bars), 3)
        self.assertEqual([b["segment"] for b in bars], [0, 0, 1])
        self.assertEqual(time_col, "timestamp_utc")
        self.assertEqual(len(digest), 64)

    def test_load_prefers_time_utc_iso_when_epoch_column_also_exists(self):
        csv_text = (
            "time_epoch_seconds,time_utc_iso,open,high,low,close\\n"
            "1790856000,2026-10-01T12:00:00Z,100,101,99,100.5\\n"
            "1790856060,2026-10-01T12:01:00Z,100.5,102,100,101.5\\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bars.csv"
            path.write_text(csv_text, encoding="utf-8")
            bars, digest, time_col = AUDIT.load(path)
        self.assertEqual(len(bars), 2)
        self.assertEqual(time_col, "time_utc_iso")
        self.assertEqual(bars[1]["time"] - bars[0]["time"], 60)

    def test_rejects_duplicate_or_nonmonotonic_timestamps(self):
        csv_text = (
            "time,open,high,low,close\n"
            "2026-10-01T12:00:00Z,100,101,99,100.5\n"
            "2026-10-01T12:00:00Z,100.5,102,100,101.5\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bars.csv"
            path.write_text(csv_text, encoding="utf-8")
            with self.assertRaises(ValueError):
                AUDIT.load(path)

    def test_ema_is_deterministic(self):
        bars = [{"close": 10.0}, {"close": 12.0}, {"close": 14.0}]
        values = AUDIT.ema(bars, 3)
        self.assertEqual(values, [10.0, 11.0, 12.5])

    def test_trend_filter_respects_max_opposite_moves(self):
        bars = [
            {"high": 10, "low": 5}, {"high": 11, "low": 6},
            {"high": 10, "low": 5}, {"high": 9, "low": 4},
        ]
        self.assertTrue(AUDIT.trend_ok(bars, 0, 2, "BUY"))
        self.assertFalse(AUDIT.trend_ok(bars, 0, 3, "BUY"))


if __name__ == "__main__":
    unittest.main()
