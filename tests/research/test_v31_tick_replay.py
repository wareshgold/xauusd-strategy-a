import unittest
from datetime import datetime, timezone

from research.capital_matrix.matrix import build_matrix, Family
from research.capital_matrix.replay_v31_tick_matrix import (
    Portfolio, round_price, parse_utc_epoch, process_candidate_due,
    fill_pending, LATENCY_SECONDS,
)


class ReplayContractTests(unittest.TestCase):
    def test_executable_run_population_is_49_and_dual_is_blocked(self):
        runs = build_matrix()
        executable = [r for r in runs if r.family in
                      (Family.FIXED_TP, Family.EXACT_RUNNER, Family.NORMALIZED_RUNNER)]
        dual = [r for r in runs if r.family is Family.DUAL_INDEPENDENT]
        self.assertEqual(len(runs), 89)
        self.assertEqual(len(executable), 49)
        self.assertEqual(len(dual), 40)

    def test_price_rounding_is_conservative_on_tick_grid(self):
        self.assertEqual(round_price(4012.347, 0.01, "BUY"), 4012.34)
        self.assertEqual(round_price(4012.343, 0.01, "SELL"), 4012.35)

    def test_candidate_submits_after_bar_close_and_declared_latency(self):
        run = next(r for r in build_matrix() if r.family is Family.FIXED_TP)
        p = Portfolio(run)
        ts = 1790000000
        row = {
            "entry_time_utc": datetime.fromtimestamp(ts, timezone.utc).isoformat().replace("+00:00","Z"),
            "direction":"BUY","entry_proxy":"4000","sl_initial":"3998",
            "risk_price":"2","target":"4008",
        }
        due = (ts + 60 + int(LATENCY_SECONDS))*1000
        process_candidate_due(p, [row], due-1, 3999.0, 4001.0, 2000)
        self.assertEqual(p.state, "FLAT")
        process_candidate_due(p, [row], due, 3999.0, 4001.0, 2000)
        self.assertEqual(p.state, "PENDING")
        self.assertEqual(p.pending["submit_ms"], due)

    def test_pending_order_expires_before_late_quote_can_fill(self):
        run = next(r for r in build_matrix() if r.family is Family.FIXED_TP)
        p = Portfolio(run)
        row = {"entry_time_utc":"2026-01-01T00:00:00Z","direction":"BUY",
               "entry_proxy":"4000","sl_initial":"3998","risk_price":"2","target":"4008"}
        p.pending = {"row":row,"submit_ms":1000,"expires_ms":2000}
        p.state = "PENDING"
        fill_pending(p, 2000, 3998.0, 3999.0)
        self.assertEqual(p.state, "FLAT")
        self.assertIsNone(p.position)
        self.assertEqual(p.counts["UNFILLED_EXPIRED"], 1)

    def test_utc_parser_requires_aware_timestamp(self):
        self.assertEqual(parse_utc_epoch("1970-01-01T00:00:00Z"), 0)
        with self.assertRaises(ValueError):
            parse_utc_epoch("1970-01-01T00:00:00")


if __name__ == "__main__":
    unittest.main()
