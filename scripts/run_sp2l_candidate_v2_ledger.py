"""Run the frozen V2 research candidate and emit signal/trade ledgers.

Research-only. This runner does not promote rules or emit production decisions.
It wraps the existing V2 detector/backtest semantics and records every setup
that reaches the candidate entry search plus every accepted trade.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from sp2l_candidate_ledger import candidate_manifest, record_signal, write_jsonl
from run_sp2l_strategy_a_v2_mt5_backtest import (
    fetch_rates,
    resolve_symbol,
    run_backtest,
    build_signals,
)
from mt5_terminal_resolver import find_mt5_terminal
import MetaTrader5 as mt5


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "artifacts" / "candidate-ledger"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CANDIDATE_ID = "V2-CANDIDATE-001"
DETECTOR_SHA = "3cb93ad5cfb5b743213e8bceb1db2e440b57086a1"


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--symbol", default="XAUUSD")
    parser.add_argument("--mt5-path", default=None)
    args = parser.parse_args()

    start = parse_utc(args.start)
    end = parse_utc(args.end)

    if args.mt5_path:
        initialized = mt5.initialize(path=args.mt5_path)
    else:
        initialized = mt5.initialize()

    if not initialized:
        terminal = find_mt5_terminal()
        initialized = terminal is not None and mt5.initialize(path=str(terminal))

    if not initialized:
        raise RuntimeError(f"MT5 initialization failed: {mt5.last_error()}")

    try:
        requested = args.symbol
        symbol, resolution = resolve_symbol(requested)
        rates = fetch_rates(symbol, start, end)
        signals = build_signals(rates)
        result = run_backtest(rates, signals)

        manifest = candidate_manifest(
            candidate_id=CANDIDATE_ID,
            detector_sha=DETECTOR_SHA,
            configuration={
                "p_gap_price": 1.0,
                "spike_multiplier": 1.5,
                "max_sl_distance": 10.0,
                "tp_r": 1.0,
                "trigger": "first post-setup lower-low / higher-high",
                "entry": "trigger candle Low / High",
                "sl_anchor": "candle before Spike Low / High",
                "second_entry": False,
                "filters": [],
            },
            dataset={
                "symbol_requested": requested,
                "symbol_used": symbol,
                "symbol_resolution": resolution,
                "timeframe": "M1",
                "start_utc": start.isoformat(),
                "end_utc": end.isoformat(),
                "bars": int(len(rates)),
            },
            execution_convention={
                "same_bar_sl_tp": "SL_FIRST",
                "entry_bar_exit": "disabled",
                "end_of_data": "MARK_TO_MARKET",
            },
        )

        signal_records = []
        accepted_ids = set()

        for signal in signals:
            sid = record_signal(
                candidate_id=CANDIDATE_ID,
                direction=signal["direction"],
                before_spike_time=int(signal["before_spike_time"]),
                spike_time=int(signal["spike_time"]),
                after_spike_time=int(signal["after_spike_time"]),
                entry_time=int(signal["entry_time"]),
                entry=float(signal["entry"]),
                sl=float(signal["sl"]),
                tp=float(signal["tp"]),
                risk=float(signal["risk"]),
                status="ACCEPTED",
            )
            signal_records.append(sid)
            accepted_ids.add(sid.signal_id)

        trade_records = []
        for trade in result["trades_detail"]:
            signal_id = None
            for s in signal_records:
                if (
                    s.direction == trade["direction"]
                    and s.entry_time == int(trade["entry_time"])
                    and s.entry is not None
                    and abs(s.entry - float(trade["entry"])) < 1e-12
                ):
                    signal_id = s.signal_id
                    break

            if signal_id is None:
                raise RuntimeError(
                    f"trade has no ledger signal: entry_time={trade['entry_time']} "
                    f"direction={trade['direction']}"
                )

            trade_records.append({
                "candidate_id": CANDIDATE_ID,
                "signal_id": signal_id,
                "direction": trade["direction"],
                "entry_time": int(trade["entry_time"]),
                "entry": float(trade["entry"]),
                "sl": float(trade["sl"]),
                "tp": float(trade["tp"]),
                "exit_time": int(trade["exit_time"]),
                "exit": float(trade["exit"]),
                "exit_reason": trade["exit_reason"],
                "realized_r": float(trade["r"]),
                "completed": bool(trade["completed"]),
            })

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = OUT_DIR / f"V2_CANDIDATE_001_{stamp}"

        (base.with_suffix(".manifest.json")).write_text(
            json.dumps({
                "manifest": manifest.__dict__,
                "manifest_id": manifest.stable_id(),
                "status": "RESEARCH_ONLY",
            }, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        write_jsonl(base.with_name(base.name + ".signals.jsonl"), signal_records)

        with open(base.with_name(base.name + ".trades.jsonl"), "w", encoding="utf-8") as handle:
            for trade in trade_records:
                handle.write(json.dumps(trade, sort_keys=True))
                handle.write("\n")

        (base.with_name(base.name + ".summary.json")).write_text(
            json.dumps({
                "status": "COMPLETE",
                "candidate_id": CANDIDATE_ID,
                "manifest_id": manifest.stable_id(),
                "signal_records": len(signal_records),
                "trade_records": len(trade_records),
                "backtest_results": {
                    k: v for k, v in result.items() if k != "trades_detail"
                },
                "canonical": False,
            }, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print(json.dumps({
            "status": "COMPLETE",
            "candidate_id": CANDIDATE_ID,
            "manifest_id": manifest.stable_id(),
            "signals": len(signal_records),
            "trades": len(trade_records),
            "output_prefix": str(base),
            "canonical": False,
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
