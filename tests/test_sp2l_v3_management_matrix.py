import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_sp2l_v3_xauusd_management_matrix import simulate


class PartialRunnerAccountingTests(unittest.TestCase):
    def setUp(self):
        self.candidate = {
            "direction": "BUY",
            "theoretical_entry": 100.0,
            "sl": 99.0,
            "tp": 102.0,
            "risk": 1.0,
            "trigger_time": 1,
        }

    def test_stop_before_partial_target_counts_full_position_loss(self):
        bars = [
            {"time": 1, "open": 100.0, "high": 100.2, "low": 99.8, "close": 100.0},
            {"time": 2, "open": 100.0, "high": 100.5, "low": 98.8, "close": 99.0},
        ]
        result = simulate(bars, self.candidate, 0, "PARTIAL_RUNNER", 2.0, 1.0, 1.5)
        self.assertEqual(result["reason"], "SL")
        self.assertFalse(result["partial_done"])
        self.assertAlmostEqual(result["realized_R"], -1.0)

    def test_stop_after_partial_target_applies_half_runner_exposure(self):
        bars = [
            {"time": 1, "open": 100.0, "high": 100.2, "low": 99.8, "close": 100.0},
            {"time": 2, "open": 100.0, "high": 101.6, "low": 99.5, "close": 101.0},
            {"time": 3, "open": 100.0, "high": 100.2, "low": 98.8, "close": 99.0},
        ]
        result = simulate(bars, self.candidate, 0, "PARTIAL_RUNNER", 2.0, 1.0, 1.5)
        self.assertEqual(result["reason"], "SL")
        self.assertTrue(result["partial_done"])
        self.assertAlmostEqual(result["realized_R"], 0.25)

if __name__ == "__main__":
    unittest.main()
