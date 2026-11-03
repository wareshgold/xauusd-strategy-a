"""Pure helpers for broker-safe, research-only trailing SL placement."""
from __future__ import annotations

import math


RETRYABLE_TRAIL_RETCODES = frozenset({10004, 10016, 10020})


def normalize_trailing_sl(direction: str, raw_price: float, tick_size: float, digits: int) -> float:
    """Align BUY SL downward and SELL SL upward to the broker tick grid."""
    values = (raw_price, tick_size)
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("trailing prices must be finite")
    if tick_size <= 0 or digits < 0:
        raise ValueError("tick_size must be positive and digits non-negative")
    units = float(raw_price) / float(tick_size)
    if direction == "BUY":
        aligned_units = math.floor(units + 1e-10)
    elif direction == "SELL":
        aligned_units = math.ceil(units - 1e-10)
    else:
        raise ValueError("direction must be BUY or SELL")
    return round(aligned_units * float(tick_size), int(digits))


def trailing_sl_is_placeable(
    direction: str, sl: float, bid: float, ask: float, min_distance: float
) -> bool:
    """Require a strictly valid side and distance from the live executable quote."""
    values = (sl, bid, ask, min_distance)
    if not all(math.isfinite(float(value)) for value in values):
        return False
    if min_distance < 0:
        return False
    if direction == "BUY":
        return bid > 0 and sl < bid - min_distance - 1e-9
    if direction == "SELL":
        return ask > 0 and sl > ask + min_distance + 1e-9
    return False


def should_retry_trailing(retcode: int | None, attempt_count: int, max_attempts: int) -> bool:
    """Retry only known transient quote/stop rejections, with a hard attempt cap."""
    return (
        retcode in RETRYABLE_TRAIL_RETCODES
        and attempt_count >= 1
        and attempt_count < max_attempts
    )


def mt5_last_error_detail(last_error) -> str:
    """Return MT5 last_error safely for diagnostics when order_send returns None."""
    if not callable(last_error):
        return "last_error unavailable: function unavailable"
    try:
        return str(last_error())
    except Exception as exc:
        return f"last_error unavailable: {type(exc).__name__}: {exc}"
