"""Synthetic tests for account-scoped broker-object ownership."""
from __future__ import annotations

import unittest

from scripts.sp2l_account_isolation_contract_research import (
    AccountIdentity,
    ObservedAccountIdentity,
    AccountIdentityMismatch,
)
from scripts.sp2l_broker_object_ownership_contract_research import (
    BrokerObjectKind,
    BrokerObjectObservation,
    BrokerObjectKey,
    BrokerObjectOwnershipError,
    broker_object_namespace,
    classify_broker_inventory,
)


EXPECTED = AccountIdentity(
    account_key="alpha",
    broker="Synthetic Broker",
    server="Synthetic-Demo",
    login_ref="opaque-alpha",
)
OBSERVED = ObservedAccountIdentity(
    broker="Synthetic Broker",
    server="Synthetic-Demo",
    login_ref="opaque-alpha",
)


class BrokerObjectOwnershipContractResearch(unittest.TestCase):
    def classify(self, objects, *, expected=EXPECTED, observed=OBSERVED):
        return classify_broker_inventory(
            expected,
            observed,
            symbol="XAUUSD.ecn",
            magic=26092301,
            objects=objects,
        )

    def test_exact_account_symbol_magic_object_is_owned(self):
        result = self.classify([
            BrokerObjectObservation(BrokerObjectKind.ORDER, "XAUUSD.ecn", 26092301, 101)
        ])
        self.assertEqual(
            result.owned_objects,
            (BrokerObjectKey("alpha", BrokerObjectKind.ORDER, 101),),
        )
        self.assertEqual(result.ignored_foreign_count, 0)

    def test_account_identity_mismatch_halts_before_object_filtering(self):
        foreign_session = ObservedAccountIdentity(
            broker="Synthetic Broker",
            server="Synthetic-Demo",
            login_ref="opaque-beta",
        )
        with self.assertRaises(AccountIdentityMismatch):
            self.classify([
                BrokerObjectObservation(BrokerObjectKind.ORDER, "XAUUSD.ecn", 26092301, 101)
            ], observed=foreign_session)

    def test_same_symbol_and_magic_on_another_account_is_not_adopted(self):
        beta = AccountIdentity("beta", "Synthetic Broker", "Synthetic-Demo", "opaque-beta")
        beta_observed = ObservedAccountIdentity("Synthetic Broker", "Synthetic-Demo", "opaque-beta")
        with self.assertRaises(AccountIdentityMismatch):
            self.classify(
                [BrokerObjectObservation(BrokerObjectKind.POSITION, "XAUUSD.ecn", 26092301, 202)],
                expected=EXPECTED,
                observed=beta_observed,
            )

    def test_foreign_magic_is_ignored(self):
        result = self.classify([
            BrokerObjectObservation(BrokerObjectKind.ORDER, "XAUUSD.ecn", 777, 101)
        ])
        self.assertEqual(result.owned_objects, ())
        self.assertEqual(result.ignored_foreign_count, 1)

    def test_foreign_symbol_is_ignored(self):
        result = self.classify([
            BrokerObjectObservation(BrokerObjectKind.POSITION, "EURUSD", 26092301, 202)
        ])
        self.assertEqual(result.owned_objects, ())
        self.assertEqual(result.ignored_foreign_count, 1)

    def test_same_ticket_for_order_and_position_has_distinct_keys(self):
        result = self.classify([
            BrokerObjectObservation(BrokerObjectKind.ORDER, "XAUUSD.ecn", 26092301, 500),
            BrokerObjectObservation(BrokerObjectKind.POSITION, "XAUUSD.ecn", 26092301, 500),
        ])
        self.assertEqual(len(result.owned_objects), 2)
        self.assertNotEqual(result.owned_objects[0], result.owned_objects[1])

    def test_identical_duplicate_observation_is_deduplicated(self):
        item = BrokerObjectObservation(BrokerObjectKind.ORDER, "XAUUSD.ecn", 26092301, 101)
        result = self.classify([item, item])
        self.assertEqual(len(result.owned_objects), 1)
        self.assertEqual(result.duplicate_observations, 1)

    def test_conflicting_duplicate_ticket_halts(self):
        with self.assertRaises(BrokerObjectOwnershipError):
            self.classify([
                BrokerObjectObservation(BrokerObjectKind.ORDER, "XAUUSD.ecn", 26092301, 101),
                BrokerObjectObservation(BrokerObjectKind.ORDER, "EURUSD", 26092301, 101),
            ])

    def test_invalid_ticket_halts_even_for_foreign_object(self):
        with self.assertRaises(BrokerObjectOwnershipError):
            self.classify([
                BrokerObjectObservation(BrokerObjectKind.ORDER, "EURUSD", 777, 0)
            ])

    def test_invalid_magic_scope_is_rejected(self):
        with self.assertRaises(ValueError):
            classify_broker_inventory(
                EXPECTED, OBSERVED, symbol="XAUUSD.ecn", magic=True, objects=[]
            )

    def test_empty_verified_inventory_is_valid(self):
        result = self.classify([])
        self.assertEqual(result.owned_objects, ())
        self.assertEqual(result.ignored_foreign_count, 0)

    def test_object_namespaces_include_account_kind_and_ticket(self):
        self.assertEqual(
            broker_object_namespace("alpha", BrokerObjectKind.ORDER, 101),
            "accounts/alpha/broker/order/101",
        )
        self.assertEqual(
            broker_object_namespace("beta", BrokerObjectKind.ORDER, 101),
            "accounts/beta/broker/order/101",
        )
        self.assertNotEqual(
            broker_object_namespace("alpha", BrokerObjectKind.ORDER, 101),
            broker_object_namespace("alpha", BrokerObjectKind.POSITION, 101),
        )

    def test_invalid_kind_or_ticket_is_rejected_by_namespace(self):
        with self.assertRaises(ValueError):
            broker_object_namespace("alpha", "order", 101)
        with self.assertRaises(ValueError):
            broker_object_namespace("alpha", BrokerObjectKind.ORDER, -1)


if __name__ == "__main__":
    unittest.main()
