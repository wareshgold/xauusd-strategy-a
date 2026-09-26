"""Research-only MT5 tick-level forensic for ambiguous SP2L outcomes.

This tool does NOT define canonical fill/execution semantics. It retrieves
historical MT5 ticks for the ambiguous bars identified by the local replay and
reports threshold-touch order under several raw price fields (last, bid, ask).
The purpose is to determine whether preserved tick data contains enough
information to constrain the unresolved OHLC ordering.

No orders, Telegram messages, detector evaluation, or geometry changes occur.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import MetaTrader5 as mt5

DEFAULT_ARTIFACT = (
    "artifacts/backtest-mt5-local/"
    "SP2L_MT5_LOCAL_MULTI_SYMBOL_20260926T124056Z.json"
)
SYMBOL = "XAUUSD.ecn"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", default=DEFAULT_ARTIFACT)
    parser.add_argument("--output", default=None)
    parser.add_argument("--mt5-path", default=None)
    return parser.parse_args()


def iso_from_epoch(seconds: float) -> str:
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat()


def load_ambiguous(root: Path, artifact: str):
    data = json.loads((root / artifact).read_text(encoding="utf-8"))
    rows = data["outcomes"]["XAUUSD"]["signals_detail"]
    return [row for row in rows if row["result"] == "AMBIGUOUS"]


def threshold_hits(direction: str, entry: float, sl: float, tp: float, value: float):
    if direction == "BUY":
        return {
            "ENTRY": value <= entry,
            "SL": value <= sl,
            "TP": value >= tp,
        }
    return {
        "ENTRY": value >= entry,
        "SL": value >= sl,
        "TP": value <= tp,
    }


def first_hits(direction, entry, sl, tp, ticks, field):
    hits = {}
    for i, tick in enumerate(ticks):
        value = tick.get(field)
        if value is None or value == 0:
            continue
        touched = threshold_hits(direction, entry, sl, tp, float(value))
        for name, yes in touched.items():
            if yes and name not in hits:
                hits[name] = {
                    "tick_index": i,
                    "time_msc": int(tick["time_msc"]),
                    "time_utc": iso_from_epoch(int(tick["time_msc"]) / 1000),
                    "price": float(value),
                }
    return hits


def tick_dict(row):
    return {
        "time_msc": int(row["time_msc"]),
        "time_utc": iso_from_epoch(int(row["time_msc"]) / 1000),
        "bid": float(row["bid"]),
        "ask": float(row["ask"]),
        "last": float(row["last"]),
        "volume": int(row["volume"]),
        "flags": int(row["flags"]),
    }


def main():
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    artifact_path = root / args.artifact
    ambiguous = load_ambiguous(root, args.artifact)

    init_kwargs = {} if args.mt5_path is None else {"path": args.mt5_path}
    if not mt5.initialize(**init_kwargs):
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"symbol_select failed: {mt5.last_error()}")

        results = []
        for row in ambiguous:
            trace = row["outcome_trace"]
            bar = trace["exit_bar"]
            bar_start = datetime.fromtimestamp(
                int(trace["exit_time"]), timezone.utc
            )
            bar_end = bar_start + timedelta(minutes=1)

            ticks_raw = mt5.copy_ticks_range(
                SYMBOL, bar_start, bar_end, mt5.COPY_TICKS_ALL
            )
            err = mt5.last_error()
            ticks = [] if ticks_raw is None else [tick_dict(x) for x in ticks_raw]

            field_results = {}
            for field in ("last", "bid", "ask"):
                field_results[field] = first_hits(
                    row["direction"],
                    float(row["entry"]),
                    float(row["sl"]),
                    float(row["tp"]),
                    ticks,
                    field,
                )

            first_order = {}
            for field, hits in field_results.items():
                ordered = sorted(
                    (
                        (name, info["time_msc"])
                        for name, info in hits.items()
                    ),
                    key=lambda x: x[1],
                )
                first_order[field] = [name for name, _ in ordered]

            results.append({
                "signal_index": int(trace["signal_index"]),
                "signal_time_utc": iso_from_epoch(int(trace["signal_time"])),
                "direction": row["direction"],
                "entry": float(row["entry"]),
                "sl": float(row["sl"]),
                "tp": float(row["tp"]),
                "exit_reason_ohlc": trace["exit_reason"],
                "bar_utc": bar_start.isoformat(),
                "bar_ohlc": {
                    "open": float(bar["open"]),
                    "high": float(bar["high"]),
                    "low": float(bar["low"]),
                    "close": float(bar["close"]),
                },
                "mt5_last_error": [int(err[0]), str(err[1])],
                "tick_count": len(ticks),
                "first_tick": ticks[0] if ticks else None,
                "last_tick": ticks[-1] if ticks else None,
                "first_threshold_hits": field_results,
                "first_threshold_order": first_order,
                "coverage": {
                    "has_ticks": bool(ticks),
                    "bar_start_utc": bar_start.isoformat(),
                    "bar_end_utc": bar_end.isoformat(),
                    "tick_first_utc": ticks[0]["time_utc"] if ticks else None,
                    "tick_last_utc": ticks[-1]["time_utc"] if ticks else None,
                },
                "note": (
                    "Raw tick evidence only. Bid/ask/last differences are "
                    "reported rather than selected as canonical execution price."
                ),
            })

        result = {
            "status": "COMPLETE",
            "research_only": True,
            "canonical": False,
            "symbol": SYMBOL,
            "timeframe_context": "M1 ambiguous exit/fill bars",
            "source_artifact": args.artifact,
            "ambiguous_count": len(ambiguous),
            "tick_results": results,
            "summary": {
                "with_any_ticks": sum(1 for x in results if x["tick_count"] > 0),
                "without_ticks": sum(1 for x in results if x["tick_count"] == 0),
                "fields_compared": ["last", "bid", "ask"],
                "canonical_semantics_selected": False,
            },
            "notes": [
                "A complete tick stream can constrain intrabar ordering but does not by itself define canonical fill semantics.",
                "Missing or sparse historical ticks leave the corresponding case unresolved.",
                "Bid/ask/last are intentionally compared separately; no execution-price assumption is promoted.",
                "No Strategy A geometry, P-Gap formula, or production behavior is changed.",
            ],
        }

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output = (
            Path(args.output)
            if args.output
            else root / "artifacts" / "forensic" / "2026-09-26"
            / f"INTRABAR_TICK_FORENSIC_{stamp}.json"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(json.dumps({
            "status": result["status"],
            "report": str(output),
            "ambiguous_count": len(ambiguous),
            "with_any_ticks": result["summary"]["with_any_ticks"],
            "without_ticks": result["summary"]["without_ticks"],
        }, indent=2))
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
