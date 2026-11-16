"""Synthetic tests for the injected, read-only history adapter contract.

No MetaTrader5 package, terminal, broker, filesystem, or Runner is used.
"""
from __future__ import annotations

import unittest
from dataclasses import dataclass

from scripts.sp2l_read_only_history_adapter_research import (
    HistoryFailureCode,
    HistoryQueryKind,
    HistoryQueryStatus,
    ReadOnlyHistoryAdapterResearch,
)


@dataclass(frozen=True)
class FakeRecord:
    ticket: int
    position_id: int


class FakeHistoryProvider:
    def __init__(self, *, orders=(), deals=(), last_error=(0, "No error")):
        self.orders = orders
        self.deals = deals
        self.error = last_error
        self.calls = []

    def history_orders_get(self, *, position):
        self.calls.append(("orders", position))
        if isinstance(self.orders, Exception):
            raise self.orders
        return self.orders

    def history_deals_get(self, *, position):
        self.calls.append(("deals", position))
        if isinstance(self.deals, Exception):
            raise self.deals
        return self.deals

    def last_error(self):
        return self.error


class TestReadOnlyHistoryAdapterResearch(unittest.TestCase):
    def test_order_query_passes_position_identifier_not_ticket(self):
        provider = FakeHistoryProvider(orders=())
        adapter = ReadOnlyHistoryAdapterResearch(provider)
        result = adapter.history_orders(position_identifier=9001)
        self.assertEqual(provider.calls, [("orders", 9001)])
        self.assertEqual(result.position_identifier, 9001)

    def test_deal_query_passes_position_identifier_not_ticket(self):
        provider = FakeHistoryProvider(deals=())
        adapter = ReadOnlyHistoryAdapterResearch(provider)
        result = adapter.history_deals(position_identifier=9001)
        self.assertEqual(provider.calls, [("deals", 9001)])
        self.assertEqual(result.position_identifier, 9001)

    def test_empty_tuple_is_a_valid_empty_result(self):
        provider = FakeHistoryProvider(orders=())
        result = ReadOnlyHistoryAdapterResearch(provider).history_orders(
            position_identifier=9001
        )
        self.assertEqual(result.status, HistoryQueryStatus.EMPTY)
        self.assertEqual(result.records, ())
        self.assertIsNone(result.failure_code)

    def test_nonempty_tuple_is_preserved_without_row_rewriting(self):
        rows = (FakeRecord(8001, 9001), FakeRecord(8002, 9001))
        result = ReadOnlyHistoryAdapterResearch(
            FakeHistoryProvider(orders=rows)
        ).history_orders(position_identifier=9001)
        self.assertEqual(result.status, HistoryQueryStatus.NON_EMPTY)
        self.assertIs(result.records[0], rows[0])
        self.assertEqual(result.records, rows)

    def test_none_is_an_error_not_a_valid_empty_result(self):
        result = ReadOnlyHistoryAdapterResearch(
            FakeHistoryProvider(orders=None, last_error=(1001, "history unavailable"))
        ).history_orders(position_identifier=9001)
        self.assertEqual(result.status, HistoryQueryStatus.ERROR)
        self.assertEqual(result.failure_code, HistoryFailureCode.API_RETURNED_NONE)
        self.assertEqual(result.api_last_error, (1001, "history unavailable"))
        self.assertEqual(result.records, ())

    def test_deal_none_is_also_an_error(self):
        result = ReadOnlyHistoryAdapterResearch(
            FakeHistoryProvider(deals=None, last_error=(1002, "query failed"))
        ).history_deals(position_identifier=9001)
        self.assertEqual(result.status, HistoryQueryStatus.ERROR)
        self.assertEqual(result.failure_code, HistoryFailureCode.API_RETURNED_NONE)
        self.assertEqual(result.api_last_error, (1002, "query failed"))

    def test_provider_exception_is_classified_and_not_raised(self):
        result = ReadOnlyHistoryAdapterResearch(
            FakeHistoryProvider(orders=RuntimeError("synthetic"))
        ).history_orders(position_identifier=9001)
        self.assertEqual(result.status, HistoryQueryStatus.ERROR)
        self.assertEqual(result.failure_code, HistoryFailureCode.PROVIDER_EXCEPTION)
        self.assertEqual(result.diagnostic_exception_type, "RuntimeError")

    def test_last_error_exception_is_not_misreported_as_api_error(self):
        class BrokenLastErrorProvider(FakeHistoryProvider):
            def last_error(self):
                raise LookupError("synthetic")

        result = ReadOnlyHistoryAdapterResearch(
            BrokenLastErrorProvider(orders=None)
        ).history_orders(position_identifier=9001)
        self.assertEqual(result.failure_code, HistoryFailureCode.API_RETURNED_NONE)
        self.assertIsNone(result.api_last_error)
        self.assertEqual(result.last_error_exception_type, "LookupError")

    def test_last_error_is_read_exactly_once_for_none_result(self):
        class CountingErrorProvider(FakeHistoryProvider):
            def __init__(self):
                super().__init__(orders=None)
                self.error_reads = 0

            def last_error(self):
                self.error_reads += 1
                return (1003, "single read")

        provider = CountingErrorProvider()
        result = ReadOnlyHistoryAdapterResearch(provider).history_orders(
            position_identifier=9001
        )
        self.assertEqual(provider.error_reads, 1)
        self.assertEqual(result.api_last_error, (1003, "single read"))

    def test_non_tuple_result_is_rejected_instead_of_coerced(self):
        result = ReadOnlyHistoryAdapterResearch(
            FakeHistoryProvider(orders=[FakeRecord(8001, 9001)])
        ).history_orders(position_identifier=9001)
        self.assertEqual(result.status, HistoryQueryStatus.ERROR)
        self.assertEqual(result.failure_code, HistoryFailureCode.INVALID_RESULT_TYPE)
        self.assertEqual(result.diagnostic_exception_type, "list")

    def test_missing_provider_method_is_a_provider_exception(self):
        class OrdersOnlyProvider:
            def history_orders_get(self, *, position):
                return ()

            def last_error(self):
                return (0, "No error")

        result = ReadOnlyHistoryAdapterResearch(
            OrdersOnlyProvider()
        ).history_deals(position_identifier=9001)
        self.assertEqual(result.status, HistoryQueryStatus.ERROR)
        self.assertEqual(result.failure_code, HistoryFailureCode.PROVIDER_EXCEPTION)
        self.assertEqual(result.diagnostic_exception_type, "AttributeError")

    def test_order_and_deal_queries_are_separate_calls(self):
        provider = FakeHistoryProvider(orders=(), deals=())
        adapter = ReadOnlyHistoryAdapterResearch(provider)
        adapter.history_orders(position_identifier=9001)
        adapter.history_deals(position_identifier=9001)
        self.assertEqual(provider.calls, [("orders", 9001), ("deals", 9001)])

    def test_invalid_identifiers_are_rejected_before_provider_call(self):
        for value in (0, -1):
            provider = FakeHistoryProvider()
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    ReadOnlyHistoryAdapterResearch(provider).history_orders(
                        position_identifier=value
                    )
                self.assertEqual(provider.calls, [])

    def test_non_integer_and_boolean_identifiers_are_rejected(self):
        for value in (True, 9001.0, "9001", None):
            provider = FakeHistoryProvider()
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    ReadOnlyHistoryAdapterResearch(provider).history_deals(
                        position_identifier=value
                    )
                self.assertEqual(provider.calls, [])

    def test_raw_rows_are_not_filtered_or_reconciled_by_adapter(self):
        rows = (FakeRecord(8001, 9001), FakeRecord(8002, 9002))
        result = ReadOnlyHistoryAdapterResearch(
            FakeHistoryProvider(orders=rows)
        ).history_orders(position_identifier=9001)
        # Deliberately preserve the provider's exact payload. Any independent
        # field-level verification belongs to a separate evidence check.
        self.assertEqual(result.records, rows)
        self.assertEqual(len(result.records), 2)

    def test_result_records_are_immutable_tuple_container(self):
        rows = (FakeRecord(8001, 9001),)
        result = ReadOnlyHistoryAdapterResearch(
            FakeHistoryProvider(deals=rows)
        ).history_deals(position_identifier=9001)
        self.assertIsInstance(result.records, tuple)
        with self.assertRaises(AttributeError):
            result.records.append(FakeRecord(8002, 9001))

    def test_query_kind_is_explicit(self):
        orders = ReadOnlyHistoryAdapterResearch(
            FakeHistoryProvider(orders=())
        ).history_orders(position_identifier=9001)
        deals = ReadOnlyHistoryAdapterResearch(
            FakeHistoryProvider(deals=())
        ).history_deals(position_identifier=9001)
        self.assertEqual(orders.query_kind, HistoryQueryKind.ORDERS)
        self.assertEqual(deals.query_kind, HistoryQueryKind.DEALS)


if __name__ == "__main__":
    unittest.main()
