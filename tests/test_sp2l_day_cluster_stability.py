import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_sp2l_day_cluster_stability import (
    daily_aggregates,
    direction_day_report,
    summarize_rr,
)


def row(day, direction, delta, actual=0.0):
    return {
        "day": day,
        "direction": direction,
        "actual_net": actual,
        "deltas": {rr: delta for rr in range(1, 7)},
    }


class DayClusterStabilityTests(unittest.TestCase):
    def test_daily_aggregation_counts_signs_and_sums(self):
        rows = [
            row("D01", "BUY", 2.0),
            row("D01", "SELL", -1.0),
            row("D02", "BUY", 3.0),
        ]
        daily = daily_aggregates(rows)
        self.assertEqual(daily["D01"]["n"], 2)
        self.assertEqual(daily["D01"]["buy_n"], 1)
        self.assertEqual(daily["D01"]["sell_n"], 1)
        self.assertEqual(daily["D01"]["rr"]["RR1"]["delta_sum_usd"], 1.0)
        self.assertEqual(daily["D01"]["rr"]["RR1"]["positive_trade_n"], 1)
        self.assertEqual(daily["D01"]["rr"]["RR1"]["negative_trade_n"], 1)

    def test_equal_day_and_trade_weighted_means_are_distinct(self):
        rows = [
            row("D01", "BUY", 10.0),
            row("D01", "SELL", 10.0),
            row("D01", "BUY", 10.0),
            row("D02", "SELL", -2.0),
        ]
        daily = daily_aggregates(rows)
        summary = summarize_rr(rows, daily)["RR1"]
        self.assertEqual(summary["trade_weighted_mean_delta_usd"], 7.0)
        self.assertEqual(summary["equal_weight_day_mean_delta_usd"], 4.0)
        self.assertEqual(summary["positive_day_n"], 1)
        self.assertEqual(summary["negative_day_n"], 1)

    def test_lodo_removes_exact_day_and_recomputes(self):
        rows = [
            row("D01", "BUY", 10.0),
            row("D02", "BUY", 2.0),
            row("D03", "SELL", -4.0),
            row("D04", "SELL", 0.0),
        ]
        daily = daily_aggregates(rows)
        summary = summarize_rr(rows, daily)["RR1"]
        self.assertEqual(summary["leave_one_day_out"]["D01"]["trade_weighted_mean_delta_usd"], -0.6667)
        self.assertEqual(summary["leave_one_day_out"]["D03"]["trade_weighted_mean_delta_usd"], 4.0)

    def test_day_contribution_shares_sum_to_one_when_defined(self):
        rows = [
            row("D01", "BUY", 2.0),
            row("D02", "SELL", 3.0),
        ]
        daily = daily_aggregates(rows)
        summary = summarize_rr(rows, daily)["RR1"]
        shares = [
            value["share_of_total_delta_sum"]
            for value in summary["day_contribution"].values()
        ]
        self.assertAlmostEqual(sum(shares), 1.0)

    def test_zero_total_delta_has_null_contribution_shares(self):
        rows = [
            row("D01", "BUY", 2.0),
            row("D02", "SELL", -2.0),
        ]
        daily = daily_aggregates(rows)
        summary = summarize_rr(rows, daily)["RR1"]
        self.assertIsNone(summary["day_contribution"]["D01"]["share_of_total_delta_sum"])
        self.assertIsNone(summary["day_contribution"]["D02"]["share_of_total_delta_sum"])

    def test_direction_report_keeps_day_cells_separate(self):
        rows = [
            row("D01", "BUY", 2.0),
            row("D01", "SELL", -3.0),
            row("D02", "BUY", -1.0),
        ]
        daily = daily_aggregates(rows)
        report = direction_day_report(rows, daily)
        self.assertEqual(report["BUY"]["trade_n"], 2)
        self.assertEqual(report["SELL"]["trade_n"], 1)
        self.assertEqual(report["BUY"]["rr_summary"]["RR1"]["positive_day_n"], 1)
        self.assertEqual(report["BUY"]["rr_summary"]["RR1"]["negative_day_n"], 1)
        self.assertEqual(report["SELL"]["by_day"]["D02"]["n"], 0)

    def test_only_four_day_clusters_and_no_cluster_ci(self):
        rows = [
            row("D01", "BUY", 1.0),
            row("D02", "BUY", 1.0),
            row("D03", "SELL", -1.0),
            row("D04", "SELL", -1.0),
        ]
        daily = daily_aggregates(rows)
        summary = summarize_rr(rows, daily)["RR1"]
        self.assertEqual(summary["cluster_inference_status"], "NOT_ESTIMATED_ONLY_4_DAY_CLUSTERS")
        self.assertFalse(summary["iid_trade_bootstrap_used"])


if __name__ == "__main__":
    unittest.main()
