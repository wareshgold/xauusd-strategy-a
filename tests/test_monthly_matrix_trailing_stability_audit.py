import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "research" / "monthly_matrix_trailing_stability_audit.py"
SPEC = importlib.util.spec_from_file_location("trailing_stability_audit", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TrailingStabilityAuditTests(unittest.TestCase):
    def test_daily_groups_by_utc_exit_date_and_excludes_unresolved(self):
        rows = [
            {"closed": True, "exit_time": MODULE.parse_time("2026-10-01T23:59:00Z", "exit", 2),
             "r": 1.0, "direction": "BUY", "reason": "TP", "entry_time": MODULE.parse_time("2026-10-01T23:58:00Z", "entry", 2), "row_number": 2},
            {"closed": True, "exit_time": MODULE.parse_time("2026-10-02T00:01:00Z", "exit", 3),
             "r": -0.5, "direction": "SELL", "reason": "SL", "entry_time": MODULE.parse_time("2026-10-01T23:59:00Z", "entry", 3), "row_number": 3},
            {"closed": False, "exit_time": None, "r": None, "direction": "BUY", "reason": "UNRESOLVED", "entry_time": MODULE.parse_time("2026-10-02T00:00:00Z", "entry", 4), "row_number": 4},
        ]
        daily = MODULE.aggregate_period(rows, "day")
        self.assertEqual([x["period_utc"] for x in daily], ["2026-10-01", "2026-10-02"])
        self.assertEqual([x["total_R"] for x in daily], [1.0, -0.5])
        self.assertEqual(daily[1]["period_end_drawdown_R"], 0.0)

    def test_drawdown_and_profit_factor_are_deterministic(self):
        self.assertEqual(MODULE.max_drawdown([1.0, -0.5, -1.0, 0.75]), 1.5)
        self.assertEqual(MODULE.profit_factor([2.0, -1.0, -1.0]), 1.0)
        self.assertEqual(MODULE.profit_factor([1.0]), "INF")
        self.assertIsNone(MODULE.profit_factor([0.0]))

    def test_csv_reader_counts_unresolved_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trades.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=[
                    "setup_time_utc", "entry_time_utc", "exit_time_utc", "direction", "exit_reason", "r_multiple", "status"
                ])
                writer.writeheader()
                writer.writerow({
                    "setup_time_utc": "2026-10-01T10:00:00Z",
                    "entry_time_utc": "2026-10-01T10:01:00Z",
                    "exit_time_utc": "2026-10-01T10:02:00Z",
                    "direction": "BUY", "exit_reason": "TP", "r_multiple": "2.0", "status": "CLOSED"
                })
                writer.writerow({
                    "setup_time_utc": "2026-10-01T11:00:00Z",
                    "entry_time_utc": "2026-10-01T11:01:00Z",
                    "exit_time_utc": "", "direction": "SELL", "exit_reason": "OPEN_AT_END_OF_DATA",
                    "r_multiple": "", "status": "UNRESOLVED"
                })
            rows, digest = MODULE.load_trades(path, "test")
            summary = MODULE.summarize(rows)
            self.assertEqual(len(digest), 64)
            self.assertEqual(summary["candidate_rows"], 2)
            self.assertEqual(summary["closed_rows"], 1)
            self.assertEqual(summary["unresolved_or_unscored_rows"], 1)
            self.assertEqual(summary["total_R"], 2.0)


if __name__ == "__main__":
    unittest.main()
