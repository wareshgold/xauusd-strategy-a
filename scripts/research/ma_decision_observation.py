"""Research-only MA decision-observation record builder.

This module is deliberately standalone: it does not import the Runner, MT5,
or any trading/execution code. Callers must supply the bar boundaries observed
at the decision boundary; this module never infers them from trigger_time.
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone

SCHEMA_VERSION = "MA_DECISION_OBSERVATION_V1"
M1_SECONDS = 60


def _utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _canonical_bar_bytes(bars):
    return json.dumps(
        bars, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def build_observation_record(
    *,
    candidate_id,
    process_session_id,
    poll_sequence,
    trigger_time_server_epoch,
    current_m1_bar_open_server_epoch,
    last_completed_m1_bar_open_server_epoch,
    last_completed_m1_bar_close_server_epoch,
    server_utc_offset_seconds,
    bars_snapshot,
    decision_observed_at_utc=None,
    decision_monotonic_ns=None,
):
    """Build one immutable observation record; missing boundaries fail closed."""
    if not candidate_id or not process_session_id:
        raise ValueError("candidate_id and process_session_id are required")
    if isinstance(poll_sequence, bool) or not isinstance(poll_sequence, int) or poll_sequence < 0:
        raise ValueError("poll_sequence must be a non-negative integer")
    if not isinstance(bars_snapshot, list) or len(bars_snapshot) < 2:
        raise ValueError("bars_snapshot must contain current and prior M1 bars")
    if any(not isinstance(bar, dict) for bar in bars_snapshot):
        raise ValueError("each bars_snapshot item must be a mapping")

    observed = _utc_now() if decision_observed_at_utc is None else decision_observed_at_utc
    if not isinstance(observed, str) or not observed.endswith("Z"):
        raise ValueError("decision_observed_at_utc must be an ISO-8601 UTC string ending in Z")
    try:
        parsed_observed = datetime.fromisoformat(observed[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError("decision_observed_at_utc must be a valid ISO-8601 UTC timestamp") from exc
    if parsed_observed.tzinfo is None or parsed_observed.utcoffset() != timezone.utc.utcoffset(parsed_observed):
        raise ValueError("decision_observed_at_utc must identify UTC")

    monotonic = time.monotonic_ns() if decision_monotonic_ns is None else decision_monotonic_ns
    if isinstance(monotonic, bool) or not isinstance(monotonic, int) or monotonic < 0:
        raise ValueError("decision_monotonic_ns must be a non-negative integer")

    snapshot_hash = hashlib.sha256(_canonical_bar_bytes(bars_snapshot)).hexdigest()
    times = [bar.get("time") for bar in bars_snapshot]
    range_valid = all(isinstance(t, int) and not isinstance(t, bool) for t in times)
    strictly_ordered = range_valid and all(b > a for a, b in zip(times, times[1:]))
    boundary_values = (
        current_m1_bar_open_server_epoch,
        last_completed_m1_bar_open_server_epoch,
        last_completed_m1_bar_close_server_epoch,
    )
    boundaries_present = all(isinstance(v, int) and not isinstance(v, bool) for v in boundary_values)
    boundary_consistent = (
        boundaries_present
        and last_completed_m1_bar_close_server_epoch
            == last_completed_m1_bar_open_server_epoch + M1_SECONDS
        and last_completed_m1_bar_close_server_epoch
            <= current_m1_bar_open_server_epoch
    )
    # The snapshot must contain the current bar last and the immediately
    # preceding observed bar must be the declared last completed bar. A gap
    # between those two bars is permitted; a skipped intervening bar is not.
    snapshot_consistent = (
        strictly_ordered
        and times[-1] == current_m1_bar_open_server_epoch
        and times[-2] == last_completed_m1_bar_open_server_epoch
    )
    alignment_status = (
        "READY_FOR_RESEARCH_ALIGNMENT"
        if boundary_consistent and snapshot_consistent
        else "UNRESOLVED"
    )

    return {
        "event_schema_version": SCHEMA_VERSION,
        "candidate_id": str(candidate_id),
        "process_session_id": str(process_session_id),
        "poll_sequence": poll_sequence,
        "decision_observed_at_utc": observed,
        "decision_monotonic_ns": monotonic,
        "trigger_time_server_epoch": trigger_time_server_epoch,
        "current_m1_bar_open_server_epoch": current_m1_bar_open_server_epoch,
        "last_completed_m1_bar_open_server_epoch": last_completed_m1_bar_open_server_epoch,
        "last_completed_m1_bar_close_server_epoch": last_completed_m1_bar_close_server_epoch,
        "server_utc_offset_seconds": server_utc_offset_seconds,
        "bar_snapshot_sha256": snapshot_hash,
        "bar_snapshot_range": {
            "first_open_server_epoch": times[0] if range_valid else None,
            "last_open_server_epoch": times[-1] if range_valid else None,
            "count": len(bars_snapshot),
        },
        "alignment_status": alignment_status,
    }
