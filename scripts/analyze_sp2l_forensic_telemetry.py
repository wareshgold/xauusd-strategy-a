"""Analyze a pushed SP2L forensic telemetry JSONL capture.

Research-only. This tool summarizes acquisition/poll health and detector behavior.
It does not change SP2L geometry, session, fill, or execution semantics.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from statistics import median

DEFAULT = Path("artifacts/forensic/runtime/SP2L_FORWARD_FORENSIC_TELEMETRY_20260926T055934Z.jsonl")


def load(path: Path):
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            rows.append((n, json.loads(line)))
    return rows


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    rows = load(path)
    starts = [x for _, x in rows if x.get("event") == "FORENSIC_START"]
    polls = [x for _, x in rows if x.get("event") == "POLL"]
    stops = [x for _, x in rows if x.get("event") == "FORENSIC_STOP"]

    gaps = []
    returned_counts = []
    errors = []
    detector_signals = []
    non_monotonic = []
    bad_poll_elapsed = []
    connected_false = []

    for p in polls:
        c = p.get("copy_rates_call", {})
        returned_counts.append(c.get("returned_count"))
        e1 = p.get("mt5_last_error_before")
        e2 = p.get("mt5_last_error_after_rates")
        e3 = p.get("mt5_last_error_after_detector")
        for label, e in (("before", e1), ("after_rates", e2), ("after_detector", e3)):
            if e not in (None, [1, "Success"], (1, "Success")):
                errors.append({"poll_id": p.get("poll_id"), "stage": label, "error": e})

        elapsed = p.get("elapsed_since_previous_poll_seconds")
        if elapsed is not None:
            gaps.append(float(elapsed))
        pe = p.get("poll_elapsed_seconds")
        if pe is not None and float(pe) >= 2.0:
            bad_poll_elapsed.append({"poll_id": p.get("poll_id"), "seconds": pe})

        snap = p.get("data_snapshot") or {}
        if snap.get("strictly_increasing") is False:
            non_monotonic.append(p.get("poll_id"))

        ts = (p.get("terminal_state") or {}).get("terminal_connected")
        if ts is False:
            connected_false.append(p.get("poll_id"))

        sig = (p.get("detector") or {}).get("signal")
        if sig is not None:
            detector_signals.append({
                "poll_id": p.get("poll_id"),
                "poll_ts_utc": p.get("ts_utc"),
                "signal_time": sig.get("signal_time"),
                "direction": sig.get("direction"),
                "entry": sig.get("entry"),
                "sl": sig.get("sl"),
                "tp": sig.get("tp"),
            })

    summary = {
        "status": "ANALYZED",
        "research_only": True,
        "canonical": False,
        "file": str(path),
        "start_events": len(starts),
        "poll_events": len(polls),
        "stop_events": len(stops),
        "first_poll_utc": polls[0].get("ts_utc") if polls else None,
        "last_poll_utc": polls[-1].get("ts_utc") if polls else None,
        "poll_id_min": min((p.get("poll_id") for p in polls), default=None),
        "poll_id_max": max((p.get("poll_id") for p in polls), default=None),
        "returned_count_distribution": {
            str(k): returned_counts.count(k) for k in sorted(set(returned_counts))
        },
        "poll_interval_seconds": {
            "min": min(gaps) if gaps else None,
            "median": median(gaps) if gaps else None,
            "max": max(gaps) if gaps else None,
            "over_3_seconds": sum(x > 3.0 for x in gaps),
            "over_10_seconds": sum(x > 10.0 for x in gaps),
        },
        "non_monotonic_poll_ids": non_monotonic,
        "terminal_disconnected_poll_ids": connected_false,
        "mt5_non_success_errors": errors,
        "slow_poll_ids": bad_poll_elapsed,
        "detector_signal_count": len(detector_signals),
        "detector_signals": detector_signals,
        "stop_present": bool(stops),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
