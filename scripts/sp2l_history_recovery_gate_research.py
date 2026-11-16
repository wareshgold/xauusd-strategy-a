"""Fail-closed history-to-recovery gate for offline research.

This layer consumes an already-paired observation. It performs no I/O and
never treats tuple emptiness as proof of history completeness.
"""
from __future__ import annotations

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
    decide_recovery,
)


def decide_recovery_with_history_evidence(
    *,
    state_status: StateStatus,
    observation: RecoveryObservation,
    history_pair: HistoryPairObservation,
    history_completeness_verified: bool,
) -> RecoveryDisposition:
    """Permit existing recovery logic only after independent evidence gates.

    The completeness flag must come from a separate, explicit evidence source;
    it is not derived from a successful or empty history query. This function
    merely requires that assertion and a fully valid paired query observation.
    """
    if not isinstance(history_pair, HistoryPairObservation):
        raise TypeError("history_pair must be a HistoryPairObservation")
    if not isinstance(history_pair.orders, HistoryQueryResult):
        return RecoveryDisposition.HALT
    if not isinstance(history_pair.deals, HistoryQueryResult):
        return RecoveryDisposition.HALT
    if history_pair.orders.query_kind is not HistoryQueryKind.ORDERS:
        return RecoveryDisposition.HALT
    if history_pair.deals.query_kind is not HistoryQueryKind.DEALS:
        return RecoveryDisposition.HALT
    if history_pair.position_identifier != history_pair.orders.position_identifier:
        return RecoveryDisposition.HALT
    if history_pair.position_identifier != history_pair.deals.position_identifier:
        return RecoveryDisposition.HALT

    outcomes_valid = {
        HistoryQueryStatus.EMPTY,
        HistoryQueryStatus.NON_EMPTY,
    }
    expected_pair_status = (
        HistoryPairStatus.BOTH_RESPONSES_VALID
        if history_pair.orders.status in outcomes_valid
        and history_pair.deals.status in outcomes_valid
        else HistoryPairStatus.AT_LEAST_ONE_QUERY_FAILED
    )
    if history_pair.status is not expected_pair_status:
        return RecoveryDisposition.HALT
    if history_pair.status is not HistoryPairStatus.BOTH_RESPONSES_VALID:
        return RecoveryDisposition.HALT
    if not history_completeness_verified:
        return RecoveryDisposition.HALT
    return decide_recovery(state_status, observation)
