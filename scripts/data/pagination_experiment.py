#!/usr/bin/env python3
"""Credit-bounded Twelve Data XAU/USD M1 pagination experiment.

Purpose: validate historical windowing, page overlap, continuity and credit
headers before any bulk acquisition. This script intentionally makes only a
small fixed number of requests and never writes market data to disk.

API key is read only from TWELVE_DATA_API_KEY and is never printed/stored.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://api.twelvedata.com"
SYMBOL = "XAU/USD"
INTERVAL = "1min"
TZ = "UTC"
PAGE_SIZE = 5000
MAX_REQUESTS = 5


def call(endpoint: str, params: dict[str, str | int]) -> tuple[int, dict, dict[str, str]]:
    url = f"{BASE}/{endpoint}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": "xauusd-strategy-a/pagination-experiment"})
    try:
        with urlopen(req, timeout=45) as r:
            body = json.loads(r.read().decode("utf-8"))
            headers = {k.lower(): v for k, v in r.headers.items()}
            return r.status, body, headers
    except Exception as exc:
        return 0, {"status": "error", "message": str(exc)}, {}


def parse_dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def fmt_dt(d: datetime) -> str:
    return d.strftime("%Y-%m-%d %H:%M:%S")


def credit_fields(headers: dict[str, str]) -> str:
    used = headers.get("api-credits-used", "n/a")
    left = headers.get("api-credits-left", "n/a")
    return f"credits_used={used}, credits_left={left}"


def validate_rows(rows: list[dict]) -> tuple[int, list[tuple[str, str, int]], int]:
    ordered = sorted(rows, key=lambda x: x["datetime"])
    gaps: list[tuple[str, str, int]] = []
    invalid = 0
    for r in ordered:
        try:
            o, h, l, c = map(float, (r["open"], r["high"], r["low"], r["close"]))
            if not (l <= min(o, c) <= max(o, c) <= h):
                invalid += 1
        except (KeyError, ValueError):
            invalid += 1
    for a, b in zip(ordered, ordered[1:]):
        seconds = int((parse_dt(b["datetime"]) - parse_dt(a["datetime"])).total_seconds())
        if seconds != 60:
            gaps.append((a["datetime"], b["datetime"], seconds))
    return len(ordered), gaps, invalid


def main() -> int:
    key = os.getenv("TWELVE_DATA_API_KEY")
    print("Twelve Data XAU/USD bounded pagination experiment")
    print("=" * 52)
    print(f"symbol:          {SYMBOL}")
    print(f"interval:        {INTERVAL}")
    print(f"timezone:        {TZ}")
    print(f"page size:       {PAGE_SIZE}")
    print(f"request budget:  {MAX_REQUESTS}")
    print(f"api_key:         {'SET (value hidden)' if key else 'NOT_SET'}")
    if not key:
        return 2

    common = {"symbol": SYMBOL, "interval": INTERVAL, "timezone": TZ, "apikey": key}
    requests = 0
    pages: list[tuple[str, list[dict], dict[str, str]]] = []

    # 1) Earliest timestamp: use the documented dedicated endpoint.
    requests += 1
    status, body, headers = call("earliest_timestamp", {**common})
    print(f"\n[1/{MAX_REQUESTS}] earliest_timestamp HTTP={status} {credit_fields(headers)}")
    print(f"response: {json.dumps(body, ensure_ascii=False)}")

    # 2) Recent maximum page.
    requests += 1
    status, body, headers = call("time_series", {**common, "outputsize": PAGE_SIZE})
    print(f"\n[2/{MAX_REQUESTS}] recent page HTTP={status} {credit_fields(headers)}")
    if body.get("status") != "ok":
        print(f"response: {json.dumps(body, ensure_ascii=False)}")
        print("RESULT: FAIL — recent page failed")
        return 1
    rows = body.get("values") or []
    pages.append(("recent", rows, headers))
    n, gaps, invalid = validate_rows(rows)
    ordered = sorted(rows, key=lambda x: x["datetime"])
    print(f"rows={n}; oldest={ordered[0]['datetime']}; newest={ordered[-1]['datetime']}; gaps={len(gaps)}; invalid_ohlc={invalid}")

    # 3) Repeat using end_date at the previous page's oldest timestamp.
    # The boundary row is intentionally retained so we can measure overlap.
    boundary = ordered[0]["datetime"]
    requests += 1
    status, body, headers = call("time_series", {**common, "end_date": boundary, "outputsize": PAGE_SIZE})
    print(f"\n[3/{MAX_REQUESTS}] backward page HTTP={status} {credit_fields(headers)}")
    if body.get("status") != "ok":
        print(f"response: {json.dumps(body, ensure_ascii=False)}")
        print("RESULT: FAIL — backward page failed")
        return 1
    rows2 = body.get("values") or []
    pages.append(("backward", rows2, headers))
    n2, gaps2, invalid2 = validate_rows(rows2)
    ordered2 = sorted(rows2, key=lambda x: x["datetime"])
    print(f"rows={n2}; oldest={ordered2[0]['datetime']}; newest={ordered2[-1]['datetime']}; gaps={len(gaps2)}; invalid_ohlc={invalid2}")

    set1 = {r["datetime"] for r in rows}
    set2 = {r["datetime"] for r in rows2}
    overlap = sorted(set1 & set2)
    print(f"overlap rows between pages: {len(overlap)}")
    if overlap:
        print(f"overlap range: {overlap[0]} -> {overlap[-1]}")

    # 4) Exact bounded window around the page boundary, without outputsize.
    # This validates combined start/end semantics on a deliberately tiny window.
    boundary_dt = parse_dt(boundary)
    window_start = boundary_dt - timedelta(minutes=9)
    window_end = boundary_dt + timedelta(minutes=9)
    requests += 1
    status, body, headers = call("time_series", {**common, "start_date": fmt_dt(window_start), "end_date": fmt_dt(window_end)})
    print(f"\n[4/{MAX_REQUESTS}] bounded 19-minute window HTTP={status} {credit_fields(headers)}")
    if body.get("status") == "ok":
        tiny = body.get("values") or []
        n3, gaps3, invalid3 = validate_rows(tiny)
        print(f"rows={n3}; requested={fmt_dt(window_start)} -> {fmt_dt(window_end)}; gaps={len(gaps3)}; invalid_ohlc={invalid3}")
        if tiny:
            tiny_ordered = sorted(tiny, key=lambda x: x["datetime"])
            print(f"returned range: {tiny_ordered[0]['datetime']} -> {tiny_ordered[-1]['datetime']}")
    else:
        print(f"response: {json.dumps(body, ensure_ascii=False)}")

    print("\nINTERPRETATION")
    print("- Do not infer complete historical coverage from this experiment.")
    print("- Page overlap determines whether the downloader must de-duplicate boundary candles.")
    print("- Combined start/end behaviour is tested only on a tiny bounded window.")
    print("- Credit headers are recorded for each successful HTTP response when exposed by the provider.")
    print("- No bulk historical data is written to disk.")
    print("- A production downloader must be resumable and provenance-tracked.")
    print(f"\nrequests attempted: {requests}/{MAX_REQUESTS}")
    print("RESULT: PASS — pagination/windowing experiment completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
