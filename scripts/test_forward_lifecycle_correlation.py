"""Deterministic regression checks for forward lifecycle authorization.

Research/infrastructure only. These tests verify that MT5 lifecycle telemetry
cannot be authorized by a shared magic number or stale state membership alone.
"""

from types import SimpleNamespace

from run_sp2l_author_replica_multi_symbol_forward_test import _deal_is_authorized


def deal(*, order=0, position=0, magic=26092201):
    return SimpleNamespace(order=order, position_id=position, magic=magic)


def main() -> None:
    state = {
        "signal_orders": {"62240001": {"signal_id": "S1"}},
        "position_orders": {},
    }

    # Shared magic alone must never authorize an unrelated deal.
    assert not _deal_is_authorized(
        state, deal(order=99999999, position=88888888, magic=26092201)
    )

    # The exact runner-created order authorizes its entry deal.
    assert _deal_is_authorized(state, deal(order=62240001, position=70001))

    # A position previously linked to the runner order authorizes its exit.
    state["position_orders"]["70001"] = {62240001}
    assert _deal_is_authorized(state, deal(order=62240002, position=70001))

    # A different position must not inherit authorization from another position.
    assert not _deal_is_authorized(state, deal(order=62240003, position=70002))

    # Stale state["orders"] / state["positions"] membership is intentionally ignored.
    state["orders"] = {62240004}
    state["positions"] = {70003}
    assert not _deal_is_authorized(state, deal(order=62240004, position=70003))

    print("FORWARD_LIFECYCLE_CORRELATION_TESTS: PASS")


if __name__ == "__main__":
    main()
