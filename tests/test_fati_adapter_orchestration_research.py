from __future__ import annotations

import unittest

from scripts.fati_rr1_be5_no_tp_policy_research import FatiProtectionAction
from scripts.fati_adapter_orchestration_research import (
    ApprovedSignal,
    FatiAccountProfile,
    FatiAdapterState,
    QuoteObservation,
    build_initial_order_intent,
    evaluate_protection,
    reconcile_sl_modification,
)


def profile(**overrides):
    values = dict(
        account_server="SYNTHETIC_SERVER",
        account_type="SYNTHETIC_TYPE",
        account_currency="USD",
        symbol="XAUUSD.SYNTHETIC",
        digits=2,
        point=0.01,
        tick_size=0.01,
        tick_value=1.0,
        contract_size=100.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level_points=0,
        freeze_level_points=0,
        filling_mode="SYNTHETIC",
        commission_amount=0.0,
        commission_currency="USD",
        commission_convention="SYNTHETIC",
        pip_size_price=0.10,
        rr1_quote_semantics="SYNTHETIC_QUOTE",
        rr1_sampling_rule="SYNTHETIC_SAMPLE",
    )
    values.update(overrides)
    return FatiAccountProfile(**values)


class TestFatiAdapterOrchestrationResearch(unittest.TestCase):
    def test_initial_order_intent_always_has_zero_tp(self):
        p = profile()
        signal = ApprovedSignal("s1", "BUY", p.symbol, 0.01, 4000.0, 3998.0)
        intent = build_initial_order_intent(signal, p)
        self.assertEqual(intent.take_profit, 0.0)

    def test_signal_symbol_must_match_profile(self):
        p = profile()
        signal = ApprovedSignal("s1", "BUY", "XAUUSD.OTHER", 0.01, 4000.0, 3998.0)
        with self.assertRaises(ValueError):
            build_initial_order_intent(signal, p)

    def test_invalid_volume_step_is_rejected(self):
        p = profile()
        signal = ApprovedSignal("s1", "BUY", p.symbol, 0.015, 4000.0, 3998.0)
        with self.assertRaises(ValueError):
            build_initial_order_intent(signal, p)

    def test_profile_rejects_missing_quote_semantics(self):
        p = profile(rr1_quote_semantics="")
        with self.assertRaises(ValueError):
            p.validate()

    def test_profile_rejects_non_positive_pip_size(self):
        p = profile(pip_size_price=0.0)
        with self.assertRaises(ValueError):
            p.validate()

    def test_rr1_quote_semantics_must_match_profile(self):
        p = profile()
        q = QuoteObservation(2.0, "UNAPPROVED", "SYNTHETIC_SAMPLE", "t0")
        with self.assertRaises(ValueError):
            evaluate_protection(
                profile=p, direction="BUY", actual_fill_price=4000.0,
                initial_sl_price=3998.0, current_sl_price=3998.0,
                quote=q, broker_confirmed=False,
            )

    def test_rr1_waits_below_threshold(self):
        p = profile()
        q = QuoteObservation(1.99, "SYNTHETIC_QUOTE", "SYNTHETIC_SAMPLE", "t0")
        result = evaluate_protection(
            profile=p, direction="BUY", actual_fill_price=4000.0,
            initial_sl_price=3998.0, current_sl_price=3998.0,
            quote=q, broker_confirmed=False,
        )
        self.assertEqual(result.action, FatiProtectionAction.WAIT_FOR_RR1)
        self.assertEqual(result.next_state, FatiAdapterState.WAITING_FOR_RR1)

    def test_rr1_returns_one_sl_intent_without_broker_call(self):
        p = profile()
        q = QuoteObservation(2.0, "SYNTHETIC_QUOTE", "SYNTHETIC_SAMPLE", "t0")
        result = evaluate_protection(
            profile=p, direction="BUY", actual_fill_price=4000.0,
            initial_sl_price=3998.0, current_sl_price=3998.0,
            quote=q, broker_confirmed=False,
        )
        self.assertEqual(result.action, FatiProtectionAction.REQUEST_BE_PLUS_5_SL)
        self.assertAlmostEqual(result.proposed_sl_price, 4000.5)
        self.assertEqual(result.next_state, FatiAdapterState.BE_REQUEST_PENDING)

    def test_sell_rr1_target_is_be_minus_five_pips(self):
        p = profile()
        q = QuoteObservation(2.0, "SYNTHETIC_QUOTE", "SYNTHETIC_SAMPLE", "t0")
        result = evaluate_protection(
            profile=p, direction="SELL", actual_fill_price=4000.0,
            initial_sl_price=4002.0, current_sl_price=4002.0,
            quote=q, broker_confirmed=False,
        )
        self.assertAlmostEqual(result.proposed_sl_price, 3999.5)

    def test_confirmed_sl_requires_broker_value_match(self):
        self.assertEqual(
            reconcile_sl_modification(
                requested_sl_price=4000.5, broker_sl_price=4000.5,
                broker_result="CONFIRMED", tolerance=0.001,
            ),
            FatiAdapterState.BE_CONFIRMED,
        )

    def test_mismatched_broker_sl_requires_reconciliation(self):
        self.assertEqual(
            reconcile_sl_modification(
                requested_sl_price=4000.5, broker_sl_price=4000.4,
                broker_result="CONFIRMED", tolerance=0.001,
            ),
            FatiAdapterState.RECONCILIATION_REQUIRED,
        )

    def test_rejected_modification_never_becomes_confirmed(self):
        self.assertEqual(
            reconcile_sl_modification(
                requested_sl_price=4000.5, broker_sl_price=3998.0,
                broker_result="REJECTED", tolerance=0.001,
            ),
            FatiAdapterState.RECONCILIATION_REQUIRED,
        )

    def test_unknown_modification_result_requires_reconciliation(self):
        self.assertEqual(
            reconcile_sl_modification(
                requested_sl_price=4000.5, broker_sl_price=None,
                broker_result="TIMEOUT", tolerance=0.001,
            ),
            FatiAdapterState.RECONCILIATION_REQUIRED,
        )

    def test_unrecognized_broker_result_is_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_sl_modification(
                requested_sl_price=4000.5, broker_sl_price=4000.5,
                broker_result="MAYBE", tolerance=0.001,
            )


if __name__ == "__main__":
    unittest.main()
