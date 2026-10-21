from __future__ import annotations

"""Read-only descriptive summary for an XAUUSD tick CSV.GZ.

Reports raw-file-order descriptions only. It does not sort/deduplicate rows,
infer undocumented flag meanings, or model executable tick paths.
"""

import argparse
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def _utc_day(raw: str | None) -> str | None:
    try:
        parsed = datetime.fromisoformat((raw or "").strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc).date().isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def summarize_dataset(source: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual_hash = _sha256(source)
    actual_size = source.stat().st_size
    row_count = 0
    valid_quote_count = 0
    invalid_quote_count = 0
    crossed_quote_count = 0
    spread_count = 0
    spread_sum = 0.0
    spread_min: float | None = None
    spread_max: float | None = None
    spread_counts: Counter[str] = Counter()
    flag_counts: Counter[str] = Counter()
    rows_by_day: Counter[str] = Counter()
    bid_changes_vs_previous_input_row = 0
    ask_changes_vs_previous_input_row = 0
    both_quote_changed_vs_previous_input_row = 0
    previous_bid: float | None = None
    previous_ask: float | None = None
    columns: list[str] = []

    with gzip.open(source, "rt", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = list(reader.fieldnames or [])
        for row in reader:
            row_count += 1
            day = _utc_day(row.get("time_utc"))
            if day is not None:
                rows_by_day[day] += 1
            raw_flags = (row.get("flags") or "").strip()
            if raw_flags:
                flag_counts[raw_flags] += 1

            try:
                bid = float(row.get("bid") or "")
                ask = float(row.get("ask") or "")
            except (TypeError, ValueError):
                invalid_quote_count += 1
                previous_bid = previous_ask = None
                continue
            if not (math.isfinite(bid) and math.isfinite(ask) and bid > 0 and ask > 0):
                invalid_quote_count += 1
                previous_bid = previous_ask = None
                continue
            if ask < bid:
                crossed_quote_count += 1
                previous_bid, previous_ask = bid, ask
                continue

            valid_quote_count += 1
            spread = round(ask - bid, 10)
            spread_count += 1
            spread_sum += spread
            spread_min = spread if spread_min is None else min(spread_min, spread)
            spread_max = spread if spread_max is None else max(spread_max, spread)
            spread_counts[f"{spread:.10f}".rstrip("0").rstrip(".")] += 1

            if previous_bid is not None and previous_bid != bid:
                bid_changes_vs_previous_input_row += 1
            if previous_ask is not None and previous_ask != ask:
                ask_changes_vs_previous_input_row += 1
            if previous_bid is not None and previous_ask is not None and previous_bid != bid and previous_ask != ask:
                both_quote_changed_vs_previous_input_row += 1
            previous_bid, previous_ask = bid, ask

    result = {
        "summary_schema_version": 1,
        "summary_type": "READ_ONLY_XAUUSD_TICK_DESCRIPTIVE_SUMMARY",
        "source_artifact": str(source),
        "source_manifest": str(manifest_path),
        "source_sha256": actual_hash,
        "manifest_sha256": manifest.get("artifact_sha256"),
        "sha256_matches_manifest": actual_hash.lower() == str(manifest.get("artifact_sha256", "")).lower(),
        "source_size_bytes": actual_size,
        "manifest_size_bytes": manifest.get("artifact_size_bytes"),
        "size_matches_manifest": actual_size == manifest.get("artifact_size_bytes"),
        "csv_columns": columns,
        "csv_row_count": row_count,
        "manifest_tick_count": manifest.get("tick_count"),
        "row_count_matches_manifest": row_count == manifest.get("tick_count"),
        "utc_day_row_counts": dict(sorted(rows_by_day.items())),
        "quote_rows": {
            "valid_non_crossed_bidask": valid_quote_count,
            "missing_or_invalid_bidask": invalid_quote_count,
            "crossed_bidask": crossed_quote_count,
        },
        "spread": {
            "count": spread_count,
            "minimum": spread_min,
            "maximum": spread_max,
            "mean": spread_sum / spread_count if spread_count else None,
            "exact_value_counts": dict(sorted(spread_counts.items(), key=lambda item: float(item[0]))),
        },
        "flag_value_counts": dict(sorted(flag_counts.items(), key=lambda item: int(item[0]))),
        "input_row_order_diagnostics": {
            "bid_changes_vs_previous_input_row": bid_changes_vs_previous_input_row,
            "ask_changes_vs_previous_input_row": ask_changes_vs_previous_input_row,
            "both_bid_and_ask_changed_vs_previous_input_row": both_quote_changed_vs_previous_input_row,
            "warning": "These compare adjacent CSV rows only; equal-millisecond event order is unresolved and this is not an executable-path reconstruction.",
        },
        "eligibility": "DESCRIPTIVE_ONLY_NOT_EXECUTION_CERTIFICATION",
        "interpretation": (
            "Read-only descriptive statistics. Source rows were not sorted, deduplicated, repaired, or rewritten. "
            "Flags are reported as raw values; undocumented bit meanings are not inferred. "
            "No quantiles, fills, stop/target outcomes, or strategy signals are produced."
        ),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Existing .csv.gz dataset")
    parser.add_argument("--manifest", required=True, type=Path, help="Existing manifest JSON")
    parser.add_argument("--output", required=True, type=Path, help="New JSON report path; must not exist")
    args = parser.parse_args()
    if args.output.exists():
        print(f"SUMMARY_REFUSED_OUTPUT_EXISTS: {args.output}", file=sys.stderr)
        return 4
    try:
        result = summarize_dataset(args.input, args.manifest)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    except Exception as exc:
        print(f"SUMMARY_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    # Descriptive completion is not an integrity or execution eligibility gate.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
