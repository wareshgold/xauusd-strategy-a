#!/usr/bin/env python3
"""Read-only, streaming MT5 Tick ALL + M1 export for SP2L research.

No symbol_select, orders, positions, Runner files, dashboard control, or terminal
configuration changes. Existing terminal must already expose the exact symbol.
"""
from __future__ import annotations
import argparse, csv, datetime as dt, gzip, hashlib, io, json, os, sys
from pathlib import Path
from typing import Any, Sequence

UTC = dt.timezone.utc
TICK_FIELDS = ("time_msc", "time_utc", "bid", "ask", "last", "volume", "flags")
M1_FIELDS = ("time", "time_utc", "open", "high", "low", "close", "tick_volume", "spread_points", "real_volume")


def parse_utc(raw: str) -> dt.datetime:
    text = raw.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    value = dt.datetime.fromisoformat(text)
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must include a UTC offset")
    return value.astimezone(UTC)


def get(record: Any, name: str) -> Any:
    try:
        return record[name]
    except (KeyError, TypeError, IndexError):
        return getattr(record, name)


def number(raw: Any) -> float:
    try:
        x = float(raw)
    except (TypeError, ValueError):
        return 0.0
    return x if x == x and abs(x) != float("inf") else 0.0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def tick_row(tick: Any):
    ms = int(get(tick, "time_msc"))
    stamp = dt.datetime.fromtimestamp(ms / 1000, UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    return (ms, stamp, repr(number(get(tick, "bid"))), repr(number(get(tick, "ask"))),
            repr(number(get(tick, "last"))), repr(number(get(tick, "volume"))), int(get(tick, "flags")))


def m1_row(bar: Any):
    sec = int(get(bar, "time"))
    stamp = dt.datetime.fromtimestamp(sec, UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    return (sec, stamp, repr(number(get(bar, "open"))), repr(number(get(bar, "high"))),
            repr(number(get(bar, "low"))), repr(number(get(bar, "close"))),
            int(get(bar, "tick_volume")), int(get(bar, "spread")), int(get(bar, "real_volume")))


class CsvGzip:
    """Incremental gzip CSV output; refuses to overwrite final or partial files."""
    def __init__(self, path: Path, columns):
        self.path, self.partial, self.columns = path, path.with_name(path.name + ".partial"), columns
        self.count = 0

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists() or self.partial.exists():
            raise FileExistsError(f"refusing to overwrite evidence: {self.path}")
        self.raw = self.partial.open("xb")
        self.gz = gzip.GzipFile(fileobj=self.raw, mode="wb", filename="", mtime=0)
        self.text = io.TextIOWrapper(self.gz, encoding="utf-8", newline="")
        self.writer = csv.writer(self.text, lineterminator="\n")
        self.writer.writerow(self.columns)
        return self

    def write(self, row):
        self.writer.writerow(row)
        self.count += 1

    def __exit__(self, exc_type, exc, tb):
        self.text.flush()
        self.text.detach()
        self.gz.close()
        self.raw.close()
        if exc_type is None:
            if self.path.exists():
                raise FileExistsError(f"refusing to overwrite evidence: {self.path}")
            self.partial.rename(self.path)
        return False


class TickAudit:
    def __init__(self):
        self.n = self.same_ms = self.out_of_order = self.valid = self.missing = self.crossed = 0
        self.prev = self.first = self.last = None
        self.spread_min = self.spread_max = None
        self.spread_sum = 0.0
        self.spread_frequency = {}

    def add(self, r):
        ms, stamp, bid_s, ask_s = r[:4]
        ms, bid, ask = int(ms), float(bid_s), float(ask_s)
        if self.prev is not None:
            if ms == self.prev: self.same_ms += 1
            elif ms < self.prev: self.out_of_order += 1
        self.prev = ms
        if bid <= 0 or ask <= 0: self.missing += 1
        elif ask < bid: self.crossed += 1
        else:
            spread = ask - bid
            self.valid += 1
            self.spread_min = spread if self.spread_min is None else min(self.spread_min, spread)
            self.spread_max = spread if self.spread_max is None else max(self.spread_max, spread)
            self.spread_sum += spread
            key = format(spread, ".10g")
            self.spread_frequency[key] = self.spread_frequency.get(key, 0) + 1
        self.n += 1
        self.first = self.first or stamp
        self.last = stamp

    def report(self):
        return {"tick_count": self.n, "first_tick_utc": self.first, "last_tick_utc": self.last,
                "same_millisecond_timestamp_count": self.same_ms, "out_of_order_timestamp_count": self.out_of_order,
                "valid_non_crossed_bidask_count": self.valid, "missing_bid_or_ask_count": self.missing,
                "crossed_quote_count": self.crossed, "spread_price_min": self.spread_min,
                "spread_price_max": self.spread_max, "spread_price_mean": self.spread_sum / self.valid if self.valid else None,
                "spread_price_frequency": self.spread_frequency,
                "note": "Same-millisecond ticks are retained; they are not automatically classified as duplicate records."}


class M1Audit:
    def __init__(self):
        self.n = self.invalid = self.out_of_order = 0
        self.prev = self.first = self.last = None
        self.gaps = []

    def add(self, r):
        sec = int(r[0])
        o, h, low, c = map(float, r[2:6])
        if not (h >= max(o, c, low) and low <= min(o, c) and h >= low): self.invalid += 1
        if self.prev is not None:
            delta = sec - self.prev
            if delta <= 0: self.out_of_order += 1
            elif delta > 60:
                self.gaps.append({"from_utc": dt.datetime.fromtimestamp(self.prev, UTC).isoformat(),
                                  "to_utc": dt.datetime.fromtimestamp(sec, UTC).isoformat(),
                                  "elapsed_minutes": delta / 60,
                                  "nominal_missing_minute_slots": max(0, delta // 60 - 1),
                                  "classification": "interval_gap_pending_session_review"})
        self.prev = sec
        self.n += 1
        self.first = self.first or r[1]
        self.last = r[1]

    def report(self):
        return {"bar_count": self.n, "first_bar_utc": self.first, "last_bar_utc": self.last,
                "invalid_ohlc_count": self.invalid, "out_of_order_or_duplicate_timestamp_count": self.out_of_order,
                "interval_gap_count": len(self.gaps), "interval_gaps": self.gaps,
                "note": "Interval gaps are not automatically classified as missing bars; session/closure review is required."}


def symbol_spec(info):
    keys = ("name", "description", "path", "currency_base", "currency_profit", "currency_margin",
            "digits", "point", "trade_tick_size", "trade_tick_value", "trade_tick_value_profit",
            "trade_tick_value_loss", "trade_contract_size", "volume_min", "volume_max", "volume_step",
            "trade_stops_level", "trade_freeze_level", "trade_mode", "trade_calc_mode",
            "filling_mode", "order_mode", "spread", "spread_float")
    result = {}
    for key in keys:
        try: item = get(info, key)
        except (AttributeError, KeyError, TypeError, IndexError): item = None
        result[key] = item if isinstance(item, (str, int, float, bool)) or item is None else str(item)
    return result


def write_json_new(path: Path, payload):
    raw = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    with path.open("xb") as stream: stream.write(raw)


def acquire(start, end, symbol, out_dir, terminal_path=None):
    if start.tzinfo is None or end.tzinfo is None: raise ValueError("start/end must be timezone-aware")
    start, end = start.astimezone(UTC), end.astimezone(UTC)
    if start >= end: raise ValueError("start must be earlier than end")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{symbol.replace('.', '_')}_{start:%Y%m%d}_{end:%Y%m%d}"
    tick_path, m1_path = out_dir / f"{stem}_ticks.csv.gz", out_dir / f"{stem}_M1.csv.gz"
    spec_path, manifest_path = out_dir / f"{stem}_symbol_specs.json", out_dir / f"{stem}_acquisition_manifest.json"
    sums_path = out_dir / f"{stem}_SHA256SUMS.txt"
    for p in (tick_path, m1_path, spec_path, manifest_path, sums_path):
        if p.exists() or p.with_name(p.name + ".partial").exists():
            raise FileExistsError(f"refusing to overwrite evidence: {p}")

    try: import MetaTrader5 as mt5
    except ImportError as exc: raise RuntimeError("MetaTrader5 package is not installed") from exc
    kwargs = {"path": terminal_path} if terminal_path else {}
    if not mt5.initialize(**kwargs): raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        terminal, account = mt5.terminal_info(), mt5.account_info()
        if terminal is None: raise RuntimeError(f"terminal_info failed: {mt5.last_error()}")
        info = mt5.symbol_info(symbol)
        if info is None:
            raise RuntimeError(f"symbol_info({symbol!r}) unavailable: {mt5.last_error()}; no symbol_select was called")
        ta, ma = TickAudit(), M1Audit()
        empty_ticks = empty_m1 = 0
        with CsvGzip(tick_path, TICK_FIELDS) as sink:
            cursor = start
            while cursor < end:
                stop = min(cursor + dt.timedelta(days=1), end)
                chunk = mt5.copy_ticks_range(symbol, cursor, stop - dt.timedelta(milliseconds=1), mt5.COPY_TICKS_ALL)
                if chunk is None: raise RuntimeError(f"copy_ticks_range failed at {cursor.isoformat()}: {mt5.last_error()}")
                if len(chunk) == 0: empty_ticks += 1
                for tick in chunk:
                    row = tick_row(tick)
                    if int(start.timestamp() * 1000) <= row[0] < int(end.timestamp() * 1000):
                        sink.write(row); ta.add(row)
                cursor = stop
        with CsvGzip(m1_path, M1_FIELDS) as sink:
            cursor = start
            while cursor < end:
                stop = min(cursor + dt.timedelta(days=1), end)
                chunk = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, cursor, stop - dt.timedelta(seconds=1))
                if chunk is None: raise RuntimeError(f"copy_rates_range M1 failed at {cursor.isoformat()}: {mt5.last_error()}")
                if len(chunk) == 0: empty_m1 += 1
                for bar in chunk:
                    row = m1_row(bar)
                    if int(start.timestamp()) <= row[0] < int(end.timestamp()):
                        sink.write(row); ma.add(row)
                cursor = stop

        spec = {"research_only": True, "symbol": symbol, "provider": "MetaTrader5 terminal API",
                "terminal_name": getattr(terminal, "name", None), "terminal_company": getattr(terminal, "company", None),
                "terminal_build": getattr(terminal, "build", None),
                "server": getattr(account, "server", None) if account is not None else None,
                "specification": symbol_spec(info),
                "timezone_note": "MT5 epoch timestamps rendered as UTC; no broker offset or historical DST rule inferred.",
                "account_login_recorded": False}
        write_json_new(spec_path, spec)
        artifact_rows = []
        for p, rows, quality in ((tick_path, ta.n, ta.report()), (m1_path, ma.n, ma.report()), (spec_path, None, None)):
            artifact_rows.append({"path": p.name, "size_bytes": p.stat().st_size, "sha256": sha256(p), "rows": rows, "quality": quality})
        manifest = {"schema_version": 1, "research_only": True, "canonical": False, "symbol": symbol,
                    "interval_utc": {"start_inclusive": start.isoformat(), "end_exclusive": end.isoformat()},
                    "retrieved_at_utc": dt.datetime.now(UTC).isoformat(),
                    "terminal": {"name": getattr(terminal, "name", None), "company": getattr(terminal, "company", None),
                                 "build": getattr(terminal, "build", None),
                                 "server": getattr(account, "server", None) if account is not None else None},
                    "chunking": {"unit": "UTC day", "tick_empty_day_chunks": empty_ticks, "m1_empty_day_chunks": empty_m1},
                    "artifacts": artifact_rows,
                    "data_handling": {"sorted": False, "deduplicated": False, "missing_rows_fabricated": False,
                                      "raw_provider_order_preserved": True, "all_exclusions": []},
                    "operational_safety": {"orders_sent": False, "positions_modified": False, "runner_files_accessed": False,
                                           "runner_or_dashboard_stopped": False, "symbol_select_called": False,
                                           "account_login_recorded": False}}
        write_json_new(manifest_path, manifest)
        sums = "".join(f"{x['sha256']}  {x['path']}\n" for x in artifact_rows)
        sums += f"{sha256(manifest_path)}  {manifest_path.name}\n"
        with sums_path.open("xb") as stream: stream.write(sums.encode("utf-8"))
        return {"status": "EXPORTED", "symbol": symbol, "interval_utc": manifest["interval_utc"],
                "artifacts": artifact_rows, "manifest_path": str(manifest_path), "sha256sums_path": str(sums_path),
                "tick_empty_day_chunks": empty_ticks, "m1_empty_day_chunks": empty_m1}
    finally:
        mt5.shutdown()


def main(argv: Sequence[str] | None = None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--start-utc", required=True)
    p.add_argument("--end-utc", required=True, help="Exclusive UTC boundary")
    p.add_argument("--symbol", default="XAUUSD.ecn")
    p.add_argument("--out-dir", default="research_data/mt5")
    p.add_argument("--terminal-path", default=os.environ.get("MT5_TERMINAL_PATH"))
    a = p.parse_args(argv)
    try:
        result = acquire(parse_utc(a.start_utc), parse_utc(a.end_utc), a.symbol, Path(a.out_dir), a.terminal_path)
    except Exception as exc:
        print(f"MT5_RESEARCH_EXPORT_FAILED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
