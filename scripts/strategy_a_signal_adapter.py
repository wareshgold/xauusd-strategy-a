"""Strategy A signal adapter — PREPARED BUT INACTIVE (activation-gated).

Purpose: map one *scanner-output* record onto the gateway's approved-signal
payload schema (runtime/approved_signal.json) so that, IF the operator ever
activates the adapter AND a human-approved signal source is wired in, the
gateway can consume it without any further glue code.

Safety boundaries (non-negotiable, enforced here):
- The adapter computes NO strategy geometry: no P-Gap, no AB=CD, no Leg1/Leg2,
  no entry/SL/TP derivation. If a geometry field is missing from the scanner
  record, the adapter FAILS the record; it never invents a value.
- The adapter generates NO autonomous signals: it only transforms an existing
  record that must already carry status=APPROVED from a human validation gate.
- Activation requires TWO env keys (STRATEGY_A_ADAPTER_ENABLE=true AND
  STRATEGY_A_ADAPTER_SOURCE=<name>) and is default-off.
- Live trading remains governed by the gateway's own double gate
  (LIVE_TRADING_ENABLE + ALLOW_REAL_EXECUTION); this module never touches it.
"""

from __future__ import annotations

import os
from typing import Any


class AdapterError(ValueError):
    """Raised when a scanner record cannot be mapped safely."""


def adapter_state() -> dict:
    """Report the activation gate. Default: INACTIVE."""
    enabled = os.getenv("STRATEGY_A_ADAPTER_ENABLE", "false").strip().lower() == "true"
    source = os.getenv("STRATEGY_A_ADAPTER_SOURCE", "").strip()
    return {
        "adapter_active": bool(enabled and source),
        "strategy_a_adapter_enable": enabled,
        "strategy_a_adapter_source": source or None,
        "detail": (
            f"ACTIVE (source={source})" if (enabled and source)
            else "INACTIVE (default-off; set STRATEGY_A_ADAPTER_ENABLE=true AND "
            "STRATEGY_A_ADAPTER_SOURCE=<name> to activate)"
        ),
    }


def _required(record: dict, key: str) -> Any:
    value = record.get(key)
    if value is None or value == "":
        raise AdapterError(
            f"scanner record missing required field '{key}' — "
            "the adapter never invents geometry values"
        )
    return value


def _direction(record: dict) -> str:
    raw = _required(record, "direction")
    direction = str(raw).strip().upper()
    # Common scanner synonyms are normalized; anything else is refused.
    synonyms = {
        "BUY": "BUY", "LONG": "BUY", "B": "BUY",
        "SELL": "SELL", "SHORT": "SELL", "S": "SELL",
    }
    if direction not in synonyms:
        raise AdapterError(f"unmapped direction {raw!r}")
    return synonyms[direction]


def _status(record: dict) -> str:
    status = str(_required(record, "status")).strip().upper()
    if status != "APPROVED":
        raise AdapterError(
            f"scanner status {status!r} != APPROVED — only human-approved "
            "signals may pass the adapter"
        )
    return status


def map_scanner_record(record: dict, *, symbol: str) -> dict:
    """Map one scanner record to the gateway approved-signal payload.

    Identity/echo fields (entry, sl, tp, volume, timestamps, ids) are passed
    through verbatim from the scanner output; no numeric transformation of
    any geometry value happens in this module.
    """
    state = adapter_state()
    if not state["adapter_active"]:
        raise AdapterError(
            "adapter is INACTIVE (STRATEGY_A_ADAPTER_ENABLE!=true) — "
            "refusing to map records"
        )

    direction = _direction(record)
    status = _status(record)

    payload = {
        "direction": direction,
        "symbol": str(symbol),
        "entry": float(_required(record, "entry")),
        "sl": float(_required(record, "sl")),
        "tp": float(_required(record, "tp")),
        "volume": float(_required(record, "volume")),
        "signal_id": str(_required(record, "signal_id")),
        "source": str(_required(record, "source")),
        "status": status,
    }

    # Structural sanity (validation, not geometry): SL/TP must sit on the
    # protective side of the entry; anything else is a malformed record.
    if payload["sl"] == payload["entry"] or payload["tp"] == payload["entry"]:
        raise AdapterError("sl/tp must differ from entry")
    if direction == "BUY" and not (payload["sl"] < payload["entry"] < payload["tp"]):
        raise AdapterError("BUY requires sl < entry < tp")
    if direction == "SELL" and not (payload["tp"] < payload["entry"] < payload["sl"]):
        raise AdapterError("SELL requires tp < entry < sl")
    if payload["volume"] <= 0:
        raise AdapterError("volume must be positive")

    return payload


def map_scanner_batch(records: list[dict], *, symbol: str) -> list[dict]:
    """Map a batch; refuses the WHOLE batch if any record fails (no partials)."""
    return [map_scanner_record(r, symbol=symbol) for r in records]
