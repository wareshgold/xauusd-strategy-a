"""Synthetic contract tests for source-confirmed MT5 linkage fields.

These tests exercise data preservation and documented field distinctions only.
They do not validate a broker, Python history-query behavior, or execution.
"""
from __future__ import annotations

import unittest

from scripts.sp2l_order_deal_position_linkage_facts_research import (
    CloseByFact,
    DealFact,
    OrderFact,
    PositionFact,
    same_position_lifecycle,
    history_order_matches_position_identifier,
    history_deal_matches_position_identifier,
)


class TestOrderDealPositionLinkageFactsResearch(unittest.TestCase):
    def test_deal_order_is_an_explicit_order_ticket_reference(self):
        order = OrderFact(order_ticket=8001, order_position_id=9001)
        deal = DealFact(deal_ticket=6001, deal_order=8001, deal_position_id=9001)
        self.assertEqual(deal.deal_order, order.order_ticket)

    def test_order_and_deal_position_ids_reference_position_identifier(self):
        position = PositionFact("XAUUSD.ecn", 7001, 9001)
        order = OrderFact(8001, order_position_id=9001)
        deal = DealFact(6001, 8001, deal_position_id=9001)
        self.assertEqual(order.order_position_id, position.position_identifier)
        self.assertEqual(deal.deal_position_id, position.position_identifier)

    def test_position_ticket_may_differ_from_position_identifier(self):
        position = PositionFact("XAUUSD.ecn", 7001, 9001)
        self.assertNotEqual(position.position_ticket, position.position_identifier)

    def test_ticket_replacement_keeps_same_lifecycle_identifier(self):
        before = PositionFact("XAUUSD.ecn", 7001, 9001)
        after = PositionFact("XAUUSD.ecn", 7002, 9001)
        self.assertNotEqual(before.position_ticket, after.position_ticket)
        self.assertTrue(same_position_lifecycle(before, after))

    def test_netting_reversal_fixture_keeps_identifier_and_replaces_ticket(self):
        before = PositionFact("XAUUSD.ecn", 7001, 9001)
        reversal_deal = DealFact(6002, 8002, 9001, entry="INOUT")
        after = PositionFact("XAUUSD.ecn", 8002, 9001)
        self.assertEqual(reversal_deal.deal_position_id, before.position_identifier)
        self.assertTrue(same_position_lifecycle(before, after))
        self.assertNotEqual(before.position_ticket, after.position_ticket)

    def test_same_symbol_hedging_positions_keep_distinct_identifiers(self):
        long_position = PositionFact("XAUUSD.ecn", 7001, 9001)
        short_position = PositionFact("XAUUSD.ecn", 7002, 9002)
        self.assertEqual(long_position.symbol, short_position.symbol)
        self.assertFalse(same_position_lifecycle(long_position, short_position))

    def test_multiple_deals_can_share_one_position_lifecycle(self):
        deals = (
            DealFact(6001, 8001, 9001, entry="IN"),
            DealFact(6002, 8002, 9001, entry="IN"),
            DealFact(6003, 8003, 9001, entry="OUT"),
        )
        self.assertEqual({deal.deal_position_id for deal in deals}, {9001})
        self.assertEqual(len({deal.deal_ticket for deal in deals}), 3)

    def test_close_by_opposite_reference_remains_separate(self):
        close_by = CloseByFact(order_position_id=9001, order_position_by_id=9002)
        self.assertNotEqual(close_by.order_position_id, close_by.order_position_by_id)

    def test_partial_fill_fields_are_preserved_without_interpretation(self):
        order = OrderFact(
            order_ticket=8001,
            state="PARTIAL",
            filling_policy="RETURN",
            volume_initial=1.0,
            volume_current=0.6,
        )
        deal = DealFact(6001, 8001, 9001, volume=0.4)
        self.assertEqual(order.state, "PARTIAL")
        self.assertEqual(order.filling_policy, "RETURN")
        self.assertEqual(order.volume_initial, 1.0)
        self.assertEqual(order.volume_current, 0.6)
        self.assertEqual(deal.volume, 0.4)

    def test_missing_order_position_id_is_preserved_as_missing(self):
        order = OrderFact(order_ticket=8001)
        self.assertIsNone(order.order_position_id)

    def test_history_order_filter_uses_position_identifier_not_current_ticket(self):
        position = PositionFact("XAUUSD.ecn", 7001, 9001)
        order = OrderFact(8001, order_position_id=9001)
        self.assertTrue(
            history_order_matches_position_identifier(order, position.position_identifier)
        )
        self.assertFalse(
            history_order_matches_position_identifier(order, position.position_ticket)
        )

    def test_history_deal_filter_uses_position_identifier_not_current_ticket(self):
        position = PositionFact("XAUUSD.ecn", 7001, 9001)
        deal = DealFact(6001, 8001, deal_position_id=9001)
        self.assertTrue(
            history_deal_matches_position_identifier(deal, position.position_identifier)
        )
        self.assertFalse(
            history_deal_matches_position_identifier(deal, position.position_ticket)
        )

    def test_history_filter_does_not_match_unrelated_identifier(self):
        order = OrderFact(8001, order_position_id=9001)
        deal = DealFact(6001, 8001, deal_position_id=9001)
        self.assertFalse(history_order_matches_position_identifier(order, 9002))
        self.assertFalse(history_deal_matches_position_identifier(deal, 9002))

    def test_lifecycle_comparison_does_not_require_same_symbol(self):
        first = PositionFact("XAUUSD.ecn", 7001, 9001)
        later = PositionFact("XAUUSD.pro", 7002, 9001)
        self.assertTrue(same_position_lifecycle(first, later))


if __name__ == "__main__":
    unittest.main()
