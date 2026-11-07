#!/usr/bin/env python
"""Read-only SP2L V3.1 weekly evidence collector.

Collects raw evidence into a LOCAL private directory. It never places, modifies,
or closes trades; never changes MT5 settings; and never uploads raw data.
The repository is public, so only a minimal disclosure-safe manifest is written
outside the raw bundle. Review the raw ZIP before choosing a private transfer path.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

WINDOW_START_UTC = datetime(2026, 11, 1, 22, 0, tzinfo=timezone.utc)  # 2026-11-02 00:00 at pinned UTC+2
WINDOW_END_UTC = datetime(2026, 11, 7, 22, 0, tzinfo=timezone.utc)    # 2026-11-08 00:00 at pinned UTC+2
SYMBOL = "XAUUSD.ecn"
MAGIC = 26092301
EXPECTED_VERSION = "SP2L_V3_1_XAUUSD_RR4_ACT40_TRAIL40_20261101"
EXPECTED_COMMIT = "7e20e991a0880b1e209c71a72d788836d0d821df"
EXPECTED_WORKTREE = Path(r"D:\Mirzaei\Private\1\xauusd-strategy-a-v3-1-trailing-retry-20261103")
EVENT_REL = Path("artifacts/forward-test/SP2L_V3_1_XAUUSD_RR4_ACT40_FORWARD_EVENTS.jsonl")
STATE_NAME = "sp2l_v3_1_xauusd_rr4_act40_forward_state.json"


def run(cmd, cwd=None):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=20)
        return {"returncode": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}
    except Exception as e:
        return {"error": repr(e)}


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def json_safe(value):
    if hasattr(value, "_asdict"):
        return {k: json_safe(v) for k, v in value._asdict().items()}
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_safe(obj), ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worktree", default=str(EXPECTED_WORKTREE))
    ap.add_argument("--output", default=str(Path.home() / "SP2L_PRIVATE_AUDIT_20261102_20261107"))
    ap.add_argument("--server-offset-hours", type=float, default=2.0)
    ap.add_argument("--mt5-terminal-path", default=os.environ.get("SP2L_MT5_TERMINAL_PATH", "C:\\Program Files\\Otet Group MT5 Terminal\\terminal64.exe"), help="Explicit terminal64.exe path for read-only MT5 history access.")
    args = ap.parse_args()

    root = Path(args.worktree)
    out = Path(args.output).resolve()
    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    capture = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "window_server_time_assumption": {
            "start": "2026-11-02T00:00:00",
            "end_exclusive": "2026-11-08T00:00:00",
            "server_offset_hours": args.server_offset_hours,
            "utc_start": (datetime(2026, 11, 2, tzinfo=timezone(timedelta(hours=args.server_offset_hours))).astimezone(timezone.utc)).isoformat(),
            "utc_end_exclusive": (datetime(2026, 11, 8, tzinfo=timezone(timedelta(hours=args.server_offset_hours))).astimezone(timezone.utc)).isoformat(),
            "note": "Offset is an explicit assumption; verify against MT5/server clock evidence before final filtering."
        },
        "expected_identity": {
            "version": EXPECTED_VERSION, "commit": EXPECTED_COMMIT,
            "symbol": SYMBOL, "magic": MAGIC, "worktree": str(root)
        },
        "git": {
            "branch": run(["git", "branch", "--show-current"], root),
            "head": run(["git", "rev-parse", "HEAD"], root),
            "status": run(["git", "status", "--short"], root),
        },
        "python": sys.version,
        "cwd_exists": root.exists(),
        "files": [],
        "warnings": []
    }

    # Process inventory: metadata only, no process termination or interaction.
    ps = r'Get-CimInstance Win32_Process | Where-Object { $_.Name -match "python|terminal" -and ($_.CommandLine -match "sp2l|forward_test|terminal64") } | Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4'
    proc = run(["powershell", "-NoProfile", "-Command", ps])
    write_json(raw / "process_inventory.json", proc)
    capture["process_inventory_collected"] = proc.get("returncode") == 0

    # Locate event/state files without modifying them.
    candidates = []
    if root.exists():
        candidates += [root / EVENT_REL, root / STATE_NAME, root / "scripts" / "run_sp2l_v3_1_xauusd_forward_test.py"]
        candidates += list(root.glob("**/" + STATE_NAME))
        candidates += list(root.glob("**/SP2L_V3_1_XAUUSD_RR4_ACT40_FORWARD_EVENTS.jsonl"))
    for p in dict.fromkeys(candidates):
        if p.is_file():
            dest_name = "forward_events.jsonl" if p.name == EVENT_REL.name else p.name
            dest = raw / "runner_files" / dest_name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
            capture["files"].append({"artifact": dest.relative_to(out).as_posix(), "size_bytes": dest.stat().st_size, "sha256": sha256(dest), "source_path": str(p)})

    # MT5 API is strictly history/read-only here.
    try:
        import MetaTrader5 as mt5
        # Explicit path avoids relying on automatic terminal discovery. This is a read-only
        # Python API connection; it does not start/stop the trading runner or submit orders.
        terminal_path = str(Path(args.mt5_terminal_path).expanduser())
        initialized = mt5.initialize(path=terminal_path)
        mt5_meta = {"initialize": bool(initialized), "terminal_path": terminal_path, "last_error": mt5.last_error()}
        if initialized:
            ti, ai = mt5.terminal_info(), mt5.account_info()
            mt5_meta["terminal_info"] = json_safe(ti)
            mt5_meta["account_info"] = json_safe(ai)
            start = datetime(2026, 11, 2, tzinfo=timezone(timedelta(hours=args.server_offset_hours))).astimezone(timezone.utc).replace(tzinfo=None)
            end = datetime(2026, 11, 8, tzinfo=timezone(timedelta(hours=args.server_offset_hours))).astimezone(timezone.utc).replace(tzinfo=None)
            orders = mt5.history_orders_get(start, end)
            deals = mt5.history_deals_get(start, end)
            mt5_meta["orders_query"] = {"is_none": orders is None, "count": 0 if orders is None else len(orders), "last_error": mt5.last_error()}
            mt5_meta["deals_query"] = {"is_none": deals is None, "count": 0 if deals is None else len(deals), "last_error": mt5.last_error()}
            if orders is not None:
                write_json(raw / "mt5_history_orders.json", [json_safe(x) for x in orders])
            if deals is not None:
                write_json(raw / "mt5_history_deals.json", [json_safe(x) for x in deals])
            # Symbol specification is read-only.
            mt5_meta["symbol_info"] = json_safe(mt5.symbol_info(SYMBOL))
            capture["mt5"] = mt5_meta
            mt5.shutdown()
        else:
            capture["mt5"] = mt5_meta
            capture["warnings"].append("MT5 initialize failed; no history was collected.")
    except Exception as e:
        capture["mt5_error"] = repr(e)
        capture["warnings"].append("MT5 Python API collection failed; raw runner files may still be present.")

    # Event type counts only; raw events stay in the private bundle.
    event_file = raw / "runner_files" / "forward_events.jsonl"
    event_counts = Counter()
    event_rows = 0
    if event_file.exists():
        with event_file.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    event_rows += 1
                    event_counts[str(obj.get("event") or obj.get("type") or "UNKNOWN")] += 1
                except Exception:
                    event_counts["UNPARSEABLE"] += 1
        capture["event_rows"] = event_rows
        capture["event_type_counts"] = dict(sorted(event_counts.items()))

    write_json(raw / "capture_metadata.json", capture)
    # Hash manifest for every private artifact, no paths or identifying data in public summary.
    manifest = []
    for p in sorted(raw.rglob("*")):
        if p.is_file() and p.name != "SHA256_MANIFEST.json":
            manifest.append({"relative_path": p.relative_to(raw).as_posix(), "size_bytes": p.stat().st_size, "sha256": sha256(p)})
    write_json(raw / "SHA256_MANIFEST.json", manifest)

    # Sanitized public-safe aggregate only. No account IDs, tickets, timestamps, prices, or per-trade rows.
    public = {
        "audit_window_label": "2026-11-02_to_2026-11-07",
        "collector_version": "1.1-read-only-explicit-mt5-path",
        "captured_at_utc_date": datetime.now(timezone.utc).date().isoformat(),
        "raw_bundle_created_locally": True,
        "raw_bundle_uploaded": False,
        "runner_files_collected": len(capture["files"]),
        "event_row_count": capture.get("event_rows"),
        "event_type_counts": capture.get("event_type_counts", {}),
        "mt5_orders_query_succeeded": bool(capture.get("mt5", {}).get("orders_query", {}).get("is_none") is False),
        "mt5_deals_query_succeeded": bool(capture.get("mt5", {}).get("deals_query", {}).get("is_none") is False),
        "mt5_order_count": capture.get("mt5", {}).get("orders_query", {}).get("count"),
        "mt5_deal_count": capture.get("mt5", {}).get("deals_query", {}).get("count"),
        "warnings_count": len(capture["warnings"]),
        "identity_match": "NOT_ASSESSED",
        "net_pnl": "NOT_CALCULATED",
        "note": "Public-safe intake summary only. Full forensic reconciliation requires private raw evidence."
    }
    write_json(out / "PUBLIC_SAFE_SUMMARY.json", public)

    zip_path = out.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in raw.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(out))
    print("COLLECTION_COMPLETE")
    print("RAW_BUNDLE=" + str(zip_path))
    print("RAW_SHA256=" + sha256(zip_path))
    print("PUBLIC_SUMMARY=" + str(out / "PUBLIC_SAFE_SUMMARY.json"))
    print("EVENT_ROWS=" + str(public["event_row_count"]))
    print("MT5_ORDERS=" + str(public["mt5_order_count"]))
    print("MT5_DEALS=" + str(public["mt5_deal_count"]))
    print("WARNINGS=" + str(public["warnings_count"]))
    print("RAW_DATA_WAS_NOT_UPLOADED=TRUE")
    print("REVIEW_PRIVATE_BUNDLE_BEFORE_ANY_TRANSFER=TRUE")


if __name__ == "__main__":
    main()
