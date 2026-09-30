"""Full V2 3-month RR/trailing reconciliation and integrity audit.

NON_CANONICAL_FORENSIC ONLY.

This audit intentionally rebuilds the exact V2 signal population from the connected
MT5 terminal, then:
1. validates it against every matrix trade row;
2. computes a baseline RR=1, no-trailing outcome on the same population;
3. reconciles each matrix variant trade-by-trade;
4. reports outcome transitions, R deltas, ambiguous/open counts, and integrity
   failures;
5. refuses to produce a configuration recommendation.

It does NOT define canonical Strategy A rules or authorize production trading.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5
import numpy as np

from mt5_terminal_resolver import find_mt5_terminal
from sp2l_strategy_a_v2_detector import detect_setup, find_first_entry

PIP_SIZE = 0.10


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_xauusd() -> str:
    symbols = list(mt5.symbols_get() or [])
    names = {str(s.name): s for s in symbols}
    for name in ("XAUUSD", "XAUUSD.ecn", "XAUUSDm", "XAUUSD_ecn"):
        if name in names:
            return name
    for s in symbols:
        if str(s.name).upper().startswith("XAUUSD"):
            return str(s.name)
    raise RuntimeError("No XAUUSD broker symbol found")


def fetch_rates(symbol: str, start: datetime, end: datetime) -> np.ndarray:
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"symbol_select failed: {symbol}: {mt5.last_error()}")
    chunk_days = float("7")
    retries = 3
    cursor = start
    chunks = []
    while cursor < end:
        chunk_end = min(cursor + timedelta(days=chunk_days), end)
        rates = None
        err = None
        for attempt in range(1, retries + 1):
            rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, cursor, chunk_end)
            if rates is not None and len(rates):
                break
            err = mt5.last_error()
            time.sleep(0.25 * attempt)
        if rates is None or len(rates) == 0:
            raise RuntimeError(
                f"MT5 history failed {cursor.isoformat()}..{chunk_end.isoformat()}: "
                f"{err or mt5.last_error()}"
            )
        chunks.append(rates.copy())
        cursor = chunk_end + timedelta(minutes=1)
    result = np.concatenate(chunks)
    result.sort(order="time")
    _, idx = np.unique(result["time"], return_index=True)
    return result[np.sort(idx)]


def build_population(rates: np.ndarray) -> list[dict]:
    population = []
    for i in range(2, len(rates)):
        setup = detect_setup(rates[: i + 1])
        if setup is None:
            continue
        signal = find_first_entry(rates, i, setup)
        if signal is None:
            continue
        population.append({
            "signal_index": len(population),
            "direction": signal["direction"],
            "setup_time": int(signal["setup_time"]),
            "entry_index": int(signal["entry_index"]),
            "entry_time": int(signal["entry_time"]),
            "entry": float(signal["entry"]),
            "sl": float(signal["sl"]),
            "risk": float(signal["risk"]),
        })
    return population


def identity(row: dict) -> tuple:
    return (
        row.get("direction"),
        int(row.get("setup_time")),
        int(row.get("entry_time")),
        round(float(row.get("entry")), 8),
        round(float(row.get("sl")), 8),
    )


def validate_population(matrix: dict, population: list[dict]) -> dict:
    expected = {identity(x): x for x in population}
    failures = []
    duplicate_matrix = 0

    for variant in matrix["variants"]:
        seen = set()
        rows = variant["trades"]
        if len(rows) != len(population):
            failures.append({
                "type": "ROW_COUNT",
                "rr": variant["rr"],
                "trail_pips": variant["trail_pips"],
                "matrix_rows": len(rows),
                "population_rows": len(population),
            })
        for row in rows:
            k = identity(row)
            if k in seen:
                duplicate_matrix += 1
            seen.add(k)
            if k not in expected:
                failures.append({
                    "type": "UNKNOWN_SIGNAL",
                    "rr": variant["rr"],
                    "trail_pips": variant["trail_pips"],
                    "identity": k,
                })

    return {
        "population_signals": len(population),
        "matrix_variants": len(matrix["variants"]),
        "identity_failures": len(failures),
        "duplicate_matrix_rows": duplicate_matrix,
        "failure_examples": failures[:25],
        "PASS": not failures and duplicate_matrix == 0,
    }


def simulate_baseline(rates: np.ndarray, signal: dict) -> dict:
    entry = signal["entry"]
    sl = signal["sl"]
    risk = abs(entry - sl)
    tp = entry + risk if signal["direction"] == "BUY" else entry - risk

    for i in range(signal["entry_index"], len(rates)):
        high = float(rates[i]["high"])
        low = float(rates[i]["low"])
        if signal["direction"] == "BUY":
            sl_hit, tp_hit = low <= sl, high >= tp
        else:
            sl_hit, tp_hit = high >= sl, low <= tp
        if sl_hit and tp_hit:
            return {"result": "AMBIGUOUS", "r": None, "exit_index": i, "reason": "SL_AND_TP_SAME_BAR"}
        if tp_hit:
            return {"result": "WIN", "r": 1.0, "exit_index": i, "reason": "TP"}
        if sl_hit:
            return {"result": "LOSS", "r": -1.0, "exit_index": i, "reason": "SL"}
    return {"result": "OPEN_OR_UNRESOLVED", "r": None, "exit_index": None, "reason": "OPEN_OR_UNRESOLVED"}


def summarize_baseline(rows: list[dict]) -> dict:
    decisive = [r for r in rows if r["result"] in {"WIN", "LOSS"}]
    wins = sum(r["result"] == "WIN" for r in decisive)
    losses = sum(r["result"] == "LOSS" for r in decisive)
    return {
        "signals": len(rows),
        "decisive": len(decisive),
        "wins": wins,
        "losses": losses,
        "ambiguous": sum(r["result"] == "AMBIGUOUS" for r in rows),
        "open_or_unresolved": sum(r["result"] == "OPEN_OR_UNRESOLVED" for r in rows),
        "win_rate_decisive_pct": 100 * wins / len(decisive) if decisive else None,
        "net_R": wins - losses,
    }


def finite(x):
    return x is not None and math.isfinite(float(x))


def reconcile_variant(baseline_by_key: dict, variant: dict) -> dict:
    transitions = Counter()
    r_delta = []
    missing = []
    examples = []

    for row in variant["trades"]:
        k = identity(row)
        b = baseline_by_key.get(k)
        if b is None:
            missing.append(k)
            continue
        mr = row["result"]
        br = b["result"]
        transitions[f"{br}_TO_{mr}"] += 1

        if finite(b.get("r")) and finite(row.get("r")):
            r_delta.append(float(row["r"]) - float(b["r"]))

        if br != mr and len(examples) < 30:
            examples.append({
                "direction": row["direction"],
                "setup_time": row["setup_time"],
                "entry_time": row["entry_time"],
                "baseline_result": br,
                "matrix_result": mr,
                "baseline_r": b.get("r"),
                "matrix_r": row.get("r"),
                "matrix_reason": row.get("reason"),
                "matrix_exit_time": row.get("exit_time"),
            })

    return {
        "rr": variant["rr"],
        "trail_pips": variant["trail_pips"],
        "matrix_summary": variant["summary"],
        "baseline_to_matrix_transitions": dict(transitions),
        "matched_rows": len(variant["trades"]) - len(missing),
        "missing_baseline_rows": len(missing),
        "mean_R_delta_on_both_decisive": sum(r_delta) / len(r_delta) if r_delta else None,
        "changed_outcome_count": sum(v for k, v in transitions.items() if not k.endswith("_TO_" + k.split("_TO_")[0])),
        "changed_examples_first_30": examples,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--start", default="2026-06-28T00:00:00Z")
    ap.add_argument("--end", default="2026-09-25T00:00:00Z")
    ap.add_argument("--mt5-path", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    matrix_path = Path(args.matrix)
    matrix = load_json(matrix_path)
    start = parse_ts(args.start)
    end = parse_ts(args.end)

    initialized = mt5.initialize(path=str(args.mt5_path))
    if not initialized:
        print(json.dumps({"status": "MT5_INIT_FAILED", "error": mt5.last_error()}, indent=2))
        return 2

    try:
        symbol = resolve_xauusd()
        rates = fetch_rates(symbol, start, end)
        population = build_population(rates)
        integrity = validate_population(matrix, population)

        baseline_rows = []
        for signal in population:
            baseline_rows.append({
                **signal,
                **simulate_baseline(rates, signal),
            })
        baseline_summary = summarize_baseline(baseline_rows)
        baseline_by_key = {identity(x): x for x in baseline_rows}

        reconciliations = [
            reconcile_variant(baseline_by_key, variant)
            for variant in matrix["variants"]
        ]

        # Explicitly surface the key question: are the extreme WRs caused by
        # replacing baseline losses with profitable trailing exits?
        transition_totals = Counter()
        for x in reconciliations:
            transition_totals.update(x["baseline_to_matrix_transitions"])

        result = {
            "status": "COMPLETE",
            "mode": "NON_CANONICAL_FORENSIC",
            "matrix_artifact": str(matrix_path),
            "matrix_sha256": __import__("hashlib").sha256(matrix_path.read_bytes()).hexdigest(),
            "period": {"start_utc": start.isoformat(), "end_utc": end.isoformat()},
            "resolved_symbol": symbol,
            "bars": len(rates),
            "population": {
                "signals": len(population),
                "detector": "sp2l_strategy_a_v2_detector.py",
                "p_gap_price": 1.0,
                "spike_multiplier": 1.5,
                "max_sl_distance": 10.0,
                "session_filter": False,
            },
            "integrity": integrity,
            "baseline_rr1_no_trailing": baseline_summary,
            "global_transition_counts_across_all_12_variants": dict(transition_totals),
            "variants": reconciliations,
            "decision_gate": {
                "population_integrity_required": True,
                "identity_failures_must_be_zero": integrity["identity_failures"] == 0,
                "duplicate_matrix_rows_must_be_zero": integrity["duplicate_matrix_rows"] == 0,
                "production_selection": "BLOCKED",
                "reason": "This is a forensic reconciliation only; source-confirmed trailing rules do not exist.",
            },
        }

        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

        print(json.dumps({
            "status": result["status"],
            "symbol": symbol,
            "bars": len(rates),
            "population_signals": len(population),
            "integrity_PASS": integrity["PASS"],
            "identity_failures": integrity["identity_failures"],
            "duplicate_matrix_rows": integrity["duplicate_matrix_rows"],
            "baseline": baseline_summary,
            "transition_counts": dict(transition_totals),
            "output": str(out),
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
