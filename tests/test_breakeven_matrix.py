import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_sp2l_v3_xauusd_breakeven_matrix import simulate


class BreakEvenMatrixTests(unittest.TestCase):
    def setUp(self):
        self.candidate = {
            "direction": "BUY",
            "theoretical_entry": 100.0,
            "sl": 99.0,
            "tp": 102.0,
            "risk": 1.0,
            "trigger_time": 100,
        }

    def test_lock_five_cents_is_hit_on_next_bar_not_activation_bar(self):
        bars = [
            {"time": 100, "open": 100.0, "high": 100.2, "low": 99.8, "close": 100.0},
            {"time": 160, "open": 100.0, "high": 100.6, "low": 100.0, "close": 100.4},
            {"time": 220, "open": 100.3, "high": 100.4, "low": 100.04, "close": 100.1},
        ]
        row = simulate(bars, self.candidate, 0, 0.5, 0.05)
        self.assertEqual(row["exit_time"], 220)
        self.assertAlmostEqual(row["exit_price"], 100.05)
        self.assertEqual(row["reason"], "BREAK_EVEN_SL")
        self.assertTrue(row["stop_moved"])
        self.assertAlmostEqual(row["realized_R"], 0.05)

    def test_plain_break_even_exits_at_entry(self):
        bars = [
            {"time": 100, "open": 100.0, "high": 100.2, "low": 99.8, "close": 100.0},
            {"time": 160, "open": 100.0, "high": 100.6, "low": 100.1, "close": 100.4},
            {"time": 220, "open": 100.2, "high": 100.4, "low": 99.99, "close": 100.1},
        ]
        row = simulate(bars, self.candidate, 0, 0.5, 0.0)
        self.assertEqual(row["exit_time"], 220)
        self.assertAlmostEqual(row["exit_price"], 100.0)
        self.assertAlmostEqual(row["realized_R"], 0.0)

    def test_sell_lock_is_below_entry(self):
        candidate = dict(self.candidate, direction="SELL", theoretical_entry=100.0,
                         sl=101.0, tp=98.0)
        bars = [
            {"time": 100, "open": 100.0, "high": 100.2, "low": 99.8, "close": 100.0},
            {"time": 160, "open": 100.0, "high": 99.9, "low": 99.4, "close": 99.6},
            {"time": 220, "open": 99.7, "high": 99.96, "low": 99.5, "close": 99.8},
        ]
        row = simulate(bars, candidate, 0, 0.5, 0.05)
        self.assertEqual(row["exit_time"], 220)
        self.assertAlmostEqual(row["exit_price"], 99.95)
        self.assertAlmostEqual(row["realized_R"], 0.05)


if __name__ == "__main__":
    unittest.main()
