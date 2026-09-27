"""Conservative data-quality analysis for an SP2L MT5 matrix artifact.

Research-only. This script never labels a recurring broker closure as missing data.
Weekend gaps are separated first; repeated non-weekend intervals are reported as
schedule-like, while non-recurring intervals remain unclassified.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()

    data = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    by_symbol: dict[str, list[dict]] = defaultdict(list)
    for row in data["results"]:
        if row["timeframe"] == "M1" and row["session_start_utc"] is None:
            by_symbol[row["requested_symbol"]].append(row)

    print("QUALITY_ARTIFACT=", args.artifact)
    print("SYMBOLS=", sorted(by_symbol))
    print()

    for symbol, rows in sorted(by_symbol.items()):
        weeks = len(rows)
        weekend = sum(r["calendar_weekend_gap_minutes"] for r in rows)
        non_weekend = sum(r["non_weekend_gap_minutes"] for r in rows)
        signatures: Counter[tuple[int, int, int]] = Counter()

        for row in rows:
            for gap in row.get("gap_intervals", []):
                if gap["calendar_weekend_minutes"] > 0:
                    continue
                start = datetime.fromisoformat(gap["start_utc"]).astimezone(timezone.utc)
                duration = int(gap["missing_minutes"])
                signatures[(start.weekday(), start.hour * 60 + start.minute, duration)] += 1

        recurring = sum(
            count
            for count in signatures.values()
            if count >= max(3, int(weeks * 0.8))
        )
        unclassified = max(0, non_weekend - recurring)

        print(
            f"{symbol}: weeks={weeks} "
            f"weekend_gap_min={weekend} "
            f"non_weekend_gap_min={non_weekend} "
            f"recurring_schedule_like_min={recurring} "
            f"unclassified_non_weekend_min={unclassified}"
        )

        common = sorted(
            signatures.items(),
            key=lambda item: (-item[1], item[0]),
        )[:5]
        for (weekday, minute, duration), count in common:
            if count >= 3:
                hh, mm = divmod(minute, 60)
                print(
                    f"  recurring_candidate weekday={weekday} "
                    f"start={hh:02d}:{mm:02d}Z duration_min={duration} "
                    f"weeks={count}/{weeks}"
                )

    print()
    print("NOTE=recurring_schedule_like is a diagnostic classification, not an authoritative broker session calendar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
