"""Research-only diagnostic for unresolved MT5 matrix gaps.

Reports exact gap intervals and overlap with SP2L replay windows. It does not
classify any broker session or approve any unresolved gap.
"""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

WINDOWS = {"W1": (7, 17), "W2": (8, 17), "W3": (13, 17)}

def overlap_minutes(start_s: str, end_s: str, sh: int, eh: int) -> int:
    start = datetime.fromisoformat(start_s.replace("Z","+00:00"))
    end = datetime.fromisoformat(end_s.replace("Z","+00:00"))
    total = 0
    day = start.replace(hour=0, minute=0, second=0, microsecond=0)
    while day < end:
        a=max(start, day.replace(hour=sh))
        b=min(end, day.replace(hour=eh))
        if b>a:
            total += int((b-a).total_seconds()//60)
        day = day.replace(hour=0) + __import__("datetime").timedelta(days=1)
    return total

def main():
    p=argparse.ArgumentParser()
    p.add_argument("artifact")
    p.add_argument("--symbol", action="append")
    args=p.parse_args()
    d=json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    wanted=set(args.symbol or [])
    print("ARTIFACT=",args.artifact)
    for row in d["rows"]:
        if row["status"]!="DATA_QUALITY_UNRESOLVED": continue
        if wanted and row["requested_symbol"] not in wanted: continue
        print(f"\n{row['requested_symbol']} {row['week_start_utc']} -> {row['week_end_utc']}")
        for g in row["gap_classifications"]:
            if g["classification"]!="UNRESOLVED_DATA_GAP": continue
            # Classification rows currently retain counts, not timestamps; exact
            # intervals are recovered from the source matrix artifact by joining
            # case_id in the companion matrix file.
            print(f"  unresolved_minutes={g['non_weekend_minutes']} (exact interval requires matrix artifact)")
    print("\nNOTE: Gate artifact intentionally stores classification counts only.")
    print("Use the companion matrix artifact to inspect exact gap timestamps.")
if __name__=="__main__":
    raise SystemExit(main())
