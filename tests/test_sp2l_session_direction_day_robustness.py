from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import analyze_sp2l_session_direction_day_robustness as analysis


def row(day, delta=1.0):
    return {
        "day_bucket": day,
        "direction": "BUY",
        "actual_net": 0.25,
        "deltas": {rr: delta for rr in analysis.RRS},
        "memberships": {},
    }


class SessionDirectionDayRobustnessTests(unittest.TestCase):
    def test_bootstrap_is_deterministic(self):
        first = analysis.bootstrap_ci([1.0, 2.0, 3.0, 4.0], 123)
        second = analysis.bootstrap_ci([1.0, 2.0, 3.0, 4.0], 123)
        self.assertEqual(first, second)

    def test_bootstrap_skips_single_observation(self):
        self.assertIsNone(analysis.bootstrap_ci([1.0], 123))

    def test_primary_gate_blocks_small_groups_and_intervals(self):
        rows = [row("D01") for _ in range(19)]
        result = analysis.summarize(rows, "small", min_n=20, min_days=3)
        self.assertFalse(result["screen_sample_gate_pass"])
        self.assertIsNone(
            result["paired_deltas"]["RR1"]["bootstrap_iid_95pct_ci_mean_usd"]
        )

    def test_gate_requires_distinct_days(self):
        rows = [row("D01") for _ in range(20)]
        result = analysis.summarize(rows, "one-day", min_n=20, min_days=3)
        self.assertFalse(result["screen_sample_gate_pass"])

    def test_eligible_group_gets_reproducible_interval(self):
        rows = [row(f"D{(i % 3) + 1:02d}", float(i)) for i in range(20)]
        first = analysis.summarize(rows, "eligible", min_n=20, min_days=3)
        second = analysis.summarize(rows, "eligible", min_n=20, min_days=3)
        self.assertTrue(first["screen_sample_gate_pass"])
        self.assertEqual(
            first["paired_deltas"]["RR1"]["bootstrap_iid_95pct_ci_mean_usd"],
            second["paired_deltas"]["RR1"]["bootstrap_iid_95pct_ci_mean_usd"],
        )

    def test_leave_one_day_out_keeps_remaining_sample_count(self):
        rows = [row("D01"), row("D02"), row("D03")]
        result = analysis.day_sensitivity(rows)
        self.assertEqual(result["D01"]["remaining_n"], 2)
        self.assertEqual(result["D02"]["remaining_n"], 2)
        self.assertEqual(result["D03"]["remaining_n"], 2)


if __name__ == "__main__":
    unittest.main()
