#!/usr/bin/env python3
"""Build a local, read-only per-position event chronology from the V3.1 ZIP.

The tool does not connect to MT5, alter runner state, or infer missing prices.
TRAIL_UPDATE bar extrema are sparse observations, not complete MFE/MAE.
"""
from __future__ import annotations
import argparse, csv, json, sys, zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    from .sp2l_v31_forward_forensic import analyze_zip
except ImportError:  # direct script execution from the scripts directory
    from sp2l_v31_forward_forensic import analyze_zip

POSITION_EVENTS = {
    "TRAIL_UPDATE", "TRAIL_DEFERRED", "POSITION_LIFECYCLE",
    "TELEGRAM_DEAL_LIFECYCLE",
}

def epoch_iso(value):
    try:
        n = int(value)
        return datetime.fromtimestamp(n, timezone.utc).isoformat() if n > 0 else None
    except (TypeError, ValueError, OverflowError, OSError):
        return None

def event_time(event):
    stamp = event.get("ts_utc") or event.get("timestamp_utc") or event.get("time_utc")
    if stamp:
        try:
            parsed = datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
            if parsed.tzinfo is not None:
                return parsed.astimezone(timezone.utc).isoformat()
        except ValueError:
            pass
    return epoch_iso(event.get("completed_bar_time"))

def _num(value):
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None

def build_timeline(events, trades):
    by_position = defaultdict(list)
    counters = Counter()
    for trade in trades:
        pid = str(trade.get("position_id", ""))
        if not pid:
            continue
        for key, label in (("entry_time_utc", "BROKER_ENTRY_DEAL"),
                           ("exit_time_utc", "BROKER_EXIT_DEAL")):
            stamp = trade.get(key)
            if stamp:
                by_position[pid].append({
                    "position_id": pid, "event_type": label,
                    "timestamp_utc": stamp, "time_basis": "broker_deal_epoch",
                    "event_index": None, "success": None,
                    "direction": trade.get("side"), "price": (
                        trade.get("entry_price_volume_weighted") if label == "BROKER_ENTRY_DEAL"
                        else trade.get("exit_price_volume_weighted")),
                    "old_sl": None, "new_sl": None, "bar_high": None, "bar_low": None,
                    "bid": None, "ask": None, "retcode": None, "reason": trade.get("exit_reasons"),
                    "detail": "Synthesized from broker deal history; not a runner JSONL event",
                })
    for idx, event in enumerate(events):
        kind = str(event.get("event", "UNKNOWN"))
        if kind not in POSITION_EVENTS:
            continue
        raw_pid = event.get("position") or event.get("position_id")
        if raw_pid in (None, "", 0, "0"):
            continue
        pid = str(raw_pid)
        stamp = event_time(event)
        row = {
            "position_id": pid, "event_type": kind, "timestamp_utc": stamp,
            "time_basis": "runner_ts_utc" if event.get("ts_utc") else (
                "completed_bar_time" if event.get("completed_bar_time") else "missing"),
            "event_index": idx, "success": event.get("success"),
            "direction": event.get("direction"),
            "price": _num(event.get("price_current")),
            "old_sl": _num(event.get("old_sl")), "new_sl": _num(event.get("new_sl")),
            "bar_high": _num(event.get("bar_high")), "bar_low": _num(event.get("bar_low")),
            "bid": _num(event.get("bid")), "ask": _num(event.get("ask")),
            "retcode": event.get("retcode"), "reason": event.get("reason"),
            "detail": event.get("comment") or event.get("detail") or "",
        }
        by_position[pid].append(row)
        counters[kind] += 1

    rows = []
    for pid, items in by_position.items():
        # Sort known timestamps chronologically; retain original JSONL order for ties/missing times.
        items.sort(key=lambda x: (x["timestamp_utc"] is None, x["timestamp_utc"] or "", 
                                  x["event_index"] if x["event_index"] is not None else -1))
        for seq, item in enumerate(items, 1):
            item["sequence"] = seq
            rows.append(item)
    rows.sort(key=lambda x: (x["position_id"], x["sequence"]))
    return rows, counters

def analyze(zip_path):
    summary, trades, events = analyze_zip(zip_path)
    timeline, counts = build_timeline(events, trades)
    by_pid = defaultdict(list)
    for row in timeline:
        by_pid[row["position_id"]].append(row)
    per_position = []
    for trade in trades:
        pid = str(trade["position_id"])
        seq = by_pid.get(pid, [])
        trail = [x for x in seq if x["event_type"] == "TRAIL_UPDATE"]
        deferred = [x for x in seq if x["event_type"] == "TRAIL_DEFERRED"]
        first = next((x for x in seq if x["event_type"] == "BROKER_ENTRY_DEAL"), None)
        first_trail = next((x for x in trail if x["timestamp_utc"]), None)
        entry_to_trail_minutes = None
        if first and first_trail:
            try:
                a = datetime.fromisoformat(first["timestamp_utc"].replace("Z","+00:00"))
                b = datetime.fromisoformat(first_trail["timestamp_utc"].replace("Z","+00:00"))
                entry_to_trail_minutes = round((b-a).total_seconds()/60, 3)
            except ValueError:
                pass
        per_position.append({
            "position_id": pid, "status": trade.get("status"), "side": trade.get("side"),
            "net_account_currency": trade.get("net_account_currency"),
            "entry_time_utc": trade.get("entry_time_utc"), "exit_time_utc": trade.get("exit_time_utc"),
            "trail_update_count_from_deals_join": len(trail),
            "trail_deferred_count": len(deferred),
            "trail_success_count": sum(x.get("success") is True for x in trail),
            "trail_failure_count": sum(x.get("success") is False for x in trail),
            "minutes_entry_to_first_trail_event": entry_to_trail_minutes,
            "first_trail_old_sl": trail[0].get("old_sl") if trail else None,
            "first_trail_new_sl": trail[0].get("new_sl") if trail else None,
            "last_trail_new_sl": trail[-1].get("new_sl") if trail else None,
            "sparse_trail_bar_high_max": max((x["bar_high"] for x in trail if x["bar_high"] is not None), default=None),
            "sparse_trail_bar_low_min": min((x["bar_low"] for x in trail if x["bar_low"] is not None), default=None),
            "timeline_event_count": len(seq),
            "timeline_missing_timestamps": sum(x["timestamp_utc"] is None for x in seq),
        })
    names = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = sorted(n for n in zf.namelist()
                       if any(k in n.lower() for k in ("tick", "bar", "candle", "ohlc", "rate")))
    report = {
        "report_version": 1, "input_zip": zip_path.name,
        "input_zip_sha256": summary["input_zip_sha256"],
        "closed_positions": summary["realized_closed_positions"]["count"],
        "event_counts_by_type": dict(sorted(counts.items())),
        "timeline_rows": len(timeline),
        "positions_with_timeline": len(by_pid),
        "price_like_archive_members": names,
        "mfe_mae_status": "NOT_COMPUTED",
        "mfe_mae_reason": (
            "The ZIP's TRAIL_UPDATE bar_high/bar_low values are sparse and only exist when "
            "the runner reaches a trail evaluation. They do not cover every bar/tick during "
            "the holding interval and cannot be labeled MFE/MAE."
        ),
        "interpretation_limits": [
            "Runner ts_utc is used when present; completed_bar_time is a fallback event-time basis.",
            "Broker entry/exit timestamps come from deal history and are separate synthesized timeline rows.",
            "A missing event is not evidence that the underlying broker state did not change.",
            "Sparse trail bar extrema are not complete price paths; no MFE/MAE or causal trailing claim is made.",
            "Position identifiers are joined exactly as recorded; unmatched event IDs remain visible as their own groups.",
        ],
    }
    return report, timeline, per_position

def write_csv(path, rows):
    fields = ["position_id","sequence","event_type","timestamp_utc","time_basis","event_index",
              "success","direction","price","old_sl","new_sl","bar_high","bar_low","bid","ask",
              "retcode","reason","detail"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip", required=True, type=Path)
    p.add_argument("--out", type=Path, default=Path("artifacts/forensic/v31-local-20261108"))
    a=p.parse_args(argv)
    if not a.zip.is_file(): p.error(f"ZIP not found: {a.zip}")
    try:
        report, timeline, positions = analyze(a.zip)
        a.out.mkdir(parents=True, exist_ok=True)
        (a.out/"v31_event_timeline_summary.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        write_csv(a.out/"v31_position_event_timeline.csv",timeline)
        with (a.out/"v31_position_event_summary.csv").open("w",newline="",encoding="utf-8-sig") as f:
            w=csv.DictWriter(f,fieldnames=list(positions[0]) if positions else ["position_id"]); w.writeheader(); w.writerows(positions)
    except (OSError,ValueError,KeyError,zipfile.BadZipFile) as exc:
        print(f"EVENT_TIMELINE_ERROR={type(exc).__name__}: {exc}",file=sys.stderr); return 2
    print("SP2L V3.1 POSITION EVENT TIMELINE")
    print(f"CLOSED_POSITIONS={report['closed_positions']} TIMELINE_ROWS={report['timeline_rows']} POSITIONS_WITH_TIMELINE={report['positions_with_timeline']}")
    print("EVENT_COUNTS="+json.dumps(report["event_counts_by_type"],sort_keys=True))
    print(f"PRICE_LIKE_ARCHIVE_MEMBERS={json.dumps(report['price_like_archive_members'])}")
    print(f"MFE_MAE_STATUS={report['mfe_mae_status']}")
    print(f"TIMELINE_CSV={(a.out/'v31_position_event_timeline.csv').resolve()}")
    print(f"POSITION_SUMMARY_CSV={(a.out/'v31_position_event_summary.csv').resolve()}")
    print(f"REPORT_JSON={(a.out/'v31_event_timeline_summary.json').resolve()}")
    print("READ_ONLY=True MT5_CONNECTION=False RUNNER_MODIFIED=False")
    return 0

if __name__=="__main__": raise SystemExit(main())
