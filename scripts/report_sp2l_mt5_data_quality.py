"""Summarize SP2L MT5 data-quality gate by symbol and week.

Research-only. This report does not approve unresolved rows or alter replay data.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()

    data = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    by_symbol = defaultdict(list)
    for row in data["rows"]:
        by_symbol[row["requested_symbol"]].append(row)

    print("ARTIFACT=", args.artifact)
    for symbol, rows in sorted(by_symbol.items()):
        unresolved = [r for r in rows if r["status"] == "DATA_QUALITY_UNRESOLVED"]
        unresolved_minutes = sum(r["unresolved_data_gap_minutes"] for r in rows)
        print(
            f"{symbol}: cases={len(rows)} "
            f"pass={len(rows)-len(unresolved)} "
            f"unresolved={len(unresolved)} "
            f"unresolved_minutes={unresolved_minutes}"
        )
        for row in unresolved:
            print(
                f"  {row['week_start_utc']} -> {row['week_end_utc']} "
                f"unresolved_minutes={row['unresolved_data_gap_minutes']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
