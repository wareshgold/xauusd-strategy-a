"""Telegram formatting + delivery layer for SP2L reports.

Reporting/infrastructure only:
- renders an already-computed report dict into fixed text templates;
- sends via the shared Telegram client (scripts/telegram_client.py);
- appends every delivery attempt to runtime/journal/report_log.jsonl with
  report timestamp, report type, Telegram response and success/failure;
- never calculates geometry, never alters direction, never creates signals.

Research-mode labelling contract (SP2L_RESEARCH_LIVE_MODE_CONTRACT):
Telegram output is explicitly labelled RESEARCH and must not imply
production authorization.
"""

from __future__ import annotations

import hashlib
from typing import Any

try:
    from live_journal import record_report
    from telegram_client import send_telegram_message
except ModuleNotFoundError:
    from scripts.live_journal import record_report
    from scripts.telegram_client import send_telegram_message

LABELS = {
    "daily": "SP2L Daily Report — RESEARCH",
    "weekly": "SP2L Weekly Report — RESEARCH",
    "monthly": "SP2L Monthly Report — RESEARCH",
}


# ---------------------------------------------------------------------------
# Deterministic scalar formatting
# ---------------------------------------------------------------------------


def _fmt(value: Any, digits: int = 2) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.{digits}f}"


def _fmt_pips(report: dict) -> str:
    perf = report.get("performance", {})
    basis = perf.get("pips_basis")
    net_pips = perf.get("net_pips")
    if basis == "NOT_CONFIGURED":
        return "n/a (pip size not configured)"
    return f"{_fmt(net_pips, 2)} (basis: EXPLICIT_PIP_SIZE)"


def _period_line(report: dict) -> str:
    period = report.get("period", {})
    return (
        f"Trading Period: {period.get('start_utc')} → {period.get('end_utc')} "
        f"({period.get('session_timezone')})"
    )


def _date_line(report: dict) -> str:
    start = str(report.get("period", {}).get("start_utc", ""))
    return f"Date: {start[:10]} ({report.get('period', {}).get('session_timezone')})"


def _signals_section(report: dict) -> list[str]:
    sig = report.get("signals", {})
    return [
        "Signals:",
        f"- Total signals: {sig.get('total', 0)}",
        f"- WIN count: {sig.get('win', 0)}",
        f"- LOSS count: {sig.get('loss', 0)}",
        f"- AMBIGUOUS count: {sig.get('ambiguous', 0)}",
    ]


def _performance_section(report: dict) -> list[str]:
    perf = report.get("performance", {})
    win_rate = perf.get("win_rate_pct")
    win_rate_text = "n/a" if win_rate is None else f"{_fmt(win_rate, 2)}%"
    return [
        "Performance:",
        f"- Net pips: {_fmt_pips(report)}",
        f"- Net R: {_fmt(perf.get('net_r'), 4)}",
        f"- Profit factor: {_fmt(perf.get('profit_factor'), 4)}",
        f"- Win rate: {win_rate_text}",
        f"- Max drawdown: {_fmt(perf.get('max_drawdown_r'), 4)} R",
    ]


def _execution_section(report: dict) -> list[str]:
    exe = report.get("execution", {})
    return [
        "Execution:",
        f"- Open trades: {exe.get('open_trades', 0)}",
        f"- Closed trades: {exe.get('closed_trades', 0)}",
        f"- Broker reconciliation status: {exe.get('broker_reconciliation_status', 'NO_DATA')}",
    ]


def _system_section(report: dict) -> list[str]:
    system = report.get("system", {})
    return [
        "System:",
        f"- Geometry status: {system.get('geometry_status', 'UNKNOWN')}",
        f"- Live trading status: {system.get('live_trading_status', 'UNKNOWN')}",
    ]


# ---------------------------------------------------------------------------
# Breakdown renderers
# ---------------------------------------------------------------------------


def _daily_breakdown_lines(report: dict) -> list[str]:
    breakdown = report.get("daily_breakdown") or {}
    lines = [f"Daily breakdown ({breakdown.get('timezone', 'UTC')}):"]
    rows = breakdown.get("rows") or []
    if not rows:
        lines.append("- (no records)")
        return lines
    for row in rows:
        lines.append(
            f"- {row['date']}: signals={row['signals']} win={row['win']} "
            f"loss={row['loss']} ambiguous={row['ambiguous']} net_r={_fmt(row['net_r'], 4)}"
        )
    return lines


def _weekly_breakdown_lines(report: dict) -> list[str]:
    breakdown = report.get("weekly_breakdown") or {}
    lines = [f"Weekly breakdown ({breakdown.get('timezone', 'UTC')}):"]
    rows = breakdown.get("rows") or []
    if not rows:
        lines.append("- (no records)")
        return lines
    for row in rows:
        lines.append(
            f"- {row['week']}: signals={row['signals']} win={row['win']} "
            f"loss={row['loss']} ambiguous={row['ambiguous']} net_r={_fmt(row['net_r'], 4)}"
        )
    return lines


def _trade_list_lines(report: dict) -> list[str]:
    rows = report.get("trade_list_summary") or []
    lines = ["Trade list summary:"]
    if not rows:
        lines.append("- (no signals in period)")
        return lines
    for row in rows:
        lines.append(
            f"- {row.get('signal_id')} {row.get('direction')} {row.get('status')} "
            f"result={row.get('result')} r={_fmt(row.get('r_multiple'), 4)} "
            f"pips={_fmt(row.get('pips'), 2)}"
        )
    return lines


def _equity_lines(report: dict) -> list[str]:
    equity = report.get("equity_summary") or {}
    return [
        "Equity/performance summary (R-basis):",
        f"- Equity start R: {_fmt(equity.get('equity_start_r'), 4)}",
        f"- Equity end R: {_fmt(equity.get('equity_end_r'), 4)}",
        f"- Equity peak R: {_fmt(equity.get('equity_peak_r'), 4)}",
        f"- Equity trough R: {_fmt(equity.get('equity_trough_r'), 4)}",
        "Drawdown summary:",
        f"- Max drawdown: {_fmt(equity.get('max_drawdown_r'), 4)} R",
    ]


# ---------------------------------------------------------------------------
# Template dispatch
# ---------------------------------------------------------------------------


def format_report(report: dict) -> str:
    """Render a report dict into its fixed Telegram text template."""
    report_type = report.get("report_type")
    if report_type not in LABELS:
        raise ValueError(f"unsupported report type: {report_type}")

    lines: list[str] = [LABELS[report_type]]
    if report_type == "daily":
        lines.append(_date_line(report))
    lines.append(_period_line(report))
    lines.append("")
    lines.extend(_signals_section(report))
    lines.append("")
    lines.extend(_performance_section(report))
    lines.append("")
    lines.extend(_execution_section(report))
    lines.append("")

    if report_type in {"weekly", "monthly"}:
        lines.extend(_daily_breakdown_lines(report))
        lines.append("")
        lines.extend(_trade_list_lines(report))
        lines.append("")
    if report_type == "monthly":
        lines.extend(_weekly_breakdown_lines(report))
        lines.append("")
        lines.extend(_equity_lines(report))
        lines.append("")

    lines.extend(_system_section(report))
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
    result = send_telegram_message(report_text)
    record = {
        "report_type": report_type,
        "period_label": period_label,
        "period_start_utc": period_start_utc,
        "period_end_utc": period_end_utc,
        "report_timestamp_utc": report_timestamp_utc,
        "sent_at_utc": sent_at_utc,
        "telegram_response": result.response if result.response is not None else result.detail,
        "telegram_status": result.detail,
        "success": result.success,
        "report_text_sha256": report_text_sha256(report_text),
    }
    record_report(record)
    return record
