#!/usr/bin/env python3
"""Low-credit Twelve Data XAU/USD historical coverage probe.

This is a discovery tool, not a downloader/backtester. It deliberately makes a
small number of requests to establish endpoint behaviour, pagination metadata,
oldest available timestamp, and interval continuity in returned samples.

API key is read only from TWELVE_DATA_API_KEY and is never printed or stored.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://api.twelvedata.com/time_series"
SYMBOL = "XAU/USD"
INTERVAL = "1min"
TIMEZONE = "UTC"
OUTPUTSIZE = 5000


def request(params: dict[str, str | int]) -> tuple[int, dict]:
    url = f"{BASE_URL}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": "xauusd-strategy-a/coverage-probe"})
    try:
        with urlopen(req, timeout=30) as response:
            status = response.status
            payload = json.loads(response.read().decode("utf-8"))
            return status, payload
    except Exception as exc:
        print(f"request error: {exc}", file=sys.stderr)
        return 0, {"status": "error", "message": str(exc)}


def parse_dt(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def main() -> int:
    key = os.getenv("TWELVE_DATA_API_KEY")
    print("Twelve Data XAU/USD historical coverage probe")
    print("=" * 48)
    print(f"symbol:        {SYMBOL}")
    print(f"interval:      {INTERVAL}")
    print(f"timezone:      {TIMEZONE}")
    print(f"outputsize:    {OUTPUTSIZE}")
    print(f"api_key:       {'SET (value hidden)' if key else 'NOT_SET'}")
    if not key:
        print("RESULT: FAIL — set TWELVE_DATA_API_KEY in the environment.")
        return 2

    common = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "timezone": TIMEZONE,
        "apikey": key,
    }

    # Probe 1: explicit earliest timestamp endpoint behaviour.
    status, earliest = request({**common, "outputsize": 1, "start_date": "2000-01-01 00:00:00", "end_date": "2000-01-01 00:01:00"})
    # Probe 2: maximum practical page requested once, with no repeated pagination.
    status2, page = request({**common, "outputsize": OUTPUTSIZE})

    print(f"earliest probe HTTP: {status}")
    if earliest.get("status") == "ok":
        print(f"earliest probe payload: {json.dumps(earliest, ensure_ascii=False)}")
    else:
        print(f"earliest probe response: {json.dumps(earliest, ensure_ascii=False)}")

    print(f"sample page HTTP:     {status2}")
    if page.get("status") != "ok":
        print(f"sample page response: {json.dumps(page, ensure_ascii=False)}")
        print("RESULT: FAIL — historical page request failed.")
        return 1

    values = page.get("values") or []
    print(f"returned rows:        {len(values)}")
    print(f"response status:      {page.get('status')}")
    print(f"provider symbol:      {page.get('meta', {}).get('symbol', 'n/a')}")

    if not values:
        print("RESULT: FAIL — no historical rows returned.")
        return 1

    # Twelve Data normally returns newest first. Sort locally for diagnostics.
    rows = sorted(values, key=lambda r: r["datetime"])
    first = rows[0]["datetime"]
    last = rows[-1]["datetime"]
    print(f"oldest returned UTC:  {first}")
    print(f"newest returned UTC:  {last}")

    gaps = []
    for a, b in zip(rows, rows[1:]):
        delta = parse_dt(b["datetime"]) - parse_dt(a["datetime"])
        if delta.total_seconds() != 60:
            gaps.append((a["datetime"], b["datetime"], int(delta.total_seconds())))

    invalid_ohlc = []
    for r in rows:
        try:
            o, h, l, c = map(float, (r["open"], r["high"], r["low"], r["close"]))
            if not (l <= min(o, c) <= max(o, c) <= h):
                invalid_ohlc.append(r["datetime"])
        except (KeyError, ValueError):
            invalid_ohlc.append(r.get("datetime", "unknown"))

    span_days = (parse_dt(last) - parse_dt(first)).total_seconds() / 86400
    print(f"page span days:      {span_days:.3f}")
    print(f"non-1-minute gaps:   {len(gaps)}")
    print(f"invalid OHLC rows:   {len(invalid_ohlc)}")

    if gaps:
        print("first gaps:")
        for a, b, seconds in gaps[:10]:
            print(f"  {a} -> {b}: {seconds}s")

    # Do not claim full historical coverage. This script only establishes what a
    # single page returns and whether the oldest-date probe is accepted.
    print("\nINTERPRETATION:")
    print("- This is a discovery probe, not evidence of complete 2020-present M1 coverage.")
    print("- A returned page is not sufficient to infer absence/presence of gaps outside that page.")
    print("- Full acquisition should be a separate, resumable, provenance-tracked process.")
    print("- API credit consumption should be measured before bulk extraction.")
    print("\nRESULT: PASS — endpoint/page behaviour successfully probed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
