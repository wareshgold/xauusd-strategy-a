#!/usr/bin/env python3
"""Safe Twelve Data XAU/USD discovery check.

Reads TWELVE_DATA_API_KEY from the environment and never prints the key.
The script intentionally makes only two small API requests by default:
  1) earliest_timestamp for XAU/USD M1
  2) a 5-row UTC M1 sample

This is a discovery/diagnostic tool, not the historical downloader.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any

BASE_URL = "https://api.twelvedata.com"
SYMBOL = "XAU/USD"
INTERVAL = "1min"


def request_json(path: str, params: dict[str, str]) -> dict[str, Any]:
    url = f"{BASE_URL}{path}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "xauusd-strategy-a/twelvedata-discovery-v1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body[:500]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError("Unexpected API response type")
    return payload


def parse_dt(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def inspect_sample(values: list[dict[str, Any]]) -> dict[str, Any]:
    # Twelve Data returns newest first; normalize only for diagnostics.
    rows = sorted(values, key=lambda row: row.get("datetime", ""))
    timestamps = [parse_dt(row["datetime"]) for row in rows]
    gaps = []
    for previous, current in zip(timestamps, timestamps[1:]):
        minutes = int((current - previous).total_seconds() / 60)
        if minutes != 1:
            gaps.append(
                {
                    "from": previous.strftime("%Y-%m-%d %H:%M:%S"),
                    "to": current.strftime("%Y-%m-%d %H:%M:%S"),
                    "minutes": minutes,
                }
            )

    invalid_ohlc = []
    for row in rows:
        try:
            o = float(row["open"])
            h = float(row["high"])
            l = float(row["low"])
            c = float(row["close"])
            if not (l <= o <= h and l <= c <= h):
                invalid_ohlc.append(row["datetime"])
        except (KeyError, TypeError, ValueError):
            invalid_ohlc.append(row.get("datetime", "<missing datetime>"))

    return {
        "rows": len(rows),
        "oldest_sample": rows[0].get("datetime") if rows else None,
        "newest_sample": rows[-1].get("datetime") if rows else None,
        "chronological_order_after_normalization": True,
        "non_one_minute_intervals": gaps,
        "invalid_ohlc_rows": invalid_ohlc,
        "sample_rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-size", type=int, default=5)
    args = parser.parse_args()

    if not 1 <= args.sample_size <= 100:
        parser.error("--sample-size must be between 1 and 100")

    api_key = os.getenv("TWELVE_DATA_API_KEY")
    if not api_key:
        print("ERROR: TWELVE_DATA_API_KEY is not set.", file=sys.stderr)
        return 2

    common = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "apikey": api_key,
    }

    print("Twelve Data XAU/USD discovery")
    print("=" * 34)
    print(f"symbol:        {SYMBOL}")
    print(f"interval:      {INTERVAL}")
    print("timezone:      UTC")
    print("api_key:       SET (value hidden)")

    try:
        earliest = request_json(
            "/earliest_timestamp",
            {**common, "timezone": "UTC"},
        )
        print(f"earliest_timestamp status: {earliest.get('status', 'n/a')}")
        if earliest.get("status") == "ok":
            print(f"earliest_timestamp:        {earliest.get('datetime', earliest.get('timestamp', 'n/a'))}")
        else:
            print(f"earliest_timestamp response: {json.dumps(earliest, ensure_ascii=False)}")

        sample = request_json(
            "/time_series",
            {
                **common,
                "outputsize": str(args.sample_size),
                "timezone": "UTC",
            },
        )
        print(f"sample status:             {sample.get('status', 'n/a')}")
        if sample.get("status") != "ok":
            print(f"sample response:           {json.dumps(sample, ensure_ascii=False)}")
            return 1

        meta = sample.get("meta", {})
        values = sample.get("values", [])
        print(f"provider symbol:           {meta.get('symbol', 'n/a')}")
        print(f"base/quote:                {meta.get('currency_base', 'n/a')} / {meta.get('currency_quote', 'n/a')}")
        print(f"asset type:                {meta.get('type', 'n/a')}")

        report = inspect_sample(values)
        print(f"sample rows:               {report['rows']}")
        print(f"oldest sample UTC:         {report['oldest_sample']}")
        print(f"newest sample UTC:         {report['newest_sample']}")
        print(f"OHLC invalid rows:         {len(report['invalid_ohlc_rows'])}")
        print(f"non-1-minute intervals:    {len(report['non_one_minute_intervals'])}")
        print("sample values:")
        for row in report["sample_rows"]:
            print("  " + json.dumps(row, ensure_ascii=False, sort_keys=True))

        print()
        print("DISCOVERY RESULT: PASS")
        print("No API key value was printed or persisted by this script.")
        return 0

    except RuntimeError as exc:
        print(f"DISCOVERY RESULT: FAIL — {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
