"""Synthetic fixtures for repeated history-observation stability."""
from __future__ import annotations

import unittest

from scripts.sp2l_history_completeness_evidence_research import (
    HistoryCompletenessEvidence,
    HistoryEvidenceQueryKind,
    HistoryEvidenceScope,
    HistoryKindEvidence,
)
from scripts.sp2l_history_stability_research import (
    HistoryObservationFingerprint,
    HistoryStabilityDisposition,
    compare_history_observation_stability,
    stability_proves_history_completeness,
)


def make_scope(**changes):
    values = dict(
        account_identity_verified=True,
        account_identity_ref="acct-ref-01",
        terminal_session_ref="session-01",
        server_name="Broker-Demo",
        date_from="2026-11-01T00:00:00",
        date_to="2026-11-16T00:00:00",
        time_basis="broker_server_time",
        time_basis_source="approved-source-record",
        observed_at="2026-11-16T10:00:00+03:30",
        package_version="5.0.6180",
        terminal_build="build-01",
        manifest_sha256="a" * 64,
    )
    values.update(changes)
    return HistoryEvidenceScope(**values)


def make_evidence(*, scope=None, order_count=2, deal_count=1):
    return HistoryCompletenessEvidence(
        scope=scope or make_scope(),
        orders=HistoryKindEvidence(
            HistoryEvidenceQueryKind.ORDERS,
            order_count,
            tuple(object() for _ in range(order_count)),
        ),
        deals=HistoryKindEvidence(
            HistoryEvidenceQueryKind.DEALS,
            deal_count,
            tuple(object() for _ in range(deal_count)),
        ),
    )


def make_observation(
    observation_id,
    *,
    observed_at,
    orders_hash="1" * 64,
    deals_hash="2" * 64,
    algorithm="external-fingerprint-v1",
    scope_changes=None,
    order_count=2,
    deal_count=1,
):
    changes = dict(scope_changes or {})
    changes["observed_at"] = observed_at
    evidence = make_evidence(
        scope=make_scope(**changes),
        order_count=order_count,
        deal_count=deal_count,
    )
    return HistoryObservationFingerprint(
        observation_id,
        evidence,
        algorithm,
        orders_hash,
        deals_hash,
    )


class TestHistoryStabilityResearch(unittest.TestCase):
    def setUp(self):
        self.first = make_observation(
            "obs-1", observed_at="2026-11-16T10:00:00+03:30"
        )
        self.second = make_observation(
            "obs-2",
            observed_at="2026-11-16T10:05:00+03:30",
            scope_changes={"manifest_sha256": "b" * 64},
        )

    def test_identical_fingerprints_are_stable_for_observed_scope(self):
        self.assertEqual(
            compare_history_observation_stability(self.first, self.second),
            HistoryStabilityDisposition.STABLE_ACROSS_OBSERVATIONS,
        )

    def test_stable_observations_do_not_prove_completeness(self):
        self.assertFalse(
            stability_proves_history_completeness(self.first, self.second)
        )

    def test_changed_orders_fingerprint_is_detected(self):
        second = make_observation(
            "obs-2",
            observed_at="2026-11-16T10:05:00+03:30",
            orders_hash="3" * 64,
        )
        self.assertEqual(
            compare_history_observation_stability(self.first, second),
            HistoryStabilityDisposition.CHANGED_BETWEEN_OBSERVATIONS,
        )

    def test_changed_deals_fingerprint_is_detected(self):
        second = make_observation(
            "obs-2",
            observed_at="2026-11-16T10:05:00+03:30",
            deals_hash="4" * 64,
        )
        self.assertEqual(
            compare_history_observation_stability(self.first, second),
            HistoryStabilityDisposition.CHANGED_BETWEEN_OBSERVATIONS,
        )

    def test_changed_order_count_is_detected(self):
        second = make_observation(
            "obs-2",
            observed_at="2026-11-16T10:05:00+03:30",
            order_count=3,
        )
        self.assertEqual(
            compare_history_observation_stability(self.first, second),
            HistoryStabilityDisposition.CHANGED_BETWEEN_OBSERVATIONS,
        )

    def test_changed_deal_count_is_detected(self):
        second = make_observation(
            "obs-2",
            observed_at="2026-11-16T10:05:00+03:30",
            deal_count=2,
        )
        self.assertEqual(
            compare_history_observation_stability(self.first, second),
            HistoryStabilityDisposition.CHANGED_BETWEEN_OBSERVATIONS,
        )

    def test_different_account_scope_is_rejected(self):
        second = make_observation(
            "obs-2",
            observed_at="2026-11-16T10:05:00+03:30",
            scope_changes={"account_identity_ref": "other-account"},
        )
        self.assertEqual(
            compare_history_observation_stability(self.first, second),
            HistoryStabilityDisposition.SCOPE_MISMATCH,
        )

    def test_different_time_interval_is_rejected(self):
        second = make_observation(
            "obs-2",
            observed_at="2026-11-16T10:05:00+03:30",
            scope_changes={"date_to": "2026-11-17T00:00:00"},
        )
        self.assertEqual(
            compare_history_observation_stability(self.first, second),
            HistoryStabilityDisposition.SCOPE_MISMATCH,
        )

    def test_different_server_is_rejected(self):
        second = make_observation(
            "obs-2",
            observed_at="2026-11-16T10:05:00+03:30",
            scope_changes={"server_name": "Other-Server"},
        )
        self.assertEqual(
            compare_history_observation_stability(self.first, second),
            HistoryStabilityDisposition.SCOPE_MISMATCH,
        )

    def test_different_fingerprint_algorithms_are_rejected(self):
        second = make_observation(
            "obs-2",
            observed_at="2026-11-16T10:05:00+03:30",
            algorithm="another-method-v2",
        )
        self.assertEqual(
            compare_history_observation_stability(self.first, second),
            HistoryStabilityDisposition.FINGERPRINT_METHOD_MISMATCH,
        )

    def test_same_observation_id_is_insufficient(self):
        second = make_observation(
            "obs-1", observed_at="2026-11-16T10:05:00+03:30"
        )
        self.assertEqual(
            compare_history_observation_stability(self.first, second),
            HistoryStabilityDisposition.INSUFFICIENT_DISTINCT_OBSERVATIONS,
        )

    def test_same_observation_time_is_insufficient(self):
        second = make_observation(
            "obs-2", observed_at="2026-11-16T10:00:00+03:30"
        )
        self.assertEqual(
            compare_history_observation_stability(self.first, second),
            HistoryStabilityDisposition.INSUFFICIENT_DISTINCT_OBSERVATIONS,
        )

    def test_invalid_hash_is_rejected(self):
        second = make_observation(
            "obs-2",
            observed_at="2026-11-16T10:05:00+03:30",
            orders_hash="not-a-hash",
        )
        self.assertEqual(
            compare_history_observation_stability(self.first, second),
            HistoryStabilityDisposition.INVALID_OBSERVATION,
        )

    def test_invalid_underlying_evidence_is_rejected(self):
        invalid = make_observation(
            "obs-2",
            observed_at="2026-11-16T10:05:00+03:30",
            order_count=3,
        )
        # Corrupt the captured total without changing the tuple length.
        broken_evidence = HistoryCompletenessEvidence(
            invalid.evidence.scope,
            HistoryKindEvidence(HistoryEvidenceQueryKind.ORDERS, 99, ()),
            invalid.evidence.deals,
        )
        broken = HistoryObservationFingerprint(
            invalid.observation_id,
            broken_evidence,
            invalid.fingerprint_algorithm_id,
            invalid.orders_payload_sha256,
            invalid.deals_payload_sha256,
        )
        self.assertEqual(
            compare_history_observation_stability(self.first, broken),
            HistoryStabilityDisposition.INVALID_OBSERVATION,
        )

    def test_manifest_hash_and_observation_time_may_differ(self):
        self.assertEqual(
            compare_history_observation_stability(self.first, self.second),
            HistoryStabilityDisposition.STABLE_ACROSS_OBSERVATIONS,
        )


if __name__ == "__main__":
    unittest.main()
