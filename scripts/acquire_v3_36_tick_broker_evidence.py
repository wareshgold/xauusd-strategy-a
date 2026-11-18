from __future__ import annotations

"""Read-only MT5 evidence acquisition for the 36 SP2L V3 positions.

Exports COPY_TICKS_ALL plus broker history orders/deals for XAUUSD.ecn.
It refuses to continue unless the connected terminal reports the historical
runner account/server. It never sends, modifies, or closes trading orders.
"""

import argparse
import csv
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys

UTC = timezone.utc
FIELDS = ("time_msc", "time_utc", "bid", "ask", "last", "volume", "volume_real", "flags")


def parse_utc(value: str) -> datetime:
    value = value.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("timestamp must include timezone")
    return dt.astimezone(UTC)


def json_safe(value):
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat() if value.tzinfo else value.replace(tzinfo=UTC).isoformat()
    if hasattr(value, "_asdict"):
        return {k: json_safe(v) for k, v in value._asdict().items()}
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if hasattr(value, "item"):
        return value.item()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--start", required=True, help="UTC ISO timestamp, inclusive")
    p.add_argument("--end", required=True, help="UTC ISO timestamp, exclusive")
    p.add_argument("--symbol", default="XAUUSD.ecn")
    p.add_argument("--terminal-path", required=True)
    p.add_argument("--expected-login", type=int, default=812930)
    p.add_argument("--expected-server", default="OtetGroup-MT5")
    p.add_argument("--output-dir", required=True)
    args = p.parse_args()

    try:
        start, end = parse_utc(args.start), parse_utc(args.end)
        if start >= end:
            raise ValueError("--start must be earlier than --end")
        if not Path(args.terminal_path).is_file():
            raise FileNotFoundError(f"MT5 terminal not found: {args.terminal_path}")

        import MetaTrader5 as mt5
        if not mt5.initialize(path=args.terminal_path):
            raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

        try:
            terminal = mt5.terminal_info()
            account = mt5.account_info()
            if terminal is None or account is None:
                raise RuntimeError(f"terminal/account info unavailable: {mt5.last_error()}")

            actual_login = int(account.login)
            actual_server = str(account.server)
            if actual_login != args.expected_login or actual_server != args.expected_server:
                raise RuntimeError(
                    "WRONG_TERMINAL_REFUSED: "
                    f"expected login={args.expected_login} server={args.expected_server}; "
                    f"connected login={actual_login} server={actual_server}. "
                    "No market/history files were written."
                )

            spec = mt5.symbol_info(args.symbol)
            if spec is None:
                raise RuntimeError(f"symbol_info({args.symbol}) failed: {mt5.last_error()}")

            out = Path(args.output_dir)
            out.mkdir(parents=True, exist_ok=True)
            ticks_path = out / "XAUUSD_ECN_TICKS_20261001_20261006.csv.gz"
            orders_path = out / "MT5_HISTORY_ORDERS_20261001_20261006.json"
            deals_path = out / "MT5_HISTORY_DEALS_20261001_20261006.json"

            tick_count = valid_quotes = missing_quotes = crossed_quotes = 0
            out_of_order = duplicate_msc = 0
            first_tick = last_tick = None
            previous_msc = None
            daily_counts = {}

            # mtime=0 makes the compressed raw tick artifact reproducible.
            with ticks_path.open("wb") as raw:
                with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as gz:
                    import io
                    text = io.TextIOWrapper(gz, encoding="utf-8", newline="", write_through=True)
                    writer = csv.writer(text, lineterminator="\n")
                    writer.writerow(FIELDS)
                    cursor = start
                    while cursor < end:
                        chunk_end = min(cursor + timedelta(days=1), end)
                        raw_ticks = mt5.copy_ticks_range(
                            args.symbol, cursor, chunk_end - timedelta(milliseconds=1),
                            mt5.COPY_TICKS_ALL
                        )
                        if raw_ticks is None:
                            raise RuntimeError(
                                f"copy_ticks_range failed [{cursor.isoformat()}, "
                                f"{chunk_end.isoformat()}): {mt5.last_error()}"
                            )
                        for t in raw_ticks:
                            msc = int(t["time_msc"])
                            if msc < int(start.timestamp() * 1000) or msc >= int(end.timestamp() * 1000):
                                continue
                            ts = datetime.fromtimestamp(msc / 1000, UTC)
                            ts_text = ts.isoformat(timespec="milliseconds").replace("+00:00", "Z")
                            bid, ask = float(t["bid"]), float(t["ask"])
                            last, volume = float(t["last"]), float(t["volume"])
                            volume_real = float(t["volume_real"]) if "volume_real" in t.dtype.names else 0.0
                            flags = int(t["flags"])
                            writer.writerow((msc, ts_text, bid, ask, last, volume, volume_real, flags))
                            tick_count += 1
                            day = ts.strftime("%Y-%m-%d")
                            daily_counts[day] = daily_counts.get(day, 0) + 1
                            first_tick = first_tick or ts_text
                            last_tick = ts_text
                            if previous_msc is not None:
                                if msc < previous_msc:
                                    out_of_order += 1
                                elif msc == previous_msc:
                                    duplicate_msc += 1
                            previous_msc = msc
                            if bid <= 0 or ask <= 0:
                                missing_quotes += 1
                            elif ask < bid:
                                crossed_quotes += 1
                            else:
                                valid_quotes += 1
                        cursor = chunk_end
                    text.flush()
                    text.detach()

            orders = mt5.history_orders_get(start, end)
            if orders is None:
                raise RuntimeError(f"history_orders_get failed: {mt5.last_error()}")
            deals = mt5.history_deals_get(start, end)
            if deals is None:
                raise RuntimeError(f"history_deals_get failed: {mt5.last_error()}")

            order_rows = [
                json_safe(x) for x in orders
                if str(getattr(x, "symbol", "")) == args.symbol
            ]
            deal_rows = [
                json_safe(x) for x in deals
                if str(getattr(x, "symbol", "")) == args.symbol
            ]
            orders_path.write_text(json.dumps(order_rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            deals_path.write_text(json.dumps(deal_rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

            manifest = {
                "schema_version": 1,
                "status": "ACQUIRED" if tick_count and valid_quotes else "BLOCKED_NO_VALID_TICKS",
                "purpose": "READ_ONLY_36_POSITION_INTRABAR_FORENSICS",
                "symbol": args.symbol,
                "account_login": actual_login,
                "account_server": actual_server,
                "terminal_name": getattr(terminal, "name", None),
                "terminal_company": getattr(terminal, "company", None),
                "terminal_build": getattr(terminal, "build", None),
                "interval_utc": {"start_inclusive": start.isoformat(), "end_exclusive": end.isoformat()},
                "retrieved_at_utc": datetime.now(UTC).isoformat(),
                "tick_source": "MetaTrader5.copy_ticks_range(COPY_TICKS_ALL)",
                "tick_fields": list(FIELDS),
                "tick_count": tick_count,
                "valid_non_crossed_bidask_count": valid_quotes,
                "missing_bid_or_ask_count": missing_quotes,
                "crossed_bid_ask_count": crossed_quotes,
                "out_of_order_millisecond_count": out_of_order,
                "duplicate_millisecond_count": duplicate_msc,
                "first_tick_utc": first_tick,
                "last_tick_utc": last_tick,
                "daily_tick_counts": daily_counts,
                "history_orders_count_symbol": len(order_rows),
                "history_deals_count_symbol": len(deal_rows),
                "history_orders_query": "OK_EMPTY" if not order_rows else "OK_NONEMPTY",
                "history_deals_query": "OK_EMPTY" if not deal_rows else "OK_NONEMPTY",
                "symbol_info_snapshot_utc": datetime.now(UTC).isoformat(),
                "symbol_info_snapshot_only_not_historical": {
                    "digits": int(spec.digits),
                    "point": float(spec.point),
                    "trade_tick_size": float(spec.trade_tick_size),
                    "trade_stops_level_points": int(spec.trade_stops_level),
                    "trade_freeze_level_points": int(spec.trade_freeze_level),
                },
                "artifacts": {
                    ticks_path.name: {"bytes": ticks_path.stat().st_size, "sha256": sha256(ticks_path)},
                    orders_path.name: {"bytes": orders_path.stat().st_size, "sha256": sha256(orders_path)},
                    deals_path.name: {"bytes": deals_path.stat().st_size, "sha256": sha256(deals_path)},
                },
                "limitations": [
                    "History orders/deals are terminal broker-history records; they do not guarantee historical SLTP request/response acknowledgements were retained.",
                    "Current symbol stops/freeze levels are a present-time snapshot, not historical values for October 2026.",
                    "Tick order constrains observed quote chronology but does not independently define canonical fill semantics.",
                    "No tick interpolation, OHLC path inference, P/L, parameter ranking, or strategy decision is performed.",
                ],
                "trading_actions_taken": False,
                "forward_runner_touched": False,
            }
            manifest_path = out / "MT5_EVIDENCE_MANIFEST_20261001_20261006.json"
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

            print(json.dumps({
                "STATUS": manifest["status"],
                "ACCOUNT": f"{actual_login}@{actual_server}",
                "SYMBOL": args.symbol,
                "TICKS": tick_count,
                "VALID_BIDASK": valid_quotes,
                "ORDERS": len(order_rows),
                "DEALS": len(deal_rows),
                "MANIFEST": str(manifest_path),
                "MANIFEST_SHA256": sha256(manifest_path),
                "TRADING_ACTIONS": False,
            }, indent=2))
            return 0 if manifest["status"] == "ACQUIRED" else 3
        finally:
            mt5.shutdown()
    except Exception as exc:
        print(f"ACQUISITION_FAILED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
