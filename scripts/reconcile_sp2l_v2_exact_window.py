#!/usr/bin/env python3
"""Trade-level reconciliation for the legacy SP2L V2 forensic contract.

Non-canonical forensic tooling only.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

START = datetime(2026, 8, 26, tzinfo=timezone.utc)
END = datetime(2026, 9, 25, tzinfo=timezone.utc)

ALIASES = {
    "entry_time_utc": ["entry_time_utc", "entry_time", "entry_utc", "entryTimeUtc", "signal_time_utc", "time_utc"],
    "setup_time_utc": ["setup_time_utc", "setup_time", "setup_utc", "setupTimeUtc"],
    "direction": ["direction", "side", "type"],
    "entry": ["entry", "entry_price", "entryPrice"],
    "sl": ["sl", "stop_loss", "stopLoss", "stop"],
    "result": ["result", "outcome", "status"],
    "r": ["r", "R", "result_r", "net_r"],
    "completed": ["completed", "is_completed", "complete"],
    "exit_time_utc": ["exit_time_utc", "exit_time", "exit_utc", "exitTimeUtc"],
}


def pick(row, names):
    for name in names:
        value = row.get(name)
        if value not in ("", None):
            return value
    return None


def normalize(row):
    out = {key: pick(row, names) for key, names in ALIASES.items()}
    if out["entry_time_utc"] is None and row.get("timestamp") is not None:
        out["entry_time_utc"] = row["timestamp"]
    if out["direction"] is not None:
        out["direction"] = str(out["direction"]).upper()
    # The MT5 V2 backtest artifact stores completed-trade outcomes as
    # signed R values plus exit_reason, rather than a result field.
    if out["result"] is None and out["r"] not in ("", None):
        try:
            r_value = float(out["r"])
        except (TypeError, ValueError):
            r_value = None
        if r_value is not None:
            if r_value > 0:
                out["result"] = "WIN"
            elif r_value < 0:
                out["result"] = "LOSS"
            else:
                out["result"] = "BREAKEVEN"
    if out["completed"] is not None:
        text = str(out["completed"]).strip().lower()
        out["completed"] = text in {"true", "1", "yes", "y"}
    elif out["r"] not in ("", None):
        out["completed"] = True
    else:
        out["completed"] = None
    return out


def flatten(obj):
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                yield item
            yield from flatten(item)
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from flatten(value)


def parse_time(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    text = str(value).strip()
    try:
        numeric = float(text)
        return datetime.fromtimestamp(numeric, tz=timezone.utc)
    except ValueError:
        pass
    text = text.replace("Z", "+00:00")
    formats = (
        lambda: datetime.fromisoformat(text),
        lambda: datetime.strptime(text, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
        lambda: datetime.strptime(text, "%Y.%m.%d %H:%M:%S").replace(tzinfo=timezone.utc),
    )
    for parser in formats:
        try:
            result = parser()
            if result.tzinfo is None:
                result = result.replace(tzinfo=timezone.utc)
            return result.astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def load_rows(path):
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [normalize(row) for row in csv.DictReader(handle)]

    obj = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for item in flatten(obj):
        row = normalize(item)
        if row["entry_time_utc"] is not None and (
            row["direction"] is not None or row["entry"] is not None
        ):
            rows.append(row)
    return rows


def in_window(row):
    timestamp = parse_time(row["entry_time_utc"])
    return timestamp is not None and START <= timestamp < END


def number(value):
    return round(float(value), 5) if value not in (None, "") else None


def signal_key(row):
    timestamp = parse_time(row["entry_time_utc"])
    return (
        timestamp.isoformat() if timestamp else "",
        row["direction"] or "",
        number(row["entry"]),
    )


def exact_key(row):
    return signal_key(row) + (number(row["sl"]),)


def key(row):
    # Backward-compatible alias for the original strict reconciliation key.
    return exact_key(row)


def stats(rows):
    counts = Counter(
        str(row["result"]).upper()
        for row in rows
        if row["result"] is not None
    )
    decisive = counts["WIN"] + counts["LOSS"] + counts["BREAKEVEN"]
    win_rate = 100.0 * counts["WIN"] / decisive if decisive else 0.0
    net_r = sum(
        float(row["r"])
        for row in rows
        if row["r"] not in (None, "")
    )
    return {
        "signals": len(rows),
        "decisive": decisive,
        "WIN": counts["WIN"],
        "LOSS": counts["LOSS"],
        "BREAKEVEN": counts["BREAKEVEN"],
        "AMBIGUOUS": counts["AMBIGUOUS"],
        "win_rate_decisive_pct": win_rate,
        "net_R": net_r,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", required=True, type=Path)
    parser.add_argument("--backtest", required=True, type=Path)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/forensic/runtime-m1-replay"),
    )
    args = parser.parse_args()

    runtime_rows = [row for row in load_rows(args.runtime) if in_window(row)]
    backtest_rows = [row for row in load_rows(args.backtest) if in_window(row)]

    if not runtime_rows:
        raise RuntimeError("No runtime trades found in exact window.")
    if not backtest_rows:
        raise RuntimeError(
            "No backtest trades found in exact window. "
            "If the backtest artifact stores only a summary, supply its trade-level CSV/export."
        )

    # Level 1: strict identity, including SL.
    runtime_exact_counts = Counter(exact_key(row) for row in runtime_rows)
    backtest_exact_counts = Counter(exact_key(row) for row in backtest_rows)
    exact_common = sum((runtime_exact_counts & backtest_exact_counts).values())

    # Level 2: signal identity, deliberately ignoring SL.
    runtime_signal_counts = Counter(signal_key(row) for row in runtime_rows)
    backtest_signal_counts = Counter(signal_key(row) for row in backtest_rows)
    signal_common = sum((runtime_signal_counts & backtest_signal_counts).values())
    runtime_signal_only_count = sum(
        (runtime_signal_counts - backtest_signal_counts).values()
    )
    backtest_signal_only_count = sum(
        (backtest_signal_counts - runtime_signal_counts).values()
    )

    # Split the backtest artifact into signal/ledger rows and completed trade rows.
    # In the current V2 artifact, signal-ledger rows do not carry completion/outcome,
    # while trades_detail rows do. This prevents signal rows from being mistaken for trades.
    backtest_trade_rows = [row for row in backtest_rows if row["completed"] is True]
    backtest_signal_rows = [row for row in backtest_rows if row["completed"] is None]

    # Level 3: compare runtime trades against completed backtest trades only.
    runtime_by_signal = {signal_key(row): row for row in runtime_rows}
    backtest_trade_by_signal = {signal_key(row): row for row in backtest_trade_rows}
    matched_trade_signal_keys = sorted(
        set(runtime_by_signal) & set(backtest_trade_by_signal)
    )
    sl_match_count = 0
    outcome_match_count = 0
    outcome_comparable_count = 0
    runtime_outcome_counts = Counter()
    backtest_outcome_counts = Counter()
    outcome_cross_tab = Counter()
    sl_mismatch_examples = []
    outcome_mismatch_examples = []

    for match_key in matched_trade_signal_keys:
        runtime_row = runtime_by_signal[match_key]
        backtest_row = backtest_trade_by_signal[match_key]
    sl_match_count = 0
    outcome_match_count = 0
    outcome_comparable_count = 0
    runtime_outcome_counts = Counter()
    backtest_outcome_counts = Counter()
    outcome_cross_tab = Counter()
    sl_mismatch_examples = []
    outcome_mismatch_examples = []

    for match_key in matched_trade_signal_keys:
        runtime_row = runtime_by_signal[match_key]
        backtest_row = backtest_by_signal[match_key]
        runtime_sl = number(runtime_row["sl"])
        backtest_sl = number(backtest_row["sl"])
        if runtime_sl == backtest_sl:
            sl_match_count += 1
        elif len(sl_mismatch_examples) < 25:
            sl_mismatch_examples.append({
                "signal_key": match_key,
                "runtime_sl": runtime_sl,
                "backtest_sl": backtest_sl,
                "delta_sl": (
                    round(runtime_sl - backtest_sl, 5)
                    if runtime_sl is not None and backtest_sl is not None
                    else None
                ),
            })

        runtime_result = (
            str(runtime_row["result"]).upper()
            if runtime_row["result"] is not None
            else None
        )
        backtest_result = (
            str(backtest_row["result"]).upper()
            if backtest_row["result"] is not None
            else None
        )
        runtime_outcome_counts[runtime_result or "NO_OUTCOME"] += 1
        backtest_outcome_counts[backtest_result or "NO_OUTCOME"] += 1
        outcome_cross_tab[(runtime_result or "NO_OUTCOME", backtest_result or "NO_OUTCOME")] += 1

        if runtime_result in {"WIN", "LOSS", "BREAKEVEN"} and backtest_result in {
            "WIN",
            "LOSS",
            "BREAKEVEN",
        }:
            outcome_comparable_count += 1
            if runtime_result == backtest_result:
                outcome_match_count += 1
            elif len(outcome_mismatch_examples) < 25:
                outcome_mismatch_examples.append({
                    "signal_key": match_key,
                    "runtime_result": runtime_result,
                    "backtest_result": backtest_result,
                    "runtime_r": number(runtime_row["r"]),
                    "backtest_r": number(backtest_row["r"]),
                })

    backtest_completed_counts = Counter(
        "COMPLETED" if row["completed"] is True else
        "INCOMPLETE" if row["completed"] is False else
        "UNKNOWN"
        for row in backtest_rows
    )

    signal_ledger_counts = Counter(signal_key(row) for row in backtest_signal_rows)
    runtime_signal_counts_for_ledger = Counter(signal_key(row) for row in runtime_rows)
    ledger_common = sum(
        (runtime_signal_counts_for_ledger & signal_ledger_counts).values()
    )
    ledger_runtime_only = sum(
        (runtime_signal_counts_for_ledger - signal_ledger_counts).values()
    )
    ledger_backtest_only = sum(
        (signal_ledger_counts - runtime_signal_counts_for_ledger).values()
    )

    runtime_exact_only = [
        row for row in runtime_rows
        if runtime_exact_counts[exact_key(row)] > backtest_exact_counts[exact_key(row)]
    ]
    backtest_exact_only = [
        row for row in backtest_rows
        if backtest_exact_counts[exact_key(row)] > runtime_exact_counts[exact_key(row)]
    ]

    result = {
        "mode": "NON_CANONICAL_FORENSIC",
        "experiment": "SP2L_V2_EXACT_WINDOW_RECONCILIATION",
        "window_utc": {
            "start": START.isoformat(),
            "end_exclusive": END.isoformat(),
        },
        "runtime": stats(runtime_rows),
        "backtest": stats(backtest_rows),
        "three_level_match": {
            "level_1_exact_identity": {
                "definition": "entry_time_utc + direction + entry + sl",
                "common": exact_common,
                "runtime_only": sum((runtime_exact_counts - backtest_exact_counts).values()),
                "backtest_only": sum((backtest_exact_counts - runtime_exact_counts).values()),
                "coverage_match_pct": 100.0 * exact_common / max(len(runtime_rows), len(backtest_rows)),
            },
            "level_2_signal_identity": {
                "definition": "entry_time_utc + direction + entry (SL ignored)",
                "common": signal_common,
                "runtime_only": runtime_signal_only_count,
                "backtest_only": backtest_signal_only_count,
                "coverage_match_pct": 100.0 * signal_common / max(len(runtime_rows), len(backtest_rows)),
            },
            "level_3_runtime_vs_completed_backtest_trade": {
                "backtest_trade_rows": len(backtest_trade_rows),
                "matched_trade_signal_keys": len(matched_trade_signal_keys),
                "sl_match": sl_match_count,
                "sl_mismatch": len(matched_trade_signal_keys) - sl_match_count,
                "outcome_comparable": outcome_comparable_count,
                "outcome_match": outcome_match_count,
                "outcome_mismatch": outcome_comparable_count - outcome_match_count,
                "runtime_outcome_counts": dict(runtime_outcome_counts),
                "backtest_outcome_counts": dict(backtest_outcome_counts),
                "outcome_cross_tab": {
                    f"{runtime}|{backtest}": count
                    for (runtime, backtest), count in outcome_cross_tab.items()
                },
                "backtest_completion_status": dict(backtest_completed_counts),
                "signal_ledger_rows": len(backtest_signal_rows),
                "sl_mismatch_examples": sl_mismatch_examples,
                "outcome_mismatch_examples": outcome_mismatch_examples,
            },
            "signal_ledger_reconciliation": {
                "definition": "runtime signal identity vs backtest non-completed signal/ledger rows",
                "runtime_signals": len(runtime_rows),
                "backtest_signal_ledger_rows": len(backtest_signal_rows),
                "common": ledger_common,
                "runtime_only": ledger_runtime_only,
                "backtest_only": ledger_backtest_only,
                "coverage_match_pct": 100.0 * ledger_common / max(len(runtime_rows), len(backtest_signal_rows)),
            },
        },
        "matching_key": "entry_time_utc + direction + entry + sl",
        "common_trades": exact_common,
        "runtime_only": sum((runtime_exact_counts - backtest_exact_counts).values()),
        "backtest_only": sum((backtest_exact_counts - runtime_exact_counts).values()),
        "coverage_match_pct": 100.0 * exact_common / max(len(runtime_rows), len(backtest_rows)),
        "runtime_only_examples": runtime_exact_only[:25],
        "backtest_only_examples": backtest_exact_only[:25],
        "notes": [
            "Diagnostic only; does not alter geometry or execution semantics.",
            "Level 1 is strict identity including SL; Level 2 isolates signal identity by ignoring SL.",
            "Level 3 compares runtime rows only against completed backtest trade rows; signal-ledger rows are excluded from outcome comparison.",
            "Signal-ledger reconciliation is reported separately from completed-trade reconciliation.",
            "A JSON summary without trade-level records cannot support trade-level reconciliation.",
        ],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = args.output_dir / f"SP2L_EXACT_WINDOW_RECON_{stamp}.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(result, indent=2))
    print(f"RECON_JSON={output}")


if __name__ == "__main__":
    main()
