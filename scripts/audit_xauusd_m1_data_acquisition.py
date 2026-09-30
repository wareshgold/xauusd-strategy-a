"""Audit target-window M1 data acquisition across MT5 API and Tester CSV.

Research-only. No Strategy A logic is applied.

The audit:
1. reads the exact MT5 Tester-exported M1 CSV;
2. retrieves fixed recent M1 chunks from the connected MT5 terminal;
3. compares timestamp/OHLC coverage between the two sources;
4. reports union/intersection and target-window coverage.

It does not infer broker-wide availability or any trading rule.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5


DEFAULT_POSITIONS = [0, 50_000]
DEFAULT_CHUNK_SIZE = 50_000
DEFAULT_START = 1758758400  # 2025-09-25 00:00 UTC
DEFAULT_END = 1790294400    # 2026-09-25 00:00 UTC


def iso(ts: int | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(int(ts), timezone.utc).isoformat().replace("+00:00", "Z")


def load_tester_csv(path: Path) -> dict[int, tuple[float, float, float, float]]:
    data: dict[int, tuple[float, float, float, float]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"time_epoch_utc", "open", "high", "low", "close"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Tester CSV missing columns: {sorted(missing)}")
        for row in reader:
            ts = int(row["time_epoch_utc"].strip())
            if ts in data:
                raise ValueError(f"Duplicate Tester CSV timestamp: {ts}")
            data[ts] = (
                float(row["open"]),
                float(row["high"]),
                float(row["low"]),
                float(row["close"]),
            )
    return data


def load_api_data(
    symbol: str,
    mt5_path: str,
    positions: list[int],
    chunk_size: int,
) -> tuple[dict[int, tuple[float, float, float, float]], list[dict]]:
    if not mt5.initialize(path=mt5_path):
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        if not mt5.symbol_select(symbol, True):
            raise RuntimeError(f"Symbol select failed: {mt5.last_error()}")

        data: dict[int, tuple[float, float, float, float]] = {}
        probes: list[dict] = []

        for position in positions:
            rates = mt5.copy_rates_from_pos(
                symbol, mt5.TIMEFRAME_M1, position, chunk_size
            )
            error = str(mt5.last_error())
            row = {
                "position": position,
                "requested_count": chunk_size,
                "returned_count": 0 if rates is None else len(rates),
                "last_error": error,
                "success": rates is not None and len(rates) > 0,
            }

            if rates is not None and len(rates) > 0:
                for x in rates:
                    ts = int(x["time"])
                    ohlc = (
                        float(x["open"]),
                        float(x["high"]),
                        float(x["low"]),
                        float(x["close"]),
                    )
                    previous = data.get(ts)
                    if previous is not None and previous != ohlc:
                        raise ValueError(
                            f"Conflicting API OHLC for timestamp {ts}: "
                            f"{previous} vs {ohlc}"
                        )
                    data[ts] = ohlc

                times = sorted(int(x["time"]) for x in rates)
                row["first_utc"] = iso(times[0])
                row["last_utc"] = iso(times[-1])
            else:
                row["first_utc"] = None
                row["last_utc"] = None

            probes.append(row)

        return data, probes
    finally:
        mt5.shutdown()


def month_counts(data: dict[int, tuple], start: int, end: int) -> dict[str, int]:
    return dict(sorted(Counter(
        datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m")
        for ts in data
        if start <= ts < end
    ).items()))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tester-csv", required=True)
    ap.add_argument("--mt5-path", required=True)
    ap.add_argument("--symbol", default="XAUUSD.ecn")
    ap.add_argument("--start-utc", type=int, default=DEFAULT_START)
    ap.add_argument("--end-utc", type=int, default=DEFAULT_END)
    ap.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    ap.add_argument(
        "--positions",
        default=",".join(str(x) for x in DEFAULT_POSITIONS),
        help="Comma-separated copy_rates_from_pos positions.",
    )
    ap.add_argument("--output-json", default="")
    args = ap.parse_args()

    if args.end_utc <= args.start_utc:
        raise SystemExit("--end-utc must be greater than --start-utc")
    if args.chunk_size <= 0:
        raise SystemExit("--chunk-size must be positive")

    positions = [int(x.strip()) for x in args.positions.split(",") if x.strip()]
    if not positions or any(x < 0 for x in positions):
        raise SystemExit("--positions must contain non-negative integers")

    tester_path = Path(args.tester_csv)
    if not tester_path.exists():
        raise SystemExit(f"Tester CSV not found: {tester_path}")

    tester = load_tester_csv(tester_path)
    api, probes = load_api_data(
        args.symbol, args.mt5_path, positions, args.chunk_size
    )

    tester_target = {ts: v for ts, v in tester.items() if args.start_utc <= ts < args.end_utc}
    api_target = {ts: v for ts, v in api.items() if args.start_utc <= ts < args.end_utc}

    tester_times = set(tester_target)
    api_times = set(api_target)
    overlap = tester_times & api_times
    union = tester_times | api_times

    exact_ohlc_matches = 0
    ohlc_mismatches: list[int] = []
    for ts in sorted(overlap):
        if tester_target[ts] == api_target[ts]:
            exact_ohlc_matches += 1
        else:
            ohlc_mismatches.append(ts)

    report = {
        "status": "COMPLETE",
        "mode": "NON_CANONICAL_FORENSIC",
        "experiment": "XAUUSD_M1_DATA_ACQUISITION_COVERAGE_AUDIT",
        "symbol": args.symbol,
        "target_window": {
            "start_utc": iso(args.start_utc),
            "end_utc": iso(args.end_utc),
        },
        "sources": {
            "tester_csv": str(tester_path),
            "tester_rows_total": len(tester),
            "api_rows_total_unique": len(api),
        },
        "api_request": {
            "chunk_size": args.chunk_size,
            "positions": positions,
            "probes": probes,
        },
        "coverage": {
            "tester_target_rows": len(tester_target),
            "api_target_rows": len(api_target),
            "union_rows": len(union),
            "overlap_rows": len(overlap),
            "tester_only_rows": len(tester_times - api_times),
            "api_only_rows": len(api_times - tester_times),
            "first_tester_target_utc": iso(min(tester_times)) if tester_times else None,
            "last_tester_target_utc": iso(max(tester_times)) if tester_times else None,
            "first_api_target_utc": iso(min(api_times)) if api_times else None,
            "last_api_target_utc": iso(max(api_times)) if api_times else None,
        },
        "overlap_validation": {
            "exact_ohlc_matches": exact_ohlc_matches,
            "ohlc_mismatch_count": len(ohlc_mismatches),
            "first_mismatch_utc": iso(ohlc_mismatches[0]) if ohlc_mismatches else None,
        },
        "monthly_coverage": {
            "tester": month_counts(tester, args.start_utc, args.end_utc),
            "api": month_counts(api, args.start_utc, args.end_utc),
            "union": month_counts(
                {ts: tester_target.get(ts, api_target.get(ts)) for ts in union},
                args.start_utc,
                args.end_utc,
            ),
        },
        "interpretation_boundary": (
            "This compares only data exposed by the supplied Tester CSV and "
            "connected MT5 terminal API. It does not establish broker-wide "
            "historical availability and does not infer any strategy signal, "
            "outcome, parameter ranking, or canonical rule."
        ),
    }

    text = json.dumps(report, indent=2)
    print(text)
    if args.output_json:
        out = Path(args.output_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
