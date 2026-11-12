from __future__ import annotations

import unittest

from scripts.fati_rr1_be5_no_tp_policy_research import (
    FatiProtectionAction,
    FatiProtectionPolicy,
    evaluate_fati_protection,
)


class TestFatiRR1BE5NoTPResearch(unittest.TestCase):
    def setUp(self):
        # Synthetic fixture only; this is NOT an asserted broker pip size.
        self.policy = FatiProtectionPolicy(pip_size_price=0.10)

    def evaluate(self, **overrides):
        args = dict(
            policy=self.policy,
            direction="BUY",
            actual_fill_price=4000.0,
            initial_sl_price=3998.0,
            current_sl_price=3998.0,
            favorable_move_price=1.99,
            be_change_confirmed=False,
        )
        args.update(overrides)
        return evaluate_fati_protection(**args)

    def test_pip_size_is_mandatory_and_no_implicit_default_exists(self):
        with self.assertRaises(TypeError):
            FatiProtectionPolicy()

    def test_initial_order_has_no_take_profit(self):
        self.assertEqual(self.policy.initial_order_take_profit_price, 0.0)

    def test_be_offset_is_five_explicit_fixture_pips(self):
        self.assertAlmostEqual(self.policy.be_offset_price, 0.50)

    def test_waits_just_below_rr1(self):
        action, target = self.evaluate(favorable_move_price=1.999)
        self.assertEqual(action, FatiProtectionAction.WAIT_FOR_RR1)
        self.assertIsNone(target)

    def test_buy_requests_be_plus_five_at_rr1(self):
        action, target = self.evaluate(favorable_move_price=2.0)
        self.assertEqual(action, FatiProtectionAction.REQUEST_BE_PLUS_5_SL)
        self.assertAlmostEqual(target, 4000.50)

    def test_sell_requests_be_plus_five_at_rr1(self):
        action, target = self.evaluate(
            direction="SELL",
            actual_fill_price=4000.0,
            initial_sl_price=4002.0,
            current_sl_price=4002.0,
            favorable_move_price=2.0,
        )
        self.assertEqual(action, FatiProtectionAction.REQUEST_BE_PLUS_5_SL)
        self.assertAlmostEqual(target, 3999.50)

    def test_rr1_uses_actual_fill_not_an_assumed_requested_entry(self):
        action, target = self.evaluate(
            actual_fill_price=4000.20,
            initial_sl_price=3998.20,
            favorable_move_price=2.0,
        )
        self.assertEqual(action, FatiProtectionAction.REQUEST_BE_PLUS_5_SL)
        self.assertAlmostEqual(target, 4000.70)

    def test_rr1_risk_anchor_remains_the_original_sl(self):
        # Current SL is deliberately different; risk remains fill-to-initial-SL.
        action, _ = self.evaluate(
            current_sl_price=3999.50,
            favorable_move_price=1.99,
        )
        self.assertEqual(action, FatiProtectionAction.WAIT_FOR_RR1)

    def test_broker_rejection_does_not_mark_change_confirmed(self):
        args = dict(favorable_move_price=2.0, be_change_confirmed=False)
        self.assertEqual(
            self.evaluate(**args),
            self.evaluate(**args),
        )
        self.assertEqual(
            self.evaluate(**args)[0],
            FatiProtectionAction.REQUEST_BE_PLUS_5_SL,
        )

    def test_broker_confirmed_change_is_never_requested_again(self):
        action, target = self.evaluate(
            favorable_move_price=5.0,
            current_sl_price=4000.50,
            be_change_confirmed=True,
        )
        self.assertEqual(action, FatiProtectionAction.ALREADY_CONFIRMED)
        self.assertIsNone(target)

    def test_better_buy_sl_is_never_loosened(self):
        action, target = self.evaluate(
            favorable_move_price=2.0,
            current_sl_price=4000.60,
        )
        self.assertEqual(action, FatiProtectionAction.ALREADY_PROTECTED)
        self.assertIsNone(target)

    def test_better_sell_sl_is_never_loosened(self):
        action, target = self.evaluate(
            direction="SELL",
            actual_fill_price=4000.0,
            initial_sl_price=4002.0,
            current_sl_price=3999.40,
            favorable_move_price=2.0,
        )
        self.assertEqual(action, FatiProtectionAction.ALREADY_PROTECTED)
        self.assertIsNone(target)

    def test_invalid_direction_is_rejected(self):
        with self.assertRaises(ValueError):
            self.evaluate(direction="LONG")

    def test_wrong_side_buy_initial_sl_is_rejected(self):
        with self.assertRaises(ValueError):
            self.evaluate(initial_sl_price=4000.0)

    def test_wrong_side_sell_initial_sl_is_rejected(self):
        with self.assertRaises(ValueError):
            self.evaluate(
                direction="SELL",
                initial_sl_price=3998.0,
            )

    def test_non_finite_price_is_rejected(self):
        with self.assertRaises(ValueError):
            self.evaluate(actual_fill_price=float("nan"))

    def test_negative_favorable_move_is_rejected(self):
        with self.assertRaises(ValueError):
            self.evaluate(favorable_move_price=-0.01)

    def test_non_positive_pip_size_is_rejected(self):
        with self.assertRaises(ValueError):
            FatiProtectionPolicy(pip_size_price=0.0)


if __name__ == "__main__":
    unittest.main()
