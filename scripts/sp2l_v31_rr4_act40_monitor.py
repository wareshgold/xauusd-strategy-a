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
REFRESH_SECONDS = 5
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


def _read_events_with_health(limit: int = 250) -> tuple[list[dict], dict]:
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


def _read_events(limit: int = 250) -> list[dict]:
    return _read_events_with_health(limit)[0]


def _runner_status() -> dict:
    try:
        pid = int(RUNNER_LOCK.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return {"pid": None, "alive": False, "detail": "runner lock unavailable"}
    if pid <= 0:
        return {"pid": pid, "alive": False, "detail": "invalid PID"}
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
            capture_output=True, text=True, timeout=4, check=False,
        )
        alive = "python" in result.stdout.lower()
    except Exception:
        alive = False
    return {"pid": pid, "alive": alive, "detail": "process probe via tasklist"}


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
    try:
        state_age = max(0, time.time() - STATE_FILE.stat().st_mtime)
    except OSError as exc:
        state_age = None
        add("ERROR", "STATE_FILE_UNAVAILABLE", None, "Runner state file is missing or unreadable", str(exc))
    if state_age is not None and state_age > 90:
        add("WARNING", "STATE_FILE_STALE", None, "Runner state file has not been updated for more than 90 seconds", f"age_seconds={state_age:.0f}")
    if runner.get("pid") is None:
        add("WARNING", "RUNNER_LOCK_UNAVAILABLE", None, "Runner PID cannot be confirmed", runner.get("detail", ""))
    elif not runner.get("alive"):
        add("ERROR", "RUNNER_PROCESS_NOT_FOUND", None, "Runner process was not found for the PID in its lock file", f'PID={runner.get("pid")}')

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
            add("ERROR", "TRAIL_UPDATE_FAILED", event, "Trailing stop modification failed", detail)
        elif kind == "TRAIL_DEFERRED":
            add("WARNING", "TRAIL_DEFERRED", event, "Trailing stop update was deferred; inspect the retry / next attempt", detail or str(event.get("reason", "")))
        elif kind == "START_TELEGRAM" and event.get("success") is False:
            add("ERROR", "TELEGRAM_START_FAILED", event, "Telegram startup notification failed", detail)
        elif kind == "TELEGRAM_DEAL_LIFECYCLE" and telegram.get("success") is False:
            add("ERROR", "TELEGRAM_DEAL_NOTIFY_FAILED", event, "Telegram deal notification failed", detail)
        elif kind == "TELEGRAM_SIGNAL_RETRY":
            add("WARNING", "TELEGRAM_SIGNAL_RETRY", event, "Signal notification entered retry handling; delivery is not yet confirmed", detail)
        elif kind == "HEARTBEAT":
            if event.get("mt5_connected") is False:
                add("ERROR", "MT5_DISCONNECTED", event, "Runner heartbeat reports MT5 disconnected", detail)
            if event.get("trade_allowed") is False:
                add("WARNING", "TRADING_NOT_ALLOWED", event, "Runner heartbeat reports trading is not allowed", detail)
        elif kind == "EXECUTION_BLOCKED":
            add("INFO", "EXECUTION_BLOCKED", event, "Candidate execution was blocked by a gate or guard (not automatically a software defect)", detail)
        elif isinstance(kind, str) and kind.endswith("_ERROR") and kind != "SESSION_GATE_ERROR":
            add("ERROR", kind, event, f"Runner emitted {kind}", detail)

    return list(reversed(items[-100:]))


def _render() -> str:
    state = _read_json(STATE_FILE)
    events, event_health = _read_events_with_health()
    runner = _runner_status()
    probe = _mt5_probe()
    stats = _summary(events)
    diagnostics = _build_diagnostics(events, runner, event_health)

    try:
        state_age = max(0, time.time() - STATE_FILE.stat().st_mtime)
        state_health = f"state file updated {state_age:.0f}s ago"
    except OSError:
        state_health = "state file not created yet"

    account = probe.get("account") or {}
    tick = probe.get("tick") or {}
    account_label = (
        f"{account.get('account_type')} · {account.get('server')} · "
        f"balance {account.get('balance', '—'):.2f} · equity {account.get('equity', '—'):.2f}"
        if account else "unavailable"
    )
    runner_label = (
        f"ALIVE · PID {runner['pid']}" if runner["alive"]
        else f"NOT CONFIRMED · {runner['detail']}"
    )
    source_warning = (
        " · WARNING: SP2L_RUNNER_ROOT is unset; defaulting to the monitor worktree"
        if not _RUNNER_ROOT_ENV else
        " · WARNING: monitor and runner data roots differ"
        if ROOT.resolve() != RUNNER_ROOT.resolve() else ""
    )
    mt5_label = "NOT QUERIED (runner connection isolated)"
    trade_label = "not queried"
    tick_label = "not collected"

    order_rows = "".join(
        "<tr>" + "".join(f"<td>{_esc(v)}</td>" for v in (
            o["ticket"], o["type"], f'{o["volume"]:.2f}',
            f'{o["price"]:.2f}', f'{o["sl"]:.2f}', f'{o["tp"]:.2f}'
        )) + "</tr>" for o in probe["orders"]
    ) or '<tr><td colspan="6" class="dim">Not queried — MT5 is isolated from dashboard</td></tr>'

    position_rows = "".join(
        "<tr>" + "".join(f"<td>{_esc(v)}</td>" for v in (
            p["ticket"], p["type"], f'{p["volume"]:.2f}',
            f'{p["open"]:.2f}', f'{p["current"]:.2f}',
            f'{p["sl"]:.2f}', f'{p["tp"]:.2f}', f'{p["profit"]:+.2f}', p["magic"]
        )) + "</tr>" for p in probe["positions"]
    ) or '<tr><td colspan="9" class="dim">Not queried — MT5 is isolated from dashboard</td></tr>'

    event_rows = ""
    for event in reversed(events[-40:]):
        kind = event.get("event", "?")
        detail = event.get("detail") or event.get("outcome") or ""
        if kind == "ORDER_RESULT":
            result = event.get("result") or {}
            detail = f"ok={result.get('ok')} retcode={result.get('retcode')} order={result.get('order')}"
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
                value = event.get(field)
                if value is not None:
                    detail_parts.append(f"{field}={value}")
            detail = " · ".join(detail_parts)
        elif kind == "TELEGRAM_DEAL_LIFECYCLE":
            detail = (
                f"deal={event.get('deal')} position={event.get('position')} "
                f"entry={event.get('entry')} net={event.get('net')}"
            )
        event_rows += (
            "<tr><td>" + _esc(_fmt_event_time(event.get("ts_utc"))) + " Tehran" +
            "</td><td>" + _esc(kind) + "</td><td>" +
            _esc(event.get("symbol", "")) + "</td><td>" +
            _esc(detail) + "</td></tr>"
        )
    if not event_rows:
        event_rows = '<tr><td colspan="4" class="dim">No V3.1 events recorded yet</td></tr>'

    diagnostic_rows = "".join(
        "<tr><td>" + _esc(item["time_tehran"]) + " Tehran</td><td>" +
        _esc(item["level"]) + "</td><td>" + _esc(item["code"]) +
        "</td><td>" + _esc(item["event"]) + "</td><td>" +
        _esc(item["symbol"]) + "</td><td>" +
        _esc("order=" + str(item["order"]) + " position=" + str(item["position"]) +
             " deal=" + str(item["deal"])) + "</td><td>" +
        _esc(item["message"] + (" · " + item["detail"] if item["detail"] else "")) +
        "</td></tr>"
        for item in diagnostics
    ) or '<tr><td colspan="7" class="ok">No actionable error or warning detected in the latest readable event window.</td></tr>'
    diagnostic_counts = {
        level: sum(1 for item in diagnostics if item["level"] == level)
        for level in ("ERROR", "WARNING", "INFO")
    }
    diagnostic_banner = (
        f'Errors: {diagnostic_counts["ERROR"]} · Warnings: {diagnostic_counts["WARNING"]} · '
        f'Informational: {diagnostic_counts["INFO"]} · malformed JSON: {event_health["malformed_lines"]}'
    )

    cards = [
        ("Signals", stats["signals"]),
        ("Order results", stats["order_results"]),
        ("Successful orders", stats["successful_orders"]),
        ("Trail updates", stats["trail_updates"]),
        ("Trail failures", stats["trail_failures"]),
        ("Unique deal lifecycle events", stats["deal_lifecycle_events"]),
        ("Duplicate lifecycle rows suppressed", stats["deal_lifecycle_duplicate_rows"]),
        ("Net reported USD (unique deals)", f'{stats["net"]:+.2f}'),
    ]
    card_html = "".join(
        f'<div class="card"><div class="label">{_esc(k)}</div><div class="value">{_esc(v)}</div></div>'
        for k, v in cards
    )
    error = '<p class="warn">MT5 account, tick, orders and positions are intentionally not queried to protect the active runner connection.</p>'
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="{REFRESH_SECONDS}">
<title>SP2L V3.1 RR4 ACT40 Monitor</title>
<style>
body{{margin:18px;background:#0d1117;color:#d7dee8;font:14px Consolas,monospace}}
h1{{color:#8bd5ca}} h2{{color:#7aa2f7;font-size:15px;margin-top:22px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:8px}}
.card{{background:#161b22;border:1px solid #30363d;padding:10px;border-radius:6px}}
.label{{color:#8b949e;font-size:11px}} .value{{font-size:20px;margin-top:5px}}
table{{width:100%;border-collapse:collapse;margin-top:6px;font-size:12px}}
th,td{{border:1px solid #30363d;padding:5px;text-align:left}}
th{{color:#8bd5ca;background:#161b22}} .ok{{color:#a8e6a3}}
.warn{{color:#e3b341}} .bad{{color:#ff7b72}} .dim{{color:#8b949e}}
</style></head><body>
<h1>SP2L V3.1 — XAUUSD Forward Monitor</h1>
<p class="dim">{VERSION} · RR4 / ACT40 / DIST40 · research-only · read-only · refresh {REFRESH_SECONDS}s</p>
<h2>Session</h2>
<table>
<tr><th>Runner</th><td>{_esc(runner_label)}</td></tr>
<tr><th>Data root</th><td>{_esc(str(RUNNER_ROOT))} · {_esc(RUNNER_ROOT_SOURCE)}{_esc(source_warning)}</td></tr>
<tr><th>Event file</th><td>{_esc(_file_health(EVENTS))} · {_esc(str(EVENTS))}</td></tr>
<tr><th>State file</th><td>{_esc(state_health)} · {_esc(str(STATE_FILE))}</td></tr>
<tr><th>MT5</th><td>{_esc(mt5_label)} · Trade API {_esc(trade_label)}</td></tr>
<tr><th>Account</th><td>{_esc(account_label)}</td></tr>
<tr><th>Symbol tick</th><td>{_esc(tick_label)}</td></tr>
<tr><th>State tracked IDs (not live inventory)</th><td>orders={len(state.get("orders", []))} · position IDs={len(state.get("positions", []))} · observed deal events={len(state.get("deal_events", []))} · Telegram-delivered deals={len(state.get("deals", []))}</td></tr>
</table>
{error}
<h2>Automatic diagnostics — no manual log search</h2>
<p class="warn">{_esc(diagnostic_banner)}</p>
<table><tr><th>Tehran time</th><th>Level</th><th>Code</th><th>Source event</th><th>Symbol</th><th>Identifiers</th><th>What happened / technical detail</th></tr>{diagnostic_rows}</table>
<p class="dim">Deferred operations and retry notices are warnings, not final failures. Execution-blocked events are informational unless a separate error is emitted.</p>
<h2>Event counters (last {len(events)} available events)</h2><div class="grid">{card_html}</div>
<h2>Pending orders — {SYMBOL}</h2>
<table><tr><th>Ticket</th><th>Type</th><th>Volume</th><th>Price</th><th>SL</th><th>TP</th></tr>{order_rows}</table>
<h2>Live broker positions — {SYMBOL} (not queried)</h2>
<table><tr><th>Ticket</th><th>Type</th><th>Volume</th><th>Open</th><th>Current</th><th>SL</th><th>TP</th><th>Profit</th><th>Magic</th></tr>{position_rows}</table>
<h2>Latest 40 events</h2>
<table><tr><th>Tehran time</th><th>Event</th><th>Symbol</th><th>Detail</th></tr>{event_rows}</table>
<p class="dim">Read-only monitor: filesystem reads only; no MT5 initialize/shutdown, no order API, no state/event writes.</p>
</body></html>"""


@app.get("/")
def index() -> Response:
    return Response(_render(), mimetype="text/html")


@app.get("/api/status")
def api_status():
    events, event_health = _read_events_with_health()
    runner = _runner_status()
    diagnostics = _build_diagnostics(events, runner, event_health)
    try:
        state_age = time.time() - STATE_FILE.stat().st_mtime
    except OSError:
        state_age = None
    return jsonify({
        "version": VERSION,
        "runner": _runner_status(),
        "state": _read_json(STATE_FILE),
        "state_age_seconds": state_age,
        "stats": _summary(events),
        "mt5": {"queried": False, "reason": "MT5 isolated; filesystem-only monitor"},
        "event_count_read": len(events),
        "event_read_health": event_health,
        "diagnostics": diagnostics,
        "diagnostic_counts": {
            level: sum(1 for item in diagnostics if item["level"] == level)
            for level in ("ERROR", "WARNING", "INFO")
        },
        "data_root": str(RUNNER_ROOT),
        "data_root_source": RUNNER_ROOT_SOURCE,
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
