"""Read-only monitor for SP2L V3.1 RR4/ACT40/TRAIL40 Demo forward runner.

Reads the exact V3.1 state/event paths only. It deliberately does not initialize
or shut down MT5 because the runner shares that terminal connection. It never
writes runner state and binds to localhost.
Run in a separate PowerShell window:
    python scripts/sp2l_v31_rr4_act40_monitor.py
Default URL: http://127.0.0.1:8791
"""
from __future__ import annotations

import html
import json
import os
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Flask, Response, jsonify

ROOT = Path(__file__).resolve().parents[1]
# The monitor may run from a separate dashboard worktree. Bind data paths to
# the explicitly selected runner worktree instead of silently reading ROOT.
_RUNNER_ROOT_ENV = os.getenv("SP2L_RUNNER_ROOT", "").strip()
RUNNER_ROOT = (
    Path(_RUNNER_ROOT_ENV).expanduser().resolve()
    if _RUNNER_ROOT_ENV else ROOT
)
RUNNER_ROOT_SOURCE = "SP2L_RUNNER_ROOT" if _RUNNER_ROOT_ENV else "monitor-worktree fallback"
RUNTIME = RUNNER_ROOT / "runtime"
ARTIFACTS = RUNNER_ROOT / "artifacts" / "forward-test"
STATE_FILE = RUNTIME / "sp2l_v3_1_xauusd_rr4_act40_forward_state.json"
EVENTS = ARTIFACTS / "SP2L_V3_1_XAUUSD_RR4_ACT40_FORWARD_EVENTS.jsonl"
RUNNER_LOCK = RUNTIME / "sp2l_multi_symbol_forward_runner.lock"
PORT = int(os.getenv("SP2L_DASHBOARD_PORT", "8791"))
REFRESH_SECONDS = 15
SYMBOL = "XAUUSD.ecn"
VERSION = "SP2L_V3_1_XAUUSD_RR4_ACT40_TRAIL40_20261101"
# Iran uses UTC+03:30 year-round in the 2026 operating period.
# A fixed offset avoids relying on an OS-installed IANA tz database on Windows.
TEHRAN_TZ = timezone(timedelta(hours=3, minutes=30), name="Asia/Tehran")

app = Flask(__name__)


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _read_events_with_health(limit: int = 2000) -> tuple[list[dict], dict]:
    health = {
        "path": str(EVENTS), "total_lines": 0, "malformed_lines": 0,
        "last_malformed_line": None, "read_error": None,
    }
    try:
        lines = EVENTS.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        health["read_error"] = f"{type(exc).__name__}: {exc}"
        return [], health
    health["total_lines"] = len(lines)
    out = []
    start = max(0, len(lines) - limit)
    for line_number, line in enumerate(lines[start:], start=start + 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            if isinstance(item, dict):
                out.append(item)
            else:
                health["malformed_lines"] += 1
                health["last_malformed_line"] = line_number
        except json.JSONDecodeError as exc:
            health["malformed_lines"] += 1
            health["last_malformed_line"] = line_number
            health["last_parse_error"] = f"line {line_number}: {exc.msg}"
    return out, health


def _read_events(limit: int = 2000) -> list[dict]:
    return _read_events_with_health(limit)[0]


def _runner_status() -> dict:
    """Identify the Runner by its exact script path; a lock file is optional legacy metadata."""
    runner_script = RUNNER_ROOT / "scripts" / "run_sp2l_v3_1_xauusd_forward_test.py"
    if os.name != "nt":
        return {
            "pid": None, "pids": [], "alive": None,
            "detail": "process command-line probe is available only on Windows",
            "source": "unavailable",
        }
    if not runner_script.is_file():
        return {
            "pid": None, "pids": [], "alive": None,
            "detail": f"expected Runner script is missing: {runner_script}",
            "source": "runner_script_path",
        }
    # Keep the PowerShell program static. Pass the path through the child
    # environment instead of interpolating a filesystem path into a command.
    probe = r"""
$ErrorActionPreference = 'Stop'
$runnerScript = [IO.Path]::GetFullPath((Join-Path $env:SP2L_MONITOR_RUNNER_ROOT 'scripts\run_sp2l_v3_1_xauusd_forward_test.py'))
$matches = @(Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -and $_.CommandLine.IndexOf($runnerScript, [StringComparison]::OrdinalIgnoreCase) -ge 0
} | ForEach-Object {
    [PSCustomObject]@{
        pid = [int]$_.ProcessId
        parent_pid = [int]$_.ParentProcessId
        command_line = [string]$_.CommandLine
    }
})
ConvertTo-Json -InputObject $matches -Compress -Depth 3
"""
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", probe],
            capture_output=True, text=True, timeout=8, check=False,
            env={**os.environ, "SP2L_MONITOR_RUNNER_ROOT": str(RUNNER_ROOT)},
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "PowerShell process probe failed").strip()
            return {
                "pid": None, "pids": [], "alive": None,
                "detail": f"Runner process probe unavailable: {detail}",
                "source": "windows_cim_process_probe",
            }
        raw = result.stdout.strip()
        rows = json.loads(raw) if raw else []
        if isinstance(rows, dict):
            rows = [rows]
        rows = [row for row in rows if isinstance(row, dict) and row.get("pid")]
        rows.sort(key=lambda row: (int(row.get("parent_pid") or 0), int(row["pid"])))
        pids = [int(row["pid"]) for row in rows]
        pid_set = set(pids)
        roots = [int(row["pid"]) for row in rows if int(row.get("parent_pid") or 0) not in pid_set]
        primary_pid = roots[0] if roots else (pids[0] if pids else None)
        return {
            "pid": primary_pid,
            "pids": pids,
            "alive": bool(pids),
            "detail": (
                "Runner process matched by exact script path"
                if pids else "No process matched the configured Runner script path"
            ),
            "source": "windows_cim_process_probe",
        }
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, TypeError, ValueError) as exc:
        return {
            "pid": None, "pids": [], "alive": None,
            "detail": f"Runner process probe unavailable: {type(exc).__name__}: {exc}",
            "source": "windows_cim_process_probe",
        }


def _mt5_probe() -> dict:
    """MT5 is intentionally isolated: never initialize/shutdown the runner terminal."""
    return {
        "connected": None,
        "trade_allowed": None,
        "account": None,
        "tick": None,
        "orders": [],
        "positions": [],
        "error": "Not queried: dashboard must not touch the runner's MT5 terminal",
    }


def _summary(events: list[dict]) -> dict:
    counts = {
        "signals": 0, "order_results": 0, "successful_orders": 0,
        "trail_updates": 0, "trail_failures": 0, "deal_lifecycle_events": 0,
        "deal_lifecycle_duplicate_rows": 0, "net": 0.0,
    }
    seen_deal_ids = set()
    for event in events:
        kind = event.get("event")
        if kind == "TELEGRAM_SIGNAL":
            counts["signals"] += 1
        elif kind == "ORDER_RESULT":
            counts["order_results"] += 1
            if bool((event.get("result") or {}).get("ok")):
                counts["successful_orders"] += 1
        elif kind == "TRAIL_UPDATE":
            if event.get("success") is True:
                counts["trail_updates"] += 1
            elif event.get("success") is False:
                counts["trail_failures"] += 1
        elif kind == "TELEGRAM_DEAL_LIFECYCLE":
            deal_id = event.get("deal")
            if deal_id is not None:
                deal_key = str(deal_id)
                if deal_key in seen_deal_ids:
                    counts["deal_lifecycle_duplicate_rows"] += 1
                    continue
                seen_deal_ids.add(deal_key)
            counts["deal_lifecycle_events"] += 1
            try:
                counts["net"] += float(event.get("net", 0) or 0)
            except (TypeError, ValueError):
                pass
    return counts


def _esc(value) -> str:
    return html.escape(str(value))


def _fmt_time(value) -> str:
    try:
        return datetime.fromtimestamp(int(value), timezone.utc).strftime("%H:%M:%S UTC")
    except (TypeError, ValueError, OSError):
        return "—"


def _fmt_event_time(value) -> str:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(TEHRAN_TZ).strftime("%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError, OSError):
        return "—"


def _file_health(path: Path) -> str:
    try:
        stat = path.stat()
        age = max(0, time.time() - stat.st_mtime)
        return f"present · {stat.st_size} bytes · updated {age:.0f}s ago"
    except OSError:
        return "missing or unreadable"

def _build_diagnostics(events: list[dict], runner: dict, event_health: dict) -> list[dict]:
    """Convert explicit runtime evidence into actionable, timestamped dashboard diagnostics."""
    items: list[dict] = []
    successful_trail_keys = {
        (str(event.get("position")), str(event.get("completed_bar_time")))
        for event in events
        if event.get("event") == "TRAIL_UPDATE" and event.get("success") is True
        and event.get("position") is not None and event.get("completed_bar_time") is not None
    }
    delivered_signal_ids = {
        str(event.get("signal_id"))
        for event in events
        if event.get("event") == "TELEGRAM_SIGNAL"
        and event.get("signal_id") is not None
        and (
            event.get("success") is True
            or (isinstance(event.get("telegram"), dict) and event["telegram"].get("success") is True)
        )
    }

    def add(level: str, code: str, event: dict | None, message: str, detail: str = ""):
        event = event or {}
        items.append({
            "level": level,
            "code": code,
            "time_tehran": _fmt_event_time(event.get("ts_utc")) if event else "—",
            "event": event.get("event", "MONITOR_HEALTH"),
            "symbol": event.get("symbol", ""),
            "order": event.get("order") or event.get("tracked_order") or "",
            "position": event.get("position") or "",
            "deal": event.get("deal") or event.get("tracked_deal") or "",
            "message": message,
            "detail": detail,
        })

    if event_health.get("read_error"):
        add("ERROR", "EVENT_FILE_READ", None, "Event log cannot be read", event_health["read_error"])
    if event_health.get("malformed_lines", 0):
        add(
            "ERROR", "EVENT_JSON_INVALID", None,
            f'{event_health["malformed_lines"]} malformed JSON line(s) detected',
            f'Last malformed line: {event_health.get("last_malformed_line")}; '
            f'{event_health.get("last_parse_error", "")}',
        )
    if not _RUNNER_ROOT_ENV:
        add("WARNING", "RUNNER_ROOT_NOT_EXPLICIT", None,
            "SP2L_RUNNER_ROOT is unset; monitor is reading relative to its own worktree",
            f"Resolved data root: {RUNNER_ROOT}")
    elif not RUNNER_ROOT.is_dir():
        add("ERROR", "RUNNER_ROOT_UNAVAILABLE", None,
            "Configured Runner data root does not exist or is not a directory",
            f"Resolved data root: {RUNNER_ROOT}")
    try:
        state_age = max(0, time.time() - STATE_FILE.stat().st_mtime)
    except OSError as exc:
        state_age = None
        add("ERROR", "STATE_FILE_UNAVAILABLE", None, "Runner state file is missing or unreadable", str(exc))
    if state_age is not None and state_age > 90:
        add("WARNING", "STATE_FILE_STALE", None, "Runner state file has not been updated for more than 90 seconds", f"age_seconds={state_age:.0f}")
    if runner.get("alive") is False:
        add("ERROR", "RUNNER_PROCESS_NOT_FOUND", None,
            "No process matched the configured V3.1 Runner script path",
            runner.get("detail", ""))
    elif runner.get("alive") is None:
        add("WARNING", "RUNNER_PROCESS_UNVERIFIED", None,
            "Runner process status could not be verified; this is not evidence that the Runner stopped",
            runner.get("detail", ""))

    for event in events:
        kind = event.get("event")
        result = event.get("result") if isinstance(event.get("result"), dict) else {}
        telegram = event.get("telegram") if isinstance(event.get("telegram"), dict) else {}
        detail_fields = []
        for field in (
            "retcode", "comment", "last_error", "reason", "attempt_number",
            "retry_scheduled", "retry_max_attempts_per_bar", "completed_bar_time",
        ):
            if event.get(field) is not None:
                detail_fields.append(f"{field}={event[field]}")
        for field in ("ok", "retcode", "comment", "order", "deal"):
            if result.get(field) is not None:
                detail_fields.append(f"result.{field}={result[field]}")
        if telegram.get("success") is not None:
            detail_fields.append(f'telegram.success={telegram.get("success")}')
        if telegram.get("detail") is not None:
            detail_fields.append(f'telegram.detail={telegram.get("detail")}')
        detail = " · ".join(detail_fields)

        if kind == "SESSION_GATE_ERROR":
            add("ERROR", "SESSION_GATE_ERROR", event, "Session gate raised an error", detail)
        elif kind == "ORDER_RESULT" and result.get("ok") is False:
            add("ERROR", "ORDER_SEND_FAILED", event, "Order request failed", detail)
        elif kind == "TRAIL_UPDATE" and event.get("success") is False:
            trail_key = (str(event.get("position")), str(event.get("completed_bar_time")))
            if trail_key in successful_trail_keys:
                add("INFO", "TRAIL_UPDATE_RECOVERED", event, "A later trailing update succeeded for the same position and completed bar", detail)
            elif event.get("retry_scheduled") is True:
                add("WARNING", "TRAIL_UPDATE_RETRY_PENDING", event, "Trailing modification failed but a retry is scheduled; this is not yet a terminal failure", detail)
            else:
                add("ERROR", "TRAIL_UPDATE_FAILED", event, "Trailing stop modification failed without a recorded scheduled retry or recovery", detail)
        elif kind == "TRAIL_DEFERRED":
            trail_key = (str(event.get("position")), str(event.get("completed_bar_time")))
            if trail_key in successful_trail_keys:
                add("INFO", "TRAIL_DEFERRED_RECOVERED", event, "Deferred trailing update was subsequently applied for the same position and completed bar", detail or str(event.get("reason", "")))
            else:
                add("WARNING", "TRAIL_DEFERRED", event, "Trailing stop update was deferred; inspect the retry / next attempt", detail or str(event.get("reason", "")))
        elif kind == "START_TELEGRAM" and event.get("success") is False:
            add("ERROR", "TELEGRAM_START_FAILED", event, "Telegram startup notification failed", detail)
        elif kind == "TELEGRAM_DEAL_LIFECYCLE" and telegram.get("success") is False:
            add("ERROR", "TELEGRAM_DEAL_NOTIFY_FAILED", event, "Telegram deal notification failed", detail)
        elif kind == "TELEGRAM_SIGNAL_RETRY":
            signal_id = event.get("signal_id")
            if signal_id is not None and str(signal_id) in delivered_signal_ids:
                add("INFO", "TELEGRAM_RETRY_RECOVERED", event, "A later Telegram signal event confirms delivery for this signal ID", detail)
            else:
                add("WARNING", "TELEGRAM_SIGNAL_RETRY", event, "Signal notification entered retry handling; delivery is not yet confirmed", detail)
        elif kind == "HEARTBEAT":
            if event.get("mt5_connected") is False:
                add("ERROR", "MT5_DISCONNECTED", event, "Runner heartbeat reports MT5 disconnected", detail)
            if event.get("trade_allowed") is False:
                add("WARNING", "TRADING_NOT_ALLOWED", event, "Runner heartbeat reports trading is not allowed", detail)
        elif kind == "TELEGRAM_SIGNAL" and (
            event.get("success") is False or telegram.get("success") is False
        ):
            signal_id = event.get("signal_id")
            if signal_id is not None and str(signal_id) in delivered_signal_ids:
                add("INFO", "TELEGRAM_SIGNAL_RECOVERED", event, "A later Telegram signal event confirms delivery for this signal ID", detail)
            else:
                add("ERROR", "TELEGRAM_SIGNAL_FAILED", event, "Telegram signal notification failed", detail)
        elif kind in ("PENDING_ORDER_EXPIRED", "TELEGRAM_PENDING_EXPIRED"):
            add("INFO", "PENDING_ORDER_EXPIRED", event, "Pending-order lifecycle reached its recorded expiry event", detail or str(event.get("reason", "")))
        elif kind == "EXECUTION_BLOCKED":
            add("INFO", "EXECUTION_BLOCKED", event, "Candidate execution was blocked by a gate or guard (not automatically a software defect)", detail)
        elif isinstance(kind, str) and ("ERROR" in kind or "FAIL" in kind):
            add("ERROR", kind, event, f"Runner emitted {kind}", detail)

    return list(reversed(items[-100:]))


_REFRESH_SCRIPT = r"""<script>
(() => {
    const intervalMs = 15000;
    let inFlight = false;

    async function refreshDashboard() {
        if (document.hidden || inFlight) return;
        inFlight = true;
        const scrollY = window.scrollY;
        const detailsState = Array.from(
            document.querySelectorAll("main details"),
            item => item.open
        );

        try {
            const response = await fetch("/", { cache: "no-store" });
            if (!response.ok) {
                throw new Error("HTTP " + response.status);
            }
            const html = await response.text();
            const nextDocument = new DOMParser().parseFromString(html, "text/html");
            const nextMain = nextDocument.querySelector("main");
            const currentMain = document.querySelector("main");
            if (!nextMain || !currentMain) {
                throw new Error("Dashboard content not found");
            }

            currentMain.replaceChildren(
                ...Array.from(nextMain.childNodes, node => document.importNode(node, true))
            );
            document.querySelectorAll("main details").forEach((item, index) => {
                item.open = Boolean(detailsState[index]);
            });
            window.scrollTo(0, scrollY);

            const status = document.getElementById("refresh-status");
            if (status) {
                status.textContent = "آخرین بروزرسانی: " +
                    new Date().toLocaleTimeString("fa-IR");
            }
        } catch (error) {
            const status = document.getElementById("refresh-status");
            if (status) {
                status.textContent = "خطا در بروزرسانی؛ تلاش مجدد در نوبت بعد";
                status.title = String(error);
            }
        } finally {
            inFlight = false;
        }
    }

    window.setInterval(refreshDashboard, intervalMs);
})();
</script>"""

def _render() -> str:
    """Persian-first control center; filesystem-only and explicitly session-scoped."""
    state = _read_json(STATE_FILE)
    events, event_health = _read_events_with_health()
    runner = _runner_status()

    # Split diagnostics at the latest START so old incidents cannot masquerade
    # as current-session failures.
    start_indexes = [i for i, item in enumerate(events) if item.get("event") == "START"]
    if start_indexes:
        start_index = start_indexes[-1]
        previous_events = events[:start_index]
        session_events = events[start_index:]
        session_start = events[start_index].get("ts_utc")
        session_label = _fmt_event_time(session_start) + " Tehran"
    else:
        previous_events = []
        session_events = events
        session_start = None
        session_label = "رویداد START در پنجره خوانده‌شده پیدا نشد"

    clean_health = {"malformed_lines": 0, "read_error": None}
    session_diagnostics = _build_diagnostics(session_events, runner, event_health)
    historical_diagnostics = _build_diagnostics(
        previous_events, {"alive": True, "pid": None, "detail": "historical only"},
        clean_health,
    )
    historical_diagnostics = [
        item for item in historical_diagnostics
        if item.get("code") not in {
            "RUNNER_ROOT_NOT_EXPLICIT", "RUNNER_ROOT_UNAVAILABLE",
            "STATE_FILE_UNAVAILABLE", "STATE_FILE_STALE",
            "RUNNER_PROCESS_NOT_FOUND", "RUNNER_PROCESS_UNVERIFIED",
        }
    ]

    try:
        state_age = max(0, time.time() - STATE_FILE.stat().st_mtime)
        state_age_label = f"{state_age:.0f} ثانیه قبل"
    except OSError:
        state_age = None
        state_age_label = "فایل موجود نیست"

    try:
        event_stat = EVENTS.stat()
        event_age = max(0, time.time() - event_stat.st_mtime)
        event_age_label = f"{event_age:.0f} ثانیه قبل"
        event_size = event_stat.st_size
    except OSError:
        event_age = None
        event_age_label = "فایل موجود نیست"
        event_size = 0

    alive = runner.get("alive")
    if alive is True:
        runner_status = "در حال اجرا"
        runner_class = "good"
    elif alive is False:
        runner_status = "متوقف"
        runner_class = "bad"
    else:
        runner_status = "وضعیت تأیید نشده"
        runner_class = "warn"

    if state_age is not None and state_age <= 90:
        state_status, state_class = "تازه", "good"
    elif state_age is None:
        state_status, state_class = "ناموجود", "bad"
    else:
        state_status, state_class = "قدیمی", "warn"

    if event_age is not None and event_age <= 180:
        event_status, event_class = "به‌روز", "good"
    elif event_age is None:
        event_status, event_class = "ناموجود", "bad"
    else:
        event_status, event_class = "رویداد جدیدی ثبت نشده", "warn"

    stats = _summary(session_events)
    candidates = sum(1 for e in session_events if e.get("event") == "CANDIDATE")
    attempts = sum(1 for e in session_events if e.get("event") == "ORDER_ATTEMPT")
    blocked = sum(1 for e in session_events if e.get("event") == "EXECUTION_BLOCKED")
    failed_order_results = sum(
        1 for e in session_events
        if e.get("event") == "ORDER_RESULT"
        and isinstance(e.get("result"), dict)
        and e["result"].get("ok") is False
    )
    current_counts = {
        level: sum(1 for item in session_diagnostics if item["level"] == level)
        for level in ("ERROR", "WARNING", "INFO")
    }
    history_counts = {
        level: sum(1 for item in historical_diagnostics if item["level"] == level)
        for level in ("ERROR", "WARNING", "INFO")
    }

    latest = session_events[-1] if session_events else (events[-1] if events else {})
    latest_kind = latest.get("event", "هنوز رویدادی ثبت نشده")
    latest_time = _fmt_event_time(latest.get("ts_utc")) + " تهران" if latest else "—"
    latest_attempt = next(
        (e for e in reversed(session_events) if e.get("event") == "ORDER_ATTEMPT"),
        None,
    )
    if latest_attempt:
        attempt_text = (
            f"آخرین تلاش سفارش: {latest_attempt.get('direction', '—')} · "
            f"Entry {latest_attempt.get('entry', '—')} · "
            f"SL {latest_attempt.get('sl', '—')} · TP {latest_attempt.get('tp', '—')}"
        )
    else:
        attempt_text = "از زمان آخرین شروع، هنوز هیچ تلاش سفارش ثبت نشده است."

    def tracked_count(key):
        value = state.get(key, [])
        return len(value) if isinstance(value, (list, tuple, dict, set)) else 0

    diagnostic_rows = ""
    for item in reversed(session_diagnostics[-12:]):
        diagnostic_rows += (
            "<tr><td>" + _esc(item["time_tehran"]) + "</td><td>" +
            _esc(item["level"]) + "</td><td><code>" + _esc(item["code"]) +
            "</code></td><td>" + _esc(item["message"]) +
            ("<div class='technical'>" + _esc(item["detail"]) + "</div>" if item["detail"] else "") +
            "</td></tr>"
        )
    if not diagnostic_rows:
        diagnostic_rows = (
            "<tr><td colspan='4' class='good-text'>در رویدادهای نشست فعلی، خطا یا هشدار اجرایی ثبت نشده است.</td></tr>"
        )

    event_rows = ""
    event_names = {
        "START": "شروع Runner",
        "START_TELEGRAM": "اعلان شروع تلگرام",
        "STARTUP_BROKER_RECOVERY": "بازیابی وضعیت بروکر",
        "SESSION_GATE": "بررسی ساعت بازار",
        "CANDIDATE": "کاندیدای معاملاتی",
        "ORDER_ATTEMPT": "تلاش برای ثبت سفارش",
        "ORDER_RESULT": "نتیجه ثبت سفارش",
        "EXECUTION_BLOCKED": "اجرای مسدودشده توسط Guard",
        "TRAIL_UPDATE": "به‌روزرسانی Trailing",
        "TRAIL_DEFERRED": "Trailing به تعویق افتاد",
        "TELEGRAM_SIGNAL": "ارسال سیگنال تلگرام",
        "TELEGRAM_DEAL_LIFECYCLE": "رویداد معامله",
        "HEARTBEAT": "ضربان Runner",
    }
    for event in reversed(session_events[-12:]):
        kind = event.get("event", "?")
        result = event.get("result") if isinstance(event.get("result"), dict) else {}
        detail = event.get("detail") or event.get("outcome") or ""
        if kind == "ORDER_ATTEMPT":
            detail = (
                f"direction={event.get('direction')} entry={event.get('entry')} "
                f"sl={event.get('sl')} tp={event.get('tp')} volume={event.get('volume')}"
            )
        elif kind == "ORDER_RESULT":
            detail = (
                f"ok={result.get('ok')} retcode={result.get('retcode')} "
                f"order={result.get('order')} error={result.get('error')}"
            )
        elif kind == "TRAIL_UPDATE":
            detail_parts = [
                f"position={event.get('position')}",
                f"SL {event.get('old_sl')} -> {event.get('new_sl')}",
                f"success={event.get('success')}",
            ]
            for field in (
                "retcode", "comment", "last_error", "attempt_number",
                "retry_scheduled", "retry_max_attempts_per_bar",
            ):
                if event.get(field) is not None:
                    detail_parts.append(f"{field}={event[field]}")
            detail = " · ".join(detail_parts)
        elif kind == "TELEGRAM_DEAL_LIFECYCLE":
            detail = (
                f"deal={event.get('deal')} position={event.get('position')} "
                f"entry={event.get('entry')} net={event.get('net')}"
            )
        event_rows += (
            "<tr><td>" + _esc(_fmt_event_time(event.get("ts_utc"))) + " Tehran</td><td>" +
            _esc(event_names.get(kind, kind)) + "</td><td><code>" + _esc(kind) +
            "</code></td><td class='technical'>" + _esc(detail) + "</td></tr>"
        )
    if not event_rows:
        event_rows = "<tr><td colspan='4'>هنوز رویدادی ثبت نشده است.</td></tr>"

    if historical_diagnostics:
        history_text = (
            f"خطاهای تاریخی: {history_counts['ERROR']} · "
            f"هشدارهای تاریخی: {history_counts['WARNING']} · "
            f"اطلاعات تاریخی: {history_counts['INFO']}"
        )
        history_rows = "".join(
            "<tr><td>" + _esc(item["time_tehran"]) + "</td><td>" +
            _esc(item["level"]) + "</td><td><code>" + _esc(item["code"]) +
            "</code></td><td>" + _esc(item["message"]) + "</td></tr>"
            for item in reversed(historical_diagnostics[-20:])
        )
        history_html = (
            "<details><summary>" + _esc(history_text) +
            " — برای مشاهده باز کن</summary><table><tr><th>Tehran time / زمان تهران</th>"
            "<th>سطح</th><th>کد</th><th>شرح</th></tr>" + history_rows +
            "</table></details>"
        )
    else:
        history_html = "<p class='muted'>در پنجره رویدادهای قبل از نشست فعلی، تشخیص تاریخی ثبت نشده است.</p>"

    diagnostic_banner = (
        f"نشست فعلی: {current_counts['ERROR']} خطا · "
        f"{current_counts['WARNING']} هشدار · {current_counts['INFO']} اطلاع"
    )
    state_ids_text = (
        f"شناسه‌های ثبت‌شده در State: سفارش {tracked_count('orders')} · "
        f"پوزیشن {tracked_count('positions')} · رویداد Deal {tracked_count('deal_events')}"
    )

    return f"""<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8">

<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SP2L V3.1 — مرکز کنترل</title>
<style>
:root{{color-scheme:dark;--bg:#0b1220;--panel:#121d2e;--panel2:#172438;--line:#26374d;--text:#e8eef7;--muted:#9aabc0;--blue:#8ab4f8;--green:#7bd6a6;--yellow:#f3c969;--red:#ff8585}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:14px/1.7 "Segoe UI",Tahoma,Arial,sans-serif}}
main{{max-width:1500px;margin:0 auto;padding:24px}}header{{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:18px}}
h1{{font-size:25px;margin:0;color:#fff}}h2{{font-size:17px;margin:0 0 14px;color:var(--blue)}}h3{{font-size:14px;margin:0 0 8px;color:var(--muted)}}
.sub{{color:var(--muted);font-size:12px}}.pill{{border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-weight:700}}
.good{{color:var(--green);border-color:#285b47;background:#10291f}}.warn{{color:var(--yellow);border-color:#65532a;background:#2b2413}}.bad{{color:var(--red);border-color:#653535;background:#2c171a}}
.panel{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px;margin:14px 0}}
.grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}
.metric{{background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:14px;min-height:104px}}
.metric .label{{font-size:12px;color:var(--muted)}}.metric .value{{font-size:24px;font-weight:750;margin-top:5px;direction:ltr;text-align:right;overflow-wrap:anywhere}}
.metric .hint{{font-size:11px;color:var(--muted);margin-top:3px}}
.status-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}
.status-card{{background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:14px}}
.status-card .state{{font-size:18px;font-weight:700;margin-top:5px}}
.two{{display:grid;grid-template-columns:1.2fr 1fr;gap:14px}}
.note{{border-right:3px solid var(--blue);background:#13243a;padding:12px 14px;border-radius:8px;color:#dbe8f8}}
.good-text{{color:var(--green)}}.muted{{color:var(--muted)}}.warning-text{{color:var(--yellow)}}
table{{width:100%;border-collapse:collapse;font-size:12px;margin-top:10px}}
th,td{{padding:9px 10px;border-bottom:1px solid var(--line);text-align:right;vertical-align:top}}
th{{color:var(--muted);font-weight:600;background:#111b2b}}tr:hover td{{background:#162338}}
code,.technical{{direction:ltr;text-align:left;font:12px/1.6 Consolas,monospace;overflow-wrap:anywhere}}
.technical{{color:#b5c4d7;margin-top:4px}}details{{margin-top:10px}}summary{{cursor:pointer;color:var(--yellow);padding:8px 0}}
footer{{color:var(--muted);font-size:11px;margin:18px 0}}.tag{{font-size:11px;color:var(--muted);border:1px solid var(--line);border-radius:6px;padding:3px 7px}}
@media(max-width:900px){{.grid,.status-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}.two{{grid-template-columns:1fr}}}}
@media(max-width:520px){{main{{padding:12px}}.grid,.status-grid{{grid-template-columns:1fr 1fr}}h1{{font-size:20px}}.metric .value{{font-size:20px}}}}
</style></head><body><main>
<header><div><h1>SP2L V3.1 — مرکز کنترل XAUUSD</h1>
<div class="sub">{VERSION} · RR4 / ACT40 / DIST40 · فقط تحقیقاتی · فقط‌خواندنی · بروزرسانی خودکار هر {REFRESH_SECONDS} ثانیه</div></div>
<span class="pill {runner_class}">Runner: {_esc(runner_status)}</span>
<span class="tag" id="refresh-status">به‌روزرسانی خودکار: هر ۱۵ ثانیه</span></header>

<section class="panel">
<h2>وضعیت کلی سیستم</h2>
<div class="status-grid">
<div class="status-card"><div class="label">پردازش Runner</div><div class="state {_esc(runner_class)}">{_esc(runner_status)}</div><div class="hint">PID: {_esc(runner.get('pid') or '—')} · همه پردازش‌ها: {_esc(','.join(str(x) for x in runner.get('pids', [])) or '—')}</div></div>
<div class="status-card"><div class="label">فایل وضعیت Runner</div><div class="state {_esc(state_class)}">{_esc(state_status)}</div><div class="hint">آخرین تغییر: {_esc(state_age_label)}</div></div>
<div class="status-card"><div class="label">فایل رویدادها</div><div class="state {_esc(event_class)}">{_esc(event_status)}</div><div class="hint">آخرین تغییر: {_esc(event_age_label)} · {_esc(f'{event_size:,}')} بایت</div></div>
<div class="status-card"><div class="label">شروع نشست فعلی</div><div class="state">{_esc(session_label)}</div><div class="hint">رویدادهای این نشست: {_esc(len(session_events))}</div></div>
</div>
</section>

<section class="panel">
<h2>فعالیت از آخرین Restart</h2>
<div class="grid">
<div class="metric"><div class="label">کاندیداهای معاملاتی</div><div class="value">{candidates}</div><div class="hint">رویداد CANDIDATE</div></div>
<div class="metric"><div class="label">تلاش‌های ثبت سفارش</div><div class="value">{attempts}</div><div class="hint">ORDER_ATTEMPT</div></div>
<div class="metric"><div class="label">سفارش‌های موفق ثبت‌شده</div><div class="value">{stats['successful_orders']}</div><div class="hint">نتیجه موفق ORDER_RESULT</div></div>
<div class="metric"><div class="label">موارد مسدودشده توسط Guard</div><div class="value">{blocked}</div><div class="hint">به‌تنهایی به معنی خطای نرم‌افزار نیست</div></div>
<div class="metric"><div class="label">Trailing موفق ثبت‌شده</div><div class="value">{stats['trail_updates']}</div><div class="hint">رویدادهای موفق</div></div>
<div class="metric"><div class="label">Trailing ناموفق ثبت‌شده</div><div class="value">{stats['trail_failures']}</div><div class="hint">رویدادهای ناموفق</div></div>
<div class="metric"><div class="label">رویدادهای Deal یکتا</div><div class="value">{stats['deal_lifecycle_events']}</div><div class="hint">بر اساس رویدادهای قابل‌خواندن</div></div>
<div class="metric"><div class="label">خالص گزارش‌شده</div><div class="value">{stats['net']:+.2f}</div><div class="hint">واحد حساب از این منبع تأیید نشده</div></div>
</div>
</section>

<section class="two">
<div class="panel">
<h2>آخرین فعالیت</h2>
<div class="note">{_esc(attempt_text)}</div>
<p>آخرین رویداد: <b>{_esc(event_names.get(latest_kind, latest_kind))}</b></p>
<p class="sub">{_esc(latest_time)}</p>
<p class="sub">آخرین رویداد ثبت‌شده: <code>{_esc(latest_kind)}</code></p>
</div>
<div class="panel">
<h2>اطلاعات حساب و معاملات باز</h2>
<p class="warning-text">برای محافظت از اتصال MT5 Runner، این داشبورد عمداً به MT5 وصل نمی‌شود.</p>
<p>موجودی حساب، Equity، سود شناور، سفارش‌های باز و پوزیشن‌های واقعی: <b>از این داشبورد قابل مشاهده نیست.</b></p>
<p class="sub">{_esc(state_ids_text)} — این شناسه‌ها موجودی زنده بروکر نیستند.</p>
<span class="tag">MT5 NOT QUERIED</span> <span class="tag">بدون API معاملاتی</span>
</div>
</section>

<section class="panel">
<h2>هشدارها و خطاهای نشست فعلی</h2>
<p class="sub">{_esc(diagnostic_banner)}</p>
<table><tr><th>Tehran time / زمان تهران</th><th>سطح</th><th>کد</th><th>شرح قابل‌فهم / جزئیات</th></tr>{diagnostic_rows}</table>
{history_html}
</section>

<section class="panel">
<h2>آخرین رویدادهای نشست فعلی</h2>
<table><tr><th>Tehran time / زمان تهران</th><th>شرح</th><th>کد فنی</th><th>جزئیات</th></tr>{event_rows}</table>
</section>

<section class="panel">
<h2>منبع داده و محدودیت‌ها</h2>
<p>مسیر داده Runner: <code>{_esc(str(RUNNER_ROOT))}</code></p>
<p>منبع مسیر: <code>{_esc(RUNNER_ROOT_SOURCE)}</code> · فایل JSONL سالم: {_esc(event_health.get('malformed_lines', 0))} خط خراب</p>
<p>این داشبورد فقط State و Event فایل‌ها را می‌خواند؛ هیچ اتصال MT5، خواندن مستقیم پوزیشن بروکر، ارسال سفارش، تغییر SL/TP یا نوشتن در فایل‌های Runner انجام نمی‌دهد.</p>
<p class="sub">آمار عملکرد فقط از رویدادهای ثبت‌شده در نشست فعلی و پنجره حداکثر {len(events)} رویداد قابل‌خواندن محاسبه می‌شود؛ این صفحه جایگزین گزارش رسمی تاریخچه حساب یا گزارش آماری اعتبارسنجی نیست.</p>
</section>
<footer>SP2L Research Monitor · Localhost only · Read-only filesystem observer · Dashboard auto-update {REFRESH_SECONDS}s · no page reload</footer>
</main>
{_REFRESH_SCRIPT}
</body></html>"""




@app.get("/")
def index() -> Response:
    return Response(_render(), mimetype="text/html")


@app.get("/api/status")
def api_status():
    events, event_health = _read_events_with_health()
    runner = _runner_status()
    start_indexes = [i for i, item in enumerate(events) if item.get("event") == "START"]
    if start_indexes:
        start_index = start_indexes[-1]
        previous_events = events[:start_index]
        session_events = events[start_index:]
        session_start = events[start_index].get("ts_utc")
    else:
        previous_events = []
        session_events = events
        session_start = None

    session_diagnostics = _build_diagnostics(session_events, runner, event_health)
    historical_diagnostics = _build_diagnostics(
        previous_events, {"alive": True, "pid": None, "detail": "historical only"},
        {"malformed_lines": 0, "read_error": None},
    )
    historical_diagnostics = [
        item for item in historical_diagnostics
        if item.get("code") not in {
            "RUNNER_ROOT_NOT_EXPLICIT", "RUNNER_ROOT_UNAVAILABLE",
            "STATE_FILE_UNAVAILABLE", "STATE_FILE_STALE",
            "RUNNER_PROCESS_NOT_FOUND", "RUNNER_PROCESS_UNVERIFIED",
        }
    ]
    try:
        state_age = time.time() - STATE_FILE.stat().st_mtime
    except OSError:
        state_age = None
    return jsonify({
        "version": VERSION,
        "dashboard_version": "CONTROL_CENTER_20261116",
        "runner": runner,
        "state": _read_json(STATE_FILE),
        "state_age_seconds": state_age,
        "stats": _summary(session_events),
        "all_readable_window_stats": _summary(events),
        "mt5": {"queried": False, "reason": "MT5 isolated; filesystem-only monitor"},
        "event_count_read": len(events),
        "current_session_event_count": len(session_events),
        "historical_event_count": len(previous_events),
        "session_start_utc": session_start,
        "event_read_health": event_health,
        "diagnostics": session_diagnostics,
        "historical_diagnostics": historical_diagnostics,
        "diagnostic_counts": {
            level: sum(1 for item in session_diagnostics if item["level"] == level)
            for level in ("ERROR", "WARNING", "INFO")
        },
        "historical_diagnostic_counts": {
            level: sum(1 for item in historical_diagnostics if item["level"] == level)
            for level in ("ERROR", "WARNING", "INFO")
        },
        "data_root": str(RUNNER_ROOT),
        "data_root_source": RUNNER_ROOT_SOURCE,
        "data_root_valid": RUNNER_ROOT.is_dir(),
        "events_path": str(EVENTS),
        "state_path": str(STATE_FILE),
        "events_health": _file_health(EVENTS),
        "state_health": _file_health(STATE_FILE),
    })

def main() -> None:
    print(f"SP2L V3.1 read-only monitor: http://127.0.0.1:{PORT}", flush=True)
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    main()
