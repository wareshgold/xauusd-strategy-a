"""Deterministic forward/backtest signal reconciliation helper.

Research-only. It never changes detector geometry or declares canonical execution rules.

Accepted input: JSON containing a list under one of:
signals, trades, candidates, rows.

Each item may expose aliases for:
time/trigger_time/signal_time, direction, entry/theoretical_entry,
sl, tp.

The script emits a stable classification and does not infer event identity
from price alone.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


TIME_KEYS = ("trigger_time", "signal_time", "time", "timestamp")
DIRECTION_KEYS = ("direction", "side")
ENTRY_KEYS = ("entry", "theoretical_entry")
SL_KEYS = ("sl", "stop_loss")
TP_KEYS = ("tp", "take_profit")


def load(path: Path) -> tuple[Any, str]:
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


def rows_from(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("signals", "trades", "candidates", "rows"):
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
    raise ValueError("No supported signal list found")


def first(row: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in row:
            return row[key]
    return None


def norm(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "time": first(row, TIME_KEYS),
        "direction": first(row, DIRECTION_KEYS),
        "entry": first(row, ENTRY_KEYS),
        "sl": first(row, SL_KEYS),
        "tp": first(row, TP_KEYS),
    }


def same(a: Any, b: Any) -> bool:
    if a is None or b is None:
        return False
    return str(a) == str(b)


def classify(f: dict[str, Any], b: dict[str, Any]) -> str:
    price_match = all(
        same(f[k], b[k]) for k in ("direction", "entry", "sl", "tp")
    )
    time_match = same(f["time"], b["time"])

    if time_match and price_match:
        return "EXACT_MATCH"
    if price_match and not time_match:
        return "PRICE_MATCH_TIMESTAMP_MISMATCH"
    if same(f["direction"], b["direction"]) and not price_match:
        return "SAME_EVENT_DIFFERENT_PRICE"
    return "UNRESOLVED"


def reconcile(forward: list[dict[str, Any]], backtest: list[dict[str, Any]]) -> dict[str, Any]:
    f = [norm(x) for x in forward]
    b = [norm(x) for x in backtest]
    unused = set(range(len(b)))
    matches = []

    # Deterministic exact-key matching first.
    for fi, fr in enumerate(f):
        candidates = [
            bi for bi in sorted(unused)
            if same(fr["time"], b[bi]["time"])
            and same(fr["direction"], b[bi]["direction"])
            and same(fr["entry"], b[bi]["entry"])
            and same(fr["sl"], b[bi]["sl"])
            and same(fr["tp"], b[bi]["tp"])
        ]
        if candidates:
            bi = candidates[0]
            unused.remove(bi)
            matches.append({"forward_index": fi, "backtest_index": bi, "class": "EXACT_MATCH"})
            continue

        # Do not assign identity from price alone when time differs.
        price_candidates = [
            bi for bi in sorted(unused)
            if same(fr["direction"], b[bi]["direction"])
            and same(fr["entry"], b[bi]["entry"])
            and same(fr["sl"], b[bi]["sl"])
            and same(fr["tp"], b[bi]["tp"])
        ]
        if len(price_candidates) == 1:
            bi = price_candidates[0]
            unused.remove(bi)
            matches.append({"forward_index": fi, "backtest_index": bi, "class": "PRICE_MATCH_TIMESTAMP_MISMATCH"})
        else:
            matches.append({"forward_index": fi, "backtest_index": None, "class": "FORWARD_ONLY"})

    matches.extend(
        {"forward_index": None, "backtest_index": bi, "class": "BACKTEST_ONLY"}
        for bi in sorted(unused)
    )

    counts: dict[str, int] = {}
    for item in matches:
        counts[item["class"]] = counts.get(item["class"], 0) + 1

    return {
        "forward_count": len(f),
        "backtest_count": len(b),
        "classification_counts": counts,
        "matches": matches,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("forward", type=Path)
    parser.add_argument("backtest", type=Path)
    args = parser.parse_args()

    forward_payload, forward_sha = load(args.forward)
    backtest_payload, backtest_sha = load(args.backtest)

    result = reconcile(rows_from(forward_payload), rows_from(backtest_payload))
    result["inputs"] = {
        "forward": {"path": str(args.forward), "sha256": forward_sha},
        "backtest": {"path": str(args.backtest), "sha256": backtest_sha},
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
