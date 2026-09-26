"""Telegram formatting + delivery layer for SP2L reports.

Compact, HTML-formatted Telegram templates:
- summary-first (signals -> performance -> daily/weekly breakdown ->
  execution -> safety footer);
- no per-trade dump on Telegram: the trade-by-trade detail remains in the
  JSON/XLSX artifacts and period CSV for audit ("قابل بررسی" stays in the
  artifacts; Telegram stays readable);
- renders an already-computed report dict (deterministic, no wall clock);
- sends via the shared Telegram client with parse_mode=HTML (all dynamic
  values HTML-escaped);
- appends every delivery attempt to runtime/journal/report_log.jsonl;
- never calculates geometry, never alters direction, never creates signals.
"""

from __future__ import annotations

import hashlib
import html
from datetime import datetime
from typing import Any

try:
    from scripts.live_journal import record_report
    from scripts.telegram_client import send_telegram_message, telegram_delivery_status
except ModuleNotFoundError:
    from live_journal import record_report
    from telegram_client import send_telegram_message, telegram_delivery_status

TITLES = {
    "daily": "📊 SP2L Daily Report",
    "weekly": "📊 SP2L Weekly Report",
    "monthly": "📊 SP2L Monthly Report",
}
_EMOJI = {"win": "✅", "loss": "❌", "ambiguous": "⚠️"}


# ---------------------------------------------------------------------------
# Deterministic scalar formatting
# ---------------------------------------------------------------------------


def _esc(value: Any) -> str:
    return html.escape(str(value), quote=False)


def _num(value: Any, digits: int = 2, signed: bool = False) -> str:
    if value is None:
        return "—"
    return f"{float(value):+.{digits}f}" if signed else f"{float(value):.{digits}f}"


def _pct(value: Any) -> str:
    return "—" if value is None else f"{float(value):.2f}%"


def _period_header(report: dict) -> str:
    period = report.get("period", {})
    start = str(period.get("start_utc", ""))[:10]
    end = str(period.get("end_utc", ""))[:10]
    return f"🗓 {start} → {end} · {_esc(period.get('session_timezone', 'UTC'))}"


def _live_trading_flag(system: dict) -> str:
    status = str(system.get("live_trading_status", ""))
    return "OFF" if status.startswith("DISABLED") else "ON"


def _signals_block(report: dict) -> list[str]:
    sig = report.get("signals", {})
    lines = ["<b>Signals</b>"]
    lines.append(
        f"Total <b>{sig.get('total', 0)}</b> · "
        f"{_EMOJI['win']} {sig.get('win', 0)} · "
        f"{_EMOJI['loss']} {sig.get('loss', 0)} · "
        f"{_EMOJI['ambiguous']} {sig.get('ambiguous', 0)}"
    )
    win_rate = report.get("performance", {}).get("win_rate_pct")
    lines.append(f"Win rate: <b>{_pct(win_rate)}</b>")
    if sig.get("ambiguous", 0):
        lines.append(f"{_EMOJI['ambiguous']} = outcome unresolved in journal")
    return lines


def _performance_block(report: dict) -> list[str]:
    perf = report.get("performance", {})
    lines = ["<b>Performance</b>"]
    lines.append(f"Net R: <b>{_num(perf.get('net_r'), 2, signed=True)}</b>")
    if perf.get("pips_basis") == "EXPLICIT_PIP_SIZE":
        lines.append(f"Net Pips: <b>{_num(perf.get('net_pips'), 2, signed=True)}</b>")
    lines.append(f"Profit Factor: <b>{_num(perf.get('profit_factor'))}</b>")
    lines.append(f"Max Drawdown: {_num(perf.get('max_drawdown_r'))} R")
    return lines


def _execution_block(report: dict) -> list[str]:
    exe = report.get("execution", {})
    lines = ["<b>Execution</b>"]
    lines.append(
        f"Closed {exe.get('closed_trades', 0)} · Open {exe.get('open_trades', 0)}"
        + (f" · Dry-run {exe.get('dry_run_trades', 0)}" if exe.get("dry_run_trades") else "")
    )
    lines.append(f"Reconciliation: {_esc(exe.get('broker_reconciliation_status', 'NO_DATA'))}")
    return lines


def _footer_block(report: dict) -> list[str]:
    system = report.get("system", {})
    return [
        "🟡 Research mode — not a trading signal",
        f"🟢 Live trading: {_live_trading_flag(system)}",
        f"🧭 Geometry gate: {_esc(system.get('geometry_status', 'UNKNOWN'))}",
    ]


# ---------------------------------------------------------------------------
# Breakdown renderers
# ---------------------------------------------------------------------------


def _weekday_label(date_key: str) -> str:
    try:
        return datetime.strptime(date_key, "%Y-%m-%d").strftime("%a %d")
    except ValueError:
        return date_key


def _bucket_lines(rows: list[dict], key: str) -> list[str]:
    if not rows:
        return ["(no records)"]
    lines = []
    for row in rows:
        label = _weekday_label(str(row.get(key, "")))
        lines.append(
            f"{_esc(label)} · {row.get('win', 0)}W {row.get('loss', 0)}L "
            f"{row.get('ambiguous', 0)}A · {_num(row.get('net_r'), 2, signed=True)}R"
        )
    return lines


def _daily_breakdown_block(report: dict) -> list[str]:
    breakdown = report.get("daily_breakdown") or {}
    return ["<b>Daily</b>", *_bucket_lines(breakdown.get("rows") or [], "date")]


def _weekly_breakdown_block(report: dict) -> list[str]:
    breakdown = report.get("weekly_breakdown") or {}
    return ["<b>Weeks</b>", *_bucket_lines(breakdown.get("rows") or [], "week")]


def _equity_block(report: dict) -> list[str]:
    equity = report.get("equity_summary") or {}
    return [
        "<b>Equity (R)</b>",
        f"End {_num(equity.get('equity_end_r'), 2, signed=True)} · "
        f"Peak {_num(equity.get('equity_peak_r'), 2)} · "
        f"Trough {_num(equity.get('equity_trough_r'), 2, signed=True)} · "
        f"Max DD {_num(equity.get('max_drawdown_r'), 2)}",
    ]


# ---------------------------------------------------------------------------
# Template dispatch
# ---------------------------------------------------------------------------


def format_report(report: dict) -> str:
    """Render a report dict into the compact HTML Telegram template."""
    report_type = report.get("report_type")
    if report_type not in TITLES:
        raise ValueError(f"unsupported report type: {report_type}")

    lines: list[str] = [TITLES[report_type], _period_header(report), ""]
    lines.extend(_signals_block(report))
    lines.append("")
    lines.extend(_performance_block(report))
    lines.append("")

    if report_type in {"weekly", "monthly"}:
        lines.extend(_daily_breakdown_block(report))
        lines.append("")
    if report_type == "monthly":
        lines.extend(_weekly_breakdown_block(report))
        lines.append("")
        lines.extend(_equity_block(report))
        lines.append("")

    lines.extend(_execution_block(report))
    lines.append("")
    lines.extend(_footer_block(report))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Delivery + send log
# ---------------------------------------------------------------------------


def report_text_sha256(report_text: str) -> str:
    return hashlib.sha256(report_text.encode("utf-8")).hexdigest()


def send_report(
    report_text: str,
    *,
    report_type: str,
    period_start_utc: str,
    period_end_utc: str,
    period_label: str,
    report_timestamp_utc: str,
    sent_at_utc: str,
) -> dict[str, Any]:
    """Send one report via the shared client and log the delivery attempt.

    The log record contains: report timestamp, report type, Telegram
    response, and success/failure. Never raises.
    """
    result = send_telegram_message(report_text, parse_mode="HTML")
    delivery = telegram_delivery_status()
    record = {
        "report_type": report_type,
        "period_label": period_label,
        "period_start_utc": period_start_utc,
        "period_end_utc": period_end_utc,
        "report_timestamp_utc": report_timestamp_utc,
        "sent_at_utc": sent_at_utc,
        "delivery_mode": delivery["mode"],
        "telegram_response": result.response if result.response is not None else result.detail,
        "telegram_status": result.detail,
        "success": result.success,
        "report_text_sha256": report_text_sha256(report_text),
    }
    record_report(record)
    return record
