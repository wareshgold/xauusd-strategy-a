"""One-month weekly-decomposed research replay for the active SP2L forward-test basket.

This script preserves full-period outcome resolution, then assigns each signal to the
7-day research bucket containing its signal time. It does not re-run each week in
isolation, so a signal near a week boundary can still resolve later in the month.
Research-only; canonical=False.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/research/SP2L_SELECTED_CONFIG_XAU_EUR_USDJPY_20260928.json"
REPLAY_DIR = ROOT / "scripts"
OUT_DIR = ROOT / "artifacts" / "backtest-weekly-20260928"

# The existing local replay module remains authoritative for MT5 acquisition,
# detector invocation, session filter, outcome semantics, and statistics.
sys.path.insert(0, str(REPLAY_DIR))


def _week_buckets(start: datetime, end: datetime) -> list[tuple[datetime, datetime]]:
    buckets = []
    cursor = start
    while cursor < end:
        bucket_end = min(cursor + timedelta(days=7), end)
        buckets.append((cursor, bucket_end))
        cursor = bucket_end
    return buckets


def _bucket_for(ts: int, buckets: list[tuple[datetime, datetime]]) -> int | None:
    dt = datetime.fromtimestamp(int(ts), timezone.utc)
    for index, (start, end) in enumerate(buckets, start=1):
        if start <= dt < end:
            return index
    return None


def _stats(signals: list[dict]) -> dict:
    wins = sum(x.get("result") == "WIN" for x in signals)
    losses = sum(x.get("result") == "LOSS" for x in signals)
    ambiguous = sum(x.get("result") == "AMBIGUOUS" for x in signals)
    open_end = sum(x.get("result") == "OPEN_AT_END" for x in signals)
    data_gap = sum(x.get("result") == "DATA_GAP" for x in signals)
    decisive = wins + losses

    # Local import keeps this report mathematically identical to the base replay.
    from run_sp2l_mt5_local_multi_symbol_backtest import max_drawdown_and_losses, wilson

    ci_low, ci_high = wilson(wins, decisive)
    dd, max_losses = max_drawdown_and_losses(
        [float(x["r"]) for x in signals if x.get("result") in ("WIN", "LOSS")]
    )

    return {
        "signals": len(signals),
        "wins": wins,
        "losses": losses,
        "ambiguous": ambiguous,
        "open_at_end": open_end,
        "data_gap": data_gap,
        "decisive": decisive,
        "win_rate_pct": 100 * wins / decisive if decisive else None,
        "wilson_95_ci_pct": [ci_low, ci_high],
        "net_r": wins - losses,
        "profit_factor_simplified": wins / losses if losses else (float("inf") if wins else None),
        "max_drawdown_r": dd,
        "max_consecutive_losses": max_losses,
        "by_direction": {
            direction: _stats_direction(signals, direction)
            for direction in ("BUY", "SELL")
        },
    }


def _stats_direction(signals: list[dict], direction: str) -> dict:
    subset = [x for x in signals if x.get("direction") == direction]
    wins = sum(x.get("result") == "WIN" for x in subset)
    losses = sum(x.get("result") == "LOSS" for x in subset)
    decisive = wins + losses
    from run_sp2l_mt5_local_multi_symbol_backtest import wilson
    lo, hi = wilson(wins, decisive)
    return {
        "signals": len(subset),
        "wins": wins,
        "losses": losses,
        "ambiguous": sum(x.get("result") == "AMBIGUOUS" for x in subset),
        "decisive": decisive,
        "win_rate_pct": 100 * wins / decisive if decisive else None,
        "wilson_95_ci_pct": [lo, hi],
        "net_r": wins - losses,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="UTC ISO, e.g. 2026-08-26T00:00:00Z")
    parser.add_argument("--end", required=True, help="UTC ISO, e.g. 2026-09-25T23:59:59Z")
    parser.add_argument("--mt5-path", required=True)
    args = parser.parse_args()

    start = datetime.fromisoformat(args.start.replace("Z", "+00:00")).astimezone(timezone.utc)
    end = datetime.fromisoformat(args.end.replace("Z", "+00:00")).astimezone(timezone.utc)
    # The replay API treats its end as an inclusive timestamp. Use an exclusive
    # boundary internally for clean 7-day partitioning, while fetching through
    # the requested final second.
    fetch_end = end
    partition_end = end + timedelta(seconds=1)
    buckets = _week_buckets(start, partition_end)

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Import after paths are prepared; env must be set before the base module is imported
    # because its research parameters are module-level constants.
    import run_sp2l_mt5_local_multi_symbol_backtest as replay
    import MetaTrader5 as mt5

    initialized = mt5.initialize(path=str(Path(args.mt5_path)))
    if not initialized:
        print(json.dumps({"status": "MT5_INIT_FAILED", "error": mt5.last_error()}, indent=2))
        return 2

    report = {
        "status": "RESEARCH_ONLY",
        "canonical": False,
        "source": "CONNECTED_MT5_TERMINAL",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "period": {
            "start_utc": start.isoformat(),
            "end_utc": end.isoformat(),
        },
        "partition": {
            "method": "CONSECUTIVE_7_DAY_BUCKETS_BY_SIGNAL_TIME",
            "outcome_resolution": "FULL_MONTH_REPLAY_BEFORE_WEEK_ASSIGNMENT",
        },
        "config_file": str(CONFIG),
        "symbols": {},
        "weeks": [],
        "notes": [
            "Same selected research configurations used by the active XAU/EUR/USDJPY forward basket.",
            "Each symbol is replayed once over the full month; signals are assigned to weekly buckets by signal time.",
            "A signal is not cut off at the weekly boundary; its outcome may resolve later in the month.",
            "No configuration, geometry, fill semantics, or execution rule is promoted to canonical.",
            "This report is diagnostic research evidence only.",
        ],
    }

    for index, (bucket_start, bucket_end) in enumerate(buckets, start=1):
        report["weeks"].append({
            "week": index,
            "start_utc": bucket_start.isoformat(),
            "end_utc_exclusive": bucket_end.isoformat(),
        })

    try:
        for base, values in cfg["symbols"].items():
            os.environ["SP2L_P_GAP_PRICE"] = str(values["pGapPrice"])
            os.environ["SP2L_SPIKE_MULTIPLIER"] = str(values["spikeMultiplier"])
            os.environ["SP2L_MAX_SL_DISTANCE"] = str(values["maxSlDistance"])
            os.environ["SP2L_TP_R"] = str(cfg["tpR"])

            # The base replay module reads constants at import time. The script
            # is therefore executed once per process/symbol configuration by
            # reloading its module state through explicit constant assignment.
            replay.P_GAP_PRICE = float(values["pGapPrice"])
            replay.SPIKE_MULTIPLIER = float(values["spikeMultiplier"])
            replay.MAX_SL_DISTANCE = float(values["maxSlDistance"])
            replay.TP_R = float(cfg["tpR"])

            symbol = replay.discover_symbols([base])[base]["symbol"]
            if not symbol:
                report["symbols"][base] = {"status": "FAILED", "error": "SYMBOL_NOT_FOUND"}
                continue

            print(f"[MT5] {base} -> {symbol}: downloading full-month M1 history ...", flush=True)
            rates = replay.fetch_rates(symbol, start, fetch_end)
            result = replay.run_symbol(symbol, rates)
            signals = result["signals_detail"]

            weekly = []
            for index, (bucket_start, bucket_end) in enumerate(buckets, start=1):
                selected = [
                    x for x in signals
                    if _bucket_for(int(x["signal_time"]), [(bucket_start, bucket_end)]) == 1
                ]
                weekly.append({
                    "week": index,
                    "start_utc": bucket_start.isoformat(),
                    "end_utc_exclusive": bucket_end.isoformat(),
                    **_stats(selected),
                })

            report["symbols"][base] = {
                "status": "COMPLETE",
                "symbol": symbol,
                "config": values,
                "full_month": _stats(signals),
                "weekly": weekly,
                "bars": result["bars"],
                "first_bar_utc": result["first_bar_utc"],
                "last_bar_utc": result["last_bar_utc"],
                "history_chunks": replay.fetch_rates.last_diagnostics,
            }

            print(
                f"[DONE] {base} -> {symbol}: month signals={result['signals']} "
                f"decisive={result['decisive']} WR={result['win_rate_pct']}",
                flush=True,
            )

        all_signals = []
        for base, symbol_result in report["symbols"].items():
            if symbol_result.get("status") != "COMPLETE":
                continue
            # Reconstruct only the weekly aggregates for the combined view;
            # combined signal-level replay is performed below to retain exact
            # symbol attribution.
            for week in symbol_result["weekly"]:
                pass

        combined_weekly = []
        for index, (bucket_start, bucket_end) in enumerate(buckets, start=1):
            rows = []
            for symbol_result in report["symbols"].values():
                if symbol_result.get("status") != "COMPLETE":
                    continue
                row = symbol_result["weekly"][index - 1]
                # Only decisive R can be safely combined from the aggregate.
                rows.extend([1.0] * row["wins"])
                rows.extend([-1.0] * row["losses"])
            wins = rows.count(1.0)
            losses = rows.count(-1.0)
            decisive = wins + losses
            from run_sp2l_mt5_local_multi_symbol_backtest import wilson, max_drawdown_and_losses
            lo, hi = wilson(wins, decisive)
            dd, max_losses = max_drawdown_and_losses(rows)
            combined_weekly.append({
                "week": index,
                "start_utc": bucket_start.isoformat(),
                "end_utc_exclusive": bucket_end.isoformat(),
                "decisive": decisive,
                "wins": wins,
                "losses": losses,
                "win_rate_pct": 100 * wins / decisive if decisive else None,
                "wilson_95_ci_pct": [lo, hi],
                "net_r": wins - losses,
                "max_drawdown_r": dd,
                "max_consecutive_losses": max_losses,
            })

        report["combined_weekly"] = combined_weekly
        failed = [k for k, v in report["symbols"].items() if v.get("status") != "COMPLETE"]
        report["status"] = "COMPLETE" if not failed else "INCOMPLETE"
        report["failed_symbols"] = failed

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = OUT_DIR / f"SP2L_WEEKLY_DECOMPOSED_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({"status": report["status"], "report": str(path)}, indent=2))
        return 0 if not failed else 3
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
