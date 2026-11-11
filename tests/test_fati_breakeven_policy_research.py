from __future__ import annotations

import unittest

from scripts.fati_breakeven_policy_research import (
    BreakevenAction,
    BreakevenModel,
    evaluate_breakeven,
)


class TestFatiBreakevenResearchFixtures(unittest.TestCase):
    def setUp(self):
        self.model = BreakevenModel()

    def test_round_trip_commission_is_ten_cents(self):
        self.assertAlmostEqual(self.model.round_trip_commission_usd, 0.10)
        self.assertAlmostEqual(self.model.value_per_pip_usd, 0.10)
        self.assertAlmostEqual(self.model.commission_offset_pips, 1.0)
        self.assertAlmostEqual(
            self.model.commission_offset_price * self.model.contract_size * self.model.volume_lots,
            0.10,
        )

    def test_five_pip_activation_is_half_a_price_unit(self):
        self.assertAlmostEqual(self.model.activation_move_price, 0.50)

    def test_buy_breakeven_sl_is_one_commission_offset_above_entry(self):
        self.assertAlmostEqual(self.model.desired_sl("BUY", 4000.0), 4000.10)

    def test_sell_breakeven_sl_is_one_commission_offset_below_entry(self):
        self.assertAlmostEqual(self.model.desired_sl("SELL", 4000.0), 3999.90)

    def test_waits_below_five_pip_activation(self):
        action, proposed = evaluate_breakeven(
            model=self.model, direction="BUY", entry_price=4000.0,
            current_sl=3995.0, favorable_move_price=0.49, be_confirmed=False,
        )
        self.assertEqual(action, BreakevenAction.WAIT)
        self.assertIsNone(proposed)

    def test_requests_buy_sl_change_at_activation(self):
        action, proposed = evaluate_breakeven(
            model=self.model, direction="BUY", entry_price=4000.0,
            current_sl=3995.0, favorable_move_price=0.50, be_confirmed=False,
        )
        self.assertEqual(action, BreakevenAction.REQUEST_SL_CHANGE)
        self.assertAlmostEqual(proposed, 4000.10)

    def test_requests_sell_sl_change_at_activation(self):
        action, proposed = evaluate_breakeven(
            model=self.model, direction="SELL", entry_price=4000.0,
            current_sl=4005.0, favorable_move_price=0.50, be_confirmed=False,
        )
        self.assertEqual(action, BreakevenAction.REQUEST_SL_CHANGE)
        self.assertAlmostEqual(proposed, 3999.90)

    def test_existing_better_buy_sl_is_never_loosened(self):
        action, proposed = evaluate_breakeven(
            model=self.model, direction="BUY", entry_price=4000.0,
            current_sl=4000.20, favorable_move_price=0.50, be_confirmed=False,
        )
        self.assertEqual(action, BreakevenAction.ALREADY_PROTECTED)
        self.assertIsNone(proposed)

    def test_existing_better_sell_sl_is_never_loosened(self):
        action, proposed = evaluate_breakeven(
            model=self.model, direction="SELL", entry_price=4000.0,
            current_sl=3999.80, favorable_move_price=0.50, be_confirmed=False,
        )
        self.assertEqual(action, BreakevenAction.ALREADY_PROTECTED)
        self.assertIsNone(proposed)

    def test_broker_rejection_does_not_mark_breakeven_confirmed(self):
        # Re-evaluating with unchanged state remains eligible for controlled retry.
        args = dict(
            model=self.model, direction="BUY", entry_price=4000.0,
            current_sl=3995.0, favorable_move_price=0.50, be_confirmed=False,
        )
        first = evaluate_breakeven(**args)
        after_rejection = evaluate_breakeven(**args)
        self.assertEqual(first, after_rejection)
        self.assertEqual(after_rejection[0], BreakevenAction.REQUEST_SL_CHANGE)

    def test_broker_confirmed_breakeven_is_not_requested_again(self):
        action, proposed = evaluate_breakeven(
            model=self.model, direction="BUY", entry_price=4000.0,
            current_sl=4000.10, favorable_move_price=0.80, be_confirmed=True,
        )
        self.assertEqual(action, BreakevenAction.ALREADY_CONFIRMED)
        self.assertIsNone(proposed)


    def test_nan_entry_price_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_breakeven(
                model=self.model, direction="BUY", entry_price=float("nan"),
                current_sl=3995.0, favorable_move_price=0.50, be_confirmed=False,
            )

    def test_nan_favorable_move_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_breakeven(
                model=self.model, direction="BUY", entry_price=4000.0,
                current_sl=3995.0, favorable_move_price=float("nan"), be_confirmed=False,
            )

    def test_non_finite_current_sl_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_breakeven(
                model=self.model, direction="BUY", entry_price=4000.0,
                current_sl=float("inf"), favorable_move_price=0.50, be_confirmed=False,
            )

    def test_negative_current_sl_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_breakeven(
                model=self.model, direction="BUY", entry_price=4000.0,
                current_sl=-1.0, favorable_move_price=0.50, be_confirmed=False,
            )

    def test_invalid_direction_is_rejected(self):
        with self.assertRaises(ValueError):
            self.model.desired_sl("LONG", 4000.0)


if __name__ == "__main__":
    unittest.main()
