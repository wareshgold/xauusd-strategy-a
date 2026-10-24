from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


def parse_ts(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def derive_m5(candles: list[dict]) -> list[dict]:
    buckets: dict[datetime, list[dict]] = {}
    for c in candles:
        ts = parse_ts(c["timestamp"])
        bucket = ts.replace(minute=(ts.minute // 5) * 5, second=0)
        buckets.setdefault(bucket, []).append(c)
    out = []
    for ts in sorted(buckets):
        group = sorted(buckets[ts], key=lambda x: x["timestamp"])
        if len(group) != 5:
            continue
        out.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "open": group[0]["open"],
            "high": max(x["high"] for x in group),
            "low": min(x["low"] for x in group),
            "close": group[-1]["close"],
        })
    return out


def audit(path: Path, comparison_5m: Path | None) -> dict:
    raw = path.read_bytes()
    payload = json.loads(raw)
    candles = payload.get("candles", [])
    timestamps = [parse_ts(c["timestamp"]) for c in candles]
    duplicate_ts = [k for k, v in Counter(timestamps).items() if v > 1]
    non_monotonic = sum(b <= a for a, b in zip(timestamps, timestamps[1:]))
    missing_intervals = sum(
        (b - a) != timedelta(minutes=1) for a, b in zip(timestamps, timestamps[1:])
    )
    invalid_ohlc = sum(
        not (c["low"] <= min(c["open"], c["close"]) <= max(c["open"], c["close"]) <= c["high"])
        for c in candles
    )
    non_positive = sum(min(c["open"], c["high"], c["low"], c["close"]) <= 0 for c in candles)
    derived = derive_m5(candles)
    comparison = None
    if comparison_5m and comparison_5m.exists():
        p5 = json.loads(comparison_5m.read_text())
        supplied = p5.get("candles", [])
        by_ts = {x["timestamp"]: x for x in supplied}
        comparable = 0
        mismatches = 0
        for x in derived:
            y = by_ts.get(x["timestamp"])
            if y is None:
                continue
            comparable += 1
            if any(x[k] != y[k] for k in ("open", "high", "low", "close")):
                mismatches += 1
        comparison = {"supplied_count": len(supplied), "derived_complete_5m_count": len(derived), "comparable": comparable, "ohlc_mismatches": mismatches}
    return {
        "dataset_sha256": hashlib.sha256(raw).hexdigest(),
        "file_sha256": sha256_file(path),
        "symbol": payload.get("symbol"),
        "timeframe": payload.get("timeframe"),
        "source": payload.get("source"),
        "timezone": payload.get("timezone"),
        "candle_count": len(candles),
        "first_timestamp": timestamps[0].isoformat() if timestamps else None,
        "last_timestamp": timestamps[-1].isoformat() if timestamps else None,
        "duplicate_timestamps": len(duplicate_ts),
        "non_monotonic_pairs": non_monotonic,
        "missing_or_non_1m_intervals": missing_intervals,
        "invalid_ohlc": invalid_ohlc,
        "non_positive_prices": non_positive,
        "derived_complete_m5_count": len(derived),
        "supplied_5m_comparison": comparison,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--m1", type=Path, required=True)
    ap.add_argument("--m5", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    report = audit(args.m1, args.m5)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
