"""Print a broker reconciliation table from a V2 Forward excursion report.

NON_CANONICAL_FORENSIC / read-only. No MT5 orders are sent or modified.
This deliberately consumes the already-produced excursion JSON so the
reconciliation is reproducible without re-running the market-path replay.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--report", required=True)
    p.add_argument("--output", required=False)
    return p.parse_args()


def main():
    args = parse_args()
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    broker = report.get("broker_cross_validation") or {}
    by_id = {x["signal_id"]: x for x in broker.get("trades", [])}
    rows = []

    for trade in report.get("trade_level", []):
        check = by_id.get(trade["signal_id"], {})
        rows.append({
            "signal_id": trade["signal_id"],
            "direction": trade["direction"],
            "entry_ts": trade.get("entry_ts_iso"),
            "historical_exit_ts": trade.get("historical_exit_ts_iso"),
            "broker_status": check.get("status", "NO_BROKER_CHECK"),
            "mismatches": check.get("mismatches", []),
            "entry_order_found": check.get("entry_order", {}).get("found"),
            "entry_deal_found": check.get("entry_deal", {}).get("found"),
            "exit_order_found": check.get("exit_order", {}).get("found"),
            "exit_deal_found": check.get("exit_deal", {}).get("found"),
            "entry_position_ticket": trade.get("entry_position_ticket"),
            "exit_position_ticket": trade.get("exit_position_ticket"),
            "historical_r": trade.get("actual_r"),
            "mfe_r": trade.get("excursion", {}).get("mfe_r"),
            "mae_r": trade.get("excursion", {}).get("mae_r"),
            "reached_1r": trade.get("excursion", {}).get("first_1r_before_historical_exit"),
            "reached_2r": trade.get("excursion", {}).get("first_2r_before_historical_exit"),
        })

    confirmed = [r for r in rows if r["broker_status"] == "BROKER_CONFIRMED"]
    unresolved = [r for r in rows if r["broker_status"] != "BROKER_CONFIRMED"]

    mismatch_counts = {}
    for row in unresolved:
        for reason in row["mismatches"]:
            mismatch_counts[reason] = mismatch_counts.get(reason, 0) + 1

    out = {
        "status": "COMPLETE",
        "mode": "NON_CANONICAL_FORENSIC",
        "source_report": args.report,
        "counts": {
            "historical_trades": len(rows),
            "broker_confirmed": len(confirmed),
            "broker_unconfirmed_or_mismatch": len(unresolved),
        },
        "mismatch_reason_counts": dict(sorted(mismatch_counts.items())),
        "trades": rows,
        "interpretation_guard": [
            "BROKER_CONFIRMED means the lifecycle tickets were found in MT5 history and the checked symbol/price/position relationships matched.",
            "BROKER_MISMATCH_OR_MISSING must not be treated as broker-authoritative.",
            "This report does not decide Strategy A geometry or exit semantics.",
        ],
    }

    print(json.dumps(out, indent=2, sort_keys=True))
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
