from sp2l_pending_update_f11 import (
    OrderAction,
    PendingOrder,
    compare_pending_order,
    explicit_management_decision,
)


def test_unchanged_order_is_keep():
    order = PendingOrder(103.0, 99.0)
    assert compare_pending_order(order, order) is OrderAction.KEEP


def test_changed_distance_does_not_invent_threshold():
    old = PendingOrder(103.0, 99.0)
    new = PendingOrder(105.0, 99.0)
    assert compare_pending_order(old, new) is OrderAction.UNRESOLVED


def test_source_level_materiality_can_be_represented():
    assert explicit_management_decision(False) is OrderAction.KEEP
    assert explicit_management_decision(True) is OrderAction.REPLACE


def test_delete_replace_is_not_market_reclaim():
    old = PendingOrder(103.0, 99.0)
    new = PendingOrder(105.0, 99.0)
    assert compare_pending_order(old, new) is not OrderAction.REPLACE
    assert compare_pending_order(old, new) is not OrderAction.KEEP
