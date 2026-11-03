"""Durable, deterministic state for research-only trailing excursions."""
from __future__ import annotations

import json
import math
import os
import tempfile
from pathlib import Path


def update_favorable_extreme(
    direction: str,
    entry: float,
    previous_extreme: float,
    bar_high: float,
    bar_low: float,
) -> float:
    """Return the monotonic best completed-bar excursion for one position."""
    values = (entry, previous_extreme, bar_high, bar_low)
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("trailing excursion prices must be finite")
    if direction == "BUY":
        return max(float(entry), float(previous_extreme), float(bar_high))
    if direction == "SELL":
        return min(float(entry), float(previous_extreme), float(bar_low))
    raise ValueError("direction must be BUY or SELL")


def favorable_move(direction: str, entry: float, favorable_extreme: float) -> float:
    """Measure the favorable price excursion without converting it to USD."""
    if not all(math.isfinite(float(value)) for value in (entry, favorable_extreme)):
        raise ValueError("activation prices must be finite")
    if direction == "BUY":
        return float(favorable_extreme) - float(entry)
    if direction == "SELL":
        return float(entry) - float(favorable_extreme)
    raise ValueError("direction must be BUY or SELL")


def trailing_activation_reached(
    direction: str,
    entry: float,
    favorable_extreme: float,
    activation_distance: float,
) -> bool:
    """Preserve the existing price-distance activation threshold."""
    if not math.isfinite(float(activation_distance)) or activation_distance < 0:
        raise ValueError("activation_distance must be finite and non-negative")
    return favorable_move(direction, entry, favorable_extreme) >= float(activation_distance)


def trailing_record_matches(
    record: dict | None,
    *,
    symbol: str,
    magic: int,
    direction: str,
    entry: float,
    position_time_msc: int,
) -> bool:
    """Prevent a persisted ticket record being reused for another position."""
    if not isinstance(record, dict):
        return False
    try:
        return (
            str(record.get("symbol")) == str(symbol)
            and int(record.get("magic")) == int(magic)
            and str(record.get("direction")) == direction
            and math.isclose(float(record.get("entry")), float(entry), rel_tol=0.0, abs_tol=1e-8)
            and int(record.get("position_time_msc")) == int(position_time_msc)
            and math.isfinite(float(record.get("favorable_extreme")))
        )
    except (TypeError, ValueError, OverflowError):
        return False


def load_trailing_state(path: str | Path) -> dict:
    """Load durable state; malformed existing state is a fail-closed error."""
    target = Path(path)
    if not target.exists():
        return {}
    raw = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema_version") != 1:
        raise ValueError("unsupported trailing state schema")
    positions = raw.get("positions")
    if not isinstance(positions, dict):
        raise ValueError("trailing state positions must be an object")
    for ticket, record in positions.items():
        if not str(ticket).isdigit() or not isinstance(record, dict):
            raise ValueError("invalid trailing state position record")
        required = (
            "symbol", "magic", "direction", "entry",
            "position_time_msc", "favorable_extreme",
        )
        if any(key not in record for key in required):
            raise ValueError(f"incomplete trailing state record for ticket {ticket}")
        if not math.isfinite(float(record["entry"])) or not math.isfinite(float(record["favorable_extreme"])):
            raise ValueError(f"non-finite trailing state record for ticket {ticket}")
        if record["direction"] not in ("BUY", "SELL"):
            raise ValueError(f"invalid trailing direction for ticket {ticket}")
    return {str(ticket): dict(record) for ticket, record in positions.items()}


def save_trailing_state(path: str | Path, positions: dict) -> None:
    """Atomically persist trailing extrema without exposing a partial JSON file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        {"schema_version": 1, "positions": positions},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, target)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise
