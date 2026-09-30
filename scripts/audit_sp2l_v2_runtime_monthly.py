#!/usr/bin/env python3
"""Monthly reconciliation audit for an existing SP2L V2 runtime-M1 replay.

Non-canonical forensic tooling only. Aggregates the already-produced trade CSV
by entry month without changing the replay contract.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def month(ts: str) -> str:
    return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")


def utc_months(first: str, last: str) -> list[str]:
    a = datetime.fromtimestamp(first, tz=timezone.utc).replace(day=1)
    b = datetime.fromtimestamp(last, tz=timezone.utc).replace(day=1)
    out = []
    while a <= b:
        out.append(a.strftime("%Y-%m"))
        if a.month == 12:
            a = a.replace(year=a.year + 1, month=1)
        else:
            a = a.replace(month=a.month + 1)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trades", required=True, type=Path)
    ap.add_argument("--output-dir", type=Path, default=Path("artifacts/forensic/runtime-m1-replay"))
    args = ap.parse_args()

    rows = list(csv.DictReader(args.trades.open("r", encoding="utf-8-sig", newline="")))
    if not rows:
        raise RuntimeError("empty trades CSV")

    groups = defaultdict(list)
    for row in rows:
        groups[month(row["entry_time_utc"])].append(row)

    result = []
    for m in sorted(groups):
        rs = groups[m]
        counts = {k: sum(r["result"] == k for r in rs) for k in
                  ("WIN", "LOSS", "BREAKEVEN", "AMBIGUOUS", "OPEN_OR_UNRESOLVED")}
        decisive = counts["WIN"] + counts["LOSS"] + counts["BREAKEVEN"]
        gp = sum(float(r["r"]) for r in rs if float(r["r"]) > 0)
        gl = -sum(float(r["r"]) for r in rs if float(r["r"]) < 0)
        net = sum(float(r["r"]) for r in rs)
        result.append({
            "month": m,
            "signals": len(rs),
            "decisive": decisive,
            **counts,
            "win_rate_decisive_pct": 100.0 * counts["WIN"] / decisive if decisive else 0.0,
            "net_R": net,
            "profit_factor": gp / gl if gl else 0.0,
            "first_entry_utc": min(r["entry_time_utc"] for r in rs),
            "last_entry_utc": max(r["entry_time_utc"] for r in rs),
        })

    out = {
        "mode": "NON_CANONICAL_FORENSIC",
        "experiment": "SP2L_V2_RUNTIME_M1_MONTHLY_RECONCILIATION",
        "input_trades": str(args.trades),
        "months": result,
        "notes": [
            "Grouped by entry_time_utc from the already-produced replay trade CSV.",
            "No geometry, trigger, execution, or outcome semantics are changed.",
            "This is a diagnostic reconciliation artifact, not a canonical Strategy A rule."
        ],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = args.output_dir / f"SP2L_RUNTIME_M1_MONTHLY_{stamp}.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    print(f"MONTHLY_JSON={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
