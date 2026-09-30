"""Probe MT5 XAUUSD M1 history depth by position chunks.

Research-only. Deterministic data-access audit; no Strategy A signal/rule logic.
Each probe requests a fixed chunk from a fixed MT5 history position and records
the returned timestamp range. This avoids assuming maxbars or a single recent
window represents all history exposed by the terminal.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5


DEFAULT_POSITIONS = [0, 50_000, 100_000, 150_000, 200_000, 250_000, 300_000, 350_000, 400_000, 450_000]
DEFAULT_CHUNK = 50_000


def iso(ts: int | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()


def summarize(rates) -> dict:
    if rates is None or len(rates) == 0:
        return {
            "returned_count": 0,
            "first_utc": None,
            "last_utc": None,
            "duplicate_timestamps": 0,
            "span_minutes": 0,
            "missing_minutes_inside_span": None,
            "max_gap_minutes": None,
        }

    times = [int(x["time"]) for x in rates]
    unique = sorted(set(times))
    diffs = [(b - a) // 60 for a, b in zip(unique, unique[1:])]
    gaps = [d for d in diffs if d > 1]

    return {
        "returned_count": len(times),
        "first_utc": iso(min(times)),
        "last_utc": iso(max(times)),
        "duplicate_timestamps": len(times) - len(unique),
        "span_minutes": (max(times) - min(times)) // 60,
        "missing_minutes_inside_span": sum(d - 1 for d in gaps),
        "max_gap_minutes": max(gaps) if gaps else 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mt5-path", required=True)
    ap.add_argument("--symbol", default="XAUUSD.ecn")
    ap.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK)
    ap.add_argument(
        "--positions",
        default=",".join(str(x) for x in DEFAULT_POSITIONS),
        help="Comma-separated copy_rates_from_pos positions.",
    )
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    if args.chunk_size <= 0:
        raise SystemExit("--chunk-size must be positive")

    positions = [int(x.strip()) for x in args.positions.split(",") if x.strip()]
    if not positions or any(x < 0 for x in positions):
        raise SystemExit("--positions must contain non-negative integers")

    if not mt5.initialize(path=args.mt5_path):
        print(json.dumps({
            "status": "MT5_INIT_FAILED",
            "error": str(mt5.last_error()),
        }, indent=2))
        return 2

    try:
        symbol = args.symbol
        if not mt5.symbol_select(symbol, True):
            print(json.dumps({
                "status": "SYMBOL_SELECT_FAILED",
                "symbol": symbol,
                "error": str(mt5.last_error()),
            }, indent=2))
            return 2

        info = mt5.symbol_info(symbol)
        terminal = mt5.terminal_info()
        probes = []

        for position in positions:
            rates = mt5.copy_rates_from_pos(
                symbol, mt5.TIMEFRAME_M1, position, args.chunk_size
            )
            error = str(mt5.last_error())
            summary = summarize(rates)
            probes.append({
                "position": position,
                "requested_count": args.chunk_size,
                "last_error": error,
                "success": rates is not None and len(rates) > 0,
                **summary,
            })

        successful = [p for p in probes if p["success"]]
        result = {
            "status": "COMPLETE",
            "mode": "NON_CANONICAL_FORENSIC",
            "experiment": "XAUUSD_M1_HISTORY_POSITION_CHUNK_AUDIT",
            "symbol": symbol,
            "request": {
                "chunk_size": args.chunk_size,
                "positions": positions,
            },
            "terminal": {
                "name": getattr(terminal, "name", None),
                "build": getattr(terminal, "build", None),
                "connected": getattr(terminal, "connected", None),
                "trade_allowed": getattr(terminal, "trade_allowed", None),
                "maxbars": getattr(terminal, "maxbars", None),
            },
            "symbol_info": {
                "point": getattr(info, "point", None),
                "digits": getattr(info, "digits", None),
                "trade_contract_size": getattr(info, "trade_contract_size", None),
            },
            "probes": probes,
            "summary": {
                "successful_probe_count": len(successful),
                "oldest_returned_utc": (
                    min(p["first_utc"] for p in successful)
                    if successful else None
                ),
                "newest_returned_utc": (
                    max(p["last_utc"] for p in successful)
                    if successful else None
                ),
            },
            "interpretation_boundary": (
                "This measures M1 history exposed by the connected MT5 terminal "
                "through copy_rates_from_pos at the requested positions. It does "
                "not establish broker-wide historical availability and does not "
                "infer any strategy signal, outcome, trailing parameter, ranking, "
                "or canonical rule."
            ),
        }

        text = json.dumps(result, indent=2)
        if args.output:
            path = Path(args.output)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text + "\n", encoding="utf-8")
        print(text)
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
