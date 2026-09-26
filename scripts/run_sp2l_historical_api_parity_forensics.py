"""Historical MT5 API parity forensic for SP2L research.

Research-only. Compares copy_rates_range() with copy_rates_from() on the same
terminal, symbol and exact windows. No strategy geometry, fill semantics,
timestamp normalization, or execution behavior is changed.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1

DEFAULT_WINDOWS = (
    ("2026-09-24T09:55:00Z", "2026-09-24T10:20:00Z"),
    ("2026-09-24T11:40:00Z", "2026-09-24T12:10:00Z"),
    ("2026-09-24T12:30:00Z", "2026-09-24T13:00:00Z"),
)


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def bar_dict(row) -> dict:
    raw = int(row["time"])
    return {
        "time_raw": raw,
        "time_utc_interpreted": datetime.fromtimestamp(raw, timezone.utc).isoformat(),
        "open": float(row["open"]),
        "high": float(row["high"]),
        "low": float(row["low"]),
        "close": float(row["close"]),
        "tick_volume": int(row["tick_volume"]),
        "spread": int(row["spread"]),
        "real_volume": int(row["real_volume"]),
    }


def signature(rows):
    return [
        (x["time_raw"], x["open"], x["high"], x["low"], x["close"])
        for x in rows
    ]


def fetch_range(start: datetime, end: datetime):
    data = mt5.copy_rates_range(SYMBOL, TIMEFRAME, start, end)
    return [] if data is None else [bar_dict(x) for x in data]


def fetch_from(end: datetime, count: int):
    data = mt5.copy_rates_from(SYMBOL, TIMEFRAME, end, count)
    return [] if data is None else [bar_dict(x) for x in data]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--windows", nargs="*", default=None,
                        help="UTC start/end pairs, e.g. START END START END")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"symbol_select failed: {mt5.last_error()}")

        raw = args.windows or []
        if raw:
            if len(raw) % 2:
                raise SystemExit("--windows requires start/end pairs")
            windows = list(zip(raw[::2], raw[1::2]))
        else:
            windows = list(DEFAULT_WINDOWS)

        comparisons = []
        for start_s, end_s in windows:
            start, end = parse_utc(start_s), parse_utc(end_s)
            expected = int((end - start).total_seconds() // 60) + 1

            range_rows = fetch_range(start, end)
            from_rows = fetch_from(end, expected)

            def in_window(row):
                t = datetime.fromtimestamp(row["time_raw"], timezone.utc)
                return start <= t <= end

            range_rows = sorted((x for x in range_rows if in_window(x)),
                                key=lambda x: x["time_raw"])
            from_rows = sorted((x for x in from_rows if in_window(x)),
                               key=lambda x: x["time_raw"])

            range_sig = signature(range_rows)
            from_sig = signature(from_rows)
            first_difference = next(
                (i for i, pair in enumerate(zip(range_sig, from_sig))
                 if pair[0] != pair[1]),
                None,
            )

            comparisons.append({
                "window_utc": {
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
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
                    "exact_ohlc_time_sequence_equal": range_sig == from_sig,
                    "only_in_range_count": len(set(range_sig) - set(from_sig)),
                    "only_in_from_count": len(set(from_sig) - set(range_sig)),
                    "first_difference_index": first_difference,
                },
            })

        result = {
            "status": "COMPLETE",
            "research_only": True,
            "canonical": False,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "acquisition_comparison": [
                "mt5.copy_rates_range",
                "mt5.copy_rates_from",
            ],
            "timestamp_basis": (
                "raw MT5 epoch plus UTC rendering; no timestamp normalization"
            ),
            "windows": comparisons,
            "notes": [
                "Exact equality is evidence of API parity for the observed windows only.",
                "Inequality does not by itself prove a forward-loop miss.",
                "No Strategy A geometry or fill rule is changed.",
                "This runner does not place orders or send Telegram messages.",
            ],
        }

        root = Path(__file__).resolve().parents[1]
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output = (
            Path(args.output)
            if args.output
            else root / "artifacts" / "forensic" / "2026-09-26"
            / f"FORENSIC_API_PARITY_{stamp}.json"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(json.dumps({
            "status": result["status"],
            "report": str(output),
            "windows": len(comparisons),
        }, indent=2))
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
