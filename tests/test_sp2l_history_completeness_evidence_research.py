"""Synthetic tests for the offline history completeness evidence model."""
from __future__ import annotations

import unittest

from scripts.sp2l_history_completeness_evidence_research import (
    HistoryCompletenessEvidence,
    HistoryEvidenceDisposition,
    HistoryEvidenceQueryKind,
    HistoryEvidenceScope,
    HistoryKindEvidence,
    classify_history_completeness_evidence,
    history_completeness_is_proven,
)


def make_scope(**changes):
    values = dict(
        account_identity_verified=True,
        account_identity_ref="acct-ref-01",
        terminal_session_ref="terminal-session-01",
        server_name="Broker-Demo",
        date_from="2026-11-01T00:00:00",
        date_to="2026-11-16T00:00:00",
        time_basis="broker_server_time",
        time_basis_source="operator-approved-source-record",
        observed_at="2026-11-16T10:00:00+03:30",
        package_version="5.0.6180",
        terminal_build="build-observed-01",
        manifest_sha256="a" * 64,
    )
    values.update(changes)
    return HistoryEvidenceScope(**values)


def make_evidence(*, scope=None, orders=None, deals=None):
    return HistoryCompletenessEvidence(
        scope=scope or make_scope(),
        orders=orders or HistoryKindEvidence(
            HistoryEvidenceQueryKind.ORDERS, 2, (object(), object())
        ),
        deals=deals or HistoryKindEvidence(
            HistoryEvidenceQueryKind.DEALS, 1, (object(),)
        ),
    )


class TestHistoryCompletenessEvidenceResearch(unittest.TestCase):
    def test_matching_counts_are_only_consistent_for_scope(self):
        evidence = make_evidence()
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.OBSERVED_CONSISTENT_FOR_SCOPE,
        )
        self.assertFalse(history_completeness_is_proven(evidence))

    def test_two_valid_empty_collections_are_not_completeness_proof(self):
        evidence = make_evidence(
            orders=HistoryKindEvidence(HistoryEvidenceQueryKind.ORDERS, 0, ()),
            deals=HistoryKindEvidence(HistoryEvidenceQueryKind.DEALS, 0, ()),
        )
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.OBSERVED_CONSISTENT_FOR_SCOPE,
        )
        self.assertFalse(history_completeness_is_proven(evidence))

    def test_order_count_mismatch_fails_closed(self):
        evidence = make_evidence(
            orders=HistoryKindEvidence(HistoryEvidenceQueryKind.ORDERS, 3, (object(),))
        )
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.COUNT_MISMATCH,
        )

    def test_deal_count_mismatch_fails_closed(self):
        evidence = make_evidence(
            deals=HistoryKindEvidence(HistoryEvidenceQueryKind.DEALS, 2, ())
        )
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.COUNT_MISMATCH,
        )

    def test_none_collection_is_query_failure_not_empty(self):
        evidence = make_evidence(
            orders=HistoryKindEvidence(HistoryEvidenceQueryKind.ORDERS, 0, None)
        )
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.QUERY_FAILED,
        )

    def test_total_api_error_is_query_failure(self):
        evidence = make_evidence(
            orders=HistoryKindEvidence(
                HistoryEvidenceQueryKind.ORDERS, None, (), total_error=(1, "error")
            )
        )
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.QUERY_FAILED,
        )

    def test_collection_api_error_is_query_failure(self):
        evidence = make_evidence(
            deals=HistoryKindEvidence(
                HistoryEvidenceQueryKind.DEALS, 0, None, get_error=(2, "error")
            )
        )
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.QUERY_FAILED,
        )

    def test_wrong_query_kind_is_query_failure(self):
        evidence = make_evidence(
            orders=HistoryKindEvidence(HistoryEvidenceQueryKind.DEALS, 2, ())
        )
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.QUERY_FAILED,
        )

    def test_list_collection_is_rejected_not_coerced(self):
        evidence = make_evidence(
            deals=HistoryKindEvidence(HistoryEvidenceQueryKind.DEALS, 1, [object()])
        )
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.QUERY_FAILED,
        )

    def test_boolean_total_is_not_accepted_as_integer(self):
        evidence = make_evidence(
            orders=HistoryKindEvidence(HistoryEvidenceQueryKind.ORDERS, True, ())
        )
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.QUERY_FAILED,
        )

    def test_negative_total_is_query_failure(self):
        evidence = make_evidence(
            orders=HistoryKindEvidence(HistoryEvidenceQueryKind.ORDERS, -1, ())
        )
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.QUERY_FAILED,
        )

    def test_unverified_account_identity_invalidates_scope(self):
        evidence = make_evidence(scope=make_scope(account_identity_verified=False))
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.INVALID_SCOPE,
        )

    def test_missing_time_basis_source_invalidates_scope(self):
        evidence = make_evidence(scope=make_scope(time_basis_source=" "))
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.INVALID_SCOPE,
        )

    def test_equal_interval_endpoints_invalidates_scope(self):
        evidence = make_evidence(
            scope=make_scope(date_to="2026-11-01T00:00:00")
        )
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.INVALID_SCOPE,
        )

    def test_invalid_manifest_hash_invalidates_scope(self):
        evidence = make_evidence(scope=make_scope(manifest_sha256="not-a-hash"))
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.INVALID_SCOPE,
        )

    def test_blank_terminal_session_reference_invalidates_scope(self):
        evidence = make_evidence(scope=make_scope(terminal_session_ref=" "))
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.INVALID_SCOPE,
        )

    def test_opaque_error_payload_is_not_rewritten(self):
        payload = {"code": 500, "message": "captured"}
        evidence = make_evidence(
            deals=HistoryKindEvidence(
                HistoryEvidenceQueryKind.DEALS, None, None, total_error=payload
            )
        )
        self.assertIs(evidence.deals.total_error, payload)
        self.assertEqual(
            classify_history_completeness_evidence(evidence),
            HistoryEvidenceDisposition.QUERY_FAILED,
        )

    def test_absolute_completeness_never_becomes_true(self):
        for evidence in (
            make_evidence(),
            make_evidence(
                orders=HistoryKindEvidence(HistoryEvidenceQueryKind.ORDERS, 0, ()),
                deals=HistoryKindEvidence(HistoryEvidenceQueryKind.DEALS, 0, ()),
            ),
        ):
            with self.subTest(evidence=evidence):
                self.assertFalse(history_completeness_is_proven(evidence))


if __name__ == "__main__":
    unittest.main()
