from __future__ import annotations

import unittest

from scripts.sp2l_account_isolation_contract_research import candidate_idempotency_key
from scripts.sp2l_multi_account_recovery_contract_research import (
    DeliveryDisposition,
    RecoveryDisposition,
    RecoveryObservation,
    StateStatus,
    account_event_key,
    candidate_delivery_disposition,
    classify_state_snapshot,
    decide_recovery,
    validate_event_namespace,
)


def safe_observation(**overrides):
    values = {
        "account_identity_verified": True,
        "inventory_available": True,
        "inventory_is_empty": False,
        "event_journal_complete": True,
        "linkage_ambiguous": False,
    }
    values.update(overrides)
    return RecoveryObservation(**values)


class TestMultiAccountRecoveryContractResearch(unittest.TestCase):
    def test_missing_state_is_classified_explicitly(self):
        self.assertIs(
            classify_state_snapshot(
                exists=False, parse_succeeded=False, schema_version=None,
                expected_schema_version=1, payload_is_mapping=False,
            ),
            StateStatus.MISSING,
        )

    def test_parse_failure_is_corrupt_not_empty(self):
        self.assertIs(
            classify_state_snapshot(
                exists=True, parse_succeeded=False, schema_version=None,
                expected_schema_version=1, payload_is_mapping=False,
            ),
            StateStatus.CORRUPT,
        )

    def test_non_mapping_payload_is_corrupt(self):
        self.assertIs(
            classify_state_snapshot(
                exists=True, parse_succeeded=True, schema_version=1,
                expected_schema_version=1, payload_is_mapping=False,
            ),
            StateStatus.CORRUPT,
        )

    def test_schema_drift_is_incompatible(self):
        self.assertIs(
            classify_state_snapshot(
                exists=True, parse_succeeded=True, schema_version=2,
                expected_schema_version=1, payload_is_mapping=True,
            ),
            StateStatus.INCOMPATIBLE,
        )

    def test_matching_state_schema_is_valid(self):
        self.assertIs(
            classify_state_snapshot(
                exists=True, parse_succeeded=True, schema_version=1,
                expected_schema_version=1, payload_is_mapping=True,
            ),
            StateStatus.VALID,
        )

    def test_corrupt_state_fails_closed(self):
        self.assertIs(
            decide_recovery(StateStatus.CORRUPT, safe_observation()),
            RecoveryDisposition.HALT,
        )

    def test_incompatible_state_fails_closed(self):
        self.assertIs(
            decide_recovery(StateStatus.INCOMPATIBLE, safe_observation()),
            RecoveryDisposition.HALT,
        )

    def test_valid_state_can_restore_only_with_complete_observations(self):
        self.assertIs(
            decide_recovery(StateStatus.VALID, safe_observation()),
            RecoveryDisposition.RESTORE,
        )

    def test_missing_state_bootstraps_only_with_verified_empty_inventory(self):
        self.assertIs(
            decide_recovery(
                StateStatus.MISSING,
                safe_observation(inventory_is_empty=True),
            ),
            RecoveryDisposition.BOOTSTRAP_EMPTY,
        )

    def test_missing_state_with_nonempty_inventory_is_ambiguous(self):
        self.assertIs(
            decide_recovery(
                StateStatus.MISSING,
                safe_observation(inventory_is_empty=False),
            ),
            RecoveryDisposition.HALT,
        )

    def test_unverified_account_identity_halts_recovery(self):
        self.assertIs(
            decide_recovery(
                StateStatus.VALID,
                safe_observation(account_identity_verified=False),
            ),
            RecoveryDisposition.HALT,
        )

    def test_unavailable_inventory_halts_recovery(self):
        self.assertIs(
            decide_recovery(
                StateStatus.VALID,
                safe_observation(inventory_available=False),
            ),
            RecoveryDisposition.HALT,
        )

    def test_incomplete_event_journal_halts_recovery(self):
        self.assertIs(
            decide_recovery(
                StateStatus.VALID,
                safe_observation(event_journal_complete=False),
            ),
            RecoveryDisposition.HALT,
        )

    def test_ambiguous_order_position_linkage_halts_recovery(self):
        self.assertIs(
            decide_recovery(
                StateStatus.VALID,
                safe_observation(linkage_ambiguous=True),
            ),
            RecoveryDisposition.HALT,
        )

    def test_event_keys_are_scoped_per_account(self):
        primary = account_event_key("primary", "event-001")
        fati = account_event_key("fati_demo", "event-001")
        self.assertNotEqual(primary, fati)
        self.assertTrue(validate_event_namespace("primary", {primary}))
        self.assertFalse(validate_event_namespace("primary", {fati}))

    def test_event_id_is_required_and_rejects_control_characters(self):
        with self.assertRaises(ValueError):
            account_event_key("primary", " ")
        with self.assertRaises(ValueError):
            account_event_key("primary", "event\n001")

    def test_candidate_delivery_starts_new(self):
        self.assertIs(
            candidate_delivery_disposition("primary", "candidate-1", set()),
            DeliveryDisposition.NEW,
        )

    def test_duplicate_candidate_delivery_is_detected_for_same_account(self):
        key = candidate_idempotency_key("primary", "candidate-1")
        self.assertIs(
            candidate_delivery_disposition("primary", "candidate-1", {key}),
            DeliveryDisposition.DUPLICATE,
        )

    def test_same_candidate_is_independent_across_accounts(self):
        primary_key = candidate_idempotency_key("primary", "candidate-1")
        self.assertIs(
            candidate_delivery_disposition("fati_demo", "candidate-1", {primary_key}),
            DeliveryDisposition.NEW,
        )

    def test_account_scoped_event_validation_rejects_cross_account_mix(self):
        keys = {
            account_event_key("primary", "event-1"),
            account_event_key("fati_demo", "event-2"),
        }
        self.assertFalse(validate_event_namespace("primary", keys))


if __name__ == "__main__":
    unittest.main()
