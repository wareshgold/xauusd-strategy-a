import unittest
import csv
import gzip
import tempfile
from pathlib import Path
from datetime import datetime, timezone

from research.capital_matrix.matrix import build_matrix, Family
from research.capital_matrix.replay_v31_tick_matrix import (
    Portfolio, round_price, parse_utc_epoch, process_candidate_due,
    fill_pending, LATENCY_SECONDS, run_replay,
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

    def test_stream_replay_executes_first_fixed_tp_on_quote_sides(self):
        ts = 1767225600
        row = {"entry_time_utc":"2026-01-01T00:00:00Z","direction":"BUY",
               "entry_proxy":"4000","sl_initial":"3998","risk_price":"2",
               "target":"4008"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ticks.csv.gz"
            ticks = [
                [ts*1000+62000,"2026-01-01T00:01:02Z",3999.0,4001.0,0,0,0],
                [ts*1000+63000,"2026-01-01T00:01:03Z",3998.5,3999.5,0,0,0],
                [ts*1000+64000,"2026-01-01T00:01:04Z",4002.1,4002.2,0,0,0],
            ]
            with gzip.open(path,"wt",encoding="utf-8",newline="") as f:
                w=csv.writer(f);w.writerow(["time_msc","time_utc","bid","ask","last","volume","flags"]);w.writerows(ticks)
            portfolios,stats=run_replay([row],[],path,2.0)
        first=portfolios[0]
        closed=[x for x in first.rows if x.get("status")=="FILLED_AND_CLOSED"]
        self.assertEqual(len(closed),1)
        self.assertEqual(closed[0]["exit_reason"],"TP")
        self.assertEqual(closed[0]["fill_price"],3999.5)
        self.assertEqual(closed[0]["exit_price"],4002.1)
        self.assertAlmostEqual(closed[0]["gross_pnl_usd"],2.6,places=6)
        self.assertEqual(stats["tick_rows"],3)


if __name__ == "__main__":
    unittest.main()
