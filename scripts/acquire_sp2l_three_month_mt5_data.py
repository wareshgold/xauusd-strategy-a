#!/usr/bin/env python3
"""Read-only MT5 historical export for SP2L three-month management research.

Exports raw Tick ALL (Bid/Ask) and M1 data in daily half-open UTC chunks.
No symbol selection, order, position, SL/TP, runner, dashboard, or terminal
configuration changes are performed. Existing terminal must already expose the
requested symbol to the MT5 Python API; otherwise the script fails closed.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import sys
from typing import Any, Iterable, Sequence

UTC = timezone.utc
TICK_FIELDS = ("time_msc", "time_utc", "bid", "ask", "last", "volume", "flags")
M1_FIELDS = (
    "time", "time_utc", "open", "high", "low", "close",
    "tick_volume", "spread_points", "real_volume",
)


def parse_utc(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include UTC offset, e.g. 2026-08-09T00:00:00Z")
    return parsed.astimezone(UTC)


def iso_utc(value: datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def finite_float(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if number != number or abs(number) == float("inf"):
        return 0.0
    return number


def value(record: Any, key: str) -> Any:
    """Read a named field from an MT5 namedtuple/structured record."""
    try:
        return record[key]
    except (KeyError, TypeError, IndexError):
        return getattr(record, key)


def write_gzip_csv(path: Path, fields: Sequence[str], rows: Iterable[Sequence[Any]]) -> int:
    """Write deterministic gzip bytes; return the number of data rows."""
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    count = 0
    with partial.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as zipped:
            text = io.TextIOWrapper(zipped, encoding="utf-8", newline="")
            writer = csv.writer(text, lineterminator="\\n")
            writer.writerow(fields)
            for row in rows:
                writer.writerow(row)
                count += 1
            text.flush()
            text.detach()
    partial.replace(path)
    return count


def tick_row(tick: Any) -> tuple[Any, ...]:
    ms = int(value(tick, "time_msc"))
    stamp = datetime.fromtimestamp(ms / 1000, UTC).isoformat(
        timespec="milliseconds"
    ).replace("+00:00", "Z")
    return (
        ms, stamp, repr(finite_float(value(tick, "bid"))),
        repr(finite_float(value(tick, "ask"))),
        repr(finite_float(value(tick, "last"))),
        repr(finite_float(value(tick, "volume"))),
        int(value(tick, "flags")),
    )


def m1_row(bar: Any) -> tuple[Any, ...]:
    seconds = int(value(bar, "time"))
    stamp = datetime.fromtimestamp(seconds, UTC).isoformat(
        timespec="seconds"
    ).replace("+00:00", "Z")
    return (
        seconds, stamp,
        repr(finite_float(value(bar, "open"))),
        repr(finite_float(value(bar, "high"))),
        repr(finite_float(value(bar, "low"))),
        repr(finite_float(value(bar, "close"))),
        int(value(bar, "tick_volume")),
        int(value(bar, "spread")),
        int(value(bar, "real_volume")),
    )


def audit_tick_rows(rows: Sequence[Sequence[Any]]) -> dict[str, Any]:
    same_millisecond = 0
    out_of_order = 0
    valid_quotes = 0
    missing_quotes = 0
    crossed_quotes = 0
    spreads: list[float] = []
    previous = None
    for row in rows:
        ms, _, bid_raw, ask_raw = row[:4]
        ms = int(ms)
        if previous is not None:
            if ms == previous:
                same_millisecond += 1
            elif ms < previous:
                out_of_order += 1
        previous = ms
        bid, ask = float(bid_raw), float(ask_raw)
        if bid <= 0 or ask <= 0:
            missing_quotes += 1
        elif ask < bid:
            crossed_quotes += 1
        else:
            valid_quotes += 1
            spreads.append(ask - bid)
    return {
        "tick_count": len(rows),
        "same_millisecond_timestamp_count": same_millisecond,
        "out_of_order_timestamp_count": out_of_order,
        "valid_non_crossed_bidask_count": valid_quotes,
        "missing_bid_or_ask_count": missing_quotes,
        "crossed_quote_count": crossed_quotes,
        "spread_price_min": min(spreads) if spreads else None,
        "spread_price_max": max(spreads) if spreads else None,
        "spread_price_mean": sum(spreads) / len(spreads) if spreads else None,
        "note": "Same-millisecond ticks are retained; this is not treated as proof of duplicate records.",
    }


def audit_m1_rows(rows: Sequence[Sequence[Any]]) -> dict[str, Any]:
    invalid_ohlc = 0
    out_of_order = 0
    gaps = []
    previous = None
    for row in rows:
        seconds = int(row[0])
        o, h, low, close = map(float, row[2:6])
        if not (h >= max(o, close, low) and low <= min(o, close) and h >= low):
            invalid_ohlc += 1
        if previous is not None:
            delta = seconds - previous
            if delta <= 0:
                out_of_order += 1
            elif delta > 60:
                gaps.append({
                    "from_utc": datetime.fromtimestamp(previous, UTC).isoformat(),
                    "to_utc": datetime.fromtimestamp(seconds, UTC).isoformat(),
                    "elapsed_minutes": delta / 60,
                    "nominal_missing_minute_slots": max(0, delta // 60 - 1),
                    "classification": "unexplained_interval_gap_pending_session_review",
                })
        previous = seconds
    return {
        "bar_count": len(rows),
        "invalid_ohlc_count": invalid_ohlc,
        "out_of_order_or_duplicate_timestamp_count": out_of_order,
        "interval_gap_count": len(gaps),
        "interval_gaps": gaps,
        "note": "Interval gaps are not automatically classified as missing market data; closures and sessions require separate review.",
    }


def symbol_specification(info: Any) -> dict[str, Any]:
    names = (
        "name", "description", "path", "currency_base", "currency_profit",
        "currency_margin", "digits", "point", "trade_tick_size",
        "trade_tick_value", "trade_contract_size", "volume_min",
        "volume_max", "volume_step", "trade_stops_level",
        "trade_freeze_level", "trade_mode", "trade_calc_mode",
        "filling_mode", "order_mode", "spread", "spread_float",
    )
    result = {}
    for name in names:
        try:
            item = value(info, name)
        except (AttributeError, KeyError, TypeError, IndexError):
            item = None
        if isinstance(item, (str, int, float, bool)) or item is None:
            result[name] = item
        else:
            result[name] = str(item)
    return result


def acquire(
    *, start: datetime, end: datetime, symbol: str, out_dir: Path,
    terminal_path: str | None = None,
) -> dict[str, Any]:
    start, end = start.astimezone(UTC), end.astimezone(UTC)
    if start >= end:
        raise ValueError("start must be earlier than end")
    if not symbol.strip():
        raise ValueError("symbol is required")

    try:
        import MetaTrader5 as mt5
    except ImportError as exc:
        raise RuntimeError("MetaTrader5 package is not installed in this Python environment") from exc

    init_args = {"path": terminal_path} if terminal_path else {}
    if not mt5.initialize(**init_args):
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        if terminal is None:
            raise RuntimeError(f"MT5 terminal_info failed: {mt5.last_error()}")
        info = mt5.symbol_info(symbol)
        if info is None:
            raise RuntimeError(
                f"MT5 symbol_info({symbol!r}) unavailable: {mt5.last_error()}. "
                "No symbol_select call was made; verify the exact symbol is already available in Market Watch."
            )

        out_dir.mkdir(parents=True, exist_ok=True)
        stem = f"{symbol.replace('.', '_')}_{start:%Y%m%d}_{end:%Y%m%d}"
        tick_path = out_dir / f"{stem}_ticks.csv.gz"
        m1_path = out_dir / f"{stem}_M1.csv.gz"

        tick_rows: list[tuple[Any, ...]] = []
        tick_empty_chunks = 0
        cursor = start
        while cursor < end:
            chunk_end = min(cursor + timedelta(days=1), end)
            ticks = mt5.copy_ticks_range(
                symbol, cursor, chunk_end - timedelta(milliseconds=1), mt5.COPY_TICKS_ALL
            )
            if ticks is None:
                raise RuntimeError(
                    f"copy_ticks_range failed for [{cursor.isoformat()}, {chunk_end.isoformat()}): {mt5.last_error()}"
                )
            if len(ticks) == 0:
                tick_empty_chunks += 1
            for tick in ticks:
                row = tick_row(tick)
                if int(start.timestamp() * 1000) <= row[0] < int(end.timestamp() * 1000):
                    tick_rows.append(row)
            cursor = chunk_end

        m1_rows: list[tuple[Any, ...]] = []
        m1_empty_chunks = 0
        cursor = start
        while cursor < end:
            chunk_end = min(cursor + timedelta(days=1), end)
            rates = mt5.copy_rates_range(
                symbol, mt5.TIMEFRAME_M1, cursor, chunk_end - timedelta(seconds=1)
            )
            if rates is None:
                raise RuntimeError(
                    f"copy_rates_range M1 failed for [{cursor.isoformat()}, {chunk_end.isoformat()}): {mt5.last_error()}"
                )
            if len(rates) == 0:
                m1_empty_chunks += 1
            for bar in rates:
                row = m1_row(bar)
                if int(start.timestamp()) <= row[0] < int(end.timestamp()):
                    m1_rows.append(row)
            cursor = chunk_end

        tick_quality = audit_tick_rows(tick_rows)
        m1_quality = audit_m1_rows(m1_rows)
        tick_count = write_gzip_csv(tick_path, TICK_FIELDS, tick_rows)
        m1_count = write_gzip_csv(m1_path, M1_FIELDS, m1_rows)

        spec = {
            "research_only": True,
            "symbol": symbol,
            "provider": "MetaTrader5 terminal API",
            "terminal_name": getattr(terminal, "name", None),
            "terminal_company": getattr(terminal, "company", None),
            "terminal_build": getattr(terminal, "build", None),
            "server": getattr(account, "server", None) if account is not None else None,
            "specification": symbol_specification(info),
            "timezone_note": (
                "MT5 epoch timestamps are retained and rendered as UTC. "
                "No broker server offset or historical DST rule is inferred from the current terminal."
            ),
            "account_login_recorded": False,
        }
        spec_path = out_dir / f"{stem}_symbol_specs.json"
        spec_path.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\\n", encoding="utf-8")

        artifacts = []
        for path, count, quality in (
            (tick_path, tick_count, tick_quality), (m1_path, m1_count, m1_quality)
        ):
            artifacts.append({
                "path": path.name,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "rows": count,
                "quality": quality,
            })
        artifacts.append({
            "path": spec_path.name,
            "size_bytes": spec_path.stat().st_size,
            "sha256": sha256_file(spec_path),
            "rows": None,
        })

        result = {
            "schema_version": 1,
            "research_only": True,
            "canonical": False,
            "symbol": symbol,
            "interval_utc": {"start_inclusive": start.isoformat(), "end_exclusive": end.isoformat()},
            "retrieved_at_utc": datetime.now(UTC).isoformat(),
            "terminal": {
                "name": getattr(terminal, "name", None),
                "company": getattr(terminal, "company", None),
                "build": getattr(terminal, "build", None),
                "server": getattr(account, "server", None) if account is not None else None,
            },
            "chunking": {"unit": "UTC day", "tick_empty_day_chunks": tick_empty_chunks, "m1_empty_day_chunks": m1_empty_chunks},
            "artifacts": artifacts,
            "data_handling": {
                "sorted": False,
                "deduplicated": False,
                "missing_rows_fabricated": False,
                "raw_provider_order_preserved": True,
                "all_exclusions": [],
            },
            "operational_safety": {
                "orders_sent": False,
                "positions_modified": False,
                "runner_files_accessed": False,
                "runner_or_dashboard_stopped": False,
                "symbol_select_called": False,
                "account_login_recorded": False,
            },
        }
        manifest_path = out_dir / f"{stem}_acquisition_manifest.json"
        manifest_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
        sums_path = out_dir / f"{stem}_SHA256SUMS.txt"
        sums_path.write_text(
            "".join(f"{item['sha256']}  {item['path']}\\n" for item in artifacts)
            + f"{sha256_file(manifest_path)}  {manifest_path.name}\\n",
            encoding="utf-8",
        )
        result["manifest_path"] = str(manifest_path)
        result["sha256sums_path"] = str(sums_path)
        return result
    finally:
        mt5.shutdown()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-utc", required=True, help="Inclusive ISO-8601 timestamp with UTC offset")
    parser.add_argument("--end-utc", required=True, help="Exclusive ISO-8601 timestamp with UTC offset")
    parser.add_argument("--symbol", default="XAUUSD.ecn")
    parser.add_argument("--out-dir", default="research_data/mt5")
    parser.add_argument("--terminal-path", default=os.environ.get("MT5_TERMINAL_PATH"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        start, end = parse_utc(args.start_utc), parse_utc(args.end_utc)
        result = acquire(
            start=start, end=end, symbol=args.symbol,
            out_dir=Path(args.out_dir), terminal_path=args.terminal_path,
        )
    except Exception as exc:
        print(f"MT5_RESEARCH_EXPORT_FAILED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
