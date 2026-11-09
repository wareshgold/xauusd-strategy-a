import importlib.util
from datetime import timezone
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "acquire_sp2l_three_month_mt5_data.py"
SPEC = importlib.util.spec_from_file_location("sp2l_mt5_export", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TestMt5ResearchExporter(unittest.TestCase):
    def test_parse_utc_requires_explicit_timezone(self):
        parsed = MODULE.parse_utc("2026-08-09T00:00:00Z")
        self.assertEqual(parsed.tzinfo, timezone.utc)
        with self.assertRaises(ValueError):
            MODULE.parse_utc("2026-08-09T00:00:00")

    def test_tick_audit_preserves_same_millisecond_as_distinct_observation(self):
        rows = [
            (1000, "t0", "10.0", "10.2", "0", "0", 1),
            (1000, "t0", "10.1", "10.3", "0", "0", 2),
            (999, "t-1", "10.0", "9.9", "0", "0", 1),
        ]
        audit = MODULE.audit_tick_rows(rows)
        self.assertEqual(audit["tick_count"], 3)
        self.assertEqual(audit["same_millisecond_timestamp_count"], 1)
        self.assertEqual(audit["out_of_order_timestamp_count"], 1)
        self.assertEqual(audit["crossed_quote_count"], 1)

    def test_m1_audit_reports_gaps_without_repairing(self):
        rows = [
            (0, "t0", "1", "2", "0.5", "1", 2, 0, 0),
            (180, "t3", "1", "2", "0.5", "1", 2, 0, 0),
        ]
        audit = MODULE.audit_m1_rows(rows)
        self.assertEqual(audit["bar_count"], 2)
        self.assertEqual(audit["interval_gap_count"], 1)
        self.assertEqual(audit["interval_gaps"][0]["nominal_missing_minute_slots"], 2)

    def test_symbol_specification_does_not_require_mt5_runtime(self):
        class Info:
            name = "XAUUSD.ecn"
            point = 0.01
            trade_tick_size = 0.01
            trade_contract_size = 100.0
        result = MODULE.symbol_specification(Info())
        self.assertEqual(result["name"], "XAUUSD.ecn")
        self.assertEqual(result["point"], 0.01)
        self.assertEqual(result["trade_contract_size"], 100.0)


if __name__ == "__main__":
    unittest.main()
