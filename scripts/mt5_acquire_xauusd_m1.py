#!/usr/bin/env python3
"""Acquire an exact UTC XAUUSD.ecn M1 interval from a local MT5 terminal.

This tool is acquisition/provenance only. It does not calculate SP2L geometry,
signals, entries, exits, or trade decisions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import MetaTrader5 as mt5
except ImportError as exc:  # pragma: no cover - environment dependent
    raise SystemExit("MetaTrader5 Python package is required") from exc


SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1
PROVIDER = "MetaTrader5 terminal API"
SERVER_EXPECTED = "OtetGroup-MT5"


def parse_utc(value: str) -> datetime:
    text = value.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"timestamp must include UTC offset: {value}")
    return dt.astimezone(timezone.utc).replace(second=0, microsecond=0)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_rows(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    invalid = []
    gaps = []
    for index, row in enumerate(rows):
        try:
            ts = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
            numbers = [float(row[k]) for k in ("open", "high", "low", "close", "tick_volume")]
            if ts.tzinfo is None or any(not (x == x) for x in numbers):
                invalid.append({"index": index, "reason": "invalid_timestamp_or_number"})
            if not (float(row["high"]) >= max(float(row["open"]), float(row["close"])) and float(row["low"]) <= min(float(row["open"]), float(row["close"])) and float(row["high"]) >= float(row["low"])):
                invalid.append({"index": index, "reason": "invalid_ohlc"})
        except (KeyError, TypeError, ValueError):
            invalid.append({"index": index, "reason": "malformed_row"})
        if index:
            previous = datetime.fromisoformat(rows[index - 1]["timestamp"].replace("Z", "+00:00"))
            current = datetime.fromisoformat(rows[index]["timestamp"].replace("Z", "+00:00"))
            diff_minutes = (current - previous).total_seconds() / 60
            if diff_minutes != 1:
                gaps.append({
                    "from": rows[index - 1]["timestamp"],
                    "to": rows[index]["timestamp"],
                    "minutes": diff_minutes,
                    "missing_bars": max(0, int(round(diff_minutes)) - 1) if diff_minutes > 1 else 0,
                    "kind": "gap" if diff_minutes > 1 else "non_chronological",
                })
    return invalid, gaps


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="UTC ISO timestamp, e.g. 2026-04-01T00:00:00Z")
    parser.add_argument("--end", required=True, help="UTC ISO timestamp, e.g. 2026-05-01T00:00:00Z")
    parser.add_argument("--out-dir", default="data/mt5-acquisition", help="Artifact output directory")
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--config-id", default="sp2l-strategy-a-frozen-current")
    parser.add_argument("--runner-revision", default="unknown")
    args = parser.parse_args()

    start = parse_utc(args.start)
    end = parse_utc(args.end)
    if end <= start:
        raise SystemExit("end must be after start")

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        if terminal is None:
            raise SystemExit("MT5 terminal_info() unavailable")
        server = getattr(account, "server", None) if account is not None else None
        if server and server != SERVER_EXPECTED:
            raise SystemExit(f"unexpected MT5 server: {server!r}; expected {SERVER_EXPECTED!r}")
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"cannot select {SYMBOL}: {mt5.last_error()}")

        rates = mt5.copy_rates_range(SYMBOL, TIMEFRAME, start, end)
        if rates is None:
            raise SystemExit(f"copy_rates_range failed: {mt5.last_error()}")
        if len(rates) == 0:
            raise SystemExit("MT5 returned zero bars")

        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        artifact = out_dir / f"{args.dataset_id}.csv"
        manifest_path = out_dir / f"{args.dataset_id}.manifest.json"

        rows = []
        for item in rates:
            ts = datetime.fromtimestamp(int(item["time"]), tz=timezone.utc)
            rows.append({
                "timestamp": ts.isoformat().replace("+00:00", "Z"),
                "open": repr(float(item["open"])),
                "high": repr(float(item["high"])),
                "low": repr(float(item["low"])),
                "close": repr(float(item["close"])),
                "tick_volume": repr(int(item["tick_volume"])),
                "spread": repr(int(item["spread"])),
                "real_volume": repr(int(item["real_volume"])),
            })

        invalid, gaps = audit_rows(rows)
        chronological = all(not g["kind"] == "non_chronological" for g in gaps)
        first = rows[0]["timestamp"]
        last = rows[-1]["timestamp"]

        with artifact.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

        artifact_hash = sha256_file(artifact)
        retrieval_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        required_ok = all([args.dataset_id, SYMBOL, "M1", first, last, artifact_hash, args.config_id])
        audit_pass = required_ok and len(invalid) == 0 and chronological and len(gaps) == 0

        manifest = {
            "dataset_id": args.dataset_id,
            "provider": PROVIDER,
            "terminal": getattr(terminal, "name", None),
            "server": server,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "requested_interval_utc": {"start": start.isoformat().replace("+00:00", "Z"), "end": end.isoformat().replace("+00:00", "Z")},
            "actual_first_utc": first,
            "actual_last_utc": last,
            "requested_bar_count": int((end - start).total_seconds() // 60) + 1,
            "actual_bar_count": len(rows),
            "gap_count": len(gaps),
            "gap_ranges": gaps,
            "invalid_row_count": len(invalid),
            "invalid_rows": invalid,
            "retrieval_timestamp_utc": retrieval_time,
            "artifact": artifact.name,
            "artifact_sha256": artifact_hash,
            "acquisition_code_revision": "working-tree",
            "downstream_runner_revision": args.runner_revision,
            "frozen_configuration_id": args.config_id,
            "audit_status": "AUDITED_PASS" if audit_pass else "AUDITED_FAIL",
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        print(json.dumps(manifest, indent=2))
        return 0 if audit_pass else 2
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    sys.exit(main())
