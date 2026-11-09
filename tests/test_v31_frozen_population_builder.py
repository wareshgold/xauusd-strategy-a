from __future__ import annotations

import gzip
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_sp2l_v3_1_frozen_population_from_m1.py"
SPEC = importlib.util.spec_from_file_location("v31_population_builder", SCRIPT)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class TestV31FrozenPopulationBuilder(unittest.TestCase):
    def make_source(self, directory: Path, timestamps=None):
        path = directory / "m1.csv.gz"
        rows = ["time,time_utc,open,high,low,close,tick_volume,spread_points,real_volume"]
        base = 1791507600
        stamps = timestamps or [base + 60 * i for i in range(10)]
        for ts in stamps:
            stamp = BUILDER.utc_iso(ts)
            rows.append(f"{ts},{stamp},3900,3901,3899,3900.5,10,20,0")
        with gzip.open(path, "wt", encoding="utf-8", newline="") as stream:
            stream.write("\n".join(rows) + "\n")
        return path

    def test_loads_byte_bound_m1_csv_gz(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_source(Path(tmp))
            raw = path.read_bytes()
            bars, digest, size = BUILDER.load_m1_csv_gz(path, hashlib.sha256(raw).hexdigest())
            self.assertEqual(len(bars), 10)
            self.assertEqual(digest, hashlib.sha256(raw).hexdigest())
            self.assertEqual(size, len(raw))

    def test_rejects_wrong_source_sha_before_parsing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_source(Path(tmp))
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                BUILDER.load_m1_csv_gz(path, "0" * 64)

    def test_rejects_duplicate_or_out_of_order_timestamps(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = 1791507600
            path = self.make_source(Path(tmp), [base + 60 * i for i in range(5)] + [base + 60 * 4] + [base + 60 * i for i in range(6, 11)])
            raw = path.read_bytes()
            with self.assertRaisesRegex(ValueError, "duplicate or out-of-order"):
                BUILDER.load_m1_csv_gz(path, hashlib.sha256(raw).hexdigest())

    def test_gap_inventory_and_segment_split(self):
        base = 1791507600
        bars = [{"time": base + 60 * i} for i in [0, 1, 2, 5, 6, 10]]
        gaps = BUILDER.find_m1_gaps(bars)
        self.assertEqual([g["missing_minutes"] for g in gaps], [2, 3])
        segments = BUILDER.split_contiguous_segments(bars)
        self.assertEqual([[b["time"] for b in s] for s in segments],
                         [[base, base + 60, base + 120],
                          [base + 300, base + 360],
                          [base + 600]])

    def test_signal_and_entry_search_never_receive_cross_gap_bars(self):
        base = 1791507600
        times = [base + 60 * i for i in range(8)] + [base + 60 * 10 + 60 * i for i in range(8)]
        bars = [{"time": ts, "open": 10.0, "high": 11.0,
                 "low": 9.0, "close": 10.5} for ts in times]
        seen_detect_windows = []
        seen_entry_segments = []

        def detect(window, symbol):
            window_times = [b["time"] for b in window]
            self.assertTrue(all(b - a == 60 for a, b in zip(window_times, window_times[1:])))
            seen_detect_windows.append(window_times)
            return {"direction": "BUY"}

        def find_entry(segment, start_index, setup):
            segment_times = [b["time"] for b in segment]
            self.assertTrue(all(b - a == 60 for a, b in zip(segment_times, segment_times[1:])))
            seen_entry_segments.append(segment_times)
            return None

        with patch.object(BUILDER.cfg, "detect", side_effect=detect), \
             patch.object(BUILDER.cfg, "find_first_entry", side_effect=find_entry):
            BUILDER.build_population(bars, "XAUUSD.ecn")
        self.assertTrue(seen_detect_windows)
        self.assertEqual(len(set(tuple(s) for s in seen_entry_segments)), 2)

    def test_population_is_deduplicated_and_target_is_blank(self):
        bars = [{"time": 1000 + 60 * i, "open": 10.0, "high": 11.0,
                 "low": 9.0, "close": 10.5} for i in range(8)]
        candidate = {
            "trigger_time": bars[4]["time"], "direction": "BUY",
            "theoretical_entry": 10.0, "sl": 9.5, "tp": 12.0, "risk": 0.5,
        }
        with patch.object(BUILDER.cfg, "detect", return_value={"direction": "BUY"}), \
             patch.object(BUILDER.cfg, "find_first_entry", return_value=candidate):
            rows = BUILDER.build_population(bars, "XAUUSD.ecn")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["entry_time_utc"], BUILDER.utc_iso(candidate["trigger_time"]))
        self.assertEqual(rows[0]["variant"], BUILDER.cfg.VERSION)
        self.assertEqual(rows[0]["target"], "")
        self.assertEqual(rows[0]["exit_time_utc"], "")
        self.assertEqual(rows[0]["exit_price"], "")

    def test_population_is_sorted_chronologically(self):
        bars = [{"time": 1000 + 60 * i, "open": 10.0, "high": 11.0,
                 "low": 9.0, "close": 10.5} for i in range(10)]
        candidates = [
            {"trigger_time": 1000 + 60 * 8, "direction": "BUY",
             "theoretical_entry": 10.0, "sl": 9.5, "tp": 12.0, "risk": 0.5},
            {"trigger_time": 1000 + 60 * 5, "direction": "SELL",
             "theoretical_entry": 10.0, "sl": 10.5, "tp": 8.0, "risk": 0.5},
        ]
        with patch.object(BUILDER.cfg, "detect", side_effect=[{"direction": "BUY"}, {"direction": "BUY"}, None, None, None, None]), \
             patch.object(BUILDER.cfg, "find_first_entry", side_effect=candidates):
            rows = BUILDER.build_population(bars, "XAUUSD.ecn")
        self.assertEqual([r["entry_time_utc"] for r in rows],
                         sorted(r["entry_time_utc"] for r in rows))


if __name__ == "__main__":
    unittest.main()
