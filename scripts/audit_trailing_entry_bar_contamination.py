"""Deterministic offline replay of entry-bar contamination in a SELL trailing check.

This incident fixture is diagnostic only. It does not import or alter the live runner,
connect to MT5, place orders, or establish canonical Strategy A geometry.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any


def utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"Timestamp must include an offset: {value}")
    return dt.astimezone(timezone.utc)


def dec(value: str | int | float | Decimal) -> Decimal:
    return Decimal(str(value))


def audit_entry_bar(
    *,
    entry_time_utc: str,
    entry_price: str | float,
    bar_start_utc: str,
    bar_low: str | float,
    bar_low_time_utc: str,
    activation_distance: str | float,
    post_entry_min_bid: str | float,
    post_entry_min_bid_time_utc: str,
    following_minute_min_ask: str | float,
    min_broker_distance: str | float = "0",
) -> dict[str, Any]:
    """Replay only the known incident facts using the runner's SELL arithmetic."""
    entry_time = utc(entry_time_utc)
    bar_start = utc(bar_start_utc)
    bar_end = bar_start + timedelta(minutes=1)
    low_time = utc(bar_low_time_utc)
    post_min_time = utc(post_entry_min_bid_time_utc)

    entry = dec(entry_price)
    low = dec(bar_low)
    threshold = dec(activation_distance)
    post_min_bid = dec(post_entry_min_bid)
    next_min_ask = dec(following_minute_min_ask)
    broker_distance = dec(min_broker_distance)

    if not (bar_start <= entry_time < bar_end):
        raise ValueError("The supplied M1 bar does not contain the entry timestamp")
    if not (bar_start <= low_time < bar_end):
        raise ValueError("The supplied bar-low timestamp is outside the supplied M1 bar")
    if post_min_time < entry_time:
        raise ValueError("The supplied post-entry minimum is before entry")

    full_bar_favorable = entry - low
    post_entry_favorable = entry - post_min_bid
    candidate_sl = low + threshold

    # The runner's SELL guard only sends a request if new_sl > current Ask + min distance.
    # If candidate_sl <= the minimum Ask observed throughout the following minute plus
    # broker distance, it was unplaceable at every observed tick in that minute.
    rejected_by_ask_guard_throughout_following_minute = (
        candidate_sl <= next_min_ask + broker_distance
    )

    return {
        "status": "COMPLETE",
        "research_only": True,
        "canonical": False,
        "position_id": 64500649,
        "direction": "SELL",
        "entry_time_utc": entry_time.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "entry_bar": {
            "start_utc": bar_start.isoformat().replace("+00:00", "Z"),
            "end_utc_exclusive": bar_end.isoformat().replace("+00:00", "Z"),
            "low": str(low),
            "low_time_utc": low_time.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "low_occurred_before_entry": low_time < entry_time,
        },
        "activation_distance": str(threshold),
        "full_bar_favorable_move": str(full_bar_favorable),
        "full_bar_passes_activation_threshold": full_bar_favorable >= threshold,
        "post_entry_min_bid": str(post_min_bid),
        "post_entry_min_bid_time_utc": post_min_time.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "post_entry_favorable_move": str(post_entry_favorable),
        "post_entry_ticks_pass_activation_threshold": post_entry_favorable >= threshold,
        "entry_bar_contamination_demonstrated": (
            low_time < entry_time
            and full_bar_favorable >= threshold
            and post_entry_favorable < threshold
        ),
        "candidate_sl_from_full_bar_low": str(candidate_sl),
        "following_minute_min_ask": str(next_min_ask),
        "min_broker_distance": str(broker_distance),
        "candidate_rejected_by_ask_guard_throughout_following_minute": (
            rejected_by_ask_guard_throughout_following_minute
        ),
        "interpretation": (
            (
                "The full entry-bar low passes the activation threshold even though its low "
                "occurred before entry; post-entry ticks do not pass the threshold. "
                if low_time < entry_time and full_bar_favorable >= threshold and post_entry_favorable < threshold
                else "This fixture does not demonstrate pre-entry-low contamination. "
            )
            + (
                "The derived candidate SL is at or below the minimum observed Ask plus broker "
                "distance, so the SELL Ask-distance guard would reject it throughout the observed "
                "following minute. "
                if rejected_by_ask_guard_throughout_following_minute
                else "The supplied following-minute minimum Ask does not show continuous rejection "
                "by the SELL Ask-distance guard. "
            )
            + "This replay does not prove the runner's exact polling instant or broker state."
        ),
        "limitations": [
            "Incident-specific deterministic replay, not a canonical rule.",
            "Uses the supplied post-entry Bid minimum and following-minute Ask minimum.",
            "Does not emulate MT5 polling cadence, broker state, or order_send.",
            "No live runner files or trading state are read or modified.",
        ],
    }


def incident_fixture() -> dict[str, Any]:
    return audit_entry_bar(
        entry_time_utc="2026-10-27T12:56:05.552Z",
        entry_price="4006.11",
        bar_start_utc="2026-10-27T12:56:00Z",
        bar_low="4005.44",
        bar_low_time_utc="2026-10-27T12:56:00.083Z",
        activation_distance="0.40",
        post_entry_min_bid="4006.06",
        post_entry_min_bid_time_utc="2026-10-27T12:56:06.140Z",
        following_minute_min_ask="4006.94",
        min_broker_distance="0",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="Optional new JSON path; existing files are not overwritten")
    args = parser.parse_args()
    result = incident_fixture()
    if args.output:
        from pathlib import Path
        output = Path(args.output)
        if output.exists():
            raise FileExistsError(f"Refusing to overwrite existing evidence: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
