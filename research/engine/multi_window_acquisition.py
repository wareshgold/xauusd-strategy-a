"""Strategy-neutral multi-window Twelve Data acquisition orchestration."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from .acquire_xauusd import acquire
from .acquisition_request import AcquisitionRequest
from .multi_window_plan import HistoricalWindow, plan_windows


def load_windows(path: Path) -> tuple[HistoricalWindow, ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("windows file must contain a non-empty JSON list")
    windows = tuple(HistoricalWindow(**item) for item in payload)
    return windows


def run(windows: tuple[HistoricalWindow, ...], *, symbol: str, interval: str,
        max_points: int, source_timezone: str, api_key: str, output_dir: Path) -> dict:
    if not api_key:
        raise ValueError("api_key must be supplied outside source control")
    plans = plan_windows(windows, interval=interval, max_points=max_points)
    results = []
    for plan in plans:
        chunk_results = []
        for chunk in plan.chunks:
            chunk_dir = output_dir / plan.window.name / f"chunk-{chunk.index:04d}"
            request = AcquisitionRequest(
                symbol=symbol, interval=interval, outputsize=max_points,
                start_date=chunk.start_utc, end_date=chunk.end_utc,
                source_timezone=source_timezone,
            )
            manifest, artifact = acquire(request, api_key=api_key, output_dir=chunk_dir)
            chunk_results.append({
                "index": chunk.index,
                "start_utc": chunk.start_utc,
                "end_utc": chunk.end_utc,
                "quality_status": artifact.quality_status,
                "row_count": artifact.row_count,
                "raw_sha256": artifact.raw_sha256,
                "normalized_sha256": artifact.normalized_sha256,
                "artifact_sha256": artifact.fingerprint(),
            })
        results.append({"window": plan.window.name, "chunks": chunk_results})

    summary = {"symbol": symbol, "interval": interval, "source_timezone": source_timezone, "windows": results}
    canonical = json.dumps(summary, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    summary["dataset_sha256"] = hashlib.sha256(canonical).hexdigest()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "dataset_manifest.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Acquire deterministic multi-window XAU/USD history")
    parser.add_argument("--windows-file", required=True)
    parser.add_argument("--symbol", default="XAU/USD")
    parser.add_argument("--interval", default="1min")
    parser.add_argument("--max-points", type=int, default=5000)
    parser.add_argument("--source-timezone", required=True)
    parser.add_argument("--output-dir", default="data/acquired/xauusd-history")
    parser.add_argument("--api-key-env", default="TWELVE_DATA_API_KEY")
    args = parser.parse_args()
    key = os.environ.get(args.api_key_env)
    if not key:
        raise SystemExit(f"missing API key environment variable: {args.api_key_env}")
    summary = run(load_windows(Path(args.windows_file)), symbol=args.symbol, interval=args.interval,
                  max_points=args.max_points, source_timezone=args.source_timezone,
                  api_key=key, output_dir=Path(args.output_dir))
    statuses = [chunk["quality_status"] for window in summary["windows"] for chunk in window["chunks"]]
    status = "PASS" if statuses and all(s == "PASS" for s in statuses) else "BLOCKED"
    print(f"STATUS: {status}")
    print(f"WINDOWS: {len(summary['windows'])}")
    print(f"CHUNKS: {sum(len(w['chunks']) for w in summary['windows'])}")
    print(f"DATASET_SHA256: {summary['dataset_sha256']}")
    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
