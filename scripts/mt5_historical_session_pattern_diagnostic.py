#!/usr/bin/env python3
"""Summarize historical MT5 session-boundary evidence from an audit manifest.

This tool is diagnostic only. It does not redefine a session calendar, repair
missing bars, or promote inferred boundaries to canonical historical rules.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def load_json(path: Path) -> dict:
    raw = path.read_bytes()
    for enc in ("utf-8", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            return json.loads(raw.decode(enc))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    raise SystemExit(f"cannot decode JSON manifest: {path}")


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("manifest")
    args = p.parse_args()

    d = load_json(Path(args.manifest))
    missing = d.get("missing_expected_timestamps", [])
    jumps = d.get("invalid_timestamp_jumps", [])

    by_date = Counter(dt(x).date().isoformat() for x in missing)
    by_minute = Counter(dt(x).strftime("%H:%M") for x in missing)
    print(f"dataset={d.get('dataset_id')}")
    print(f"audit_status={d.get('audit_status')}")
    print(f"missing={len(missing)}")
    print(f"missing_dates={len(by_date)}")
    print(f"top_missing_dates={by_date.most_common(10)}")
    print(f"top_missing_minutes={by_minute.most_common(15)}")
    print(f"invalid_jumps={len(jumps)}")
    for j in jumps[:20]:
        print(f"jump={j['from']} -> {j['to']} ({j['delta_seconds']}s)")
    print("historical_calendar_status=UNRESOLVED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
