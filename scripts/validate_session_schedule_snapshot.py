#!/usr/bin/env python3
"""Validate raw MQL5 session-schedule diagnostic output.

Research-only. This parser validates structure and provenance; it does not
infer historical calendars, DST, holidays, gap semantics, or timezone shifts.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DAYS = {"MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"}
LINE_RE = re.compile(
    r"^(QUOTE|TRADE)\|([A-Z]+)\|session_index=(\d+)\|from=(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\|to=(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\|from_epoch=(-?\d+)\|to_epoch=(-?\d+)$"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    text = args.input.read_text(encoding="utf-8")
    records = []
    errors = []
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not (line.startswith("QUOTE|") or line.startswith("TRADE|")):
            continue
        m = LINE_RE.match(line)
        if not m:
            errors.append({"line": line_no, "reason": "malformed_session_line", "raw": line})
            continue
        kind, day, index, from_text, to_text, from_epoch, to_epoch = m.groups()
        if day not in DAYS:
            errors.append({"line": line_no, "reason": "invalid_day", "value": day})
        records.append({
            "line": line_no,
            "kind": kind,
            "day": day,
            "session_index": int(index),
            "from": from_text,
            "to": to_text,
            "from_epoch": int(from_epoch),
            "to_epoch": int(to_epoch),
            "raw": line,
        })

    by_key = {}
    for record in records:
        key = (record["kind"], record["day"])
        by_key.setdefault(key, []).append(record)

    continuity_errors = []
    for key, rows in by_key.items():
        expected = list(range(len(rows)))
        actual = [r["session_index"] for r in rows]
        if actual != expected:
            continuity_errors.append({"key": key, "expected": expected, "actual": actual})

    metadata = {
        line.split("=", 1)[0]: line.split("=", 1)[1]
        for line in text.splitlines()
        if "=" in line and line.split("=", 1)[0] in {"terminal", "company", "server", "symbol"}
    }
    required_metadata = {"terminal", "company", "server", "symbol"}
    missing_metadata = sorted(required_metadata - metadata.keys())
    if missing_metadata:
        errors.append({"reason": "missing_metadata", "fields": missing_metadata})

    result = {
        "status": "VALID_CURRENT_SNAPSHOT" if records and not errors and not continuity_errors else "INVALID_OR_INCOMPLETE_SNAPSHOT",
        "scope": "CURRENT_TERMINAL_OBSERVATION_ONLY",
        "metadata": metadata,
        "record_count": len(records),
        "quote_record_count": sum(r["kind"] == "QUOTE" for r in records),
        "trade_record_count": sum(r["kind"] == "TRADE" for r in records),
        "records": records,
        "continuity_errors": continuity_errors,
        "errors": errors,
        "prohibitions": [
            "DO_NOT_INFER_HISTORICAL_CALENDAR",
            "DO_NOT_INFER_DST",
            "DO_NOT_INFER_HOLIDAYS",
            "DO_NOT_CLASSIFY_DATASET_GAPS_AS_SESSION_CLOSURES",
            "DO_NOT_SHIFT_CANONICAL_MT5_BAR_TIMESTAMPS",
        ],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "VALID_CURRENT_SNAPSHOT" else 2


if __name__ == "__main__":
    sys.exit(main())
