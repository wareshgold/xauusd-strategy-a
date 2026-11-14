"""Synthetic regression fixtures for V3.1 final-bar trigger semantics.

Research-only tests. They assert the shared detector's current implementation;
they do not endorse it as canonical source geometry or alter runtime behavior.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sp2l_v3_1_rr4_act40_config as cfg


class TestFinalArrayElementCanTrigger(unittest.TestCase):
    def test_buy_final_array_bar_is_included_and_stamped(self):
        candles = [
            {"time": 0, "low": 90.0, "high": 100.0},
            {"time": 60, "low": 95.0, "high": 101.0},
            {"time": 120, "low": 100.0, "high": 102.0},
            {"time": 180, "low": 99.0, "high": 103.0},
        ]

        result = cfg.find_first_entry(
            candles, 2, {"direction": "BUY", "symbol": "XAUUSD.ecn"}
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["direction"], "BUY")
        self.assertEqual(result["trigger_time"], candles[-1]["time"])
        self.assertEqual(result["theoretical_entry"], candles[-1]["low"])

    def test_sell_final_array_bar_is_included_and_stamped(self):
        candles = [
            {"time": 0, "low": 100.0, "high": 110.0},
            {"time": 60, "low": 99.0, "high": 105.0},
            {"time": 120, "low": 98.0, "high": 100.0},
            {"time": 180, "low": 97.0, "high": 101.0},
        ]

        result = cfg.find_first_entry(
            candles, 2, {"direction": "SELL", "symbol": "XAUUSD.ecn"}
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["direction"], "SELL")
        self.assertEqual(result["trigger_time"], candles[-1]["time"])
        self.assertEqual(result["theoretical_entry"], candles[-1]["high"])

    def test_no_trigger_when_final_bar_does_not_break_previous_extreme(self):
        buy_candles = [
            {"time": 0, "low": 90.0, "high": 100.0},
            {"time": 60, "low": 95.0, "high": 101.0},
            {"time": 120, "low": 100.0, "high": 102.0},
            {"time": 180, "low": 100.0, "high": 103.0},
        ]
        sell_candles = [
            {"time": 0, "low": 100.0, "high": 110.0},
            {"time": 60, "low": 99.0, "high": 105.0},
            {"time": 120, "low": 98.0, "high": 100.0},
            {"time": 180, "low": 97.0, "high": 100.0},
        ]

        self.assertIsNone(
            cfg.find_first_entry(
                buy_candles, 2, {"direction": "BUY", "symbol": "XAUUSD.ecn"}
            )
        )
        self.assertIsNone(
            cfg.find_first_entry(
                sell_candles, 2, {"direction": "SELL", "symbol": "XAUUSD.ecn"}
            )
        )


if __name__ == "__main__":
    unittest.main()
