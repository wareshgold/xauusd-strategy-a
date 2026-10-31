#!/usr/bin/env python3
"""Research-only MT5 acquisition with immutable evidence and non-overwrite.
Does not modify existing artifacts. Acquisition/provenance only.
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
except ImportError as exc:
    raise SystemExit("MetaTrader5 Python package is required") from exc


SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1
PROVIDER = "MetaTrader5 terminal API"
SERVER_EXPECTED = "OtetGroup-MT5"


def utc_parse(value: str) -> datetime:
    text = value.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"timestamp must include UTC offset: {value}")
    return dt.astimezone(timezone.utc).replace(second=0, microsecond=0)


def utc_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def audit_rows(rows: list[dict]) -> tuple[list[dict], list[dict], bool]:
    """Audit row validity and timestamp order without assuming a trading calendar.

    Positive intervals longer than one minute are observed discontinuities, not
    proven missing trading bars: weekends, holidays and session breaks are not
    classified here.
    """
    invalid = []
    discontinuities = []
    chronological = True
    for i, row in enumerate(rows):
        try:
            ts = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
            nums = [float(row[k]) for k in ("open", "high", "low", "close", "tick_volume")]
            if ts.tzinfo is None or any(not __import__("math").isfinite(x) for x in nums):
                invalid.append({"index": i, "reason": "invalid_timestamp_or_number"})
            h = float(row["high"])
            l = float(row["low"])
            o = float(row["open"])
            close = float(row["close"])
            if not (h >= max(o, close) and l <= min(o, close) and h >= l):
                invalid.append({"index": i, "reason": "invalid_ohlc"})
        except Exception:
            invalid.append({"index": i, "reason": "malformed_row"})
        if i > 0:
            try:
                prev = datetime.fromisoformat(rows[i - 1]["timestamp"].replace("Z", "+00:00"))
                cur = datetime.fromisoformat(rows[i]["timestamp"].replace("Z", "+00:00"))
                diff_m = (cur - prev).total_seconds() / 60.0
            except Exception:
                continue
            if diff_m <= 0:
                chronological = False
                discontinuities.append({
                    "from": rows[i - 1]["timestamp"],
                    "to": rows[i]["timestamp"],
                    "interval_minutes": diff_m,
                    "kind": "duplicate_timestamp" if diff_m == 0 else "non_chronological",
                })
            elif diff_m > 1:
                discontinuities.append({
                    "from": rows[i - 1]["timestamp"],
                    "to": rows[i]["timestamp"],
                    "interval_minutes": diff_m,
                    "kind": "unclassified_gap",
                })
    return invalid, discontinuities, chronological


def determine_audit_status(invalid: list[dict], discontinuities: list[dict]) -> str:
    """Do not pass data with unresolved gaps or fail it merely for calendar breaks."""
    if invalid or any(x["kind"] in {"duplicate_timestamp", "non_chronological"} for x in discontinuities):
        return "AUDITED_FAIL"
    if discontinuities:
        return "AUDITED_UNCLASSIFIED_COVERAGE"
    return "AUDITED_PASS"


def main() -> int:
    p = argparse.ArgumentParser(description="Research-only MT5 evidence acquisition (non-overwrite)")
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--symbol", default=SYMBOL)
    p.add_argument("--timeframe", default="M1")
    p.add_argument("--evidence-root", default="artifacts/mt5-research-evidence")
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--note", default="")
    p.add_argument("--terminal-path", default=None, help="Explicit path to terminal64.exe for mt5.initialize(path=...)")
    args = p.parse_args()

    start = utc_parse(args.start)
    end = utc_parse(args.end)
    if end <= start:
        raise SystemExit("end must be after start")

    ts_tag = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence_dir = Path(args.evidence_root) / f"{args.dataset_id}_{ts_tag}"
    if evidence_dir.exists():
        raise SystemExit(f"refusing to overwrite existing evidence dir: {evidence_dir}")
    evidence_dir.mkdir(parents=True, exist_ok=False)
    raw_dir = evidence_dir / "raw"
    derived_dir = evidence_dir / "derived"
    raw_dir.mkdir(parents=True, exist_ok=False)
    derived_dir.mkdir(parents=True, exist_ok=False)

    if args.terminal_path:
        if not mt5.initialize(path=args.terminal_path):
            raise SystemExit(f"MT5 initialize failed with terminal-path: {mt5.last_error()}")
    else:
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
        if not mt5.symbol_select(args.symbol, True):
            raise SystemExit(f"cannot select {args.symbol}: {mt5.last_error()}")

        rates = mt5.copy_rates_range(args.symbol, TIMEFRAME, start, end)
        if rates is None:
            raise SystemExit(f"copy_rates_range failed: {mt5.last_error()}")
        if len(rates) == 0:
            raise SystemExit("MT5 returned zero bars")

        rows = []
        for item in rates:
            ts = datetime.fromtimestamp(int(item["time"]), tz=timezone.utc)
            rows.append(
                {
                    "timestamp": utc_iso(ts),
                    "open": repr(float(item["open"])),
                    "high": repr(float(item["high"])),
                    "low": repr(float(item["low"])),
                    "close": repr(float(item["close"])),
                    "tick_volume": repr(int(item["tick_volume"])),
                    "spread": repr(int(item["spread"])),
                    "real_volume": repr(int(item["real_volume"])),
                }
            )

        invalid, gaps, chronological = audit_rows(rows)
        first = rows[0]["timestamp"]
        last = rows[-1]["timestamp"]

        raw_csv = raw_dir / f"{args.dataset_id}.csv"
        with raw_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        raw_hash = sha256_file(raw_csv)

        derived_csv = derived_dir / f"{args.dataset_id}_normalized.csv"
        with derived_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        derived_hash = sha256_file(derived_csv)

        retrieval_time = utc_iso(datetime.now(timezone.utc))
        manifest = {
            "evidence_type": "research_only_mt5_acquisition",
            "dataset_id": args.dataset_id,
            "note": args.note,
            "provider": PROVIDER,
            "terminal": getattr(terminal, "name", None),
            "server": server,
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "requested_interval_utc": {"start": utc_iso(start), "end": utc_iso(end)},
            "actual_first_utc": first,
            "actual_last_utc": last,
            "requested_bar_count": int((end - start).total_seconds() // 60) + 1,
            "actual_bar_count": len(rows),
            "timestamp_discontinuities": gaps,
            "discontinuity_count": len(gaps),
            "invalid_rows": invalid,
            "invalid_row_count": len(invalid),
            "chronological": chronological,
            "ordering_anomalies": [g for g in gaps if g.get("kind") in {"duplicate_timestamp", "non_chronological"}],
            "unclassified_gaps": [g for g in gaps if g.get("kind") == "unclassified_gap"],
            "duplicates": [],
            "retrieval_timestamp_utc": retrieval_time,
            "raw": {"path": str(raw_csv), "sha256": raw_hash},
            "derived": {"path": str(derived_csv), "sha256": derived_hash, "transform": "identity_copy_with_documentation"},
            "limitations": [
                "research_only_no_strategy_logic",
                "raw_exports_immutable_by_location",
                "no_overwrite_enforced",
                "session_calendar_applicability_not_asserted",
            ],
            "audit_status": determine_audit_status(invalid, gaps),
        }
        manifest_path = evidence_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"evidence_dir": str(evidence_dir), "manifest": manifest}, indent=2))
        return 0 if manifest["audit_status"] in {"AUDITED_PASS", "AUDITED_UNCLASSIFIED_COVERAGE"} else 2
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    sys.exit(main())
