"""One-shot, strategy-neutral Twelve Data XAU/USD M1 acquisition harness.

Requires TWELVE_DATA_API_KEY in the runtime environment. The key is never
written to disk or repository. The response is preserved as received, then
parsed through the existing provider adapter and audited separately.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from .providers import parse_twelve_data_time_series
from .quality_audit import audit_candles


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def fetch_payload(symbol: str, interval: str, start: str, end: str, timezone_name: str) -> tuple[dict, str]:
    key = os.environ.get("TWELVE_DATA_API_KEY")
    if not key:
        raise RuntimeError("TWELVE_DATA_API_KEY is required; no credential is read from repository files")
    params = urllib.parse.urlencode({
        "symbol": symbol,
        "interval": interval,
        "start_date": start,
        "end_date": end,
        "timezone": timezone_name,
        "apikey": key,
        "format": "JSON",
    })
    url = "https://api.twelvedata.com/time_series?" + params
    request = urllib.request.Request(url, headers={"User-Agent": "sp2l-research/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
    payload = json.loads(raw.decode("utf-8"))
    return payload, raw.decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="UTC start, e.g. 2026-09-08 12:00:00")
    parser.add_argument("--end", required=True, help="UTC end, e.g. 2026-09-08 12:10:00")
    parser.add_argument("--out", default="artifacts/g43_real_sample")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    payload, raw_text = fetch_payload("XAU/USD", "1min", args.start, args.end, "UTC")

    raw_bytes = raw_text.encode("utf-8")
    (out / "raw_response.json").write_bytes(raw_bytes)
    (out / "raw_sha256.txt").write_text(hashlib.sha256(raw_bytes).hexdigest() + "\n", encoding="utf-8")

    batch = parse_twelve_data_time_series(payload, "XAU/USD", "1min", source_timezone="UTC")
    candles = tuple(sorted(batch.candles, key=lambda c: c.timestamp))
    audit = audit_candles(candles, 60)
    normalized = [
        {"timestamp": c.timestamp.isoformat(), "open": c.open, "high": c.high, "low": c.low, "close": c.close,
         "symbol": c.symbol, "timeframe": c.timeframe}
        for c in candles
    ]
    normalized_bytes = canonical_json_bytes(normalized)
    (out / "normalized.json").write_bytes(normalized_bytes)
    normalized_sha = hashlib.sha256(normalized_bytes).hexdigest()
    (out / "normalized_sha256.txt").write_text(normalized_sha + "\n", encoding="utf-8")

    actual_first = candles[0].timestamp.isoformat() if candles else None
    actual_last = candles[-1].timestamp.isoformat() if candles else None
    manifest = {
        "gate": "G44",
        "provider": batch.provider,
        "instrument": batch.symbol,
        "interval": batch.interval,
        "requested_start_utc": args.start,
        "requested_end_utc": args.end,
        "actual_first_utc": actual_first,
        "actual_last_utc": actual_last,
        "row_count": len(candles),
        "retrieved_at_utc": retrieved_at,
        "source_timezone": batch.source_timezone,
        "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "normalized_sha256": normalized_sha,
        "quality": audit.__dict__,
        "strategy_a_execution": "FORBIDDEN_AT_G44",
    }
    (out / "manifest.json").write_bytes(canonical_json_bytes(manifest))
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if audit.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
