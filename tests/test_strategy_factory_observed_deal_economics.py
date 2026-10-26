from strategy_factory.observed_deal_economics import (
    EconomicDeal,
    LedgerStatus,
    summarize_observed_deals,
)


def test_sums_only_explicit_observed_values_and_keeps_deal_tickets():
    result = summarize_observed_deals([
        EconomicDeal(101, 0.02, 5.0, -0.4, -0.1, -0.05),
        EconomicDeal(102, 0.01, -2.0, -0.2, 0.0, 0.0),
    ])
    assert result.status is LedgerStatus.OBSERVED_ONLY
    assert result.deal_tickets == (101, 102)
    assert result.observed_deal_count == 2
    assert result.observed_volume_sum == 0.03
    assert result.gross_profit_sum == 3.0
    assert result.commission_sum == -0.6
    assert result.swap_sum == -0.1
    assert result.fee_sum == -0.05
    assert abs(result.net_result_sum - 2.25) < 1e-12


def test_missing_cost_field_blocks_net_result_instead_of_treating_as_zero():
    result = summarize_observed_deals([
        EconomicDeal(101, 0.01, 2.0, None, 0.0, 0.0),
    ])
    assert result.status is LedgerStatus.INCOMPLETE_FIELDS
    assert result.commission_sum is None
    assert result.net_result_sum is None
    assert "REQUIRED_ECONOMIC_FIELD_MISSING" in result.issues


def test_missing_volume_blocks_volume_total():
    result = summarize_observed_deals([
        EconomicDeal(101, None, 2.0, -0.1, 0.0, 0.0),
    ])
    assert result.status is LedgerStatus.INCOMPLETE_FIELDS
    assert result.observed_volume_sum is None


def test_empty_history_is_not_zero_pnl_or_zero_volume():
    result = summarize_observed_deals([])
    assert result.status is LedgerStatus.EMPTY_LEDGER
    assert result.observed_volume_sum is None
    assert result.net_result_sum is None
    assert "NO_DEAL_ROWS_SUPPLIED" in result.issues


def test_duplicate_deal_ticket_invalidates_aggregate():
    result = summarize_observed_deals([
        EconomicDeal(101, 0.01, 2.0, 0.0, 0.0, 0.0),
        EconomicDeal(101, 0.01, 2.0, 0.0, 0.0, 0.0),
    ])
    assert result.status is LedgerStatus.INVALID_RECORD
    assert result.net_result_sum is None
    assert "DUPLICATE_DEAL_TICKET" in result.issues


def test_invalid_ticket_invalidates_aggregate():
    result = summarize_observed_deals([
        EconomicDeal(0, 0.01, 2.0, 0.0, 0.0, 0.0),
    ])
    assert result.status is LedgerStatus.INVALID_RECORD
    assert "INVALID_DEAL_TICKET" in result.issues


def test_nonfinite_economic_value_invalidates_aggregate():
    result = summarize_observed_deals([
        EconomicDeal(101, 0.01, float("nan"), 0.0, 0.0, 0.0),
    ])
    assert result.status is LedgerStatus.INVALID_RECORD
    assert "NONFINITE_PROFIT" in result.issues


def test_negative_commission_and_fee_are_preserved_as_signed_values():
    result = summarize_observed_deals([
        EconomicDeal(101, 0.01, 1.0, -0.2, -0.1, -0.05),
    ])
    assert result.net_result_sum == 0.65


def test_summary_does_not_claim_complete_fill_or_complete_history():
    result = summarize_observed_deals([
        EconomicDeal(101, 0.01, 1.0, 0.0, 0.0, 0.0),
    ])
    assert not hasattr(result, "filled_volume")
    assert not hasattr(result, "history_complete")
