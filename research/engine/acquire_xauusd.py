"""Strategy-neutral Twelve Data acquisition runner for reproducible XAU/USD samples.

API credentials are read only from the environment and are never printed.
This module performs no Strategy A detection or trading decision.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request

from .acquisition_manifest import AcquisitionManifest
from .acquisition_request import AcquisitionRequest
from .dataset_artifact import DatasetArtifact, canonicalize_json
from .provider_http import read_with_retries
from .providers import parse_twelve_data_time_series
from .quality_audit import audit_candles

API_URL = "https://api.twelvedata.com/time_series"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def acquire(request: AcquisitionRequest, *, api_key: str, output_dir: Path) -> tuple[AcquisitionManifest, DatasetArtifact]:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    normalized_dir = output_dir / "normalized"
    raw_dir.mkdir(parents=True, exist_ok=True)
    normalized_dir.mkdir(parents=True, exist_ok=True)

    params = request.query_params(api_key)
    url = f"{API_URL}?{urlencode(params)}"
    http_request = Request(url, headers={"User-Agent": "sp2l-research-data-acquisition/1.0"})
    retrieval_timestamp = _utc_now()
    raw_bytes = read_with_retries(http_request, timeout=30)

    raw_sha = hashlib.sha256(raw_bytes).hexdigest()
    raw_path = raw_dir / "time_series.json"
    raw_path.write_bytes(raw_bytes)

    payload = json.loads(raw_bytes.decode("utf-8"))
    batch = parse_twelve_data_time_series(
        payload,
        requested_symbol=request.symbol,
        requested_interval=request.interval,
        source_timezone=request.source_timezone,
    )
    ordered = tuple(sorted(batch.candles, key=lambda candle: candle.timestamp))
    expected_seconds = {"1min": 60, "5min": 300, "15min": 900, "30min": 1800, "1h": 3600}.get(request.interval)
    if expected_seconds is None:
        raise ValueError(f"unsupported interval for quality audit: {request.interval}")
    audit = audit_candles(ordered, expected_seconds)

    normalized = [
        {"datetime": c.timestamp.isoformat(), "open": c.open, "high": c.high, "low": c.low, "close": c.close,
         "symbol": c.symbol, "timeframe": c.timeframe}
        for c in ordered
    ]
    normalized_bytes = canonicalize_json(normalized)
    normalized_sha = hashlib.sha256(normalized_bytes).hexdigest()
    (normalized_dir / "candles.json").write_bytes(normalized_bytes)

    actual_start = ordered[0].timestamp.isoformat() if ordered else None
    actual_end = ordered[-1].timestamp.isoformat() if ordered else None
    source_version = str(batch.retrieval_metadata.get("meta", {}).get("exchange_timezone") or batch.retrieval_metadata.get("meta", {}).get("type") or "unspecified")
    response_metadata = dict(batch.retrieval_metadata)
    response_metadata["raw_sha256"] = raw_sha
    response_metadata["normalized_sha256"] = normalized_sha
    response_metadata["quality_audit"] = {
        "row_count": audit.row_count,
        "duplicate_timestamps": audit.duplicate_timestamps,
        "non_monotonic_pairs": audit.non_monotonic_pairs,
        "cadence_mode_seconds": audit.cadence_mode_seconds,
        "cadence_anomalies": audit.cadence_anomalies,
        "invalid_ohlc_rows": audit.invalid_ohlc_rows,
    }

    status = "PASS" if audit.passed else "BLOCKED"
    manifest = AcquisitionManifest(
        provider="Twelve Data", instrument=batch.symbol, interval=batch.interval,
        requested_start_utc=request.start_date or "UNSPECIFIED", requested_end_utc=request.end_date or "UNSPECIFIED",
        actual_first_timestamp_utc=actual_start, actual_last_timestamp_utc=actual_end,
        row_count=len(ordered), request_timestamp_utc=retrieval_timestamp,
        source_timezone=batch.source_timezone, source_version=source_version,
        raw_sha256=raw_sha, normalized_sha256=normalized_sha, response_metadata=response_metadata,
    )
    artifact = DatasetArtifact(
        provider="Twelve Data", instrument=batch.symbol, interval=batch.interval,
        requested_start_utc=request.start_date or None, requested_end_utc=request.end_date or None,
        retrieval_timestamp_utc=retrieval_timestamp, source_timezone=batch.source_timezone,
        source_version=source_version, row_count=len(ordered), actual_start_utc=actual_start,
        actual_end_utc=actual_end, raw_sha256=raw_sha, normalized_sha256=normalized_sha,
        quality_status=status,
    )
    (output_dir / "acquisition_manifest.json").write_text(manifest.canonical_json() + "\n", encoding="utf-8")
    (output_dir / "dataset_artifact.json").write_text(artifact.canonical_json() + "\n", encoding="utf-8")
    return manifest, artifact


def main() -> int:
    parser = argparse.ArgumentParser(description="Acquire a strategy-neutral XAU/USD sample from Twelve Data")
    parser.add_argument("--symbol", default="XAU/USD")
    parser.add_argument("--interval", default="1min")
    parser.add_argument("--outputsize", type=int, default=5000)
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--source-timezone", required=True)
    parser.add_argument("--output-dir", default="data/acquired/xauusd")
    parser.add_argument("--api-key-env", default="TWELVE_DATA_API_KEY")
    args = parser.parse_args()
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"missing API key environment variable: {args.api_key_env}")
    request = AcquisitionRequest(args.symbol, args.interval, args.outputsize, args.start_date, args.end_date, args.source_timezone)
    _, artifact = acquire(request, api_key=api_key, output_dir=Path(args.output_dir))
    print(f"STATUS: {artifact.quality_status}")
    print(f"ROWS: {artifact.row_count}")
    print(f"UTC: {artifact.actual_start_utc} -> {artifact.actual_end_utc}")
    print(f"RAW_SHA256: {artifact.raw_sha256}")
    print(f"NORMALIZED_SHA256: {artifact.normalized_sha256}")
    print(f"ARTIFACT_SHA256: {artifact.fingerprint()}")
    return 0 if artifact.quality_status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
