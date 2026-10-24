"""Synthetic source-fidelity checks for the Strategy B candidate detector.

These tests import only the research replay harness. They never import the live
Strategy B runner or MetaTrader5 and cannot submit orders.
"""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "research" / "compare_rr2_trail4_vs_strategy_b_monthly.py"
SPEC = importlib.util.spec_from_file_location("monthly_compare_harness", SCRIPT)
HARNESS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HARNESS)


class StrategyBCandidateSourceFidelityTests(unittest.TestCase):
    def test_buy_spike_compares_only_to_pre_and_post_spike_bodies(self):
        # The detection candle body is intentionally larger than the spike's
        # 2.0 body / 1.5. Source detection checks its LOW against the prior
        # candle, but does not compare its body against the spike body.
        bars = [
            {"time": 0, "open": 100.0, "high": 101.2, "low": 99.8, "close": 101.0},
            {"time": 60, "open": 101.5, "high": 104.1, "low": 101.4, "close": 103.5},
            {"time": 120, "open": 104.5, "high": 105.1, "low": 104.4, "close": 105.0},
            {"time": 180, "open": 105.0, "high": 106.6, "low": 104.0, "close": 106.5},
        ]
        self.assertEqual(HARNESS.b_detect(bars, 3), "BUY")

    def test_sell_spike_compares_only_to_pre_and_post_spike_bodies(self):
        # Symmetric SELL fixture: current candle body is deliberately large,
        # while its HIGH establishes the detector's current-bar condition.
        bars = [
            {"time": 0, "open": 101.0, "high": 101.2, "low": 99.8, "close": 100.0},
            {"time": 60, "open": 100.0, "high": 100.1, "low": 97.9, "close": 98.0},
            {"time": 120, "open": 97.5, "high": 97.6, "low": 96.9, "close": 97.0},
            {"time": 180, "open": 97.0, "high": 98.0, "low": 95.4, "close": 95.5},
        ]
        self.assertEqual(HARNESS.b_detect(bars, 3), "SELL")


if __name__ == "__main__":
    unittest.main()
