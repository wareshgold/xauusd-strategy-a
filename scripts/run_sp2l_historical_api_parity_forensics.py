"""Historical API parity replay for SP2L forensic research.

Research-only. Uses the same manifest-gated candidate parameters and compares
MT5 copy_rates_from() interval retrieval against copy_rates_range() retrieval
over exact forensic windows.

It does not infer missing rolling snapshots or rewrite timestamps.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

from sp2l_author_replica_detector import RESEARCH_DETECTOR_REVISION
from sp2l_research_manifest_gate import assert_manifest_compatible

SYMBOL = "XAUUSD.ecn"
P_GAP = 1.0
SPIKE_MULT = 1.5
MAX_SL = 10.0
TP_R = 1.0
MANIFEST = assert_manifest_compatible(
    p_gap_price=P_GAP,
    spike_multiplier=SPIKE_MULT,
    max_sl_distance=MAX_SL,
    tp_r=TP_R,
    detector_revision=RESEARCH_DETECTOR_REVISION,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WINDOWS = (
    ("2026-09-24T09:55:00Z", "2026-09-24T10:20:00Z"),
    ("2026-09-24T11:40:00Z", "2026-09-24T12:10:00Z"),
    ("2026-09-24T12:30:00Z", "2026-09-24T13:00:00Z"),
)


def parse(v):
    return datetime.fromisoformat(v.replace("Z", "+00:00")).astimezone(timezone.utc)


def bar_dict(r):
    return {
        "time_raw": int(r["time"]),
        "time_utc_interpreted": datetime.fromtimestamp(int(r["time"]), timezone.utc).isoformat(),
        "open": float(r["open"]),
        "high": float(r["high"]),
        "low": float(r["low"]),
        "close": float(r["close"]),
        "tick_volume": int(r["tick_volume"]),
        "spread": int(r["spread"]),
        "real_volume": int(r["real_volume"]),
    }


def signature(rows):
    return [(x["time_raw"], x["open"], x["high"], x["low"], x["close"]) for x in rows]


def fetch_range(start, end):
    data = mt5.copy_rates_range(SYMBOL, mt5.TIMEFRAME_M1, start, end)
    return [] if data is None else [bar_dict(x) for x in data]


def fetch_from(end, count):
    data = mt5.copy_rates_from(SYMBOL, mt5.TIMEFRAME_M1, end, count)
    return [] if data is None else [bar_dict(x) for x in data]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--windows", nargs="*", default=None)
    p.add_argument("--output", default=None)
    args = p.parse_args()

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"symbol_select failed: {mt5.last_error()}")

        pairs = []
        raw_windows = args.windows or []
        if raw_windows:
            if len(raw_windows) % 2:
                raise SystemExit("--windows requires start/end pairs")
            windows = list(zip(raw_windows[::2], raw_windows[1::2]))
        else:
            windows = list(DEFAULT_WINDOWS)

        for start_s, end_s in windows:
            start, end = parse(start_s), parse(end_s)
            expected = int((end - start).total_seconds() // 60) + 1
            range_rows = fetch_range(start, end)
            from_rows = fetch_from(end, expected)

            range_rows = [x for x in range_rows if start <= datetime.fromtimestamp(x["time_raw"], timezone.utc) <= end]
            from_rows = [x for x in from_rows if start <= datetime.fromtimestamp(x["time_raw"], timezone.utc) <= end]
            range_rows.sort(key=lambda x: x["time_raw"])
            from_rows.sort(key=lambda x: x["time_raw"])

            rs, fs = signature(range_rows), signature(from_rows)
            same = rs == fs
            only_range = sorted(set(rs) - set(fs))
            only_from = sorted(set(fs) - set(rs))
            first_diff = next((i for i, (a, b) in enumerate(zip(rs, fs)) if a != b), None)

            pairs.append({
                "window_utc": {"start": start.isoformat(), "end": end.isoformat()},
                "expected_minutes": expected,
                "copy_rates_range": {
                    "count": len(range_rows),
                    "first": range_rows[0] if range_rows else None,
                    "last": range_rows[-1] if range_rows else None,
                },
                "copy_rates_from": {
                    "count": len(from_rows),
                    "first": from_rows[0] if from_rows else None,
                    "last": from_rows[-1] if from_rows else None,
                },
                "parity": {
                    "exact_ohlc_time_sequence_equal": same,
                    "only_in_range_count": len(only_range),
                    "only_in_from_count": len(only_from),
                    "first_difference_index": first_diff,
                    "only_in_range": only_range[:100],
                    "only_in_from": only_from[:100],
                },
            })

        result = {
            "status": "COMPLETE",
            "research_only": True,
            "canonical": False,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "manifest_compatibility": MANIFEST,
            "acquisition_comparison": ["mt5.copy_rates_range", "mt5.copy_rates_from"],
            "timestamp_basis": "raw MT5 epoch plus UTC rendering; no timestamp normalization",
            "windows": pairs,
            "notes": [
                "This compares two MT5 historical APIs using the same terminal, symbol and windows.",
                "Exact equality is evidence of API parity for the observed windows only.",
                "Inequality does not by itself establish a forward-loop miss or prove timestamp timezone semantics.",
                "No Strategy A geometry or fill rule is changed.",
            ],
        }
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = Path(args.output) if args.output else ROOT / "artifacts" / "forensic" / "2026-09-26" / f"FORENSIC_API_PARITY_{stamp}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({"status": result["status"], "report": str(out), "windows": len(pairs)}, indent=2))
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
