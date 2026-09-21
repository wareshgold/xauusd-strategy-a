"""Live-session monitor report (reporting infrastructure only).

Renders this week's gateway session activity (signals, executions,
dry-run split, snapshots) in the same compact HTML Telegram template used by
the weekly report. Reads the journal; computes no strategy values and sends
no orders.

    python scripts/live_session_report.py                 # render only
    python scripts/live_session_report.py --send          # render + deliver
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(os.path.dirname(os.path.abspath(__file__))))

try:  # direct-script compatibility (repo pattern)
    from live_journal import read_jsonl, SIGNALS, TRADES, SNAPSHOTS, record_report  # type: ignore
    from telegram_client import send_telegram_message, telegram_delivery_status  # type: ignore
except ModuleNotFoundError:  # pytest / package mode
    from scripts.live_journal import (  # type: ignore
        read_jsonl,
        record_report,
        SIGNALS,
        SNAPSHOTS,
        TRADES,
    )
    from scripts.telegram_client import (  # type: ignore
        send_telegram_message,
        telegram_delivery_status,
    )

try:  # reuse the report template helpers without circular imports
    from live_report_telegram import _esc, _num, report_text_sha256  # type: ignore
except ModuleNotFoundError:
    from scripts.live_report_telegram import _esc, _num, report_text_sha256  # type: ignore


def _parse_ts(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def _week_start_utc(now: datetime) -> datetime:
    """Monday 00:00 UTC of the week containing `now` (UTC convention)."""
    monday = (now - timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return monday


def collect_session_stats(
    *,
    signals_path: Path = SIGNALS,
    trades_path: Path = TRADES,
    snapshots_path: Path = SNAPSHOTS,
    since_utc: datetime | None = None,
) -> dict:
    """Deterministic aggregation of one session period from the journals."""
    since = since_utc.isoformat() if since_utc else None

    def in_period(row: dict) -> bool:
        if since is None:
            return True
        ts = _parse_ts(row.get("timestamp_utc") or row.get("recorded_at_utc"))
        return ts is not None and ts.isoformat() >= since

    signals = [r for r in read_jsonl(signals_path) if in_period(r)]
    trades = [r for r in read_jsonl(trades_path) if in_period(r)]
    snapshots = [r for r in read_jsonl(snapshots_path) if in_period(r)]

    def count(rows: list[dict], status: str) -> int:
        return sum(1 for r in rows if r.get("status") == status)

    dry_run_trades = count(trades, "DRY_RUN")
    open_trades = count(trades, "OPEN")
    failed = count(trades, "EXECUTION_FAILED")
    rejected = count(signals, "DUPLICATE_REJECTED")

    executions = dry_run_trades + open_trades + failed
    gateway_uptime_rows = len(snapshots)

    last_tick = None
    for row in reversed(snapshots):
        if row.get("bid") is not None:
            last_tick = row
            break

    return {
        "signals_total": len(signals),
        "approved": count(signals, "APPROVED"),
        "duplicate_rejected": rejected,
        "executions": executions,
        "dry_run": dry_run_trades,
        "open_trades": open_trades,
        "execution_failed": failed,
        "snapshots": gateway_uptime_rows,
        "last_tick": {
            "bid": last_tick.get("bid") if last_tick else None,
            "ask": last_tick.get("ask") if last_tick else None,
            "time_utc": last_tick.get("time_utc") if last_tick else None,
        },
        "last_signal_at_utc": (signals[-1].get("timestamp_utc") if signals else None),
    }


def format_session_report(stats: dict, *, period_label: str, mode: str) -> str:
    """Render the session monitor template (compact HTML, deterministic)."""
    last_tick = stats.get("last_tick") or {}
    tick_text = (
        f"{_num(last_tick.get('bid'), 2)} / {_num(last_tick.get('ask'), 2)}"
        if last_tick.get("bid") is not None
        else "n/a"
    )
    lines = [
        "<b>🩺 SP2L Live Session Monitor</b>",
        f"🗓 {period_label} · Mode: {_esc(mode)}",
        "",
        "<b>Signals</b>",
        f"Total {_esc(stats['signals_total'])} · "
        f"Approved {_esc(stats['approved'])} · "
        f"Rejected {_esc(stats['duplicate_rejected'])}",
        f"Last: {_esc(stats['last_signal_at_utc'] or '—')}",
        "",
        "<b>Execution</b>",
        f"Executions {_esc(stats['executions'])} · "
        f"DRY_RUN {_esc(stats['dry_run'])} · "
        f"Open {_esc(stats['open_trades'])} · "
        f"Failed {_esc(stats['execution_failed'])}",
        "",
        "<b>Gateway</b>",
        f"Snapshots {_esc(stats['snapshots'])} · "
        f"Last tick (bid/ask): {tick_text}",
        "",
        "🟡 Monitoring only — not a trading signal",
        "🟢 Live trading: OFF",
        "🧭 Geometry gate: UNRESOLVED_FROZEN_GEOMETRY_GATE",
    ]
    return "\n".join(lines)


def send_session_report(
    report_text: str,
    *,
    period_label: str,
    report_timestamp_utc: str,
    sent_at_utc: str,
) -> dict:
    """Deliver via the shared client and append to the report log."""
    result = send_telegram_message(report_text, parse_mode="HTML")
    delivery = telegram_delivery_status()
    record = {
        "report_type": "live_session_monitor",
        "period_label": period_label,
        "period_start_utc": _week_start_utc(datetime.now(timezone.utc)).isoformat(),
        "period_end_utc": datetime.now(timezone.utc).isoformat(),
        "report_timestamp_utc": report_timestamp_utc,
        "sent_at_utc": sent_at_utc,
        "report_text_sha256": report_text_sha256(report_text),
        "telegram_status": result.detail,
        "telegram_response": result.raw if result.success else None,
        "delivery_mode": delivery.get("delivery_mode"),
        "success": bool(result.success),
    }
    record_report(record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Weekly live-session monitor report")
    parser.add_argument("--send", action="store_true", help="deliver via Telegram")
    parser.add_argument("--since", default=None, help="ISO UTC lower bound override")
    parser.add_argument("--out", default=None, help="optional JSON artifact path")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    since = (
        datetime.fromisoformat(args.since.replace("Z", "+00:00"))
        if args.since
        else _week_start_utc(now)
    )
    stats = collect_session_stats(since_utc=since)
    live = os.getenv("LIVE_TRADING_ENABLE", "false").strip().lower() == "true"
    allow = os.getenv("ALLOW_REAL_EXECUTION", "false").strip().lower() == "true"
    mode = "LIVE" if (live and allow) else "DRY-RUN"
    period_label = f"{since.date().isoformat()} → {now.date().isoformat()} (UTC)"
    text = format_session_report(stats, period_label=period_label, mode=mode)
    print(text)
    if not args.send:
        return 0

    record = send_session_report(
        text,
        period_label=period_label,
        report_timestamp_utc=now.isoformat(),
        sent_at_utc=datetime.now(timezone.utc).isoformat(),
    )
    print(json.dumps(record, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(record, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
