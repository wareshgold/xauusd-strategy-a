"""Append-only signal/trade journal for the live gateway.

Storage:
- runtime/journal/signals.jsonl
- runtime/journal/trades.jsonl
- runtime/journal/market_snapshots.jsonl
- runtime/journal/report_log.jsonl (Telegram report delivery log)

JSONL is the canonical raw audit layer. Excel/CSV exports are derived views.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path("runtime/journal")
SIGNALS = ROOT / "signals.jsonl"
TRADES = ROOT / "trades.jsonl"
SNAPSHOTS = ROOT / "market_snapshots.jsonl"
REPORT_LOG = ROOT / "report_log.jsonl"


def _append(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    record = dict(record)
    record.setdefault("recorded_at_utc", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def record_signal(record: dict[str, Any]) -> None:
    _append(SIGNALS, record)


def record_trade(record: dict[str, Any]) -> None:
    _append(TRADES, record)


def record_market_snapshot(record: dict[str, Any]) -> None:
    _append(SNAPSHOTS, record)


def record_report(record: dict[str, Any]) -> None:
    """Append one report-delivery record (timestamp, type, response, success)."""
    _append(REPORT_LOG, record)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _csv_export(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                keys.append(key)
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def export_csv(out_dir: Path = Path("runtime/exports")) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "signals": out_dir / "signals.csv",
        "trades": out_dir / "trades.csv",
        "market_snapshots": out_dir / "market_snapshots.csv",
        "report_log": out_dir / "report_log.csv",
    }
    _csv_export(read_jsonl(SIGNALS), outputs["signals"])
    _csv_export(read_jsonl(TRADES), outputs["trades"])
    _csv_export(read_jsonl(SNAPSHOTS), outputs["market_snapshots"])
    _csv_export(read_jsonl(REPORT_LOG), outputs["report_log"])
    return {key: str(path) for key, path in outputs.items()}


if __name__ == "__main__":
    import json as _json
    print(_json.dumps(export_csv(), indent=2))
