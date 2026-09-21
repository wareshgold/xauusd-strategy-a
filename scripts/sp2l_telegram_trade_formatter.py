"""Deterministic operator-facing Telegram trade notifications.

Reporting/infrastructure only:
- no Strategy A geometry;
- no signal generation;
- no execution decisions;
- Tehran presentation timezone is explicit and fixed for this template.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

TEHRAN = ZoneInfo("Asia/Tehran")


def _price(value: float) -> str:
    return f"{float(value):.2f}"


def _signed(value: float) -> str:
    return f"{float(value):+.2f}"


def _tehran(dt: datetime | None = None) -> tuple[str, str]:
    value = (dt or datetime.now(TEHRAN)).astimezone(TEHRAN)
    return value.strftime("%H:%M"), value.strftime("%d/%m/%Y")


def format_signal_notification(
    *,
    direction: str,
    entry: float,
    sl: float,
    tp: float,
    at: datetime | None = None,
) -> str:
    direction = direction.upper()
    marker = "🟢" if direction == "BUY" else "🔴"
    time_text, date_text = _tehran(at)
    sl_distance = -(abs(float(entry) - float(sl)))
    tp_distance = abs(float(tp) - float(entry))
    return "\n".join(
        [
            f"{marker} XAUUSD {direction}",
            "",
            f"Entry: {_price(entry)}",
            f"SL: {_price(sl)}",
            f"TP: {_price(tp)}",
            "",
            f"SL: {_signed(sl_distance)}",
            f"TP: {_signed(tp_distance)}",
            "",
            f"Time: {time_text}",
            f"Date: {date_text}",
        ]
    )


def format_result_notification(
    *,
    direction: str,
    entry: float,
    exit_price: float,
    outcome: str,
    at: datetime | None = None,
) -> str:
    direction = direction.upper()
    outcome = outcome.upper()
    time_text, date_text = _tehran(at)
    delta = (
        float(exit_price) - float(entry)
        if direction == "BUY"
        else float(entry) - float(exit_price)
    )
    tp_amount = delta if outcome == "TP" else 0.0
    sl_amount = delta if outcome == "SL" else 0.0
    icon = "✅" if outcome == "TP" else ("❌" if outcome == "SL" else "⚠️")
    return "\n".join(
        [
            f"{icon} XAUUSD {direction} — {outcome}",
            "",
            f"Entry: {_price(entry)}",
            f"Exit: {_price(exit_price)}",
            "",
            f"TP: {_signed(tp_amount)}",
            f"SL: {_signed(sl_amount)}",
            "",
            f"Time: {time_text}",
            f"Date: {date_text}",
        ]
    )
