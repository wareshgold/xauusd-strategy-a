from __future__ import annotations

"""Frozen Strategy A V3 entry-population loader.

Only the V3 entry identity and risk fields are consumed. Existing V3 exit
outcomes are intentionally ignored so each exit variant is replayed afresh.
"""

import csv
import hashlib
import io
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ENTRY_FIELDS = [
    "strategy", "variant", "direction", "setup_time_utc", "entry_time_utc",
    "entry_proxy", "sl_initial", "target", "risk_price", "exit_time_utc",
    "exit_price", "exit_reason", "status", "r_multiple",
]


def load_frozen_entry_population(
    path: str | Path,
    bars: Iterable[Any],
    expected_sha256: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Load the V3 trade CSV as the fixed entry population; ignore its exits."""
    artifact = Path(path)
    if not artifact.is_file():
        raise ValueError(f"frozen V3 entry artifact not found: {artifact}")
    raw = artifact.read_bytes()
    observed_sha256 = hashlib.sha256(raw).hexdigest()
    if observed_sha256.lower() != expected_sha256.lower():
        raise ValueError("frozen V3 entry artifact SHA-256 mismatch")

    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    if reader.fieldnames != ENTRY_FIELDS:
        raise ValueError("frozen V3 entry CSV header does not match the declared schema")

    bar_index_by_time = {int(bar["time"]): index for index, bar in enumerate(bars)}
    population: list[dict[str, Any]] = []
    seen = set()
    variants = set()
    previous_entry_time = None

    for index, row in enumerate(reader):
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"frozen V3 entry row {index} has an invalid field count")
        if row["strategy"] != "A":
            raise ValueError(f"frozen V3 entry row {index} is not Strategy A")
        variant = row["variant"].strip()
        if not variant:
            raise ValueError(f"frozen V3 entry row {index} has no source variant")
        variants.add(variant)
        if row["direction"] not in ("BUY", "SELL"):
            raise ValueError(f"frozen V3 entry row {index} has an invalid direction")

        try:
            setup_dt = datetime.fromisoformat(row["setup_time_utc"].replace("Z", "+00:00"))
            entry_dt = datetime.fromisoformat(row["entry_time_utc"].replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"frozen V3 entry row {index} has an invalid timestamp") from exc
        if setup_dt.tzinfo is None or entry_dt.tzinfo is None:
            raise ValueError(f"frozen V3 entry row {index} timestamps must include timezone")
        setup_dt = setup_dt.astimezone(timezone.utc)
        entry_dt = entry_dt.astimezone(timezone.utc)
        trigger_time = int(entry_dt.timestamp())
        if trigger_time % 60 != 0:
            raise ValueError(f"frozen V3 entry row {index} is not aligned to M1")
        if previous_entry_time is not None and trigger_time < previous_entry_time:
            raise ValueError("frozen V3 entry rows are not in chronological order")
        previous_entry_time = trigger_time

        key = (trigger_time, row["direction"])
        if key in seen:
            raise ValueError(f"duplicate frozen V3 entry identity at row {index}")
        seen.add(key)
        entry_idx = bar_index_by_time.get(trigger_time)
        if entry_idx is None:
            raise ValueError(
                f"frozen V3 entry timestamp {row['entry_time_utc']} is absent from the M1 dataset"
            )

        numeric = {}
        for field in ("entry_proxy", "sl_initial", "target", "risk_price"):
            try:
                numeric[field] = float(row[field])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"frozen V3 entry row {index} has invalid {field}") from exc
            if not math.isfinite(numeric[field]) or numeric[field] <= 0:
                raise ValueError(f"frozen V3 entry row {index} {field} must be finite and positive")

        population.append({
            "trigger_time": trigger_time,
            "signal_time_utc": entry_dt.isoformat(),
            "setup_time_utc": setup_dt.isoformat(),
            "direction": row["direction"],
            "theoretical_entry": numeric["entry_proxy"],
            "sl": numeric["sl_initial"],
            "risk": numeric["risk_price"],
            "entry_idx": entry_idx,
            "source_entry_variant": variant,
        })

    if not population:
        raise ValueError("frozen V3 entry artifact contains no Strategy A rows")
    if len(variants) != 1:
        raise ValueError("frozen V3 entry artifact must contain exactly one source variant")

    return population, {
        "source": "FROZEN_V3_ENTRY_CSV",
        "artifact": str(artifact.resolve()),
        "content_sha256": observed_sha256,
        "rows": len(population),
        "source_variant": next(iter(variants)),
        "entry_fields": [
            "direction", "setup_time_utc", "entry_time_utc",
            "entry_proxy", "sl_initial", "risk_price",
        ],
        "ignored_exit_fields": [
            "target", "exit_time_utc", "exit_price", "exit_reason", "status", "r_multiple",
        ],
    }
