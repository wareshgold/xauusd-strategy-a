import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "analyze_sp2l_v3_trailing_matrix_costs.py"
SPEC = importlib.util.spec_from_file_location("trailing_matrix_costs", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def trade(gross_r, risk_price=10.0, ambiguous="False", exit_time="100", trigger_time="1"):
    return {
        "scenario": "TRAILING",
        "activation_price": "0.05",
        "trail_distance_price": "0.04",
        "risk_price": str(risk_price),
        "realized_R": "" if gross_r is None else str(gross_r),
        "exit_time": exit_time,
        "trigger_time": trigger_time,
        "ambiguous": ambiguous,
    }


class TrailingMatrixCostAuditTests(unittest.TestCase):
    def test_fixed_round_trip_cost_is_converted_to_r_using_dollar_risk(self):
        rows = [trade(1.0, risk_price=10.0)]
        result = MODULE.summarize_net(rows, cost_usd=0.05, volume=0.01, contract_size=100.0)
        self.assertAlmostEqual(float(rows[0]["risk_usd"]), 10.0)
        self.assertAlmostEqual(float(rows[0]["cost_R"]), 0.005)
        self.assertAlmostEqual(float(rows[0]["net_R"]), 0.995)
        self.assertAlmostEqual(result["net_R"], 0.995)

    def test_cost_can_turn_a_small_gross_winner_into_a_net_loss(self):
        rows = [trade(0.003, risk_price=10.0)]
        result = MODULE.summarize_net(rows, cost_usd=0.05, volume=0.01, contract_size=100.0)
        self.assertEqual(rows[0]["net_outcome"], "LOSS")
        self.assertEqual(result["net_wins"], 0)
        self.assertEqual(result["net_losses"], 1)

    def test_ambiguous_and_unresolved_rows_are_not_given_guessed_net_results(self):
        rows = [trade(1.0, ambiguous="True"), trade(None)]
        result = MODULE.summarize_net(rows, cost_usd=0.05, volume=0.01, contract_size=100.0)
        self.assertEqual(result["net_decisive"], 0)
        self.assertEqual(rows[0]["net_outcome"], "AMBIGUOUS")
        self.assertEqual(rows[1]["net_outcome"], "UNRESOLVED")
        self.assertEqual(rows[0]["cost_usd"], "")
        self.assertEqual(rows[1]["cost_usd"], "")

    def test_cost_is_charged_once_per_completed_decisive_trade(self):
        rows = [trade(1.0), trade(-1.0, trigger_time="2", exit_time="101")]
        result = MODULE.summarize_net(rows, cost_usd=0.05, volume=0.01, contract_size=100.0)
        self.assertEqual(result["costed_trades"], 2)
        self.assertAlmostEqual(result["total_cost_usd"], 0.10)
        self.assertEqual(result["net_wins"], 1)
        self.assertEqual(result["net_losses"], 1)


if __name__ == "__main__":
    unittest.main()
