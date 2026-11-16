"""Synthetic tests for paired order/deal history observations."""
from __future__ import annotations

import unittest

from scripts.sp2l_read_only_history_adapter_research import (
    HistoryFailureCode,
    HistoryQueryKind,
    HistoryQueryResult,
    HistoryQueryStatus,
)
from scripts.sp2l_history_pair_observation_research import (
    HistoryPairStatus,
    pair_history_observations,
)


def outcome(kind, identifier, status, *, records=(), failure=None):
    return HistoryQueryResult(
        query_kind=kind,
        position_identifier=identifier,
        status=status,
        records=records,
        failure_code=failure,
    )


class TestHistoryPairObservationResearch(unittest.TestCase):
    def test_two_empty_tuples_are_two_valid_empty_observations(self):
        pair = pair_history_observations(
            orders=outcome(HistoryQueryKind.ORDERS, 9001, HistoryQueryStatus.EMPTY),
            deals=outcome(HistoryQueryKind.DEALS, 9001, HistoryQueryStatus.EMPTY),
        )
        self.assertEqual(pair.status, HistoryPairStatus.BOTH_RESPONSES_VALID)
        self.assertEqual(pair.orders.records, ())
        self.assertEqual(pair.deals.records, ())

    def test_nonempty_orders_and_empty_deals_remain_separate(self):
        row = object()
        pair = pair_history_observations(
            orders=outcome(HistoryQueryKind.ORDERS, 9001, HistoryQueryStatus.NON_EMPTY, records=(row,)),
            deals=outcome(HistoryQueryKind.DEALS, 9001, HistoryQueryStatus.EMPTY),
        )
        self.assertEqual(pair.status, HistoryPairStatus.BOTH_RESPONSES_VALID)
        self.assertIs(pair.orders.records[0], row)
        self.assertEqual(pair.deals.records, ())

    def test_empty_orders_and_nonempty_deals_remain_separate(self):
        row = object()
        pair = pair_history_observations(
            orders=outcome(HistoryQueryKind.ORDERS, 9001, HistoryQueryStatus.EMPTY),
            deals=outcome(HistoryQueryKind.DEALS, 9001, HistoryQueryStatus.NON_EMPTY, records=(row,)),
        )
        self.assertEqual(pair.status, HistoryPairStatus.BOTH_RESPONSES_VALID)
        self.assertEqual(pair.orders.records, ())
        self.assertIs(pair.deals.records[0], row)

    def test_order_failure_is_not_hidden_by_valid_deal_response(self):
        pair = pair_history_observations(
            orders=outcome(HistoryQueryKind.ORDERS, 9001, HistoryQueryStatus.ERROR, failure=HistoryFailureCode.API_RETURNED_NONE),
            deals=outcome(HistoryQueryKind.DEALS, 9001, HistoryQueryStatus.NON_EMPTY, records=(object(),)),
        )
        self.assertEqual(pair.status, HistoryPairStatus.AT_LEAST_ONE_QUERY_FAILED)
        self.assertEqual(pair.orders.failure_code, HistoryFailureCode.API_RETURNED_NONE)

    def test_deal_failure_is_not_hidden_by_valid_order_response(self):
        pair = pair_history_observations(
            orders=outcome(HistoryQueryKind.ORDERS, 9001, HistoryQueryStatus.EMPTY),
            deals=outcome(HistoryQueryKind.DEALS, 9001, HistoryQueryStatus.ERROR, failure=HistoryFailureCode.PROVIDER_EXCEPTION),
        )
        self.assertEqual(pair.status, HistoryPairStatus.AT_LEAST_ONE_QUERY_FAILED)

    def test_both_failures_are_preserved_independently(self):
        pair = pair_history_observations(
            orders=outcome(HistoryQueryKind.ORDERS, 9001, HistoryQueryStatus.ERROR, failure=HistoryFailureCode.API_RETURNED_NONE),
            deals=outcome(HistoryQueryKind.DEALS, 9001, HistoryQueryStatus.ERROR, failure=HistoryFailureCode.PROVIDER_EXCEPTION),
        )
        self.assertEqual(pair.status, HistoryPairStatus.AT_LEAST_ONE_QUERY_FAILED)
        self.assertEqual(pair.orders.failure_code, HistoryFailureCode.API_RETURNED_NONE)
        self.assertEqual(pair.deals.failure_code, HistoryFailureCode.PROVIDER_EXCEPTION)

    def test_mismatched_position_identifiers_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "share position_identifier"):
            pair_history_observations(
                orders=outcome(HistoryQueryKind.ORDERS, 9001, HistoryQueryStatus.EMPTY),
                deals=outcome(HistoryQueryKind.DEALS, 9002, HistoryQueryStatus.EMPTY),
            )

    def test_swapped_query_kinds_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "query_kind=ORDERS"):
            pair_history_observations(
                orders=outcome(HistoryQueryKind.DEALS, 9001, HistoryQueryStatus.EMPTY),
                deals=outcome(HistoryQueryKind.ORDERS, 9001, HistoryQueryStatus.EMPTY),
            )


if __name__ == "__main__":
    unittest.main()
