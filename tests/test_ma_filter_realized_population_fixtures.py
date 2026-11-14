"""Synthetic fixtures for the MA realized-population research analyzer.

These tests use no MT5 connection and no user/account data.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "research" / "analyze_ma_filter_realized_population.py"
SPEC = importlib.util.spec_from_file_location("ma_realized_analyzer", SCRIPT)
ANALYZER = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(ANALYZER)


def deal(pid, ticket, entry, deal_type, time_msc, profit=0, commission=0, swap=0, fee=0):
    return {
        "position_id": str(pid), "ticket": str(ticket), "entry": str(entry),
        "type": str(deal_type), "time_msc": str(time_msc),
        "time": str(time_msc // 1000), "profit": str(profit),
        "commission": str(commission), "swap": str(swap), "fee": str(fee),
    }


class M1TimestampFixtures(unittest.TestCase):
    def test_duplicate_m1_timestamp_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            ANALYZER.inspect_m1_timestamps([0, 60, 60, 120])

    def test_out_of_order_m1_timestamp_is_rejected_not_silently_sorted(self):
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            ANALYZER.inspect_m1_timestamps([0, 120, 60])

    def test_m1_gap_is_reported_without_synthetic_fill_bars(self):
        gaps = ANALYZER.inspect_m1_timestamps([0, 60, 180, 240])
        self.assertEqual(gaps, [
            {"index": 2, "previous": 60, "current": 180, "seconds": 120}
        ])
        self.assertEqual(len([0, 60, 180, 240]), 4)

    def test_last_completed_bar_respects_exact_completion_boundary(self):
        times = [0, 60, 120]
        self.assertIsNone(ANALYZER.last_completed_m1_index(times, 59.999))
        self.assertEqual(ANALYZER.last_completed_m1_index(times, 60), 0)
        self.assertEqual(ANALYZER.last_completed_m1_index(times, 119.999), 0)
        self.assertEqual(ANALYZER.last_completed_m1_index(times, 120), 1)


class MovingAverageFixtures(unittest.TestCase):
    def test_sma_uses_full_period_seed_and_rolling_window(self):
        self.assertEqual(
            ANALYZER.moving_average([1, 2, 3, 4], 3),
            [None, None, 2.0, 3.0],
        )

    def test_ema_uses_sma_seed_then_recursive_update(self):
        result = ANALYZER.moving_average([1, 2, 3, 4], 3, exponential=True)
        self.assertEqual(result[:3], [None, None, 2.0])
        self.assertAlmostEqual(result[3], 3.0)

    def test_insufficient_history_is_unavailable_not_zero(self):
        self.assertEqual(ANALYZER.moving_average([1, 2], 3), [None, None])


class PositionGroupingFixtures(unittest.TestCase):
    def test_partial_exits_are_aggregated_once_per_position(self):
        rows = [
            deal(10, 1, 0, 0, 100_000, commission=-1),
            deal(10, 2, 1, 1, 150_000, profit=5, commission=-1),
            deal(10, 3, 1, 1, 160_000, profit=2, commission=-1, swap=0.5),
        ]
        closed, open_count, unresolved = ANALYZER.position_groups(rows)
        self.assertEqual((open_count, unresolved, len(closed)), (0, 0, 1))
        self.assertEqual(closed[0]["direction"], "BUY")
        self.assertEqual(closed[0]["entry_time"], 100.0)
        self.assertEqual(closed[0]["exit_time"], 160.0)
        self.assertAlmostEqual(closed[0]["net"], 4.5)

    def test_open_position_is_not_counted_as_closed(self):
        rows = [deal(20, 1, 0, 1, 200_000, commission=-0.5)]
        closed, open_count, unresolved = ANALYZER.position_groups(rows)
        self.assertEqual(closed, [])
        self.assertEqual((open_count, unresolved), (1, 0))

    def test_reversal_group_is_marked_unresolved(self):
        rows = [
            deal(30, 1, 0, 0, 100_000),
            deal(30, 2, 2, 1, 120_000, profit=3),
        ]
        closed, open_count, unresolved = ANALYZER.position_groups(rows)
        self.assertEqual(closed, [])
        self.assertEqual((open_count, unresolved), (0, 1))

    def test_unsupported_entry_direction_is_marked_unresolved(self):
        rows = [
            deal(40, 1, 0, 7, 100_000),
            deal(40, 2, 1, 1, 120_000, profit=1),
        ]
        closed, open_count, unresolved = ANALYZER.position_groups(rows)
        self.assertEqual(closed, [])
        self.assertEqual((open_count, unresolved), (0, 1))


class FilterClassificationFixtures(unittest.TestCase):
    def test_price_equal_to_ma_is_neutral_and_rejected(self):
        ma = {f"{kind}{period}": 100.0 for kind in ("SMA", "EMA") for period in (20, 50, 100, 200)}
        states = ANALYZER.classify("BUY", 100.0, ma)
        self.assertTrue(states["F00"])
        for key in ("F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08", "F09", "F10", "F11", "F12", "F13"):
            self.assertFalse(states[key])

    def test_missing_long_period_ma_does_not_remove_baseline_population(self):
        ma = {f"{kind}{period}": 100.0 for kind in ("SMA", "EMA") for period in (20, 50, 100, 200)}
        ma["EMA200"] = None
        states = ANALYZER.classify("SELL", 99.0, ma)
        self.assertTrue(states["F00"])
        self.assertIsNone(states["F08"])
        self.assertTrue(states["F01"])
        # EMA200 is not an input to F13; its missing value must not
        # make this composite filter unavailable.
        self.assertTrue(states["F13"])

    def test_f13_is_unavailable_when_no_known_input_passes_and_one_is_missing(self):
        ma = {
            "SMA20": 100.0, "SMA50": 100.0, "SMA100": 100.0, "SMA200": 100.0,
            "EMA20": 100.0, "EMA50": 100.0, "EMA100": None, "EMA200": 100.0,
        }
        # For SELL at 101, all known F13 inputs reject; EMA100 is unknown.
        states = ANALYZER.classify("SELL", 101.0, ma)
        self.assertIsNone(states["F13"])


if __name__ == "__main__":
    unittest.main()
