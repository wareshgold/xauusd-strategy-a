"""Research-only forensic decomposition of V2-only/source-only reconciliation cases.

This tool consumes a completed reconciliation artifact and the same MT5 M1
history, then explains why representative non-common setups diverge.

It does not change detector rules, optimize parameters, or promote geometry.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import MetaTrader5 as mt5

from run_sp2l_strategy_a_v2_signal_reconciliation import (
    P_GAP_PRICE,
    SPIKE_MULTIPLIER,
    MAX_SL_DISTANCE,
    TP_R,
    _bar,
    contiguous_segments,
    fetch_rates,
    filter_session,
    resolve_symbol,
)
from sp2l_strategy_a_v2_detector import detect_setup, find_first_entry


def _body(c, direction):
    return (
        float(c["close"] - c["open"])
        if direction == "BUY"
        else float(c["open"] - c["close"])
    )


def _source_condition_report(a, spike, correction, trigger, direction):
    if direction == "BUY":
        checks = {
            "trigger_lower_low": float(trigger["low"]) < float(correction["low"]),
            "correction_above_spike_close": float(correction["close"]) > float(spike["close"]),
            "correction_above_spike_open": float(correction["open"]) > float(spike["open"]),
            "spike_close_above_a_close": float(spike["close"]) > float(a["close"]),
            "spike_open_above_a_open": float(spike["open"]) > float(a["open"]),
            "correction_bullish": float(correction["close"]) > float(correction["open"]),
            "spike_bullish": float(spike["close"]) > float(spike["open"]),
            "a_bullish": float(a["close"]) > float(a["open"]),
            "p_gap": float(correction["low"]) > float(a["high"]) + P_GAP_PRICE,
            "spike_body_vs_correction": _body(spike, direction) > SPIKE_MULTIPLIER * _body(correction, direction),
            "spike_body_vs_a": _body(spike, direction) > SPIKE_MULTIPLIER * _body(a, direction),
            "spike_body_vs_trigger": _body(spike, direction) > SPIKE_MULTIPLIER * _body(trigger, direction),
        }
        sl = float(spike["low"])
        entry = float(trigger["low"])
    else:
        checks = {
            "trigger_higher_high": float(trigger["high"]) > float(correction["high"]),
            "correction_below_spike_close": float(correction["close"]) < float(spike["close"]),
            "correction_below_spike_open": float(correction["open"]) < float(spike["open"]),
            "spike_close_below_a_close": float(spike["close"]) < float(a["close"]),
            "spike_open_below_a_open": float(spike["open"]) < float(a["open"]),
            "correction_bearish": float(correction["close"]) < float(correction["open"]),
            "spike_bearish": float(spike["close"]) < float(spike["open"]),
            "a_bearish": float(a["close"]) < float(a["open"]),
            "p_gap": float(correction["high"]) < float(a["low"]) - P_GAP_PRICE,
            "spike_body_vs_correction": _body(spike, direction) > SPIKE_MULTIPLIER * _body(correction, direction),
            "spike_body_vs_a": _body(spike, direction) > SPIKE_MULTIPLIER * _body(a, direction),
            "spike_body_vs_trigger": _body(spike, direction) > SPIKE_MULTIPLIER * _body(trigger, direction),
        }
        sl = float(spike["high"])
        entry = float(trigger["high"])

    risk = entry - sl if direction == "BUY" else sl - entry
    checks["source_risk_valid"] = 0 < risk <= MAX_SL_DISTANCE
    return {
        "checks": checks,
        "failed_checks": [k for k, v in checks.items() if not v],
        "source_entry": entry,
        "source_sl": sl,
        "source_risk": risk,
    }


def _locate_record(record, bars_by_time):
    before = bars_by_time[record["before_spike_time"]]
    spike = bars_by_time[record["spike_time"]]
    after = bars_by_time[record["after_spike_time"]]
    return before, spike, after


def _v2_context(record, bars_by_time, segment_times_by_time):
    before, spike, after = _locate_record(record, bars_by_time)
    ordered_times = segment_times_by_time[record["after_spike_time"]]
    after_pos = ordered_times.index(record["after_spike_time"])
    if after_pos + 1 >= len(ordered_times):
        return {"status": "NO_FOLLOWING_BAR"}
    trigger_time = ordered_times[after_pos + 1]
    trigger = bars_by_time[trigger_time]
    return {
        "trigger_time_immediate": trigger_time,
        "source_conditions": _source_condition_report(
            before, spike, after, trigger, record["direction"]
        ),
    }


def _find_v2_entry_from_setup(record, bars):
    for i in range(2, len(bars) - 1):
        setup = detect_setup(bars[i - 2 : i + 1])
        if setup is None:
            continue
        if (
            setup["direction"] == record["direction"]
            and setup["before_spike_time"] == record["before_spike_time"]
            and setup["spike_time"] == record["spike_time"]
            and setup["after_spike_time"] == record["after_spike_time"]
        ):
            return find_first_entry(bars, i, setup)
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reconciliation-report", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--symbol", default="XAUUSD")
    parser.add_argument("--mt5-path", required=True)
    parser.add_argument("--v2-only-limit", type=int, default=0, help="Maximum V2-only cases to diagnose; 0 means all.")
    args = parser.parse_args()

    recon = json.loads(open(args.reconciliation_report, encoding="utf-8").read())
    start = datetime.fromisoformat(args.start.replace("Z", "+00:00"))
    end = datetime.fromisoformat(args.end.replace("Z", "+00:00"))

    if not mt5.initialize(path=args.mt5_path):
        print(json.dumps({"status": "MT5_INIT_FAILED", "error": mt5.last_error()}, indent=2))
        return 2

    try:
        symbol, resolution = resolve_symbol(args.symbol)
        raw = fetch_rates(symbol, start, end)
        rates = filter_session(raw)

        segments = contiguous_segments(rates)
        bars_by_time = {}
        segment_times_by_time = {}
        segment_bars_by_time = {}
        for segment in segments:
            bars = [_bar(x) for x in segment]
            segment_times = [b["time"] for b in bars]
            for b in bars:
                bars_by_time[b["time"]] = b
                segment_times_by_time[b["time"]] = segment_times
                segment_bars_by_time[b["time"]] = bars

        c = recon["comparison"]
        v2_only = c["v2_only"]
        source_only = c["source_aligned_only"]

        v2_cases = []
        reason_counts = {}
        for record in v2_only:
            if args.v2_only_limit and len(v2_cases) >= args.v2_only_limit:
                break
            ctx = _v2_context(record, bars_by_time, segment_times_by_time)
            if "source_conditions" in ctx:
                failed = ctx["source_conditions"]["failed_checks"]
                for reason in failed:
                    reason_counts[reason] = reason_counts.get(reason, 0) + 1
            v2_cases.append({
                "record": record,
                **ctx,
            })

        source_cases = []
        for record in source_only:
            before, spike, after = _locate_record(record, bars_by_time)
            segment_bars = segment_bars_by_time.get(record["after_spike_time"], [])
            v2_entry = _find_v2_entry_from_setup(record, segment_bars)
            source_cases.append({
                "record": record,
                "v2_entry_from_same_setup": v2_entry,
                "v2_sl_anchor": float(before["low"] if record["direction"] == "BUY" else before["high"]),
                "v2_risk_if_source_entry": (
                    float(record["entry"] - before["low"])
                    if record["direction"] == "BUY"
                    else float(before["high"] - record["entry"])
                ),
                "source_sl": float(record["sl"]),
            })

        report = {
            "status": "COMPLETE",
            "mode": "RESEARCH_ONLY_SP2L_STRATEGY_A_RECONCILIATION_FORENSICS",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "reconciliation_report": args.reconciliation_report,
            "symbol_requested": args.symbol,
            "symbol_used": symbol,
            "symbol_resolution": resolution,
            "history": {
                "raw_bars": int(len(raw)),
                "session_filtered_bars": int(len(rates)),
                "contiguous_segments": len(segments),
            },
            "parameters": {
                "p_gap_price": P_GAP_PRICE,
                "spike_multiplier": SPIKE_MULTIPLIER,
                "max_sl_distance": MAX_SL_DISTANCE,
                "tp_r": TP_R,
            },
            "v2_only": {
                "total": len(v2_only),
                "diagnosed_cases": len(v2_cases),
                "immediate_source_rejection_reason_counts": reason_counts,
                "cases": v2_cases,
            },
            "source_aligned_only": {
                "total": len(source_only),
                "cases": source_cases,
            },
            "semantic_limits": [
                "This is a forensic decomposition of existing research implementations.",
                "It does not decide which unresolved source interpretation is correct.",
                "SL-anchor differences are documented evidence, not a recommendation.",
                "No optimization, canonical promotion, or production signal is produced.",
            ],
        }

        out = "artifacts/backtest-mt5-local/SP2L_STRATEGY_A_V2_RECONCILIATION_FORENSICS_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".json"
        from pathlib import Path
        path = Path(out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({
            "status": "COMPLETE",
            "report": str(path),
            "v2_only_total": len(v2_only),
            "v2_only_diagnosed": len(v2_cases),
            "immediate_source_rejection_reason_counts": reason_counts,
            "source_aligned_only_total": len(source_only),
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
