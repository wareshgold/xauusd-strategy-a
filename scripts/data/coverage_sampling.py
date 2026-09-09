#!/usr/bin/env python3
"""Sample historical XAU/USD M1 windows to characterize coverage without bulk download.

This is a discovery probe. It does not claim complete historical coverage and does
not contain strategy logic. It uses explicit UTC windows so each result is
reproducible and records provider response ranges, continuity, and OHLC validity.

API key is read only from TWELVE_DATA_API_KEY and is never printed or stored.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://api.twelvedata.com/time_series"
SYMBOL = "XAU/USD"
INTERVAL = "1min"
TIMEZONE = "UTC"

DEFAULT_WINDOWS = [
    ("2020-04-06 06:40:00", "2020-04-06 12:00:00"),
    ("2022-01-04 00:00:00", "2022-01-04 06:00:00"),
    ("2024-01-04 00:00:00", "2024-01-04 06:00:00"),
    ("2025-01-06 00:00:00", "2025-01-06 06:00:00"),
    ("2026-09-04 00:00:00", "2026-09-04 06:00:00"),
]


def parse_dt(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def request(params: dict[str, str | int]) -> tuple[int, dict, dict[str, str]]:
    url = f"{BASE_URL}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": "xauusd-strategy-a/coverage-sampling"})
    try:
        with urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return response.status, payload, {k.lower(): v for k, v in response.headers.items()}
    except Exception as exc:
        return 0, {"status": "error", "message": str(exc)}, {}


def inspect(values: list[dict]) -> dict:
    rows = sorted(values, key=lambda r: r["datetime"])
    gaps = []
    invalid = []
    for a, b in zip(rows, rows[1:]):
        delta = int((parse_dt(b["datetime"]) - parse_dt(a["datetime"])).total_seconds())
        if delta != 60:
            gaps.append({"from": a["datetime"], "to": b["datetime"], "seconds": delta})
    for r in rows:
        try:
            o, h, l, c = map(float, (r["open"], r["high"], r["low"], r["close"]))
            if not (l <= min(o, c) <= max(o, c) <= h):
                invalid.append(r["datetime"])
        except (KeyError, ValueError, TypeError):
            invalid.append(r.get("datetime", "unknown"))
    return {
        "rows": len(rows),
        "oldest": rows[0]["datetime"] if rows else None,
        "newest": rows[-1]["datetime"] if rows else None,
        "non_1min_gaps": len(gaps),
        "gap_examples": gaps[:10],
        "invalid_ohlc": len(invalid),
        "invalid_examples": invalid[:10],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="docs/data/TWELVE_DATA_COVERAGE_SAMPLING_2026-09-09.md")
    args = ap.parse_args()

    key = os.getenv("TWELVE_DATA_API_KEY")
    print("Twelve Data XAU/USD M1 coverage sampling probe")
    print("=" * 50)
    print(f"windows: {len(DEFAULT_WINDOWS)}")
    print(f"api_key: {'SET (value hidden)' if key else 'NOT_SET'}")
    if not key:
        return 2

    results = []
    for i, (start_s, end_s) in enumerate(DEFAULT_WINDOWS, 1):
        start, end = parse_dt(start_s), parse_dt(end_s)
        params = {
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "timezone": TIMEZONE,
            "start_date": start_s,
            "end_date": end_s,
            "apikey": key,
        }
        http, payload, headers = request(params)
        used = headers.get("api-credits-used")
        left = headers.get("api-credits-left")
        print(f"[{i}/{len(DEFAULT_WINDOWS)}] HTTP={http} credits_used={used or 'n/a'} credits_left={left or 'n/a'} {start_s} -> {end_s}")
        if payload.get("status") != "ok":
            print(json.dumps(payload, ensure_ascii=False))
            return 3
        values = payload.get("values") or []
        if not values:
            return 4
        check = inspect(values)
        print(f"  rows={check['rows']} oldest={check['oldest']} newest={check['newest']} gaps={check['non_1min_gaps']} invalid={check['invalid_ohlc']}")
        results.append({
            "requested_start_utc": start_s,
            "requested_end_utc": end_s,
            "http_status": http,
            "api_credits_used": used,
            "api_credits_left": left,
            **check,
        })

    lines = [
        "# Twelve Data XAU/USD M1 Coverage Sampling",
        "",
        "Status: **sampling probe only** — not proof of complete historical coverage.",
        "",
        "The probe samples explicit UTC windows across the available history to detect whether the provider returns data in those periods and whether the returned windows are internally continuous and OHLC-valid.",
        "",
        "## Results",
        "",
        "| Requested UTC window | Rows | Returned range | Gaps | Invalid OHLC | Credits used |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for r in results:
        lines.append(f"| {r['requested_start_utc']} → {r['requested_end_utc']} | {r['rows']} | {r['oldest']} → {r['newest']} | {r['non_1min_gaps']} | {r['invalid_ohlc']} | {r['api_credits_used'] or 'n/a'} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- Successful samples establish availability only for the sampled windows.",
        "- A zero-gap result applies only inside each returned sample; it does not establish global continuity.",
        "- The earliest timestamp must be treated as a provider boundary, not as evidence that every minute after it exists.",
        "- Full historical acquisition remains a separate resumable process with manifests, checkpoints, de-duplication, and SHA-256 provenance.",
        "- Strategy rules are intentionally absent from this probe.",
    ]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"report: {out}")
    print("RESULT: PASS — sampled windows returned successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
