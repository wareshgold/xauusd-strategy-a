"""Compact deterministic analysis of an SP2L forensic telemetry JSONL capture.

Research-only. No strategy geometry, session, fill, or execution rules are changed.

Usage:
  python scripts/analyze_sp2l_forensic_telemetry.py <telemetry.jsonl>
"""

from __future__ import annotations

import json
import statistics
import sys
from datetime import datetime
from pathlib import Path


def parse_iso(value: str):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load(path: Path):
    events = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            events.append((line_no, json.loads(line)))
    return events


def analyze(path: Path):
    events = load(path)
    starts = [e for _, e in events if e.get("event") == "FORENSIC_START"]
    polls = [e for _, e in events if e.get("event") == "POLL"]
    stops = [e for _, e in events if e.get("event") == "FORENSIC_STOP"]

    intervals = []
    wall_offsets = []
    returned = {}
    errors = []
    nonmono = []
    disconnected = []
    detector_signals = []

    previous_ts = None
    for p in polls:
        ts = parse_iso(p["ts_utc"])
        if previous_ts is not None:
            intervals.append((ts - previous_ts).total_seconds())
        previous_ts = ts

        count = p.get("copy_rates_call", {}).get("returned_count", 0)
        returned[str(count)] = returned.get(str(count), 0) + 1

        for field in (
            "mt5_last_error_before",
            "mt5_last_error_after_rates",
            "mt5_last_error_after_detector",
        ):
            err = p.get(field)
            if err not in (None, [1, "Success"], (1, "Success")):
                errors.append({"poll_id": p.get("poll_id"), "field": field, "error": err})

        snap = p.get("data_snapshot") or {}
        if snap.get("strictly_increasing") is False:
            nonmono.append(p.get("poll_id"))

        if (p.get("terminal_state") or {}).get("terminal_connected") is False:
            disconnected.append(p.get("poll_id"))

        sig = (p.get("detector") or {}).get("signal")
        if sig:
            detector_signals.append({
                "poll_id": p.get("poll_id"),
                "poll_utc": p.get("ts_utc"),
                "signal_time": sig.get("signal_time"),
                "direction": sig.get("direction"),
                "entry": sig.get("entry"),
                "sl": sig.get("sl"),
                "tp": sig.get("tp"),
            })

        bars = snap.get("bars") or []
        if bars:
            newest = parse_iso(bars[-1]["time_interpreted_utc"])
            wall_offsets.append((ts - newest).total_seconds())

    report = {
        "status": "ANALYZED",
        "research_only": True,
        "canonical": False,
        "input": str(path),
        "start_events": len(starts),
        "poll_events": len(polls),
        "stop_events": len(stops),
        "stop_present": bool(stops),
        "first_poll_utc": polls[0]["ts_utc"] if polls else None,
        "last_poll_utc": polls[-1]["ts_utc"] if polls else None,
        "returned_count_distribution": returned,
        "poll_interval_seconds": {
            "min": min(intervals) if intervals else None,
            "median": statistics.median(intervals) if intervals else None,
            "max": max(intervals) if intervals else None,
            "over_3s": sum(x > 3 for x in intervals),
            "over_10s": sum(x > 10 for x in intervals),
        },
        "wall_clock_minus_newest_bar_seconds": {
            "min": min(wall_offsets) if wall_offsets else None,
            "median": statistics.median(wall_offsets) if wall_offsets else None,
            "max": max(wall_offsets) if wall_offsets else None,
        },
        "non_monotonic_poll_ids": nonmono,
        "terminal_disconnected_poll_ids": disconnected,
        "mt5_non_success_errors": errors,
        "detector_signal_count": len(detector_signals),
        "detector_signals": detector_signals,
        "interpretation_scope": (
            "This report describes only the telemetry observation interval. "
            "It cannot prove runner uptime or detector behavior on dates not "
            "covered by this capture."
        ),
    }

    out_json = path.with_name(path.stem + "_ANALYSIS.json")
    out_md = path.with_name(path.stem + "_ANALYSIS.md")
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# SP2L Forensic Telemetry Analysis",
        "",
        f"- Input: {path}",
        f"- Polls: {len(polls)}",
        f"- STOP present: {bool(stops)}",
        f"- Detector signals observed: {len(detector_signals)}",
        f"- Returned-count distribution: {json.dumps(returned, sort_keys=True)}",
        "",
        "## Poll cadence",
        f"- min: {report['poll_interval_seconds']['min']} s",
        f"- median: {report['poll_interval_seconds']['median']} s",
        f"- max: {report['poll_interval_seconds']['max']} s",
        f"- gaps >3 s: {report['poll_interval_seconds']['over_3s']}",
        f"- gaps >10 s: {report['poll_interval_seconds']['over_10s']}",
        "",
        "## MT5/data health",
        f"- non-monotonic polls: {len(nonmono)}",
        f"- disconnected polls: {len(disconnected)}",
        f"- non-success MT5 errors: {len(errors)}",
        "",
        "## Timestamp diagnostic",
        "- wall_clock_minus_newest_bar_seconds compares telemetry wall-clock UTC with the newest bar interpreted as UTC.",
        f"- min/median/max: {report['wall_clock_minus_newest_bar_seconds']}",
        "",
        "## Detector",
    ]
    if detector_signals:
        for s in detector_signals:
            lines.append(
                f"- poll {s['poll_id']}: {s['direction']} signal_time={s['signal_time']} "
                f"entry={s['entry']} sl={s['sl']} tp={s['tp']}"
            )
    else:
        lines.append("- No detector signals observed in this capture.")

    lines += ["", "## Scope guard", report["interpretation_scope"]]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "COMPLETE",
        "input": str(path),
        "analysis_json": str(out_json),
        "analysis_markdown": str(out_md),
        "polls": len(polls),
        "stop_present": bool(stops),
        "detector_signal_count": len(detector_signals),
        "mt5_non_success_errors": len(errors),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/analyze_sp2l_forensic_telemetry.py <telemetry.jsonl>")
    analyze(Path(sys.argv[1]))
