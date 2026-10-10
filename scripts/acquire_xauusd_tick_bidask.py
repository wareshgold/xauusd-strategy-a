from __future__ import annotations

"""Acquire immutable research-only MT5 ticks with Bid/Ask and SHA-256 provenance.

This utility does not place orders, modify the forward runner, or infer strategy
rules. It writes a raw compressed tick stream plus a sidecar manifest. Run only
against the intended demo terminal; the script never needs trading permissions.
"""

import argparse
import csv
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Iterable, Sequence

UTC = timezone.utc
CSV_FIELDS = ("time_msc", "time_utc", "bid", "ask", "last", "volume", "flags")


def parse_utc(value: str) -> datetime:
    """Parse an ISO-8601 timestamp and require an explicit timezone."""
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise argparse.ArgumentTypeError("timestamp must include timezone, e.g. 2026-08-21T00:00:00Z")
    return parsed.astimezone(UTC)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _float(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return number if number == number and abs(number) != float("inf") else 0.0


def _tick_row(tick: object) -> tuple[int, str, float, float, float, float, int]:
    time_msc = int(tick["time_msc"])
    timestamp = datetime.fromtimestamp(time_msc / 1000, UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    return (
        time_msc,
        timestamp,
        _float(tick["bid"]),
        _float(tick["ask"]),
        _float(tick["last"]),
        _float(tick["volume"]),
        int(tick["flags"]),
    )


def acquire(
    *,
    start: datetime,
    end: datetime,
    symbol: str,
    output: Path,
    terminal_path: str | None = None,
) -> dict[str, object]:
    """Acquire [start, end) in daily chunks. Requires MetaTrader5 installed."""
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("start/end must be timezone-aware")
    start = start.astimezone(UTC)
    end = end.astimezone(UTC)
    if start >= end:
        raise ValueError("start must be earlier than end")
    if not symbol.strip():
        raise ValueError("symbol is required")
    if output.suffix.lower() != ".gz":
        raise ValueError("output must end in .csv.gz to make the artifact compact and deterministic")

    try:
        import MetaTrader5 as mt5
    except ImportError as exc:
        raise RuntimeError("MetaTrader5 package is missing from the selected Python environment") from exc

    init_kwargs = {"path": terminal_path} if terminal_path else {}
    if not mt5.initialize(**init_kwargs):
        raise RuntimeError(f"MetaTrader5 initialize failed: {mt5.last_error()}")
    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        if terminal is None:
            raise RuntimeError(f"terminal_info failed: {mt5.last_error()}")
        if not mt5.symbol_select(symbol, True):
            raise RuntimeError(f"symbol_select({symbol!r}) failed: {mt5.last_error()}")
        spec = mt5.symbol_info(symbol)
        if spec is None:
            raise RuntimeError(f"symbol_info({symbol!r}) failed: {mt5.last_error()}")

        output.parent.mkdir(parents=True, exist_ok=True)
        temp_path = output.with_name(output.name + ".partial")
        tick_count = 0
        valid_quote_count = 0
        crossed_quote_count = 0
        missing_quote_count = 0
        first_tick_utc = None
        last_tick_utc = None
        previous_time_msc = None
        duplicate_or_out_of_order_count = 0
        min_spread = None
        max_spread = None
        spread_sum = 0.0
        spread_count = 0

        # gzip mtime=0 makes identical CSV bytes compress deterministically.
        with temp_path.open("wb") as raw:
            with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed:
                import io
                text = io.TextIOWrapper(compressed, encoding="utf-8", newline="", write_through=True)
                writer = csv.writer(text, lineterminator="\n")
                writer.writerow(CSV_FIELDS)
                cursor = start
                while cursor < end:
                    chunk_end = min(cursor + timedelta(days=1), end)
                    # copy_ticks_range's endpoints are inclusive; subtract 1 ms
                    # so adjacent half-open chunks do not intentionally overlap.
                    query_end = chunk_end - timedelta(milliseconds=1)
                    ticks = mt5.copy_ticks_range(
                        symbol, cursor, query_end, mt5.COPY_TICKS_ALL
                    )
                    if ticks is None:
                        raise RuntimeError(
                            f"copy_ticks_range failed for [{cursor.isoformat()}, "
                            f"{chunk_end.isoformat()}): {mt5.last_error()}"
                        )
                    for tick in ticks:
                        row = _tick_row(tick)
                        time_msc, time_text, bid, ask, last, volume, flags = row
                        if time_msc < int(start.timestamp() * 1000) or time_msc >= int(end.timestamp() * 1000):
                            continue
                        if previous_time_msc is not None and time_msc < previous_time_msc:
                            duplicate_or_out_of_order_count += 1
                        if previous_time_msc == time_msc:
                            duplicate_or_out_of_order_count += 1
                        previous_time_msc = time_msc
                        writer.writerow(row)
                        tick_count += 1
                        first_tick_utc = first_tick_utc or time_text
                        last_tick_utc = time_text
                        if bid > 0 and ask > 0:
                            if ask < bid:
                                crossed_quote_count += 1
                            else:
                                valid_quote_count += 1
                                spread = ask - bid
                                min_spread = spread if min_spread is None else min(min_spread, spread)
                                max_spread = spread if max_spread is None else max(max_spread, spread)
                                spread_sum += spread
                                spread_count += 1
                        else:
                            missing_quote_count += 1
                    cursor = chunk_end
                text.flush()
                text.detach()
        temp_path.replace(output)
        digest = sha256_file(output)
        manifest = {
            "schema_version": 1,
            "dataset_id": f"{symbol.lower().replace('.', '-')}-tick-bidask-{start:%Y%m%d}-{end:%Y%m%d}",
            "purpose": "RESEARCH_ONLY_OFFLINE_STRATEGY_COMPARISON",
            "status": "ACQUIRED" if tick_count and valid_quote_count else "BLOCKED_NO_VALID_QUOTES",
            "provider": "MetaTrader5 terminal API",
            "terminal_name": getattr(terminal, "name", None),
            "terminal_company": getattr(terminal, "company", None),
            "terminal_build": getattr(terminal, "build", None),
            "server": getattr(account, "server", None) if account is not None else None,
            "symbol": symbol,
            "timeframe": "TICK_ALL",
            "quote_fields": ["bid", "ask"],
            "interval_utc": {"start_inclusive": start.isoformat(), "end_exclusive": end.isoformat()},
            "retrieved_at_utc": datetime.now(UTC).isoformat(),
            "tick_count": tick_count,
            "valid_non_crossed_bidask_tick_count": valid_quote_count,
            "missing_bid_or_ask_count": missing_quote_count,
            "crossed_quote_count": crossed_quote_count,
            "duplicate_or_out_of_order_timestamp_count": duplicate_or_out_of_order_count,
            "first_tick_utc": first_tick_utc,
            "last_tick_utc": last_tick_utc,
            "spread_price_min": min_spread,
            "spread_price_max": max_spread,
            "spread_price_mean": spread_sum / spread_count if spread_count else None,
            "artifact": output.name,
            "artifact_size_bytes": output.stat().st_size,
            "artifact_sha256": digest,
            "compressed_csv_columns": list(CSV_FIELDS),
            "tick_flags_note": "MT5 TICK_FLAG_* bit field retained; zero Bid/Ask rows are preserved, not silently dropped.",
            "quality_gate": {
                "has_ticks": tick_count > 0,
                "has_valid_bidask": valid_quote_count > 0,
                "no_crossed_quotes": crossed_quote_count == 0,
                "ordered_unique_millisecond_timestamps": duplicate_or_out_of_order_count == 0,
                "note": "Duplicate timestamps may occur in valid MT5 feeds; any nonzero count requires explicit review, not automatic rejection."
            },
            "trading_actions_taken": False,
            "forward_runner_touched": False,
            "account_login_recorded": False
        }
        manifest_path = output.with_suffix("").with_suffix(".manifest.json")
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return manifest
    finally:
        mt5.shutdown()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True, help="UTC/offset-aware ISO timestamp, inclusive")
    parser.add_argument("--end", required=True, help="UTC/offset-aware ISO timestamp, exclusive")
    parser.add_argument("--symbol", default="XAUUSD.ecn")
    parser.add_argument("--terminal-path", default=os.environ.get("MT5_TERMINAL_PATH"))
    parser.add_argument("--output", required=True, help="Output path ending .csv.gz")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        start = parse_utc(args.start)
        end = parse_utc(args.end)
        manifest = acquire(
            start=start, end=end, symbol=args.symbol,
            output=Path(args.output), terminal_path=args.terminal_path,
        )
    except Exception as exc:
        print(f"ACQUISITION_FAILED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if manifest["status"] == "ACQUIRED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
