"""Entry-geometry audit for the current SP2L V3 research variant.

This module measures how the current-candle extreme entry differs from the
source-noted previous-candle Low/High. It does not select canonical geometry,
infer intrabar order, or simulate fills/performance.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "v3"


def audit_candidates(bars, candidates, eps: float = 1e-7) -> list[dict]:
    """Return one transparent geometry row per (candidate, entry_index)."""
    rows = []
    for candidate, entry_idx in candidates:
        if entry_idx <= 0 or entry_idx >= len(bars):
            raise ValueError(f"entry index out of range: {entry_idx}")
        direction = str(candidate["direction"]).upper()
        if direction not in {"BUY", "SELL"}:
            raise ValueError(f"unsupported direction: {direction}")
        current = bars[entry_idx]
        previous = bars[entry_idx - 1]
        entry = float(candidate["theoretical_entry"])
        current_high, current_low = float(current["high"]), float(current["low"])
        if direction == "BUY":
            current_extreme = current_low
            previous_level = float(previous["low"])
            source_level_name = "previous_candle_low"
            crossed_beyond_previous_level = current_low < previous_level - eps
        else:
            current_extreme = current_high
            previous_level = float(previous["high"])
            source_level_name = "previous_candle_high"
            crossed_beyond_previous_level = current_high > previous_level + eps

        inside_range = current_low - eps <= previous_level <= current_high + eps
        delta = entry - previous_level
        rows.append({
            "direction": direction,
            "trigger_time": int(candidate["trigger_time"]),
            "entry_index": int(entry_idx),
            "entry_price_current_variant": entry,
            "current_bar_high": current_high,
            "current_bar_low": current_low,
            "current_bar_extreme": current_extreme,
            "previous_level_name": source_level_name,
            "previous_candle_level": previous_level,
            "entry_minus_previous_level": delta,
            "absolute_entry_level_difference": abs(delta),
            "entry_equals_current_extreme": abs(entry - current_extreme) <= eps,
            "entry_equals_previous_level": abs(entry - previous_level) <= eps,
            "previous_level_inside_entry_bar_range": inside_range,
            "bar_extends_beyond_previous_level": crossed_beyond_previous_level,
            "level_outside_entry_bar_range": not inside_range,
            "intrabar_order_resolved": False,
            "fill_semantics_resolved": False,
            "canonical_rule_selected": False,
        })
    return rows


def summarize_rows(rows: list[dict]) -> dict:
    def summarize_group(group: list[dict]) -> dict:
        deltas = [float(row["entry_minus_previous_level"]) for row in group]
        abs_deltas = [abs(value) for value in deltas]
        return {
            "count": len(group),
            "entry_equals_current_extreme_count": sum(bool(r["entry_equals_current_extreme"]) for r in group),
            "entry_equals_previous_level_count": sum(bool(r["entry_equals_previous_level"]) for r in group),
            "previous_level_inside_entry_bar_range_count": sum(bool(r["previous_level_inside_entry_bar_range"]) for r in group),
            "bar_extends_beyond_previous_level_count": sum(bool(r["bar_extends_beyond_previous_level"]) for r in group),
            "level_outside_entry_bar_range_count": sum(bool(r["level_outside_entry_bar_range"]) for r in group),
            "median_absolute_entry_level_difference": statistics.median(abs_deltas) if abs_deltas else None,
            "max_absolute_entry_level_difference": max(abs_deltas) if abs_deltas else None,
            "min_signed_entry_minus_previous_level": min(deltas) if deltas else None,
            "max_signed_entry_minus_previous_level": max(deltas) if deltas else None,
        }

    return {
        "candidate_count": len(rows),
        "all_rows_research_only": True,
        "intrabar_order_inferred": False,
        "fills_simulated": False,
        "canonical_rule_selected": False,
        "overall": summarize_group(rows),
        "by_direction": {
            direction: summarize_group([r for r in rows if r["direction"] == direction])
            for direction in ("BUY", "SELL")
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mt5-path", required=True)
    parser.add_argument("--symbol", default="XAUUSD.ecn")
    parser.add_argument("--start", default="2026-07-13T00:00:00+00:00")
    parser.add_argument("--end", default="2026-10-13T00:00:00+00:00")
    parser.add_argument("--config-module", default="sp2l_v3_rr2_trail4_config")
    parser.add_argument("--output-dir", default=str(OUT))
    args = parser.parse_args()

    import run_sp2l_v3_xauusd_trailing_matrix as matrix
    import MetaTrader5 as mt5

    start, end = datetime.fromisoformat(args.start), datetime.fromisoformat(args.end)
    if start.tzinfo is None or end.tzinfo is None or start >= end:
        raise ValueError("--start and --end must be timezone-aware and start < end")
    cfg = importlib.import_module(args.config_module)
    if not mt5.initialize(path=args.mt5_path):
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        bars = matrix.fetch_m1_rates(args.symbol, start, end)
        candidates = matrix.collect_candidates(bars, cfg, args.symbol)
        rows = audit_candidates(bars, candidates)
        summary = summarize_rows(rows)
        payload = {
            "status": "COMPLETE",
            "research_only": True,
            "source_semantics": {
                "source_note": "BUY retrace to previous candle Low / SELL retrace to previous candle High",
                "unresolved": [
                    "previous-candle identity beyond the observed adjacent candle",
                    "touch versus penetration versus close",
                    "intrabar event order",
                    "entry/fill semantics",
                ],
                "canonical_rule_selected": False,
            },
            "dataset": {
                "symbol": args.symbol,
                "timeframe": "M1",
                "start": start.isoformat(),
                "end": end.isoformat(),
                "bar_count": len(bars),
                "bars_sha256": hashlib.sha256(bars.tobytes()).hexdigest(),
                "candidate_count": len(candidates),
            },
            "summary": summary,
            "rows": rows,
        }
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = output_dir / f"SP2L_V3_ENTRY_GEOMETRY_AUDIT_{stamp}"
        json_path = base.with_suffix(".json")
        csv_path = base.with_name(base.name + "_rows.csv")
        json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        if rows:
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
        print(json.dumps({
            "status": payload["status"],
            "research_only": True,
            "candidate_count": len(candidates),
            "bars_sha256": payload["dataset"]["bars_sha256"],
            "summary": summary,
            "json": str(json_path),
            "csv": str(csv_path) if rows else None,
        }, indent=2))
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
