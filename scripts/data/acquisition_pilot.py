#!/usr/bin/env python3
"""Bounded, resumable XAU/USD M1 acquisition pilot.

Purpose: exercise the real acquisition path on a small explicit UTC window.
This is NOT the full historical downloader and does not infer strategy rules.

The pilot:
- uses only TWELVE_DATA_API_KEY from the environment;
- requests bounded pages with start_date/end_date;
- de-duplicates candles by UTC timestamp;
- validates OHLC and 1-minute continuity;
- writes raw CSV plus a JSON provenance manifest;
- writes a checkpoint only after a successful page;
- refuses to overwrite existing outputs unless --force is supplied.

Default window is intentionally small (24 hours) and can be overridden with
--start/--end. Default page size is 5000 and default maximum requests is 5.
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
TZ = "UTC"
PAGE_SIZE = 5000
DEFAULT_REQUESTS = 5
DEFAULT_START = "2026-09-04 00:00:00"
DEFAULT_END = "2026-09-05 00:00:00"
OUT_DIR = Path("data/raw/twelvedata/pilot")


def parse_dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def fmt_dt(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def fetch(params: dict[str, str | int]) -> tuple[int, dict, dict[str, str]]:
    url = f"{BASE_URL}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": "xauusd-strategy-a/acquisition-pilot"})
    try:
        with urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body), {k.lower(): v for k, v in resp.headers.items()}
    except Exception as exc:
        return 0, {"status": "error", "message": str(exc)}, {}


def validate(rows: list[dict]) -> tuple[int, int, list[tuple[str, str, int]]]:
    invalid = 0
    gaps: list[tuple[str, str, int]] = []
    ordered = sorted(rows, key=lambda r: r["datetime"])
    for r in ordered:
        try:
            o, h, l, c = map(float, (r["open"], r["high"], r["low"], r["close"]))
            if not (l <= min(o, c) <= max(o, c) <= h):
                invalid += 1
        except (KeyError, ValueError, TypeError):
            invalid += 1
    for a, b in zip(ordered, ordered[1:]):
        delta = int((parse_dt(b["datetime"]) - parse_dt(a["datetime"])).total_seconds())
        if delta != 60:
            gaps.append((a["datetime"], b["datetime"], delta))
    return invalid, len(gaps), gaps


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default=DEFAULT_START, help="UTC start, inclusive")
    ap.add_argument("--end", default=DEFAULT_END, help="UTC end, inclusive")
    ap.add_argument("--requests", type=int, default=DEFAULT_REQUESTS)
    ap.add_argument("--output-dir", default=str(OUT_DIR))
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    key = os.getenv("TWELVE_DATA_API_KEY")
    print("Twelve Data XAU/USD historical acquisition pilot")
    print("=" * 52)
    print(f"window UTC:      {args.start} -> {args.end}")
    print(f"page size:       {PAGE_SIZE}")
    print(f"request budget:  {args.requests}")
    print(f"api_key:         {'SET (value hidden)' if key else 'NOT_SET'}")
    if not key:
        return 2
    start, end = parse_dt(args.start), parse_dt(args.end)
    if end < start:
        print("ERROR: end precedes start", file=sys.stderr)
        return 2
    if args.requests < 1:
        print("ERROR: requests must be >= 1", file=sys.stderr)
        return 2

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = start.strftime("%Y%m%dT%H%M%SZ") + "__" + end.strftime("%Y%m%dT%H%M%SZ")
    csv_path = out / f"XAUUSD_M1_{stamp}.csv"
    manifest_path = out / f"XAUUSD_M1_{stamp}.manifest.json"
    checkpoint_path = out / f"XAUUSD_M1_{stamp}.checkpoint.json"
    if not args.force and any(p.exists() for p in (csv_path, manifest_path, checkpoint_path)):
        print("ERROR: output exists; use --force only when intentionally replacing a pilot artifact.")
        return 3

    all_rows: dict[str, dict] = {}
    requests = []
    cursor_end = end
    completed = False

    for n in range(1, args.requests + 1):
        params = {
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "timezone": TZ,
            "start_date": fmt_dt(start),
            "end_date": fmt_dt(cursor_end),
            "apikey": key,
        }
        http, payload, headers = fetch(params)
        credits_used = headers.get("api-credits-used")
        credits_left = headers.get("api-credits-left")
        print(f"[{n}/{args.requests}] HTTP={http} credits_used={credits_used or 'n/a'} credits_left={credits_left or 'n/a'}")
        if payload.get("status") != "ok":
            print(f"response: {json.dumps(payload, ensure_ascii=False)}")
            return 4
        values = payload.get("values") or []
        if not values:
            print("ERROR: successful response contained no values")
            return 5

        before = len(all_rows)
        for row in values:
            all_rows[row["datetime"]] = row
        duplicates = len(values) - (len(all_rows) - before)
        ordered = sorted(values, key=lambda r: r["datetime"])
        page_oldest = ordered[0]["datetime"]
        page_newest = ordered[-1]["datetime"]
        invalid, gaps, _ = validate(ordered)
        print(f"  rows={len(values)} oldest={page_oldest} newest={page_newest} duplicates={duplicates} gaps={gaps} invalid_ohlc={invalid}")

        requests.append({
            "request_number": n,
            "requested_start": fmt_dt(start),
            "requested_end": fmt_dt(cursor_end),
            "returned_rows": len(values),
            "returned_oldest": page_oldest,
            "returned_newest": page_newest,
            "duplicates_against_accumulator": duplicates,
            "invalid_ohlc": invalid,
            "non_1min_gaps": gaps,
            "http_status": http,
            "api_credits_used": credits_used,
            "api_credits_left": credits_left,
        })

        checkpoint = {
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "timezone": TZ,
            "requested_start": fmt_dt(start),
            "requested_end": fmt_dt(end),
            "next_cursor_end": page_oldest,
            "rows_accumulated": len(all_rows),
            "requests_completed": n,
            "last_page_oldest": page_oldest,
            "last_page_newest": page_newest,
            "updated_at_utc": fmt_dt(datetime.now(timezone.utc)),
        }
        checkpoint_path.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")

        # If the oldest returned candle has reached the requested start, coverage is complete.
        if parse_dt(page_oldest) <= start:
            completed = True
            break
        next_cursor = parse_dt(page_oldest) - timedelta(minutes=1)
        if next_cursor >= cursor_end:
            print("ERROR: pagination cursor did not move backwards", file=sys.stderr)
            return 6
        cursor_end = next_cursor
        time.sleep(0.25)

    ordered_all = sorted(all_rows.values(), key=lambda r: r["datetime"])
    # Retain only the requested interval. The final page can straddle the start boundary.
    final_rows = [r for r in ordered_all if start <= parse_dt(r["datetime"]) <= end]
    invalid, gaps, gap_detail = validate(final_rows)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["datetime", "open", "high", "low", "close"])
        writer.writeheader()
        writer.writerows({k: r[k] for k in writer.fieldnames} for r in final_rows)

    manifest = {
        "dataset_type": "raw_market_data_pilot",
        "provider": "Twelve Data",
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "timezone": TZ,
        "requested_start_utc": fmt_dt(start),
        "requested_end_utc": fmt_dt(end),
        "completed_requested_range": completed,
        "rows_written": len(final_rows),
        "first_written": final_rows[0]["datetime"] if final_rows else None,
        "last_written": final_rows[-1]["datetime"] if final_rows else None,
        "invalid_ohlc": invalid,
        "non_1min_gaps": len(gaps),
        "gap_examples": gap_detail[:20],
        "requests_completed": len(requests),
        "request_budget": args.requests,
        "requests": requests,
        "created_at_utc": fmt_dt(datetime.now(timezone.utc)),
        "api_key_persisted": False,
        "notes": [
            "Pilot only; not evidence of complete historical coverage.",
            "Boundary duplicates are de-duplicated by UTC datetime.",
            "Raw values are preserved as returned by the provider.",
            "No strategy logic is applied.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    checkpoint_path.unlink(missing_ok=True)

    print("\nFINAL")
    print(f"rows written:     {len(final_rows)}")
    print(f"completed range:  {completed}")
    print(f"gaps:             {len(gaps)}")
    print(f"invalid OHLC:     {invalid}")
    print(f"csv sha256:       {sha256_file(csv_path)}")
    print(f"csv:              {csv_path}")
    print(f"manifest:         {manifest_path}")
    print("API key value was never printed or persisted.")
    return 0 if completed and not gaps and not invalid else 7


if __name__ == "__main__":
    raise SystemExit(main())
