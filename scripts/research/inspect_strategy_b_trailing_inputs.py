#!/usr/bin/env python3
"""Read-only discovery audit for Strategy B trailing-matrix input files.

Scans a chosen repository/artifacts tree for CSVs that resemble M1 OHLC candles
or Strategy B candidate/trade ledgers. It does not modify files, launch MT5,
connect to a broker, or upload any data. It reports exact paths, SHA-256,
columns, row counts, timestamp ranges, and a small header-only schema preview.

Example:
  python scripts/research/inspect_strategy_b_trailing_inputs.py --root artifacts

Copy the report back for building a schema-aligned replay adapter. Do not infer
entry fills from an OHLC candle if the source artifact marks them unresolved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    raise SystemExit("Missing dependency: pandas. Install with: python -m pip install pandas")


OHLC_SETS = [
    {"timestamp", "open", "high", "low", "close"},
    {"time", "open", "high", "low", "close"},
    {"datetime", "open", "high", "low", "close"},
]
ENTRY_HINTS = {
    "entry_time", "signal_time", "candidate_time", "time", "timestamp",
    "side", "direction", "signal", "entry_price", "entry", "sl_price",
    "stop_loss", "initial_sl", "tp_price", "take_profit",
}
BLOCKING_HINTS = {
    "unresolved_market_fill_not_in_m1_ohlc", "fill_status", "execution_status",
    "entry_fill_status", "market_fill_status", "ambiguous", "unresolved",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_columns(path: Path):
    try:
        header = pd.read_csv(path, nrows=0)
        return {str(c).strip().lower(): str(c) for c in header.columns}
    except Exception:
        return {}


def inspect_csv(path: Path, root: Path):
    columns = normalized_columns(path)
    keys = set(columns)
    is_ohlc = any(required.issubset(keys) for required in OHLC_SETS)
    hint_score = len(keys & ENTRY_HINTS)
    block_columns = sorted(keys & BLOCKING_HINTS)
    if not is_ohlc and hint_score < 2:
        return None
    result = {
        "path": str(path.resolve()),
        "relative_path": str(path.resolve().relative_to(root.resolve())) if path.resolve().is_relative_to(root.resolve()) else str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "kind_guess": "OHLC_CANDIDATE" if is_ohlc else ("ENTRY_OR_TRADE_CANDIDATE" if hint_score >= 2 else "UNKNOWN"),
        "columns": list(columns.values()),
        "blocking_or_uncertainty_columns": block_columns,
    }
    try:
        frame = pd.read_csv(path)
        result["rows"] = int(len(frame))
        lower = {str(c).strip().lower(): c for c in frame.columns}
        ts_col = next((lower[k] for k in ("timestamp", "time", "datetime", "entry_time", "signal_time", "candidate_time", "open_time") if k in lower), None)
        if ts_col is not None:
            ts = pd.to_datetime(frame[ts_col], utc=True, errors="coerce").dropna()
            if not ts.empty:
                result["time_column"] = str(ts_col)
                result["first_time_utc"] = ts.min().isoformat()
                result["last_time_utc"] = ts.max().isoformat()
        if not is_ohlc:
            # Header/schema only: no trade prices or personal data printed.
            result["sample_values"] = {
                str(c): [None if pd.isna(v) else str(v)[:80] for v in frame[c].head(2).tolist()]
                for c in frame.columns[:min(12, len(frame.columns))]
            }
    except Exception as exc:
        result["read_error"] = f"{type(exc).__name__}: {exc}"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path("artifacts"), help="Search root (default: artifacts)")
    parser.add_argument("--out", type=Path, default=None, help="Optional report path; must not already exist")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Search root does not exist or is not a directory: {root}")
    if args.out is not None and args.out.exists():
        raise SystemExit(f"Refusing to overwrite existing report: {args.out}")

    results = []
    for path in sorted(root.rglob("*.csv")):
        try:
            item = inspect_csv(path, root)
            if item is not None:
                results.append(item)
        except (OSError, ValueError) as exc:
            results.append({"path": str(path.resolve()), "read_error": f"{type(exc).__name__}: {exc}"})

    results.sort(key=lambda x: (
        0 if x.get("kind_guess") == "OHLC_CANDIDATE" else 1,
        0 if any(k in x.get("relative_path", "").lower() for k in ("strategy_b", "candidate", "monthly", "signal")) else 1,
        x.get("relative_path", ""),
    ))
    report = {
        "mode": "read_only_local_input_discovery",
        "root": str(root),
        "csv_candidates_found": len(results),
        "results": results,
        "next_step": "Choose the exact 1-month OHLC file and source-aligned Strategy B candidate artifact. Confirm unresolved market-fill semantics before replay."
    }
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
        print(f"Report saved: {args.out.resolve()}")
    print(rendered)


if __name__ == "__main__":
    main()
