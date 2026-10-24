#!/usr/bin/env python3
"""Read-only accounting/overlap diagnostic for author-replica replay JSON.

This is a diagnostic only. It does not re-run signals, connect to MT5, infer
missing exits, or establish executable fills/profitability.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


VALID_OUTCOMES = {"WIN", "LOSS", "AMBIGUOUS"}


def close_enough(left: Any, right: float) -> bool:
    return isinstance(left, (int, float)) and math.isclose(
        float(left), right, rel_tol=1e-9, abs_tol=1e-9
    )


def audit(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Top-level JSON value must be an object.")

    signals = data.get("signals")
    trades = data.get("trades")
    signals = signals if isinstance(signals, list) else []
    trades = trades if isinstance(trades, list) else []
    config = data.get("config") if isinstance(data.get("config"), dict) else {}
    tp_r = config.get("tpR")
    warnings: list[str] = []

    outcomes: dict[str, int] = {name: 0 for name in VALID_OUTCOMES}
    malformed_trade_indexes: list[int] = []
    for idx, trade in enumerate(trades):
        if not isinstance(trade, dict) or trade.get("outcome") not in VALID_OUTCOMES:
            malformed_trade_indexes.append(idx)
            continue
        outcomes[trade["outcome"]] += 1

    if malformed_trade_indexes:
        warnings.append(
            f"{len(malformed_trade_indexes)} trade rows have missing/unknown outcomes."
        )

    signal_keys = []
    for signal in signals:
        if isinstance(signal, dict):
            signal_keys.append((
                signal.get("index"), signal.get("time"), signal.get("direction")
            ))
        else:
            signal_keys.append((None, None, None))

    trade_keys = []
    for trade in trades:
        if isinstance(trade, dict):
            trade_keys.append((
                trade.get("index"), trade.get("time"), trade.get("direction")
            ))
        else:
            trade_keys.append((None, None, None))

    signal_key_set = set(signal_keys)
    orphan_trade_count = sum(key not in signal_key_set for key in trade_keys)
    if orphan_trade_count:
        warnings.append(
            f"{orphan_trade_count} trade rows do not match a signal by (index, time, direction)."
        )

    closed_count = sum(outcomes.values())
    decisive = outcomes["WIN"] + outcomes["LOSS"]
    wins = outcomes["WIN"]
    losses = outcomes["LOSS"]
    ambiguous = outcomes["AMBIGUOUS"]
    unresolved_from_lists = max(0, len(signals) - closed_count)

    # Conditional model only: a WIN earns config.tpR and a LOSS loses 1R.
    # It does not account for price gaps, partial exits, costs, or execution.
    conditional_total_r = None
    conditional_pf = None
    if isinstance(tp_r, (int, float)) and not isinstance(tp_r, bool) and tp_r >= 0:
        conditional_total_r = wins * float(tp_r) - losses
        conditional_pf = (
            wins * float(tp_r) / losses if losses else (None if wins == 0 else "infinite")
        )
        if not close_enough(data.get("totalR"), conditional_total_r):
            warnings.append(
                "Reported totalR differs from conditional fixed-R accounting "
                "(wins × config.tpR − losses); inspect the original ledger and assumptions."
            )
        if losses and not close_enough(data.get("profit_factor"), conditional_pf):
            warnings.append(
                "Reported profit_factor differs from conditional fixed-R accounting "
                "(wins × config.tpR ÷ losses)."
            )
    else:
        warnings.append("config.tpR is missing or invalid; conditional R accounting unavailable.")

    if data.get("wins") != wins or data.get("losses") != losses or data.get("ambiguous") != ambiguous:
        warnings.append("Top-level outcome counts do not match outcomes counted from trade rows.")
    if data.get("signals_detected", len(signals)) != len(signals):
        warnings.append("signals_detected does not match the signals array length.")
    if data.get("trades_closed_or_ambiguous", len(trades)) != len(trades):
        warnings.append("trades_closed_or_ambiguous does not match the trades array length.")
    if data.get("open_or_unresolved", unresolved_from_lists) != unresolved_from_lists:
        warnings.append("open_or_unresolved does not match signals minus listed trade outcomes.")

    # The source output contains signal index and outcome but no exit candle index.
    # Therefore actual holding overlap cannot be established from this JSON alone.
    fill_assessment = {
        "status": "NOT_VERIFIABLE_FROM_ARTIFACT",
        "reason": "The replay JSON has no subsequent candle series, entry-fill event, or broker execution record.",
        "signals_with_entry_price": sum(
            isinstance(s, dict) and isinstance(s.get("entry"), (int, float))
            for s in signals
        ),
        "signals_with_explicit_fill_evidence": sum(
            isinstance(s, dict) and any(k in s for k in ("filled", "fill_time", "fill_price"))
            for s in signals
        ),
    }
    warnings.append(
        "Entry fills are not verified: an entry price plus a later SL/TP touch does not prove the entry was filled."
    )

    overlap_assessment = {
        "status": "NOT_DETERMINABLE_FROM_ARTIFACT",
        "reason": "Trade rows do not contain exit candle index/time or position lifecycle events.",
        "signals_sorted_by_index": all(
            isinstance(k[0], int) for k in signal_keys
        ) and all(
            signal_keys[i][0] <= signal_keys[i + 1][0]
            for i in range(len(signal_keys) - 1)
        ),
        "consecutive_signal_index_gaps": [
            signal_keys[i + 1][0] - signal_keys[i][0]
            for i in range(len(signal_keys) - 1)
            if isinstance(signal_keys[i][0], int) and isinstance(signal_keys[i + 1][0], int)
        ],
    }
    warnings.append(
        "Concurrent-position/holding overlap cannot be validated because exit indexes/timestamps are absent."
    )

    return {
        "research_only": True,
        "audit_version": 2,
        "input_path": str(path),
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "input_size_bytes": len(raw),
        "config": {"tpR": tp_r},
        "counts_from_trade_rows": {
            "signals": len(signals),
            "trade_rows": len(trades),
            "wins": wins,
            "losses": losses,
            "ambiguous": ambiguous,
            "malformed_outcomes": len(malformed_trade_indexes),
            "orphan_trade_rows": orphan_trade_count,
            "unresolved_signal_count_derived": unresolved_from_lists,
            "decisive_win_rate": wins / decisive if decisive else None,
        },
        "reported_metrics": {
            "wins": data.get("wins"),
            "losses": data.get("losses"),
            "ambiguous": data.get("ambiguous"),
            "open_or_unresolved": data.get("open_or_unresolved"),
            "totalR": data.get("totalR"),
            "profit_factor": data.get("profit_factor"),
        },
        "conditional_fixed_R_accounting": {
            "assumption": "each WIN = config.tpR; each LOSS = -1R; AMBIGUOUS excluded",
            "totalR": conditional_total_r,
            "profit_factor": conditional_pf,
            "warning": "Conditional diagnostic only; not execution-aware P&L or validated profitability.",
        },
        "entry_fill_assessment": fill_assessment,
        "overlap_assessment": overlap_assessment,
        "warnings": warnings,
        "interpretation": (
            "Offline ledger-structure and arithmetic diagnostic only. Does not validate "
            "timestamp mapping, signal semantics, fills, source fidelity, costs, or profitability."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Existing replay JSON (read-only).")
    parser.add_argument(
        "--output", type=Path,
        help="Optional NEW output path; existing files are never overwritten.",
    )
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"Input file does not exist: {args.input}")
    report = audit(args.input)
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        if args.output.exists():
            parser.error(f"Refusing to overwrite existing output: {args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
