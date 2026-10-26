from strategy_factory.order_deal_reconciliation import (
    DealRecord,
    OrderRecord,
    PositionRecord,
    ReconciliationStatus,
    reconcile_order_deals_positions,
)


def test_links_one_order_multiple_deals_to_one_position_without_collapsing_tickets():
    rows = reconcile_order_deals_positions(
        [OrderRecord(10, 30)],
        [DealRecord(20, 10, 30), DealRecord(21, 10, 30)],
        [PositionRecord(30)],
    )
    assert len(rows) == 1
    assert rows[0].status is ReconciliationStatus.LINKED
    assert rows[0].deal_tickets == (20, 21)


def test_missing_deal_is_incomplete_not_assumed_filled():
    rows = reconcile_order_deals_positions([OrderRecord(10)], [], [])
    assert rows[0].status is ReconciliationStatus.INCOMPLETE
    assert "NO_LINKED_DEAL_OBSERVED" in rows[0].issues


def test_orphan_deal_is_explicit():
    rows = reconcile_order_deals_positions([], [DealRecord(20, 10, 30)], [PositionRecord(30)])
    assert rows[0].status is ReconciliationStatus.INCOMPLETE
    assert "ORPHAN_DEAL_NO_UNIQUE_ORDER" in rows[0].issues


def test_conflicting_position_ids_are_not_silently_joined():
    rows = reconcile_order_deals_positions(
        [OrderRecord(10, 30)],
        [DealRecord(20, 10, 31)],
        [PositionRecord(30), PositionRecord(31)],
    )
    assert rows[0].status is ReconciliationStatus.CONFLICT
    assert "CONFLICT_ORDER_DEAL_POSITION_ID" in rows[0].issues


def test_duplicate_order_ticket_is_reported():
    rows = reconcile_order_deals_positions(
        [OrderRecord(10), OrderRecord(10)],
        [DealRecord(20, 10, 0)],
        [],
    )
    assert rows[0].status is ReconciliationStatus.DUPLICATE
    assert "DUPLICATE_ORDER_TICKET" in rows[0].issues


def test_duplicate_deal_ticket_is_reported_without_deduplication():
    rows = reconcile_order_deals_positions(
        [OrderRecord(10)],
        [DealRecord(20, 10, 0), DealRecord(20, 10, 0)],
        [],
    )
    assert rows[0].status is ReconciliationStatus.DUPLICATE
    assert "DUPLICATE_DEAL_TICKET" in rows[0].issues
    assert rows[0].deal_tickets == (20, 20)


def test_unreferenced_position_is_preserved_as_issue():
    rows = reconcile_order_deals_positions([], [], [PositionRecord(30)])
    assert rows[0].status is ReconciliationStatus.INCOMPLETE
    assert "UNREFERENCED_POSITION_IN_SUPPLIED_SNAPSHOT" in rows[0].issues


def test_invalid_identifier_remains_unresolved():
    rows = reconcile_order_deals_positions(
        [OrderRecord(0)], [DealRecord(-1, 0, -2)], []
    )
    assert any(row.status is ReconciliationStatus.UNRESOLVED for row in rows)


def test_order_without_position_id_can_link_deals_but_missing_snapshot_is_visible():
    rows = reconcile_order_deals_positions(
        [OrderRecord(10)],
        [DealRecord(20, 10, 30)],
        [],
    )
    assert rows[0].status is ReconciliationStatus.INCOMPLETE
    assert rows[0].position_id == 30
    assert "POSITION_NOT_PRESENT_IN_SUPPLIED_SNAPSHOT" in rows[0].issues


def test_reconciliation_does_not_claim_fill_completion():
    rows = reconcile_order_deals_positions(
        [OrderRecord(10, 30)],
        [DealRecord(20, 10, 30)],
        [PositionRecord(30)],
    )
    assert not hasattr(rows[0], "filled_volume")
    assert not hasattr(rows[0], "complete_fill")
