"""Run the SP2L research matrix against the user's connected MT5 terminal.

The runner is research-only. It downloads MT5 bars and records symbol metadata,
weekly cases, pip accounting, and data quality. Strategy execution remains
delegated to the existing V2 replay engine; no production signals are emitted.
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

from discover_mt5_research_symbols import require_unique_resolution
from mt5_terminal_resolver import find_mt5_terminal
from sp2l_pip_contract import make_contract
from sp2l_v2_test_matrix import build_matrix


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "matrix-mt5"
OUT.mkdir(parents=True, exist_ok=True)


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def init_mt5(path: str | None) -> None:
    if path:
        ok = mt5.initialize(path=path)
    else:
        ok = mt5.initialize()

    if not ok:
        terminal = find_mt5_terminal()
        if terminal is not None:
            ok = mt5.initialize(path=str(terminal))

    if not ok:
        raise RuntimeError(f"MT5 initialization failed: {mt5.last_error()}")


def fetch_week(symbol: str, start: datetime, end: datetime):
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start, end)
    if rates is None:
        raise RuntimeError(f"copy_rates_range failed for {symbol}: {mt5.last_error()}")
    return rates


def expected_minutes(start: datetime, end: datetime) -> int:
    return max(0, int((end - start).total_seconds() // 60))


def week_cases(start: date, end: date):
    return build_matrix(start, end)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2026-01-01")
    parser.add_argument("--end", default="2026-09-25")
    parser.add_argument("--symbols", default="XAUUSD,USDJPY,EURJPY,GBPUSD,GBPJPY,EURUSD,USDCHF,USDCAD")
    parser.add_argument("--mt5-path", default=None)
    parser.add_argument("--population", choices=["ALL", "PRIMARY", "FX_M1"], default="ALL")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    start_date = parse_date(args.start)
    # End is inclusive at date level; MT5 query uses next midnight.
    end_date = parse_date(args.end) + timedelta(days=1)
    selected = {s.strip().upper() for s in args.symbols.split(",") if s.strip()}

    init_mt5(args.mt5_path)

    try:
        symbol_map = require_unique_resolution(tuple(sorted(selected)))
        cases = [
            c for c in week_cases(start_date, end_date)
            if c.symbol.upper() in selected
            and (args.population == "ALL" or c.population == args.population)
        ]

        results = []
        for case in cases:
            broker_symbol = symbol_map[case.symbol.upper()]
            info = mt5.symbol_info(broker_symbol)
            if info is None:
                raise RuntimeError(f"symbol_info failed: {broker_symbol}")

            week_start = datetime.fromisoformat(case.window_start_utc).replace(tzinfo=timezone.utc)
            week_end = datetime.fromisoformat(case.window_end_utc).replace(tzinfo=timezone.utc)

            rates = fetch_week(broker_symbol, week_start, week_end)
            bars = len(rates)

            contract = make_contract(
                broker_symbol,
                float(info.point),
                int(info.digits),
                0.01,
            )

            timestamps = [int(x["time"]) for x in rates] if bars else []
            gaps = 0
            weekend_gap_minutes = 0
            non_weekend_gap_minutes = 0
            gap_intervals = []

            def weekend_closure_overlap_minutes(start_ts: int, end_ts: int) -> int:
                """Classify the continuous Fri->Mon market-closure span.
                
                The existing day-of-week counter only marked Sat/Sun minutes,
                which incorrectly exposed the Friday-evening and Monday-morning
                portions of the same weekly closure as non-weekend gaps.
                This is calendar classification only; it does not infer broker
                session hours within Friday/Monday.
                """
                start = datetime.fromtimestamp(start_ts, tz=timezone.utc)
                end = datetime.fromtimestamp(end_ts, tz=timezone.utc)
                if start.weekday() == 4 and end.weekday() == 0:
                    return int((end - start).total_seconds() // 60)
                if start.weekday() in {5, 6} and end.weekday() == 0:
                    return int((end - start).total_seconds() // 60)
                return 0

            if timestamps:
                for prev, cur in zip(timestamps, timestamps[1:]):
                    delta = cur - prev
                    missing = max(0, delta // 60 - 1)
                    if missing:
                        weekend = weekend_closure_overlap_minutes(prev + 60, cur)
                        non_weekend = max(0, missing - weekend)
                        gaps += missing
                        weekend_gap_minutes += weekend
                        non_weekend_gap_minutes += non_weekend
                        gap_intervals.append({
                            "start_utc": datetime.fromtimestamp(
                                prev + 60, tz=timezone.utc
                            ).isoformat(),
                            "end_utc": datetime.fromtimestamp(
                                cur - 60, tz=timezone.utc
                            ).isoformat(),
                            "missing_minutes": missing,
                            "calendar_weekend_minutes": weekend,
                            "non_weekend_minutes": non_weekend,
                        })

            results.append({
                "case_id": case.case_id,
                "population": case.population,
                "requested_symbol": case.symbol,
                "broker_symbol": broker_symbol,
                "timeframe": case.timeframe,
                "week_start_utc": case.window_start_utc,
                "week_end_utc": case.window_end_utc,
                "session_start_utc": case.session_start_utc,
                "session_end_utc": case.session_end_utc,
                "bars_m1": bars,
                "expected_minutes": expected_minutes(week_start, week_end),
                "internal_gap_minutes": gaps,
                "calendar_weekend_gap_minutes": weekend_gap_minutes,
                "non_weekend_gap_minutes": non_weekend_gap_minutes,
                "gap_intervals": gap_intervals,
                "point": contract.point,
                "digits": contract.digits,
                "pip_size": contract.pip_size,
                "volume_lots": contract.volume_lots,
                "trade_mode": int(info.trade_mode),
                "contract_size": float(info.trade_contract_size),
                "currency_base": info.currency_base,
                "currency_profit": info.currency_profit,
                "currency_margin": info.currency_margin,
                "spread_points": int(info.spread),
                "trade_tick_size": float(info.trade_tick_size),
                "trade_tick_value": float(info.trade_tick_value),
            })

        payload = {
            "status": "COMPLETE",
            "mode": "RESEARCH_MT5_MATRIX_DATASET",
            "canonical": False,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "start_date": start_date.isoformat(),
            "end_date_inclusive": args.end,
            "symbols_requested": sorted(selected),
            "symbol_mapping": symbol_map,
            "population": args.population,
            "cases": len(results),
            "results": results,
        }

        output = Path(args.output) if args.output else OUT / (
            "SP2L_MT5_MATRIX_"
            + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + ".json"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

        print(json.dumps({
            "status": "COMPLETE",
            "cases": len(results),
            "output": str(output),
            "canonical": False,
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
