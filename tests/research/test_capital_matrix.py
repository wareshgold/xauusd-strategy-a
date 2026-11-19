from decimal import Decimal
import unittest

from research.capital_matrix.matrix import (
    BrokerSpec, Family, INITIAL_CAPITAL, build_matrix, matrix_counts,
    risk_budget, size_leg, size_run,
)


class CapitalMatrixTests(unittest.TestCase):
    def setUp(self):
        self.broker = BrokerSpec(
            tick_size=Decimal("0.01"),
            tick_value_per_lot=Decimal("1"),
            volume_min=Decimal("0.01"),
            volume_max=Decimal("100"),
            volume_step=Decimal("0.01"),
        )

    def test_matrix_has_exactly_89_unique_primary_runs(self):
        runs = build_matrix()
        self.assertEqual(len(runs), 89)
        self.assertEqual(len({r.run_id for r in runs}), 89)
        exact = next(r for r in runs if r.family is Family.EXACT_RUNNER)
        self.assertEqual(exact.runner_profile.trail_activation_price, Decimal("0.40"))
        self.assertEqual(exact.runner_profile.trail_distance_price, Decimal("0.40"))
        self.assertEqual(exact.runner_profile.take_profit_r, Decimal("4"))
        self.assertEqual(matrix_counts(runs), {
            "FIXED_TP": 40, "DUAL_INDEPENDENT": 40,
            "EXACT_RUNNER": 1, "NORMALIZED_RUNNER": 8, "TOTAL": 89,
        })

    def test_matrix_is_deterministic(self):
        self.assertEqual(build_matrix(), build_matrix())

    def test_compound_and_fixed_base_diverge_after_equity_change(self):
        compound = risk_budget(
            initial_capital=INITIAL_CAPITAL, current_equity=Decimal("1200"),
            risk_fraction=Decimal("0.005"), sizing_mode="COMPOUND",
        )
        fixed = risk_budget(
            initial_capital=INITIAL_CAPITAL, current_equity=Decimal("1200"),
            risk_fraction=Decimal("0.005"), sizing_mode="FIXED_BASE",
        )
        self.assertEqual(compound, Decimal("6.000"))
        self.assertEqual(fixed, Decimal("5.000"))

    def test_dual_legs_split_aggregate_budget_not_double_it(self):
        run = next(r for r in build_matrix()
                   if r.family is Family.DUAL_INDEPENDENT
                   and r.sizing_mode == "FIXED_BASE"
                   and r.risk_fraction == Decimal("0.005"))
        legs = size_run(
            run, initial_capital=INITIAL_CAPITAL, current_equity=INITIAL_CAPITAL,
            stop_distance_price=Decimal("1"), broker=self.broker,
        )
        self.assertEqual(len(legs), 2)
        self.assertEqual(sum(x.requested_risk_usd for x in legs), Decimal("5"))
        self.assertEqual(sum(x.actual_risk_usd for x in legs), Decimal("5.00"))

    def test_volume_is_rounded_down_and_never_over_budget(self):
        leg = size_leg(
            budget_usd=Decimal("5.009"),
            stop_distance_price=Decimal("1"),
            broker=self.broker,
        )
        self.assertTrue(leg.feasible)
        self.assertEqual(leg.volume_lots, Decimal("0.05"))
        self.assertLessEqual(leg.actual_risk_usd, leg.requested_risk_usd)

    def test_infeasible_below_minimum_volume_is_explicit(self):
        tiny = BrokerSpec(
            tick_size=Decimal("0.01"), tick_value_per_lot=Decimal("100"),
            volume_min=Decimal("0.01"), volume_max=Decimal("10"),
            volume_step=Decimal("0.01"),
        )
        leg = size_leg(
            budget_usd=Decimal("0.1"), stop_distance_price=Decimal("10"),
            broker=tiny,
        )
        self.assertFalse(leg.feasible)
        self.assertEqual(leg.reason, "RISK_BUDGET_BELOW_MINIMUM_VOLUME")

    def test_exact_runner_is_fixed_volume_reference_not_risk_normalized(self):
        run = next(r for r in build_matrix() if r.family is Family.EXACT_RUNNER)
        legs = size_run(
            run, initial_capital=INITIAL_CAPITAL, current_equity=INITIAL_CAPITAL,
            stop_distance_price=Decimal("1"), broker=self.broker,
        )
        self.assertEqual(len(legs), 1)
        self.assertEqual(legs[0].volume_lots, Decimal("0.01"))
        self.assertEqual(legs[0].reason, "EXACT_REFERENCE_VOLUME")

    def test_invalid_risk_and_broker_metadata_fail_closed(self):
        with self.assertRaises(ValueError):
            risk_budget(
                initial_capital=INITIAL_CAPITAL, current_equity=INITIAL_CAPITAL,
                risk_fraction=Decimal("0"), sizing_mode="COMPOUND",
            )
        with self.assertRaises(ValueError):
            BrokerSpec(*(Decimal("0"),) * 5)


if __name__ == "__main__":
    unittest.main()
