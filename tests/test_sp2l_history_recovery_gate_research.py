"""Synthetic tests for fail-closed history-to-recovery gating."""
from __future__ import annotations

import unittest

from scripts.sp2l_history_pair_observation_research import (
    HistoryPairObservation,
    HistoryPairStatus,
)
from scripts.sp2l_read_only_history_adapter_research import (
    HistoryQueryKind,
    HistoryQueryResult,
    HistoryQueryStatus,
)
from scripts.sp2l_multi_account_recovery_contract_research import (
    RecoveryDisposition,
    RecoveryObservation,
    StateStatus,
)
from scripts.sp2l_history_recovery_gate_research import (
    decide_recovery_with_history_evidence,
)


def observation(**overrides):
    values = dict(
        account_identity_verified=True,
        inventory_available=True,
        inventory_is_empty=True,
        event_journal_complete=True,
        linkage_ambiguous=False,
    )
    values.update(overrides)
    return RecoveryObservation(**values)


def pair(status):
    # The recovery gate tests only the paired observation status contract.
    query_status = (
        HistoryQueryStatus.EMPTY
        if status is HistoryPairStatus.BOTH_RESPONSES_VALID
        else HistoryQueryStatus.ERROR
    )
    return HistoryPairObservation(
        position_identifier=9001,
        orders=HistoryQueryResult(
            query_kind=HistoryQueryKind.ORDERS,
            position_identifier=9001,
            status=query_status,
        ),
        deals=HistoryQueryResult(
            query_kind=HistoryQueryKind.DEALS,
            position_identifier=9001,
            status=query_status,
        ),
        status=status,
    )


class TestHistoryRecoveryGateResearch(unittest.TestCase):
    def test_failed_order_or_deal_pair_halts_even_when_other_facts_are_safe(self):
        self.assertIs(
            decide_recovery_with_history_evidence(
                state_status=StateStatus.MISSING,
                observation=observation(),
                history_pair=pair(HistoryPairStatus.AT_LEAST_ONE_QUERY_FAILED),
                history_completeness_verified=True,
            ),
            RecoveryDisposition.HALT,
        )

    def test_two_valid_empty_results_do_not_prove_history_completeness(self):
        self.assertIs(
            decide_recovery_with_history_evidence(
                state_status=StateStatus.MISSING,
                observation=observation(),
                history_pair=pair(HistoryPairStatus.BOTH_RESPONSES_VALID),
                history_completeness_verified=False,
            ),
            RecoveryDisposition.HALT,
        )

    def test_valid_empty_pair_plus_independent_completeness_can_bootstrap_empty(self):
        self.assertIs(
            decide_recovery_with_history_evidence(
                state_status=StateStatus.MISSING,
                observation=observation(inventory_is_empty=True),
                history_pair=pair(HistoryPairStatus.BOTH_RESPONSES_VALID),
                history_completeness_verified=True,
            ),
            RecoveryDisposition.BOOTSTRAP_EMPTY,
        )

    def test_valid_nonempty_pair_does_not_override_missing_state_nonempty_inventory(self):
        self.assertIs(
            decide_recovery_with_history_evidence(
                state_status=StateStatus.MISSING,
                observation=observation(inventory_is_empty=False),
                history_pair=pair(HistoryPairStatus.BOTH_RESPONSES_VALID),
                history_completeness_verified=True,
            ),
            RecoveryDisposition.HALT,
        )

    def test_valid_pair_does_not_override_corrupt_state(self):
        self.assertIs(
            decide_recovery_with_history_evidence(
                state_status=StateStatus.CORRUPT,
                observation=observation(),
                history_pair=pair(HistoryPairStatus.BOTH_RESPONSES_VALID),
                history_completeness_verified=True,
            ),
            RecoveryDisposition.HALT,
        )

    def test_valid_pair_does_not_override_unverified_account_identity(self):
        self.assertIs(
            decide_recovery_with_history_evidence(
                state_status=StateStatus.VALID,
                observation=observation(account_identity_verified=False),
                history_pair=pair(HistoryPairStatus.BOTH_RESPONSES_VALID),
                history_completeness_verified=True,
            ),
            RecoveryDisposition.HALT,
        )

    def test_valid_pair_does_not_override_unavailable_inventory(self):
        self.assertIs(
            decide_recovery_with_history_evidence(
                state_status=StateStatus.VALID,
                observation=observation(inventory_available=False),
                history_pair=pair(HistoryPairStatus.BOTH_RESPONSES_VALID),
                history_completeness_verified=True,
            ),
            RecoveryDisposition.HALT,
        )

    def test_valid_pair_does_not_override_incomplete_event_journal(self):
        self.assertIs(
            decide_recovery_with_history_evidence(
                state_status=StateStatus.VALID,
                observation=observation(event_journal_complete=False),
                history_pair=pair(HistoryPairStatus.BOTH_RESPONSES_VALID),
                history_completeness_verified=True,
            ),
            RecoveryDisposition.HALT,
        )

    def test_valid_pair_does_not_override_ambiguous_linkage(self):
        self.assertIs(
            decide_recovery_with_history_evidence(
                state_status=StateStatus.VALID,
                observation=observation(linkage_ambiguous=True),
                history_pair=pair(HistoryPairStatus.BOTH_RESPONSES_VALID),
                history_completeness_verified=True,
            ),
            RecoveryDisposition.HALT,
        )

    def test_valid_pair_can_restore_valid_state_when_all_independent_gates_pass(self):
        self.assertIs(
            decide_recovery_with_history_evidence(
                state_status=StateStatus.VALID,
                observation=observation(inventory_is_empty=False),
                history_pair=pair(HistoryPairStatus.BOTH_RESPONSES_VALID),
                history_completeness_verified=True,
            ),
            RecoveryDisposition.RESTORE,
        )

    def test_wrong_pair_type_is_rejected(self):
        with self.assertRaises(TypeError):
            decide_recovery_with_history_evidence(
                state_status=StateStatus.VALID,
                observation=observation(),
                history_pair=object(),  # type: ignore[arg-type]
                history_completeness_verified=True,
            )

    def test_forged_pair_with_missing_order_result_halts(self):
        malformed = HistoryPairObservation(
            position_identifier=9001,
            orders=None,  # type: ignore[arg-type]
            deals=HistoryQueryResult(
                query_kind=HistoryQueryKind.DEALS,
                position_identifier=9001,
                status=HistoryQueryStatus.EMPTY,
            ),
            status=HistoryPairStatus.BOTH_RESPONSES_VALID,
        )
        self.assertIs(
            decide_recovery_with_history_evidence(
                state_status=StateStatus.MISSING,
                observation=observation(),
                history_pair=malformed,
                history_completeness_verified=True,
            ),
            RecoveryDisposition.HALT,
        )

    def test_forged_pair_status_cannot_hide_failed_query(self):
        malformed = HistoryPairObservation(
            position_identifier=9001,
            orders=HistoryQueryResult(
                query_kind=HistoryQueryKind.ORDERS,
                position_identifier=9001,
                status=HistoryQueryStatus.ERROR,
            ),
            deals=HistoryQueryResult(
                query_kind=HistoryQueryKind.DEALS,
                position_identifier=9001,
                status=HistoryQueryStatus.EMPTY,
            ),
            status=HistoryPairStatus.BOTH_RESPONSES_VALID,
        )
        self.assertIs(
            decide_recovery_with_history_evidence(
                state_status=StateStatus.MISSING,
                observation=observation(),
                history_pair=malformed,
                history_completeness_verified=True,
            ),
            RecoveryDisposition.HALT,
        )


if __name__ == "__main__":
    unittest.main()
