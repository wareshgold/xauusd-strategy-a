"""Research-only V2 forward population/lifecycle ledger.

This module records the deterministic state of each V2 signal without defining
canonical geometry, fill semantics, or a production trading rule.

The ledger is intentionally observational in this phase:
DETECTED -> ORDER_PLACED/ORDER_REJECTED -> FILLED -> CLOSED
                                      -> EXPIRED

A signal may also be marked SUPPRESSED/BLOCKED before execution.  Such records
remain in the ledger so Backtest/Forward population differences are attributable
rather than silently discarded.
"""
from __future__ import annotations

from copy import deepcopy


TERMINAL_STATUSES = {"ORDER_REJECTED", "CLOSED", "EXPIRED", "BLOCKED", "SUPPRESSED"}


def ensure_state(state: dict) -> dict:
    ledger = state.setdefault("v2_forward_ledger", {})
    ledger.setdefault("signals", {})
    ledger.setdefault("orders", {})
    ledger.setdefault("positions", {})
    return ledger


def signal_id(candidate: dict) -> str:
    existing = str(candidate.get("signal_id") or "").strip()
    if existing:
        return existing
    return (
        f"{candidate.get('symbol','?')}:"
        f"{int(candidate.get('trigger_time', 0))}:"
        f"{candidate.get('direction','?')}"
    )


def _record(state: dict, candidate: dict, **fields) -> dict:
    ledger = ensure_state(state)
    sid = signal_id(candidate)
    rec = ledger["signals"].setdefault(sid, {
        "signal_id": sid,
        "symbol": str(candidate.get("symbol") or ""),
        "direction": str(candidate.get("direction") or ""),
        "trigger_time": int(candidate.get("trigger_time", 0) or 0),
        "theoretical_entry": float(candidate.get("theoretical_entry", 0.0) or 0.0),
        "sl": float(candidate.get("sl", 0.0) or 0.0),
        "tp": float(candidate.get("tp", 0.0) or 0.0),
        "risk": float(candidate.get("risk", 0.0) or 0.0),
        "status": "DETECTED",
    })
    rec.update(deepcopy(fields))
    return rec


def record_detected(state: dict, candidate: dict) -> dict:
    return _record(state, candidate, status="DETECTED")


def record_blocked(state: dict, candidate: dict, reason: str, stage: str) -> dict:
    return _record(state, candidate, status="BLOCKED", block_stage=str(stage), block_reason=str(reason))


def record_suppressed(state: dict, candidate: dict, reason: str) -> dict:
    return _record(state, candidate, status="SUPPRESSED", suppression_reason=str(reason))


def record_order_result(state: dict, candidate: dict, result: dict) -> dict:
    sid = signal_id(candidate)
    ok = bool(result.get("ok"))
    order = int(result.get("order", 0) or 0)
    deal = int(result.get("deal", 0) or 0)
    rec = _record(
        state,
        candidate,
        status="ORDER_PLACED" if ok else "ORDER_REJECTED",
        order_id=order or None,
        immediate_deal_id=deal or None,
        execution_result=deepcopy(result),
    )
    if order:
        ensure_state(state)["orders"][str(order)] = sid
    if deal:
        ensure_state(state)["signals"][sid]["immediate_deal_id"] = deal
    return rec


def record_order_lifecycle(state: dict, order_id: int, state_name: str, position_id: int | None = None) -> None:
    ledger = ensure_state(state)
    sid = ledger["orders"].get(str(int(order_id)))
    if not sid or sid not in ledger["signals"]:
        return
    rec = ledger["signals"][sid]
    rec.setdefault("order_lifecycle", []).append({
        "state": str(state_name),
        "position_id": int(position_id) if position_id else None,
    })
    if state_name == "EXPIRED":
        rec["status"] = "EXPIRED"
    elif state_name == "FILLED" and rec["status"] == "ORDER_PLACED":
        rec["status"] = "FILLED"


def record_deal(state: dict, execution_meta: dict, deal: dict) -> None:
    sid = str(execution_meta.get("signal_id") or "")
    if not sid:
        return
    ledger = ensure_state(state)
    rec = ledger["signals"].get(sid)
    if rec is None:
        return
    entry = int(deal.get("entry", -1))
    ticket = int(deal.get("deal", 0) or 0)
    position = int(deal.get("position", 0) or 0)
    order = int(deal.get("order", 0) or 0)
    if entry == 0:  # MT5 DEAL_ENTRY_IN
        rec["status"] = "FILLED"
        rec["filled_deal_id"] = ticket or None
        rec["position_id"] = position or None
        rec["fill_price"] = deal.get("entry_price")
        rec["entry_slippage"] = deal.get("entry_slippage")
        if position:
            ledger["positions"][str(position)] = sid
        if order:
            ledger["orders"][str(order)] = sid
    else:
        rec["status"] = "CLOSED"
        rec["exit_deal_id"] = ticket or None
        rec["exit_price"] = deal.get("exit_price")
        rec["actual_r"] = deal.get("actual_r")
        rec["net"] = deal.get("net")
        rec["exit_reason"] = deal.get("reason")
        rec["position_id"] = position or rec.get("position_id")
        if position:
            ledger["positions"][str(position)] = sid


def record_expired_order(state: dict, order_id: int) -> None:
    ledger = ensure_state(state)
    sid = ledger["orders"].get(str(int(order_id)))
    if sid and sid in ledger["signals"]:
        ledger["signals"][sid]["status"] = "EXPIRED"


def summarize(state: dict) -> dict:
    ledger = ensure_state(state)
    records = list(ledger["signals"].values())
    return {
        "signals": len(records),
        "detected": sum(r.get("status") == "DETECTED" for r in records),
        "order_placed": sum(r.get("status") == "ORDER_PLACED" for r in records),
        "filled": sum(r.get("status") == "FILLED" for r in records),
        "closed": sum(r.get("status") == "CLOSED" for r in records),
        "expired": sum(r.get("status") == "EXPIRED" for r in records),
        "rejected": sum(r.get("status") == "ORDER_REJECTED" for r in records),
        "blocked": sum(r.get("status") == "BLOCKED" for r in records),
        "suppressed": sum(r.get("status") == "SUPPRESSED" for r in records),
    }
