from __future__ import annotations

import unittest

import numpy as np

from research.capital_matrix.trade_behavior_analyzer import (
    TICK_DTYPE, compute_path_metrics, reconstruct_fill,
)


def ticks(rows):
    return np.array(rows, dtype=TICK_DTYPE)


class TradeBehaviorAnalyzerTests(unittest.TestCase):
    def test_buy_uses_bid_for_excursions_and_threshold_times(self):
        data = ticks([
            (1000, 9990, 10010),
            (2000, 10050, 10070),
            (3000, 10100, 10120),
            (4000, 10020, 10040),
        ])
        result = compute_path_metrics(
            data, "BUY", fill_ticks=10000, risk_ticks=100,
            start_ms=1000, end_ms=4000,
        )
        self.assertAlmostEqual(result["mfe_r"], 1.0)
        self.assertAlmostEqual(result["mae_r"], 0.1)
        self.assertEqual(result["time_to_plus_0_5r_seconds"], 1.0)
        self.assertEqual(result["time_to_plus_1_0r_seconds"], 2.0)
        self.assertIsNone(result["time_to_minus_0_5r_seconds"])

    def test_sell_uses_ask_for_excursions(self):
        data = ticks([
            (1000, 9990, 10010),
            (2000, 9940, 9950),
            (3000, 9890, 9900),
            (4000, 9970, 9980),
        ])
        result = compute_path_metrics(
            data, "SELL", fill_ticks=10000, risk_ticks=100,
            start_ms=1000, end_ms=4000,
        )
        self.assertAlmostEqual(result["mfe_r"], 1.0)
        self.assertAlmostEqual(result["mae_r"], 0.1)

    def test_gap_crossing_trade_interval_is_flagged(self):
        data = ticks([
            (1000, 10000, 10002),
            (2000, 10001, 10003),
            (70001, 10002, 10004),
            (71000, 10003, 10005),
        ])
        result = compute_path_metrics(
            data, "BUY", fill_ticks=10000, risk_ticks=100,
            start_ms=1000, end_ms=71000,
        )
        self.assertEqual(result["tick_gap_count_gt_60s"], 1)
        self.assertTrue(result["tick_gap_exposed"])

    def test_gap_before_fill_is_not_counted_as_trade_exposure(self):
        data = ticks([
            (0, 10000, 10002),
            (61001, 10001, 10003),
            (62000, 10002, 10004),
        ])
        result = compute_path_metrics(
            data, "BUY", fill_ticks=10000, risk_ticks=100,
            start_ms=61001, end_ms=62000,
        )
        self.assertEqual(result["tick_gap_count_gt_60s"], 0)

    def test_fill_reconstruction_uses_first_eligible_executable_quote(self):
        data = ticks([
            (1000, 10000, 10002),
            (1000, 9999, 10001),
            (1000, 9998, 9999),
        ])
        self.assertEqual(reconstruct_fill(data, 1000, "BUY", 10000), 9999)
        self.assertEqual(reconstruct_fill(data, 1000, "SELL", 10000), 10000)

    def test_missing_fill_tick_is_not_guessed(self):
        data = ticks([(1000, 10000, 10002), (2000, 10001, 10003)])
        self.assertIsNone(reconstruct_fill(data, 1500, "BUY", 10000))


if __name__ == "__main__":
    unittest.main()
