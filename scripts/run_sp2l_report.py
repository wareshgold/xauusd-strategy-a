"""SP2L report runner CLI (reporting/infrastructure only).

Builds deterministic daily/weekly/monthly reports from the live journal and
(optionally) sends them through the shared Telegram layer.

Safety boundaries:
- does not generate BUY/SELL signals;
- does not enable live trading (LIVE_TRADING_ENABLE stays false);
- does not define or modify SP2L geometry.

Usage:
  python scripts/run_sp2l_report.py --type weekly \
      --start 2026-09-14T00:00:00+00:00 --end 2026-09-19T21:00:00+00:00 \
      [--send] [--json-out artifacts/...] [--csv-out ...]

With --start/--end omitted, period bounds come from the deterministic
scheduler for the current instant. Without --send, nothing leaves the host.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from live_journal import _csv_export
    from live_report_engine import (
        ReportConfig,
        build_report,
        load_journal,
        load_report_config,
        period_csv_rows,
        report_to_json,
    )
    from live_report_scheduler import (
        ScheduleConfig,
        daily_report_bounds,
        load_schedule_config,
        monthly_report_bounds,
        weekly_report_bounds,
    )
    from live_report_telegram import format_report, send_report
except ModuleNotFoundError:
    from scripts.live_journal import _csv_export
    from scripts.live_report_engine import (
        ReportConfig,
        build_report,
        load_journal,
        load_report_config,
        period_csv_rows,
        report_to_json,
    )
    from scripts.live_report_scheduler import (
        ScheduleConfig,
        daily_report_bounds,
        load_schedule_config,
        monthly_report_bounds,
        weekly_report_bounds,
    )
    from scripts.live_report_telegram import format_report, send_report


def _parse_ts(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _period_bounds(report_type: str, now_utc: datetime, schedule: ScheduleConfig):
    if report_type == "daily":
        return daily_report_bounds(now_utc, schedule)
    if report_type == "weekly":
        return weekly_report_bounds(now_utc, schedule)
    if report_type == "monthly":
        return monthly_report_bounds(now_utc, schedule)
    raise ValueError(f"unsupported report type: {report_type}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build (and optionally send) an SP2L report.")
    parser.add_argument("--type", choices=["daily", "weekly", "monthly"], required=True)
    parser.add_argument("--start", help="period start ISO timestamp (UTC offset required or assumed UTC)")
    parser.add_argument("--end", help="period end ISO timestamp (exclusive)")
    parser.add_argument("--now", help="reference instant for scheduler bounds (ISO); default: current UTC")
    parser.add_argument("--send", action="store_true", help="send the rendered report via Telegram and log it")
    parser.add_argument("--json-out", help="write the canonical JSON artifact to this path")
    parser.add_argument("--csv-out", help="write period trade rows CSV to this path")
    args = parser.parse_args(argv)

    engine_config = load_report_config()
    schedule = load_schedule_config()

    if args.start and args.end:
        start, end = _parse_ts(args.start), _parse_ts(args.end)
    else:
        now_utc = _parse_ts(args.now) if args.now else datetime.now(timezone.utc)
        start, end = _period_bounds(args.type, now_utc, schedule)

    signals, trades = load_journal(Path(engine_config.journal_source))

    generated_at_utc = datetime.now(timezone.utc).isoformat()
    report = build_report(args.type, start, end, generated_at_utc, signals, trades, engine_config)
    report_text = format_report(report)

    if args.json_out:
        json_path = Path(args.json_out)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(report_to_json(report) + "\n", encoding="utf-8")

    if args.csv_out:
        csv_path = Path(args.csv_out)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        _csv_export(period_csv_rows(trades, start, end), csv_path)

    if args.send:
        record = send_report(
            report_text,
            report_type=args.type,
            period_start_utc=start.isoformat(),
            period_end_utc=end.isoformat(),
            period_label=f"{args.type}:{start.date().isoformat()}",
            report_timestamp_utc=generated_at_utc,
            sent_at_utc=datetime.now(timezone.utc).isoformat(),
        )
        print(json.dumps({"telegram_delivery": record}, indent=2, sort_keys=True))
        if not record["success"]:
            print(
                "Telegram delivery failed; the attempt is logged in "
                "runtime/journal/report_log.jsonl. Report artifact remains valid.",
                file=sys.stderr,
            )

    print(report_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
