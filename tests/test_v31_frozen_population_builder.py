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
    def make_source(self, directory: Path):
        path = directory / "m1.csv.gz"
        rows = [
            "time_epoch_seconds,time_utc_iso,open,high,low,close,tick_volume,spread,real_volume",
            "1791507600,2026-10-09T01:00:00Z,3900,3901,3899,3900.5,10,20,0",
            "1791507660,2026-10-09T01:01:00Z,3900.5,3902,3900,3901,11,20,0",
            "1791507720,2026-10-09T01:02:00Z,3901,3903,3900.5,3902,12,20,0",
            "1791507780,2026-10-09T01:03:00Z,3902,3904,3901,3903,13,20,0",
        ]
        with gzip.open(path, "wt", encoding="utf-8", newline="") as stream:
            stream.write("\n".join(rows) + "\n")
        return path

    def test_loads_byte_bound_m1_csv_gz(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_source(Path(tmp))
            raw = path.read_bytes()
            bars, digest, size = BUILDER.load_m1_csv_gz(path, hashlib.sha256(raw).hexdigest())
            self.assertEqual(len(bars), 4)
            self.assertEqual(digest, hashlib.sha256(raw).hexdigest())
            self.assertEqual(size, len(raw))

    def test_rejects_wrong_source_sha_before_parsing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_source(Path(tmp))
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                BUILDER.load_m1_csv_gz(path, "0" * 64)

    def test_population_is_single_deduplicated_v31_entry_set(self):
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
        self.assertEqual(rows[0]["exit_time_utc"], "")
        self.assertEqual(rows[0]["exit_price"], "")


if __name__ == "__main__":
    unittest.main()
