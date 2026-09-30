"""Deterministic temporal-stability cohort analysis for SP2L V2.

Research-only. Uses the frozen V2 detector, entry/initial-SL contract, and the
same RR/trailing exit matrix. Signals are generated once over the full combined
window, then assigned to fixed entry-time cohorts. No parameter tuning or
variant selection is performed.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from run_sp2l_v2_xauusd_exact_window_exit_matrix import (
    TRAILS_PIPS,
    build_population,
    filter_population,
    fetch_rates,
    parse_ts,
    resolve_xauusd,
    simulate,
    summarize,
    variant_name,
)
import MetaTrader5 as mt5
from mt5_terminal_resolver import find_mt5_terminal


COHORTS = [
    ("2026-07-01T00:00:00Z", "2026-07-15T00:00:00Z"),
    ("2026-07-15T00:00:00Z", "2026-07-29T00:00:00Z"),
    ("2026-07-29T00:00:00Z", "2026-08-12T00:00:00Z"),
    ("2026-08-12T00:00:00Z", "2026-08-26T00:00:00Z"),
    ("2026-08-26T00:00:00Z", "2026-09-10T00:00:00Z"),
    ("2026-09-10T00:00:00Z", "2026-09-25T00:00:00Z"),
]


def cohort_for(entry_time: int) -> str | None:
    for start_s, end_s in COHORTS:
        start = int(parse_ts(start_s).timestamp())
        end = int(parse_ts(end_s).timestamp())
        if start <= entry_time < end:
            return f"{start_s[:10]}__{end_s[:10]}"
    return None


def run(args) -> dict:
    start = parse_ts(COHORTS[0][0])
    end = parse_ts(COHORTS[-1][1])

    initialized = mt5.initialize(path=str(args.mt5_path)) if args.mt5_path else mt5.initialize()
    if not initialized:
        terminal = None if args.mt5_path else find_mt5_terminal()
        if terminal is None or not mt5.initialize(path=str(terminal)):
            raise RuntimeError(f"MT5_INIT_FAILED: {mt5.last_error()}")

    try:
        symbol = resolve_xauusd()
        info = mt5.symbol_info(symbol)
        if info is None:
            raise RuntimeError(f"symbol_info failed: {symbol}: {mt5.last_error()}")
        contract_size = float(info.trade_contract_size)
        rates = fetch_rates(symbol, start, end)
        population = build_population(rates)

        cohort_map = {s["signal_index"]: cohort_for(s["entry_time"]) for s in population}
        configs = [("FIXED_TP", rr, None) for rr in args.rr] + [
            ("NO_TP_TRAILING", None, trail) for trail in args.trail_pips
        ]

        rows = []
        for session in ("ALL_MARKET_HOURS", "LONDON_TO_NEW_YORK"):
            session_population = filter_population(population, session)
            for exit_mode, rr, trail_pips in configs:
                for signal in session_population:
                    outcome = simulate(
                        rates, signal, exit_mode=exit_mode, rr=rr, trail_pips=trail_pips
                    )
                    cohort = cohort_map.get(signal["signal_index"])
                    if cohort is None:
                        continue
                    rows.append({
                        "cohort": cohort,
                        "session": session,
                        "variant": variant_name(exit_mode, rr, trail_pips),
                        "signal_index": signal["signal_index"],
                        **signal,
                        **outcome,
                    })

        cohort_summaries = []
        for cohort in [f"{a[:10]}__{b[:10]}" for a, b in COHORTS]:
            for session in ("ALL_MARKET_HOURS", "LONDON_TO_NEW_YORK"):
                for exit_mode, rr, trail_pips in configs:
                    variant = variant_name(exit_mode, rr, trail_pips)
                    subset = [
                        r for r in rows
                        if r["cohort"] == cohort
                        and r["session"] == session
                        and r["variant"] == variant
                    ]
                    summary = summarize(subset, contract_size, args.volume)
                    cohort_summaries.append({
                        "cohort": cohort,
                        "session": session,
                        "variant": variant,
                        **summary,
                    })

        result = {
            "status": "COMPLETE",
            "mode": "NON_CANONICAL_FORENSIC_TEMPORAL_STABILITY",
            "experiment": "V2_XAUUSD_FIXED_ENTRY_COHORT_STABILITY",
            "canonical": False,
            "cohort_contract": {
                "cohort_assignment": "entry_time",
                "cohort_boundaries": "fixed, predeclared, no optimization",
                "signal_population_built_once": True,
                "exit_may_extend_beyond_cohort_boundary": True,
            },
            "period": {
                "start_utc": start.isoformat(),
                "end_utc": end.isoformat(),
                "end_inclusive": False,
            },
            "resolved_symbol": symbol,
            "bars": int(len(rates)),
            "population_signals_all_hours": len(population),
            "cohorts": COHORTS,
            "rr": args.rr,
            "trail_pips": args.trail_pips,
            "results": cohort_summaries,
        }
        return result
    finally:
        mt5.shutdown()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rr", nargs="+", type=float, default=[1.0, 2.0])
    ap.add_argument("--trail-pips", nargs="+", type=float, default=TRAILS_PIPS)
    ap.add_argument("--volume", type=float, default=0.01)
    ap.add_argument("--mt5-path", default=None)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    if args.volume != 0.01:
        raise SystemExit("This experiment is frozen at 0.01 lot. Use --volume 0.01.")

    result = run(args)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(args.output) if args.output else Path("artifacts/backtest-mt5-local") / (
        f"SP2L_V2_TEMPORAL_STABILITY_{stamp}.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    csv_out = out.with_suffix(".csv")
    fields = [
        "cohort", "session", "variant", "signals", "decisive", "wins", "losses",
        "breakeven", "ambiguous", "open_or_unresolved", "win_rate_decisive_pct",
        "net_R", "net_usd", "profit_factor", "max_drawdown_R",
        "max_losing_streak", "trailing_activated_count",
    ]
    with csv_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: row.get(k) for k in fields} for row in result["results"])

    print(json.dumps({
        "status": result["status"],
        "symbol": result["resolved_symbol"],
        "bars": result["bars"],
        "population_signals_all_hours": result["population_signals_all_hours"],
        "output": str(out),
        "summary_csv": str(csv_out),
        "cohorts": result["cohorts"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
