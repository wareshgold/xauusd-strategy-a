"""Fail-closed V3.1 startup identity and account-inventory checks.

These checks are operational safeguards only; they do not define SP2L rules.
"""

from __future__ import annotations


def inspect_account_identity(*, account, expected_login: str, expected_server: str) -> dict:
    """Require an explicit operator-pinned login and exact server identity."""
    if account is None:
        return {"ok": False, "reason": "ACCOUNT_INFO_UNAVAILABLE"}
    login_text = str(expected_login or "").strip()
    server_text = str(expected_server or "").strip()
    if not login_text or not server_text:
        return {"ok": False, "reason": "EXPECTED_ACCOUNT_IDENTITY_NOT_CONFIGURED"}
    try:
        expected_login_int = int(login_text)
        actual_login_int = int(getattr(account, "login", None))
    except (TypeError, ValueError, OverflowError):
        return {"ok": False, "reason": "ACCOUNT_LOGIN_INVALID"}
    actual_server = getattr(account, "server", None)
    if not isinstance(actual_server, str) or not actual_server.strip():
        return {"ok": False, "reason": "ACCOUNT_SERVER_UNAVAILABLE"}
    if actual_login_int != expected_login_int:
        return {"ok": False, "reason": "ACCOUNT_LOGIN_MISMATCH"}
    if actual_server != server_text:
        return {"ok": False, "reason": "ACCOUNT_SERVER_MISMATCH"}
    return {"ok": True, "reason": "ACCOUNT_IDENTITY_MATCH"}


def inspect_account_inventory(*, orders, positions, owned_pairs) -> dict:
    """Reject any account-wide active object not owned by a configured V3.1 slot.

    owned_pairs is an iterable of exact (symbol, magic) tuples. None broker
    results mean query failure, not empty inventory. Every record is validated.
    """
    if orders is None or positions is None:
        missing = []
        if orders is None:
            missing.append("orders")
        if positions is None:
            missing.append("positions")
        return {
            "ok": False,
            "reason": "BROKER_INVENTORY_UNAVAILABLE",
            "failed_queries": missing,
            "foreign_orders": [],
            "foreign_positions": [],
        }

    allowed = {(str(symbol), int(magic)) for symbol, magic in owned_pairs}
    if not allowed:
        return {
            "ok": False,
            "reason": "NO_CONFIGURED_OWNERSHIP_SCOPE",
            "failed_queries": [],
            "foreign_orders": [],
            "foreign_positions": [],
        }

    def classify(items, kind):
        foreign = []
        seen = set()
        for index, item in enumerate(items):
            symbol = getattr(item, "symbol", None)
            magic_raw = getattr(item, "magic", None)
            ticket_raw = getattr(item, "ticket", None)
            if not isinstance(symbol, str) or not symbol.strip():
                raise ValueError(f"account inventory {kind}[{index}] missing/invalid symbol")
            if magic_raw is None:
                raise ValueError(f"account inventory {kind}[{index}] missing magic")
            if ticket_raw is None:
                raise ValueError(f"account inventory {kind}[{index}] missing ticket")
            try:
                magic = int(magic_raw)
                ticket = int(ticket_raw)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(f"account inventory {kind}[{index}] has invalid numeric fields") from exc
            if ticket <= 0:
                raise ValueError(f"account inventory {kind}[{index}] has non-positive ticket")
            identity = (symbol, magic, ticket)
            if identity in seen:
                raise ValueError(f"duplicate account inventory {kind} ticket: {ticket}")
            seen.add(identity)
            if (symbol, magic) not in allowed:
                foreign.append({"symbol": symbol, "magic": magic, "ticket": ticket})
        return foreign

    foreign_orders = classify(orders, "orders")
    foreign_positions = classify(positions, "positions")
    foreign = bool(foreign_orders or foreign_positions)
    return {
        "ok": not foreign,
        "reason": "UNRECOGNIZED_ACCOUNT_INVENTORY" if foreign else "ACCOUNT_INVENTORY_RECOGNIZED",
        "failed_queries": [],
        "foreign_orders": foreign_orders,
        "foreign_positions": foreign_positions,
    }


class BrokerInventoryQueryError(RuntimeError):
    """Raised when an MT5 inventory query throws instead of returning a snapshot."""

    def __init__(self, query_name: str, cause: Exception):
        self.query_name = str(query_name)
        self.cause = cause
        super().__init__(f"{self.query_name} raised {type(cause).__name__}: {cause}")


def query_inventory_snapshot(*, query_name: str, query):
    """Run a required MT5 query without masking exceptions.

    A returned None is preserved for the inventory classifier to reject;
    a raised exception is tagged with the exact query name for startup alerting.
    """
    try:
        return query()
    except Exception as exc:
        raise BrokerInventoryQueryError(query_name, exc) from exc
