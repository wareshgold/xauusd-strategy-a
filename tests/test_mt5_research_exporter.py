import importlib.util
from datetime import timezone
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "acquire_sp2l_three_month_mt5_data.py"
SPEC = importlib.util.spec_from_file_location("sp2l_mt5_export", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TestMt5ResearchExporter(unittest.TestCase):
    def test_parse_utc_requires_explicit_timezone(self):
        self.assertEqual(MODULE.parse_utc("2026-08-09T00:00:00Z").tzinfo, timezone.utc)
        with self.assertRaises(ValueError):
            MODULE.parse_utc("2026-08-09T00:00:00")

    def test_tick_audit_retains_same_millisecond_and_counts_bad_quotes(self):
        audit = MODULE.TickAudit()
        audit.add((1000, "t0", "10.0", "10.2", "0", "0", 1))
        audit.add((1000, "t0", "10.1", "10.3", "0", "0", 2))
        audit.add((999, "t-1", "10.0", "9.9", "0", "0", 1))
        result = audit.report()
        self.assertEqual(result["tick_count"], 3)
        self.assertEqual(result["same_millisecond_timestamp_count"], 1)
        self.assertEqual(result["out_of_order_timestamp_count"], 1)
        self.assertEqual(result["crossed_quote_count"], 1)

    def test_m1_audit_reports_gaps_without_filling(self):
        audit = MODULE.M1Audit()
        audit.add((0, "t0", "1", "2", "0.5", "1", 2, 0, 0))
        audit.add((180, "t3", "1", "2", "0.5", "1", 2, 0, 0))
        result = audit.report()
        self.assertEqual(result["bar_count"], 2)
        self.assertEqual(result["interval_gap_count"], 1)
        self.assertEqual(result["interval_gaps"][0]["nominal_missing_minute_slots"], 2)

    def test_symbol_specification_is_independent_of_mt5_runtime(self):
        class Info:
            name = "XAUUSD.ecn"
            point = 0.01
            trade_tick_size = 0.01
            trade_contract_size = 100.0
        result = MODULE.symbol_spec(Info())
        self.assertEqual(result["name"], "XAUUSD.ecn")
        self.assertEqual(result["point"], 0.01)
        self.assertEqual(result["trade_contract_size"], 100.0)

    def test_gzip_csv_is_streamed_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.csv.gz"
            with MODULE.CsvGzip(path, ("a", "b")) as sink:
                sink.write((1, 2))
                sink.write((3, 4))
            self.assertTrue(path.exists())
            self.assertEqual(sink.count, 2)
            with self.assertRaises(FileExistsError):
                with MODULE.CsvGzip(path, ("a", "b")):
                    pass


if __name__ == "__main__":
    unittest.main()
