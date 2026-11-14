"""Research-only MT5 export for the XAUUSD MA-filter study.

Run locally on the Factory PC against the intended MT5 terminal.
This script never places, modifies, or closes orders.
All requested timestamps are UTC; MT5 rates/deal history are exported as returned.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import MetaTrader5 as mt5
except ImportError as exc:
    raise SystemExit("MetaTrader5 package is required in the selected Python environment") from exc


DEAL_FIELDS = (
    "ticket", "order", "time", "time_msc", "type", "entry", "magic",
    "position_id", "reason", "volume", "price", "commission", "swap",
    "profit", "fee", "symbol", "comment", "external_id",
)
RATE_FIELDS = ("time", "open", "high", "low", "close", "tick_volume", "spread", "real_volume")


def parse_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise argparse.ArgumentTypeError("Timestamp must include timezone, preferably Z (UTC)")
    return dt.astimezone(timezone.utc)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_records(path: Path, records, fields: tuple[str, ...]) -> int:
    count = 0
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        for record in records:
            row = record._asdict() if hasattr(record, "_asdict") else dict(record)
            writer.writerow({k: row.get(k, "") for k in fields})
            count += 1
    return count


def main() -> int:
    p = argparse.ArgumentParser(description="Export MT5 XAUUSD deals and M1 candles; research only.")
    p.add_argument("--terminal", required=True, help="Exact terminal64.exe path for the intended MT5 instance")
    p.add_argument("--symbol", default="XAUUSD.ecn")
    p.add_argument("--magic", type=int, default=26092301)
    p.add_argument("--start-utc", required=True, type=parse_utc, help="Inclusive ISO timestamp, e.g. 2026-11-09T00:00:00Z")
    p.add_argument("--end-utc", required=True, type=parse_utc, help="Exclusive ISO timestamp, e.g. 2026-11-14T00:00:00Z")
    p.add_argument("--expected-login", type=int, required=True, help="Safety check: expected account login")
    p.add_argument("--expected-server", required=True, help="Safety check: expected broker server name")
    p.add_argument("--out", default="artifacts/ma_filter_week_20261109")
    args = p.parse_args()

    terminal = Path(args.terminal).expanduser().resolve()
    if not terminal.is_file():
        raise SystemExit(f"Terminal executable not found: {terminal}")
    if args.end_utc <= args.start_utc:
        raise SystemExit("--end-utc must be later than --start-utc")

    initialized = mt5.initialize(path=str(terminal))
    if not initialized:
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        ti = mt5.terminal_info()
        ai = mt5.account_info()
        if ti is None or ai is None:
            raise SystemExit(f"MT5 terminal/account info unavailable: {mt5.last_error()}")
        actual_path = str(getattr(ti, "path", ""))
        if actual_path and Path(actual_path).resolve() != terminal.parent:
            raise SystemExit(f"Connected terminal path mismatch: {actual_path}")
        if int(ai.login) != args.expected_login:
            raise SystemExit(f"Account login mismatch: expected {args.expected_login}, got {ai.login}")
        if str(ai.server) != args.expected_server:
            raise SystemExit(f"Account server mismatch: expected {args.expected_server}, got {ai.server}")

        symbol_info = mt5.symbol_info(args.symbol)
        if symbol_info is None:
            raise SystemExit(f"Symbol not found in this terminal: {args.symbol}")
        if not symbol_info.visible and not mt5.symbol_select(args.symbol, True):
            raise SystemExit(f"Could not select symbol {args.symbol}: {mt5.last_error()}")

        deals = mt5.history_deals_get(args.start_utc, args.end_utc)
        if deals is None:
            raise SystemExit(f"history_deals_get failed: {mt5.last_error()}")
        selected_deals = [
            d for d in deals
            if str(d.symbol) == args.symbol and int(d.magic) == args.magic
        ]
        rates = mt5.copy_rates_range(args.symbol, mt5.TIMEFRAME_M1, args.start_utc, args.end_utc)
        if rates is None:
            raise SystemExit(f"copy_rates_range failed: {mt5.last_error()}")

        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        deals_path = out / "runner_deals.csv"
        rates_path = out / "xauusd_m1.csv"
        deal_count = write_records(deals_path, selected_deals, DEAL_FIELDS)
        rate_count = write_records(rates_path, rates, RATE_FIELDS)

        manifest = {
            "research_only": True,
            "canonical_rules_changed": False,
            "mt5_trade_actions": False,
            "terminal_executable": str(terminal),
            "terminal_path_reported": actual_path,
            "account_login": int(ai.login),
            "account_server": str(ai.server),
            "account_currency": str(ai.currency),
            "symbol": args.symbol,
            "magic": args.magic,
            "start_utc": args.start_utc.isoformat(),
            "end_utc_exclusive": args.end_utc.isoformat(),
            "deals_exported": deal_count,
            "m1_bars_exported": rate_count,
            "deals_sha256": sha256(deals_path),
            "m1_sha256": sha256(rates_path),
            "python": sys.version,
            "mt5_package_version": getattr(mt5, "__version__", "unknown"),
        }
        manifest_path = out / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(json.dumps(manifest, indent=2))
        print(f"OUTPUT_DIR={out.resolve()}")
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
