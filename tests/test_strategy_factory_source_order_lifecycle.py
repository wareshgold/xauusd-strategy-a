from strategy_factory.source_order_lifecycle import (
    DealEntry,
    DealObservation,
    EvidenceClass,
    OrderLifecycle,
    OrderObservation,
    classify_lifecycle,
)


def test_placed_order_is_not_a_fill():
    result = classify_lifecycle(OrderObservation(10, "PLACED"), None)
    assert result.evidence is EvidenceClass.ORDER_STATE_ONLY
    assert result.deal_entry is None


def test_partial_order_without_volume_evidence_is_unresolved():
    result = classify_lifecycle(OrderObservation(10, "PARTIAL"), None)
    assert result.evidence is EvidenceClass.UNRESOLVED
    assert result.reason == "PARTIAL_STATE_WITHOUT_VOLUME_EVIDENCE"


def test_partial_order_preserves_remaining_volume_evidence():
    result = classify_lifecycle(
        OrderObservation(10, "PARTIAL", volume_initial=0.10, volume_current=0.06),
        None,
    )
    assert result.evidence is EvidenceClass.PARTIAL_VOLUME_REMAINS
    assert result.order_state is OrderLifecycle.PARTIAL


def test_filled_order_state_is_not_substituted_for_deal_ledger():
    result = classify_lifecycle(OrderObservation(10, "FILLED"), None)
    assert result.evidence is EvidenceClass.TERMINAL_ORDER_STATE
    assert "NOT_A_DEAL_LEDGER" in result.reason


def test_deal_record_does_not_infer_full_order_completion():
    result = classify_lifecycle(
        OrderObservation(10, "PARTIAL", 0.10, 0.06),
        DealObservation(20, 10, 30, "IN", 0.04),
    )
    assert result.evidence is EvidenceClass.DEAL_RECORDED
    assert result.deal_entry is DealEntry.IN
    assert "NOT_INFERRED" in result.reason


def test_exit_deal_remains_distinct_from_entry_deal():
    result = classify_lifecycle(
        None, DealObservation(21, 10, 30, "OUT", 0.04)
    )
    assert result.evidence is EvidenceClass.DEAL_RECORDED
    assert result.deal_entry is DealEntry.OUT


def test_unknown_order_state_is_unresolved_not_guessed():
    result = classify_lifecycle(OrderObservation(10, "FILLED_PARTIAL_MYSTERY"), None)
    assert result.evidence is EvidenceClass.UNRESOLVED
    assert result.order_state is OrderLifecycle.UNKNOWN


def test_unknown_deal_entry_does_not_become_entry_or_exit():
    result = classify_lifecycle(None, DealObservation(21, 10, 30, "MYSTERY", 0.04))
    assert result.evidence is EvidenceClass.UNRESOLVED
    assert result.deal_entry is DealEntry.UNKNOWN


def test_missing_observations_are_unresolved():
    result = classify_lifecycle(None, None)
    assert result.evidence is EvidenceClass.UNRESOLVED
    assert result.reason == "NO_ORDER_OR_DEAL_OBSERVATION"


def test_invalid_partial_volume_is_unresolved():
    result = classify_lifecycle(
        OrderObservation(10, "PARTIAL", volume_initial=0.10, volume_current=0.12),
        None,
    )
    assert result.evidence is EvidenceClass.UNRESOLVED
    assert result.reason == "CURRENT_VOLUME_EXCEEDS_INITIAL"
