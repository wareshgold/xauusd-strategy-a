from __future__ import annotations

import unittest

from scripts.sp2l_account_isolation_contract_research import (
    AccountIdentity,
    AccountIdentityMismatch,
    ObservedAccountIdentity,
    account_state_namespace,
    assert_account_identity,
    candidate_idempotency_key,
)


def expected(**overrides):
    values = {
        "account_key": "fati_demo",
        "broker": "SYNTHETIC_BROKER",
        "server": "SYNTHETIC_SERVER",
        "login_ref": "SYNTHETIC_LOGIN_REF",
    }
    values.update(overrides)
    return AccountIdentity(**values)


def observed(**overrides):
    values = {
        "broker": "SYNTHETIC_BROKER",
        "server": "SYNTHETIC_SERVER",
        "login_ref": "SYNTHETIC_LOGIN_REF",
    }
    values.update(overrides)
    return ObservedAccountIdentity(**values)


class TestAccountIsolationContractResearch(unittest.TestCase):
    def test_exact_identity_match_is_accepted(self):
        assert_account_identity(expected(), observed())

    def test_broker_mismatch_fails_closed(self):
        with self.assertRaisesRegex(AccountIdentityMismatch, "broker"):
            assert_account_identity(expected(), observed(broker="OTHER"))

    def test_server_mismatch_fails_closed(self):
        with self.assertRaisesRegex(AccountIdentityMismatch, "server"):
            assert_account_identity(expected(), observed(server="OTHER"))

    def test_login_reference_mismatch_fails_closed(self):
        with self.assertRaisesRegex(AccountIdentityMismatch, "login_ref"):
            assert_account_identity(expected(), observed(login_ref="OTHER"))

    def test_mismatch_error_does_not_echo_identity_values(self):
        with self.assertRaises(AccountIdentityMismatch) as caught:
            assert_account_identity(expected(), observed(server="PRIVATE_VALUE"))
        self.assertNotIn("PRIVATE_VALUE", str(caught.exception))
        self.assertNotIn("SYNTHETIC_SERVER", str(caught.exception))

    def test_account_key_is_required(self):
        with self.assertRaises(ValueError):
            expected(account_key="").validate()

    def test_account_key_rejects_path_traversal(self):
        with self.assertRaises(ValueError):
            account_state_namespace("../fati")

    def test_account_key_rejects_uppercase_and_spaces(self):
        for value in ("Fati", "fati account", "fati/demo"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                account_state_namespace(value)

    def test_state_namespaces_are_account_scoped(self):
        self.assertEqual(account_state_namespace("primary"), "accounts/primary")
        self.assertEqual(account_state_namespace("fati_demo"), "accounts/fati_demo")
        self.assertNotEqual(
            account_state_namespace("primary"),
            account_state_namespace("fati_demo"),
        )

    def test_candidate_idempotency_is_scoped_per_account(self):
        primary = candidate_idempotency_key("primary", "candidate-001")
        fati = candidate_idempotency_key("fati_demo", "candidate-001")
        self.assertNotEqual(primary, fati)
        self.assertEqual(primary, "accounts/primary/candidate/candidate-001")

    def test_candidate_id_is_required(self):
        with self.assertRaises(ValueError):
            candidate_idempotency_key("fati_demo", " ")

    def test_candidate_id_rejects_control_characters(self):
        with self.assertRaises(ValueError):
            candidate_idempotency_key("fati_demo", "candidate\n001")


if __name__ == "__main__":
    unittest.main()
