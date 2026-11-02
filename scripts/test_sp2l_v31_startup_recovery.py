"""Synthetic tests for fail-closed V3.1 broker inventory recovery."""
from __future__ import annotations

import unittest
from types import SimpleNamespace

from sp2l_v31_startup_recovery import (
    BrokerInventoryRecoveryError,
    recover_owned_broker_inventory,
)


class StartupBrokerRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.state = {"orders": set(), "positions": set()}
        self.kwargs = {
            "symbol": "XAUUSD.ecn",
            "magic": 26092301,
            "buy_limit_type": 2,
            "sell_limit_type": 3,
        }

    def test_recovers_owned_pending_orders_and_positions(self):
        orders = [
            SimpleNamespace(ticket=101, symbol="XAUUSD.ecn", magic=26092301, type=2),
            SimpleNamespace(ticket=102, symbol="XAUUSD.ecn", magic=26092301, type=3),
            SimpleNamespace(ticket=999, symbol="XAUUSD.ecn", magic=26092201, type=2),
            SimpleNamespace(ticket=998, symbol="EURUSD", magic=26092301, type=2),
        ]
        positions = [
            SimpleNamespace(ticket=201, symbol="XAUUSD.ecn", magic=26092301),
            SimpleNamespace(ticket=202, symbol="XAUUSD.ecn", magic=26092201),
        ]
        result = recover_owned_broker_inventory(
            self.state, orders=orders, positions=positions, **self.kwargs
        )
        self.assertEqual(self.state["orders"], {101, 102})
        self.assertEqual(self.state["positions"], {201})
        self.assertEqual(result["orders_recovered"], 2)
        self.assertEqual(result["positions_recovered"], 1)

    def test_valid_empty_inventory_is_accepted(self):
        result = recover_owned_broker_inventory(
            self.state, orders=(), positions=(), **self.kwargs
        )
        self.assertEqual(result["orders_recovered"], 0)
        self.assertEqual(result["positions_recovered"], 0)

    def test_order_query_failure_fails_closed(self):
        with self.assertRaises(BrokerInventoryRecoveryError):
            recover_owned_broker_inventory(
                self.state, orders=None, positions=(), **self.kwargs
            )
        self.assertEqual(self.state["orders"], set())

    def test_position_query_failure_fails_closed(self):
        with self.assertRaises(BrokerInventoryRecoveryError):
            recover_owned_broker_inventory(
                self.state, orders=(), positions=None, **self.kwargs
            )
        self.assertEqual(self.state["positions"], set())

    def test_unknown_owned_order_type_fails_closed(self):
        order = SimpleNamespace(
            ticket=103, symbol="XAUUSD.ecn", magic=26092301, type=99
        )
        with self.assertRaises(BrokerInventoryRecoveryError):
            recover_owned_broker_inventory(
                self.state, orders=[order], positions=(), **self.kwargs
            )
        self.assertEqual(self.state["orders"], set())

    def test_invalid_owned_order_ticket_fails_closed(self):
        order = SimpleNamespace(
            ticket=0, symbol="XAUUSD.ecn", magic=26092301, type=2
        )
        with self.assertRaises(BrokerInventoryRecoveryError):
            recover_owned_broker_inventory(
                self.state, orders=[order], positions=(), **self.kwargs
            )

    def test_invalid_owned_position_ticket_fails_closed(self):
        position = SimpleNamespace(
            ticket=0, symbol="XAUUSD.ecn", magic=26092301
        )
        with self.assertRaises(BrokerInventoryRecoveryError):
            recover_owned_broker_inventory(
                self.state, orders=(), positions=[position], **self.kwargs
            )

    def test_existing_state_is_extended_not_replaced(self):
        self.state["orders"].add(55)
        self.state["positions"].add(66)
        order = SimpleNamespace(
            ticket=101, symbol="XAUUSD.ecn", magic=26092301, type=2
        )
        position = SimpleNamespace(
            ticket=201, symbol="XAUUSD.ecn", magic=26092301
        )
        recover_owned_broker_inventory(
            self.state, orders=[order], positions=[position], **self.kwargs
        )
        self.assertEqual(self.state["orders"], {55, 101})
        self.assertEqual(self.state["positions"], {66, 201})


if __name__ == "__main__":
    unittest.main()
