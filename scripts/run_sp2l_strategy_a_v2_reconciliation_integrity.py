"""Research-only integrity audit for reconciliation source-only cases.

This tool checks whether SOURCE_ALIGNED_ONLY setups are actually detectable by
the V2 setup detector and verifies that reconciliation preserves every detected
setup rather than applying execution-style entry-key deduplication.

It does not change detector rules or reconciliation behavior.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import MetaTrader5 as mt5

from run_sp2l_strategy_a_v2_signal_reconciliation import (
    contiguous_segments,
    fetch_rates,
    filter_session,
    resolve_symbol,
    _bar,
)
from sp2l_strategy_a_v2_detector import detect_setup, find_first_entry


def _setup_key(record: dict) -> tuple:
    return (
        record["direction"],
        record["before_spike_time"],
        record["spike_time"],
        record["after_spike_time"],
    )


def _entry_key(record: dict) -> tuple:
    return (int(record["entry_time"]), record["direction"])


def _find_setup_in_segment(segment: list[dict], record: dict):
    for i in range(2, len(segment)):
        setup = detect_setup(segment[i - 2 : i + 1])
        if setup is None:
            continue
        if (
            setup["direction"] == record["direction"]
            and setup["before_spike_time"] == record["before_spike_time"]
            and setup["spike_time"] == record["spike_time"]
            and setup["after_spike_time"] == record["after_spike_time"]
        ):
            return i, setup
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reconciliation-report", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--symbol", default="XAUUSD")
    parser.add_argument("--mt5-path", required=True)
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

        segments = [[_bar(x) for x in segment] for segment in contiguous_segments(rates)]

        # Reproduce the corrected geometry-reconciliation V2 output.
        # Do not deduplicate by entry key: setup identity is the reconciliation unit.
        v2_records = []
        setup_records = []
        for segment_index, bars in enumerate(segments):
            for i in range(2, len(bars)):
                setup = detect_setup(bars[i - 2 : i + 1])
                if setup is None:
                    continue
                setup_records.append({
                    "segment_index": segment_index,
                    "setup": setup,
                })
                entry = find_first_entry(bars, i, setup)
                if entry is None:
                    continue
                v2_records.append(entry)

        v2_by_setup = {_setup_key(x): x for x in v2_records}
        v2_entry_keys = {_entry_key(x) for x in v2_records}

        source_only = recon["comparison"]["source_aligned_only"]
        cases = []

        for record in source_only:
            found = None
            for segment_index, bars in enumerate(segments):
                found = _find_setup_in_segment(bars, record)
                if found is not None:
                    setup_index, setup = found
                    entry = find_first_entry(bars, setup_index, setup)
                    cases.append({
                        "record": record,
                        "v2_setup_detected_directly": True,
                        "segment_index": segment_index,
                        "v2_setup": setup,
                        "v2_entry_direct": entry,
                        "v2_setup_present_in_collect_output": _setup_key(record) in v2_by_setup,
                        "entry_key_in_collect_output": (
                            _entry_key(entry) in v2_entry_keys if entry is not None else False
                        ),
                        "entry_key_shared_with_other_setup": (
                            entry is not None
                            and sum(_entry_key(x) == _entry_key(entry) for x in v2_records) > 1
                        ),
                    })
                    break
            if found is None:
                cases.append({
                    "record": record,
                    "v2_setup_detected_directly": False,
                    "segment_index": None,
                    "v2_setup": None,
                    "v2_entry_direct": None,
                    "v2_setup_present_in_collect_output": False,
                    "entry_key_in_collect_output": False,
                    "entry_key_was_deduplicated": False,
                })

        summary = {
            "source_aligned_only_total": len(source_only),
            "direct_v2_setup_detected": sum(
                bool(x["v2_setup_detected_directly"]) for x in cases
            ),
            "direct_v2_entry_found": sum(
                x["v2_entry_direct"] is not None for x in cases
            ),
            "present_in_collect_v2_output": sum(
                bool(x["v2_setup_present_in_collect_output"]) for x in cases
            ),
            "entry_key_present_in_collect_v2_output": sum(
                bool(x["entry_key_in_collect_output"]) for x in cases
            ),
            "cases_missing_from_corrected_collect_v2_output": sum(
                bool(
                    x["v2_setup_detected_directly"]
                    and x["v2_entry_direct"] is not None
                    and not x["v2_setup_present_in_collect_output"]
                )
                for x in cases
            ),
        }

        report = {
            "status": "COMPLETE",
            "mode": "RESEARCH_ONLY_SP2L_RECONCILIATION_INTEGRITY",
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
            "collect_v2_reproduction": {
                "setup_candidates": len(setup_records),
                "v2_output_records": len(v2_records),
                "entry_dedup_key": null,
                "geometry_reconciliation_key": "(direction, before_spike_time, spike_time, after_spike_time)",
            },
            "summary": summary,
            "cases": cases,
            "semantic_limits": [
                "This audits reconciliation integrity only.",
                "It does not decide which detector geometry is source-correct.",
                "It does not modify collect_v2 or promote any rule.",
                "Entry-key deduplication is intentionally excluded from geometry reconciliation.",
            ],
        }

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = (
            "artifacts/backtest-mt5-local/"
            f"SP2L_STRATEGY_A_V2_RECONCILIATION_INTEGRITY_{stamp}.json"
        )
        from pathlib import Path
        path = Path(out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        print(json.dumps({
            "status": "COMPLETE",
            "report": str(path),
            "summary": summary,
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
