#!/usr/bin/env python3
"""Resumable, provenance-tracked XAU/USD M1 historical acquisition v1.

Research-data acquisition only. No strategy logic.

The downloader:
- reads TWELVE_DATA_API_KEY only from the environment;
- walks backward through bounded UTC windows;
- uses at most 5000 provider rows per request;
- de-duplicates exact UTC timestamps;
- validates OHLC and minute continuity within the acquired range;
- persists a checkpoint after every successful page;
- writes raw CSV and JSON manifest only when the requested range completes;
- never stores the API key.

Because XAU/USD has market closures, a missing minute is reported by the
validator rather than silently classified as a market-session closure.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://api.twelvedata.com/time_series"
SYMBOL = "XAU/USD"
INTERVAL = "1min"
TIMEZONE = "UTC"
PAGE_SIZE = 5000
DEFAULT_START = "2020-04-06 06:40:00"
DEFAULT_END = "2026-09-05 00:00:00"
DEFAULT_REQUEST_BUDGET = 100
DEFAULT_OUT_DIR = Path("data/raw/twelvedata/historical_v1")


def parse_dt(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def fmt_dt(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def fetch(params: dict[str, str | int]) -> tuple[int, dict, dict[str, str]]:
    url = f"{BASE_URL}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "xauusd-strategy-a/historical-acquisition-v1"})
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body), {k.lower(): v for k, v in response.headers.items()}
    except Exception as exc:
        return 0, {"status": "error", "message": str(exc)}, {}


def validate(rows: list[dict]) -> tuple[int, int, list[tuple[str, str, int]]]:
    invalid = 0
    gaps: list[tuple[str, str, int]] = []
    ordered = sorted(rows, key=lambda row: row["datetime"])
    for row in ordered:
        try:
            o, h, l, c = map(float, (row["open"], row["high"], row["low"], row["close"]))
            if not (l <= min(o, c) <= max(o, c) <= h):
                invalid += 1
        except (KeyError, ValueError, TypeError):
            invalid += 1
    for left, right in zip(ordered, ordered[1:]):
        delta = int((parse_dt(right["datetime"]) - parse_dt(left["datetime"])).total_seconds())
        if delta != 60:
            gaps.append((left["datetime"], right["datetime"], delta))
    return invalid, len(gaps), gaps


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_write_json(path: Path, payload: dict) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default=DEFAULT_START, help="UTC start, inclusive")
    parser.add_argument("--end", default=DEFAULT_END, help="UTC end, inclusive")
    parser.add_argument("--requests", type=int, default=DEFAULT_REQUEST_BUDGET, help="maximum API requests for this run")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--sleep", type=float, default=0.25, help="seconds between requests")
    parser.add_argument("--force", action="store_true", help="replace an existing completed artifact")
    args = parser.parse_args()

    key = os.getenv("TWELVE_DATA_API_KEY")
    print("Twelve Data XAU/USD M1 historical acquisition v1")
    print("=" * 54)
    print(f"requested UTC:   {args.start} -> {args.end}")
    print(f"page size:       {PAGE_SIZE}")
    print(f"request budget:  {args.requests}")
    print(f"api_key:         {'SET (value hidden)' if key else 'NOT_SET'}")
    if not key:
        return 2
    if args.requests < 1:
        print("ERROR: requests must be >= 1", file=sys.stderr)
        return 2
    if args.sleep < 0:
        print("ERROR: sleep must be >= 0", file=sys.stderr)
        return 2

    start, end = parse_dt(args.start), parse_dt(args.end)
    if end < start:
        print("ERROR: end precedes start", file=sys.stderr)
        return 2

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = start.strftime("%Y%m%dT%H%M%SZ") + "__" + end.strftime("%Y%m%dT%H%M%SZ")
    csv_path = out / f"XAUUSD_M1_{stamp}.csv"
    manifest_path = out / f"XAUUSD_M1_{stamp}.manifest.json"
    checkpoint_path = out / f"XAUUSD_M1_{stamp}.checkpoint.json"
    if not args.force and (csv_path.exists() or manifest_path.exists()):
        print("ERROR: completed artifact exists; use --force only for intentional replacement.")
        return 3

    # A checkpoint stores the next cursor and accumulated rows, so an interrupted
    # run can resume without trusting partially written CSV output.
    all_rows: dict[str, dict] = {}
    cursor_end = end
    request_log: list[dict] = []
    resumed = checkpoint_path.exists()
    if resumed:
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if checkpoint.get("requested_start_utc") != fmt_dt(start) or checkpoint.get("requested_end_utc") != fmt_dt(end):
            print("ERROR: checkpoint range does not match requested range", file=sys.stderr)
            return 3
        all_rows = {row["datetime"]: row for row in checkpoint.get("rows", [])}
        cursor_end = parse_dt(checkpoint["next_cursor_end_utc"])
        request_log = checkpoint.get("requests", [])
        print(f"resuming checkpoint: {len(all_rows)} rows, next cursor {fmt_dt(cursor_end)}")

    completed = False
    for local_number in range(1, args.requests + 1):
        params = {
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "timezone": TIMEZONE,
            "start_date": fmt_dt(start),
            "end_date": fmt_dt(cursor_end),
            "apikey": key,
        }
        http, payload, headers = fetch(params)
        used = headers.get("api-credits-used")
        left = headers.get("api-credits-left")
        absolute_number = len(request_log) + 1
        print(f"[{local_number}/{args.requests}] HTTP={http} credits_used={used or 'n/a'} credits_left={left or 'n/a'}")
        if payload.get("status") != "ok":
            print(f"response: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
            print("Checkpoint retained; rerun to resume.")
            return 4

        values = payload.get("values") or []
        if not values:
            print("ERROR: successful response contained no values", file=sys.stderr)
            return 5
        page = sorted(values, key=lambda row: row["datetime"])
        page_oldest, page_newest = page[0]["datetime"], page[-1]["datetime"]
        before = len(all_rows)
        for row in values:
            all_rows[row["datetime"]] = row
        duplicates = len(values) - (len(all_rows) - before)
        invalid, page_gap_count, _ = validate(page)
        print(f"  rows={len(values)} oldest={page_oldest} newest={page_newest} duplicates={duplicates} gaps={page_gap_count} invalid={invalid}")

        request_log.append({
            "request_number": absolute_number,
            "requested_start_utc": fmt_dt(start),
            "requested_end_utc": fmt_dt(cursor_end),
            "returned_rows": len(values),
            "returned_oldest_utc": page_oldest,
            "returned_newest_utc": page_newest,
            "duplicates_against_accumulator": duplicates,
            "invalid_ohlc": invalid,
            "non_1min_gaps": page_gap_count,
            "http_status": http,
            "api_credits_used": used,
            "api_credits_left": left,
        })

        if parse_dt(page_oldest) <= start:
            completed = True
            break

        next_cursor = parse_dt(page_oldest) - timedelta(minutes=1)
        if next_cursor >= cursor_end:
            print("ERROR: pagination cursor did not move backwards", file=sys.stderr)
            return 6
        cursor_end = next_cursor
        checkpoint = {
            "dataset_type": "raw_market_data_historical_v1_checkpoint",
            "provider": "Twelve Data",
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "timezone": TIMEZONE,
            "requested_start_utc": fmt_dt(start),
            "requested_end_utc": fmt_dt(end),
            "next_cursor_end_utc": fmt_dt(cursor_end),
            "rows_accumulated": len(all_rows),
            "requests_completed": len(request_log),
            "requests": request_log,
            "rows": sorted(all_rows.values(), key=lambda row: row["datetime"]),
            "api_key_persisted": False,
            "updated_at_utc": fmt_dt(datetime.now(timezone.utc)),
        }
        atomic_write_json(checkpoint_path, checkpoint)
        if args.sleep:
            time.sleep(args.sleep)

    if not completed:
        print("REQUEST BUDGET EXHAUSTED — checkpoint retained; no final artifact declared.")
        print(f"checkpoint: {checkpoint_path}")
        return 7

    final_rows = [row for row in sorted(all_rows.values(), key=lambda row: row["datetime"]) if start <= parse_dt(row["datetime"]) <= end]
    invalid, gap_count, gap_detail = validate(final_rows)
    if not final_rows or final_rows[0]["datetime"] != fmt_dt(start) or final_rows[-1]["datetime"] != fmt_dt(end):
        print("ERROR: completed response did not cover exact requested boundaries", file=sys.stderr)
        return 8

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["datetime", "open", "high", "low", "close"])
        writer.writeheader()
        writer.writerows({field: row[field] for field in writer.fieldnames} for row in final_rows)

    manifest = {
        "dataset_type": "raw_market_data_historical_v1",
        "provider": "Twelve Data",
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "timezone": TIMEZONE,
        "requested_start_utc": fmt_dt(start),
        "requested_end_utc": fmt_dt(end),
        "completed_requested_range": True,
        "rows_written": len(final_rows),
        "first_written_utc": final_rows[0]["datetime"],
        "last_written_utc": final_rows[-1]["datetime"],
        "invalid_ohlc": invalid,
        "non_1min_gaps": gap_count,
        "gap_examples": gap_detail[:50],
        "requests_completed": len(request_log),
        "request_budget_per_run": args.requests,
        "resumed_from_checkpoint": resumed,
        "requests": request_log,
        "csv_sha256": sha256_file(csv_path),
        "created_at_utc": fmt_dt(datetime.now(timezone.utc)),
        "api_key_persisted": False,
        "research_status": "RAW_ONLY_NOT_STRATEGY_VALIDATED",
        "notes": [
            "This dataset is raw provider data for research only.",
            "No strategy logic or resampling is applied.",
            "Continuity gaps are reported, not interpreted as market closures.",
            "Provider feed differences versus MT5/broker data must be audited separately.",
        ],
    }
    atomic_write_json(manifest_path, manifest)
    checkpoint_path.unlink(missing_ok=True)

    print("\nFINAL")
    print(f"rows written:     {len(final_rows)}")
    print(f"completed range:  True")
    print(f"gaps:             {gap_count}")
    print(f"invalid OHLC:     {invalid}")
    print(f"requests:         {len(request_log)}")
    print(f"csv sha256:       {manifest['csv_sha256']}")
    print(f"csv:              {csv_path}")
    print(f"manifest:         {manifest_path}")
    print("API key value was never printed or persisted.")
    return 0 if gap_count == 0 and invalid == 0 else 9


if __name__ == "__main__":
    raise SystemExit(main())
