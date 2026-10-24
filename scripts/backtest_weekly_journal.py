"""Convert the canonical author-replica weekly backtest artifact into the
journal row schema consumed by the SP2L report engine, and validate it.

Reporting/infrastructure only:
- consumes the committed research-only author-replica MT5 M1 replay output
  (e.g. artifacts/SP2L_author_replica_2026-09-14_2026-09-18.json);
- does NOT re-implement, modify, or extend any SP2L strategy/geometry rule;
- does NOT generate trading signals and does NOT enable live trading.

Conversion rules (deterministic, documented):
- WIN/LOSS -> trade status CLOSED with result WIN/LOSS and r_multiple = R.
- AMBIGUOUS (e.g. SL_AND_TP_SAME_BAR, exit price unknown) -> status CLOSED
  with result None and r_multiple None; the report engine classifies it as
  AMBIGUOUS. Nothing is invented to resolve the outcome.
- pips require an explicitly supplied pip size (repository convention:
  never inferred); otherwise pips are None with basis NOT_CONFIGURED.
- holding time = exit bar time - signal time, in minutes (None if no exit).

Outputs:
- runtime journal directory (signals.jsonl + trades.jsonl) compatible with
  scripts/live_report_engine.load_journal, kept separate from the live
  journal;
- trade-journal artifact JSON with the full required field set;
- validation artifact JSON (Phase 3 checks).
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_TRADE_JOURNAL = "sp2l.weekly_backtest_trade_journal.v1"
SCHEMA_VALIDATION = "sp2l.weekly_backtest_validation.v1"

SOURCE_LABEL = "AUTHOR_REPLICA_MT5_M1_REPLAY_BACKTEST"


def _parse_ts(value: str) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def directional_pips(entry: float, exit_price: float, direction: str, pip_size: float) -> float:
    move = (exit_price - entry) if direction == "BUY" else (entry - exit_price)
    return move / pip_size


def convert_signal(row: dict[str, Any], signal_id: str, pip_size: float | None) -> tuple[dict, dict, dict]:
    """Source signal row -> (signal journal row, trade journal row, engine trade row)."""
    direction = str(row["direction"]).upper()
    entry = float(row["entry"])
    sl = float(row["sl"])
    tp = float(row["tp"])
    outcome = str(row.get("outcome", "")).upper() or "AMBIGUOUS"
    reason = row.get("reason")
    signal_time = _parse_ts(row["signal_time_utc"])

    exit_time_raw = row.get("exit_time_utc")
    exit_price_raw = row.get("exit_price")
    exit_time = _parse_ts(exit_time_raw) if exit_time_raw else None
    try:
        exit_price = float(exit_price_raw) if exit_price_raw not in (None, "") else None
    except (TypeError, ValueError):
        exit_price = None

    r_raw = row.get("R")
    r_multiple = float(r_raw) if r_raw is not None else None

    resolved = outcome in {"WIN", "LOSS"}
    result = outcome if resolved else None
    status = "CLOSED" if exit_time is not None else "OPEN"

    holding_minutes = (
        round((exit_time - signal_time).total_seconds() / 60.0, 2)
        if exit_time is not None else None
    )
    pips = (
        round(directional_pips(entry, exit_price, direction, pip_size), 2)
        if (exit_price is not None and pip_size is not None and pip_size > 0)
        else None
    )

    signal_row = {
        "signal_id": signal_id,
        "status": "APPROVED",
        "direction": direction,
        "symbol": str(row.get("symbol", "XAUUSD")),
        "source": SOURCE_LABEL,
        "timestamp_utc": _iso(signal_time),
        "recorded_at_utc": _iso(signal_time),
        "signal_entry": entry,
        "sl": sl,
        "tp": tp,
        "backtest_outcome": outcome,
        "backtest_reason": reason,
    }

    trade_row = {
        "signal_id": signal_id,
        "status": status,
        "direction": direction,
        "result": result,
        "r_multiple": r_multiple,
        "signal_entry": entry,
        "sl": sl,
        "tp": tp,
        "exit_time_utc": _iso(exit_time) if exit_time else None,
        "exit_price": exit_price,
        "pips": pips,
        "holding_minutes": holding_minutes,
        "backtest_outcome": outcome,
        "backtest_reason": reason,
        # Engine period filter chain: closed_at_utc first, recorded_at_utc last.
        "closed_at_utc": _iso(exit_time) if exit_time else None,
        "recorded_at_utc": _iso(exit_time) if exit_time else _iso(signal_time),
    }

    trade_journal_entry = {
        "signal_id": signal_id,
        "signal_timestamp_utc": _iso(signal_time),
        "direction": direction,
        "entry": entry,
        "stop_loss": sl,
        "take_profit": tp,
        "exit_time_utc": _iso(exit_time) if exit_time else None,
        "exit_price": exit_price,
        "result": outcome if resolved else "AMBIGUOUS",
        "pips": pips,
        "r_multiple": r_multiple,
        "holding_minutes": holding_minutes,
        "backtest_reason": reason,
    }
    return signal_row, trade_row, trade_journal_entry


def validate(signal_rows: list[dict], trade_rows: list[dict], source: dict) -> dict[str, Any]:
    """Phase 3 checks: duplicates, missing outcomes, engine schema compatibility."""
    ids = [r["signal_id"] for r in signal_rows]
    duplicate_ids = sorted({i for i in ids if ids.count(i) > 1})
    keys = [(r["timestamp_utc"], r["direction"], r["signal_entry"]) for r in signal_rows]
    duplicate_keys = sorted({k for k in keys if keys.count(k) > 1})

    missing_outcome = sum(1 for r in trade_rows if r["status"] == "CLOSED" and r["result"] not in {"WIN", "LOSS"})
    open_or_unresolved = sum(1 for r in trade_rows if r["status"] != "CLOSED")
    closed_missing_r = sum(1 for r in trade_rows if r["status"] == "CLOSED" and r["r_multiple"] is None)
    closed_missing_exit = sum(1 for r in trade_rows if r["status"] == "CLOSED" and r["exit_price"] is None)

    # Engine compatibility: every row must resolve a timestamp, and engine
    # classification over the converted rows must reproduce the source summary.
    try:
        from live_report_engine import classify_signals, record_timestamp_utc
    except ModuleNotFoundError:
        from scripts.live_report_engine import classify_signals, record_timestamp_utc

    timestamps_ok = all(record_timestamp_utc(r) is not None for r in signal_rows + trade_rows)
    engine_counts = classify_signals(signal_rows, trade_rows)

    summary = source.get("summary", {})
    net_r = sum(r["r_multiple"] for r in trade_rows if r["r_multiple"] is not None)
    wins = sum(1 for r in trade_rows if r["result"] == "WIN")
    losses = sum(1 for r in trade_rows if r["result"] == "LOSS")
    recomputed_pf = (wins / losses) if losses else None
    source_pf = summary.get("profit_factor")
    pf_match = recomputed_pf is not None and source_pf is not None and abs(recomputed_pf - float(source_pf)) < 1e-9

    consistency_ok = bool(
        timestamps_ok
        and not duplicate_ids
        and not duplicate_keys
        and engine_counts["win"] == wins == int(summary.get("wins", -1))
        and engine_counts["loss"] == losses == int(summary.get("losses", -1))
        and engine_counts["ambiguous"] == (len(trade_rows) - wins - losses) == int(summary.get("ambiguous", -1))
        and abs(net_r - float(summary.get("total_R", -1))) < 1e-9
        and pf_match
    )

    return {
        "schema": SCHEMA_VALIDATION,
        "source_artifact": source.get("_source_path"),
        "week_start_utc": source.get("week_start_utc"),
        "week_end_utc": source.get("week_end_utc"),
        "signal_count": len(signal_rows),
        "trade_count": len(trade_rows),
        "win": wins,
        "loss": losses,
        "ambiguous": engine_counts["ambiguous"],
        "missing_outcome": missing_outcome,
        "open_or_unresolved": open_or_unresolved,
        "duplicate_signal_ids": duplicate_ids,
        "duplicate_time_direction_entry": duplicate_keys,
        "closed_missing_r": closed_missing_r,
        "closed_missing_exit_price": closed_missing_exit,
        "unparsable_timestamp_rows": 0 if timestamps_ok else -1,
        "engine_signal_counts": engine_counts,
        "recomputed_net_r": round(net_r, 6),
        "recomputed_profit_factor": round(recomputed_pf, 6) if recomputed_pf is not None else None,
        "source_summary": summary,
        "consistency_ok": consistency_ok,
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert weekly author-replica backtest artifact into report-engine journal rows.")
    parser.add_argument("--source", default="artifacts/SP2L_author_replica_2026-09-14_2026-09-18.json")
    parser.add_argument("--journal-dir", default="runtime/journal_backtest")
    parser.add_argument("--trade-journal-out", default=None, help="write the trade-journal artifact JSON here")
    parser.add_argument("--validation-out", default=None, help="write the validation artifact JSON here")
    parser.add_argument("--pip-size", type=float, default=None, help="explicit XAUUSD pip size in price units (never inferred)")
    args = parser.parse_args(argv)

    source_path = Path(args.source)
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source["_source_path"] = str(source_path).replace("\\", "/")

    pip_size = args.pip_size
    if pip_size is not None and pip_size <= 0:
        raise SystemExit("pip size must be > 0 when supplied")

    signals_in = sorted(source["signals"], key=lambda r: (r["signal_time_utc"], r["direction"], r["entry"]))
    week_start = str(source.get("week_start_utc", ""))[:10].replace("-", "")
    if not week_start:
        week_start = _parse_ts(signals_in[0]["signal_time_utc"]).strftime("%Y%m%d")

    signal_rows: list[dict] = []
    trade_rows: list[dict] = []
    trade_journal_entries: list[dict] = []
    for i, row in enumerate(signals_in, start=1):
        signal_id = f"BT-{week_start}-{i:03d}"
        s_row, t_row, entry = convert_signal(row, signal_id, pip_size)
        signal_rows.append(s_row)
        trade_rows.append(t_row)
        trade_journal_entries.append(entry)

    journal_dir = Path(args.journal_dir)
    write_jsonl(journal_dir / "signals.jsonl", signal_rows)
    write_jsonl(journal_dir / "trades.jsonl", trade_rows)

    validation = validate(signal_rows, trade_rows, source)

    trade_journal = {
        "schema": SCHEMA_TRADE_JOURNAL,
        "source_artifact": source["_source_path"],
        "week_start_utc": source.get("week_start_utc"),
        "week_end_utc": source.get("week_end_utc"),
        "pip_size": pip_size,
        "pips_basis": "EXPLICIT_PIP_SIZE" if pip_size else "NOT_CONFIGURED",
        "signal_count": len(trade_journal_entries),
        "trades": trade_journal_entries,
    }

    if args.trade_journal_out:
        out = Path(args.trade_journal_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(trade_journal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.validation_out:
        out = Path(args.validation_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "journal_dir": str(journal_dir).replace("\\", "/"),
        "signals": len(signal_rows),
        "trades": len(trade_rows),
        "win": validation["win"],
        "loss": validation["loss"],
        "ambiguous": validation["ambiguous"],
        "recomputed_net_r": validation["recomputed_net_r"],
        "recomputed_profit_factor": validation["recomputed_profit_factor"],
        "consistency_ok": validation["consistency_ok"],
    }, indent=2, sort_keys=True))
    return 0 if validation["consistency_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
