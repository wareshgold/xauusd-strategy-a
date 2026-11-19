import unittest
from decimal import Decimal

from research.capital_matrix.matrix import BrokerSpec
from research.capital_matrix.partial_matrix import (
    PartialExit, build_partial_matrix, size_partial_run,
)
from research.capital_matrix.replay_v31_partial_matrix import (
    PartialPortfolio, process_tick,
)

BROKER = BrokerSpec(Decimal("0.01"), Decimal("1"), Decimal("0.01"),
                    Decimal("100"), Decimal("0.01"))


class PartialMatrixDefinitionTests(unittest.TestCase):
    def test_matrix_has_three_fixed_and_twenty_four_normalized_variants(self):
        runs = build_partial_matrix()
        self.assertEqual(len(runs), 27)
        self.assertEqual(len({r.run_id for r in runs}), 27)
        self.assertEqual(sum(r.fixed_volume_reference for r in runs), 3)
        self.assertEqual(sum(not r.fixed_volume_reference for r in runs), 24)

    def test_fixed_reference_is_two_equal_minimum_lot_legs(self):
        run = next(r for r in build_partial_matrix() if r.fixed_volume_reference)
        sized = size_partial_run(
            run, initial_capital=Decimal("1000"), current_equity=Decimal("1000"),
            stop_distance_price=Decimal("2"), broker=BROKER,
        )
        self.assertTrue(sized.feasible)
        self.assertEqual(sized.total_lots, Decimal("0.02"))
        self.assertEqual(sized.leg_lots, Decimal("0.01"))

    def test_risk_normalized_size_rounds_down_to_two_equal_legs(self):
        run = next(r for r in build_partial_matrix()
                   if r.sizing_mode == "FIXED_BASE"
                   and r.risk_fraction == Decimal("0.01")
                   and r.exit_mode is PartialExit.TP2_2R)
        sized = size_partial_run(
            run, initial_capital=Decimal("1000"), current_equity=Decimal("1000"),
            stop_distance_price=Decimal("2"), broker=BROKER,
        )
        self.assertTrue(sized.feasible)
        self.assertEqual(sized.total_lots, Decimal("0.04"))
        self.assertEqual(sized.leg_lots, Decimal("0.02"))
        self.assertLessEqual(sized.actual_risk_usd, sized.requested_risk_usd)

    def test_too_small_budget_is_infeasible_not_rounded_up(self):
        run = next(r for r in build_partial_matrix()
                   if r.sizing_mode == "FIXED_BASE"
                   and r.risk_fraction == Decimal("0.0025")
                   and r.exit_mode is PartialExit.TP2_2R)
        sized = size_partial_run(
            run, initial_capital=Decimal("1000"), current_equity=Decimal("1000"),
            stop_distance_price=Decimal("2"), broker=BROKER,
        )
        self.assertFalse(sized.feasible)
        self.assertEqual(sized.total_lots, Decimal("0"))


class PartialExecutionTests(unittest.TestCase):
    def _portfolio(self):
        run = next(r for r in build_partial_matrix()
                   if r.fixed_volume_reference and r.exit_mode is PartialExit.TP2_2R)
        p = PartialPortfolio(run)
        p.position = {
            "row": {"entry_time_utc":"2026-01-01T00:00:00Z","direction":"BUY"},
            "fill_ms": 1000, "fill_price":4000.0, "theoretical_entry":4000.0,
            "initial_sl":3998.0, "sl":3998.0, "tp1":4002.0, "tp2":4004.0,
            "first_lots":0.01, "remaining_lots":0.02, "first_done":False,
            "actual_initial_risk_price":2.0, "requested_risk_usd":4.0,
            "sizing_actual_risk_usd":4.0, "submission_ms":900,
            "trail_active":False, "favorable_extreme":4000.0,
            "gap_exposed":False, "is_runner":False,
        }
        p.state = "OPEN"
        return p

    def test_tp1_closes_first_001_and_leaves_second_001(self):
        p = self._portfolio()
        process_tick(p, 2000, 4002.1, 4002.2)
        self.assertIsNotNone(p.position)
        self.assertTrue(p.position["first_done"])
        self.assertAlmostEqual(p.position["remaining_lots"], 0.01)
        self.assertEqual(p.counts["PARTIAL_LEG_CLOSED"], 1)
        self.assertAlmostEqual(float(p.equity), 1002.1, places=6)

    def test_tp2_closes_remaining_leg_and_completes_trade(self):
        p = self._portfolio()
        process_tick(p, 2000, 4002.1, 4002.2)
        process_tick(p, 3000, 4004.1, 4004.2)
        self.assertIsNone(p.position)
        self.assertEqual(p.counts["PARTIAL_LEG_CLOSED"], 1)
        self.assertEqual(p.counts["FILLED_AND_CLOSED"], 1)
        self.assertAlmostEqual(float(p.equity), 1004.2, places=6)

    def test_stop_before_tp1_closes_full_002_position(self):
        p = self._portfolio()
        process_tick(p, 2000, 3997.9, 3998.0)
        self.assertIsNone(p.position)
        self.assertEqual(p.counts["FILLED_AND_CLOSED"], 1)
        closed = [r for r in p.rows if r["status"] == "FILLED_AND_CLOSED"]
        self.assertAlmostEqual(closed[0]["lots"], 0.02)
        self.assertAlmostEqual(float(p.equity), 995.8, places=6)


if __name__ == "__main__":
    unittest.main()
