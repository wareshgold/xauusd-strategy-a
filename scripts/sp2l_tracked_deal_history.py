"""Fetch lifecycle deals by runner-owned MT5 order/position IDs.

Avoid host-UTC time windows when broker timestamps use a different clock basis.
Callers must supply only IDs they own or have explicitly reconciled.
Active orders are observed through orders_get, not history_orders_get.
Terminal orders are resolved with history_orders_get(ticket=...), then linked
position histories are collected with history_deals_get(position=...).
Query failures remain distinct from valid empty results and are returned
alongside any deals that could still be collected.
"""
from __future__ import annotations

from dataclasses import dataclass


class DealHistoryQueryError(RuntimeError):
    """An MT5 history query failed or returned None instead of a result."""

    def __init__(self, query: str, target: int, detail: str):
        self.query = query
        self.target = int(target)
        self.detail = detail
        super().__init__(f"{query}({target}) failed: {detail}")


@dataclass(frozen=True)
class DealHistoryCollection:
    """Partial, explicit result: usable deals plus independent query failures."""

    deals: list
    failures: list[DealHistoryQueryError]


def _last_error_detail(last_error) -> str | None:
    if not callable(last_error):
        return None
    try:
        value = last_error()
    except Exception as exc:
        return f"last_error unavailable: {type(exc).__name__}: {exc}"
    return str(value)


def _history_result(function, query: str, target: int, *, last_error=None, **kwargs):
    if not callable(function):
        raise DealHistoryQueryError(query, target, "query function unavailable")
    try:
        result = function(**kwargs)
    except Exception as exc:
        detail = f"{type(exc).__name__}: {exc}"
        extra = _last_error_detail(last_error)
        if extra:
            detail = f"{detail}; MT5 last_error={extra}"
        raise DealHistoryQueryError(query, target, detail) from exc
    if result is None:
        detail = "MT5 returned None"
        extra = _last_error_detail(last_error)
        if extra:
            detail = f"{detail}; MT5 last_error={extra}"
        raise DealHistoryQueryError(query, target, detail)
    return result


def collect_tracked_deals(
    *,
    history_deals_get,
    history_orders_get,
    symbol,
    tracked_orders,
    tracked_positions,
    active_order_ids=(),
    last_error=None,
):
    """Collect deals for runner-owned IDs without conflating active/history APIs.

    Active order IDs are skipped because they belong to orders_get, not the
    historical-order lookup. A failed terminal-order lookup is recorded but
    does not prevent known position histories from being queried. A failed
    position query is likewise recorded without discarding deals from other
    positions. Empty tuples/lists remain valid empty results.
    """
    orders = {int(x) for x in tracked_orders if int(x) > 0}
    positions = {int(x) for x in tracked_positions if int(x) > 0}
    active = {int(x) for x in active_order_ids if int(x) > 0}
    failures = []

    for order_id in sorted(orders - active):
        try:
            historical_orders = _history_result(
                history_orders_get, "history_orders_get", order_id,
                last_error=last_error, ticket=order_id,
            )
        except DealHistoryQueryError as exc:
            failures.append(exc)
            continue
        for order in historical_orders:
            if str(getattr(order, "symbol", symbol) or symbol) != symbol:
                continue
            if int(getattr(order, "ticket", 0) or 0) != order_id:
                continue
            position_id = int(getattr(order, "position_id", 0) or 0)
            if position_id > 0:
                positions.add(position_id)

    found = {}
    for position_id in sorted(positions):
        try:
            position_deals = _history_result(
                history_deals_get, "history_deals_get(position)", position_id,
                last_error=last_error, position=position_id,
            )
        except DealHistoryQueryError as exc:
            failures.append(exc)
            continue
        for deal in position_deals:
            if str(getattr(deal, "symbol", symbol) or symbol) != symbol:
                continue
            deal_order = int(getattr(deal, "order", 0) or 0)
            deal_position = int(getattr(deal, "position_id", 0) or 0)
            if deal_order not in orders and deal_position != position_id:
                continue
            found[int(deal.ticket)] = deal

    deals = sorted(found.values(), key=lambda d: (int(d.time), int(d.ticket)))
    return DealHistoryCollection(deals=deals, failures=failures)


def collect_runner_scoped_deals(
    *,
    orders_get,
    history_deals_get,
    history_orders_get,
    symbol,
    magic,
    tracked_orders,
    tracked_positions,
    last_error=None,
):
    """Resolve active inventory and collect history, failing closed on uncertainty.

    If orders_get returns None or raises, every tracked order is treated as
    active/unknown and excluded from history_orders_get. Known position IDs
    are still queried independently. A successful empty inventory is distinct
    from an unavailable inventory.
    """
    tracked = {int(x) for x in tracked_orders if int(x) > 0}
    inventory_failure = None
    try:
        active_orders = orders_get(symbol=symbol)
        if active_orders is None:
            raise RuntimeError("MT5 orders_get returned None")
    except Exception as exc:
        active_ids = tracked
        detail = f"{type(exc).__name__}: {exc}"
        extra = _last_error_detail(last_error)
        if extra:
            detail += f"; MT5 last_error={extra}"
        inventory_failure = DealHistoryQueryError("orders_get", 0, detail)
    else:
        active_ids = {
            int(getattr(order, "ticket", 0) or 0)
            for order in active_orders
            if int(getattr(order, "ticket", 0) or 0) > 0
            and str(getattr(order, "symbol", "") or "") == symbol
            and int(getattr(order, "magic", 0) or 0) == int(magic)
        }

    collection = collect_tracked_deals(
        history_deals_get=history_deals_get,
        history_orders_get=history_orders_get,
        symbol=symbol,
        tracked_orders=tracked,
        tracked_positions=tracked_positions,
        active_order_ids=active_ids,
        last_error=last_error,
    )
    failures = ([inventory_failure] if inventory_failure else []) + collection.failures
    return DealHistoryCollection(deals=collection.deals, failures=failures)


def log_deal_history_failures(*, failures, should_log, log_event, version, symbol):
    """Emit deduplicated, non-canonical failure telemetry for a collection."""
    logged = 0
    for exc in failures:
        if should_log(exc.query, exc.target, exc.detail):
            log_event({
                "event": "MT5_DEAL_HISTORY_QUERY_FAILED",
                "version": version,
                "symbol": symbol,
                "query": exc.query,
                "target": exc.target,
                "detail": exc.detail,
                "canonical": False,
            })
            logged += 1
    return logged
