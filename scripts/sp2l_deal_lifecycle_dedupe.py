"""Small idempotency helper for V3.1 observed deal lifecycle events.

This tracks event observation separately from successful Telegram delivery.
It does not define trading, fill, or execution semantics.
"""
from __future__ import annotations


def claim_deal_lifecycle_event(state: dict, ticket: int) -> bool:
    """Return True once per deal ticket; persist the observation in state."""
    observed = state.get("deal_events")
    if not isinstance(observed, set):
        observed = set(observed or ())
        state["deal_events"] = observed
    key = int(ticket)
    if key in observed:
        return False
    observed.add(key)
    return True
