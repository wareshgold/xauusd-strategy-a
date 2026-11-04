"""SP2L V3.1 local monitoring dashboard V3.

Filesystem-only observer. Imports the existing read-only monitor module for
Runner paths, event/state readers and Windows process identification.
Never imports MetaTrader5, initializes/shuts down a terminal, or calls trade APIs.
Binds to 127.0.0.1 only. Intended for a separate local port (default 8793).

Required environment:
  SP2L_RUNNER_ROOT=<absolute V3.1 Runner worktree>
  SP2L_DASHBOARD_PORT=8793
Run:
  python scripts/sp2l_v31_local_monitoring_dashboard_v3.py
"""
from __future__ import annotations

import hashlib
import html
import json
import time
from datetime import datetime, timezone
from collections import Counter

from flask import Flask, Response, jsonify, request

import sp2l_v31_rr4_act40_monitor as source

APP = Flask(__name__)
VERSION = "SP2L V3.1 LOCAL MONITORING DASHBOARD V4"
PORT = int(__import__("os").environ.get("SP2L_DASHBOARD_PORT", "8793"))
REFRESH_SECONDS = 5
TEHRAN = source.TEHRAN_TZ
EVENT_LIMIT = 5000


def _esc(value) -> str:
    return html.escape(str(value if value is not None else "—"), quote=True)


def _stamp(event: dict):
    raw = event.get("ts_utc")
    try:
        dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
    except (TypeError, ValueError):
        return None


def _tehran_time(event: dict) -> str:
    stamp = _stamp(event)
    return stamp.astimezone(TEHRAN).strftime("%Y-%m-%d %H:%M:%S") if stamp else "time unavailable"


def _event_id(event: dict) -> str:
    for key in ("deal", "position", "order", "tracked_order", "signal_id"):
        value = event.get(key)
        if value is not None:
            return str(value)
    return "—"


def _deal_rows(events: list[dict]) -> list[dict]:
    """Unique Runner-reported deal lifecycle rows; not independently broker-reconciled."""
    unique = {}
    for event in events:
        if event.get("event") != "TELEGRAM_DEAL_LIFECYCLE":
            continue
        deal = event.get("deal")
        key = str(deal) if deal is not None else (
            f'{event.get("position")}:{event.get("ts_utc")}:{event.get("net")}'
        )
        unique.setdefault(key, event)
    return list(unique.values())


def _metrics(events: list[dict]) -> dict:
    now_day = datetime.now(TEHRAN).date()
    today = [
        e for e in events
        if (stamp := _stamp(e)) is not None
        and stamp.astimezone(TEHRAN).date() == now_day
    ]
    deals_all = _deal_rows(events)
    deals_today = _deal_rows(today)

    def deal_stats(rows):
        nets = []
        for event in rows:
            try:
                nets.append(float(event.get("net", 0) or 0))
            except (TypeError, ValueError):
                continue
        return {
            "closed_deals": len(rows),
            "wins": sum(v > 0 for v in nets),
            "losses": sum(v < 0 for v in nets),
            "breakeven": sum(v == 0 for v in nets),
            "net": round(sum(nets), 2),
        }

    def counts(rows):
        kinds = Counter(e.get("event", "UNKNOWN") for e in rows)
        sends_ok = sum(
            e.get("event") == "ORDER_RESULT"
            and isinstance(e.get("result"), dict)
            and e["result"].get("ok") is True for e in rows
        )
        trail_ok = sum(e.get("event") == "TRAIL_UPDATE" and e.get("success") is True for e in rows)
        trail_failed = sum(e.get("event") == "TRAIL_UPDATE" and e.get("success") is False for e in rows)
        return {
            "signals": kinds["TELEGRAM_SIGNAL"],
            "order_attempts": kinds["ORDER_ATTEMPT"],
            "order_results": kinds["ORDER_RESULT"],
            "accepted_send_responses": sends_ok,
            "trail_success": trail_ok,
            "trail_failed_attempts": trail_failed,
            "trail_deferred": kinds["TRAIL_DEFERRED"],
            "history_query_errors": kinds["MT5_DEAL_HISTORY_QUERY_FAILED"],
            "execution_blocked": kinds["EXECUTION_BLOCKED"],
            "pending_lifecycle_events": kinds["PENDING_ORDER_LIFECYCLE"],
        }

    return {
        "today": {**deal_stats(deals_today), **counts(today)},
        "all_time_read_window": {**deal_stats(deals_all), **counts(events)},
        "timezone": "Asia/Tehran (UTC+03:30 fixed offset)",
        "deal_metric_source": "TELEGRAM_DEAL_LIFECYCLE events; Runner-reported net",
    }


def _diagnostics(events: list[dict], health: dict, runner: dict, state_age):
    items = []

    def add(level, code, message, event=None, detail=""):
        event = event or {}
        items.append({
            "level": level, "code": code, "message": message,
            "time": _tehran_time(event) if event else "—",
            "event": event.get("event", "MONITOR_HEALTH"),
            "id": _event_id(event),
            "detail": detail,
        })

    if health.get("read_error"):
        add("ERROR", "EVENT_FILE_READ", "Event log could not be read", detail=health["read_error"])
    malformed = int(health.get("malformed_lines", 0) or 0)
    if malformed:
        add("ERROR", "EVENT_JSON_INVALID", f"{malformed} malformed JSON line(s)",
            detail=f'Last malformed line: {health.get("last_malformed_line")} · {health.get("last_parse_error", "")}')
    if not source._RUNNER_ROOT_ENV:
        add("WARNING", "RUNNER_ROOT_NOT_EXPLICIT",
            "SP2L_RUNNER_ROOT is unset; dashboard may read the wrong worktree",
            detail=str(source.RUNNER_ROOT))
    elif not source.RUNNER_ROOT.is_dir():
        add("ERROR", "RUNNER_ROOT_UNAVAILABLE", "Configured Runner root is unavailable",
            detail=str(source.RUNNER_ROOT))
    if state_age is None:
        add("ERROR", "STATE_FILE_UNAVAILABLE", "Runner state file missing or unreadable")
    elif state_age > 90:
        add("WARNING", "STATE_FILE_STALE", "State file has not changed for more than 90 seconds",
            detail=f"age_seconds={state_age:.0f}")
    if runner.get("alive") is False:
        add("ERROR", "RUNNER_PROCESS_NOT_FOUND", "No process matched the exact Runner script path",
            detail=runner.get("detail", ""))
    elif runner.get("alive") is None:
        add("WARNING", "RUNNER_PROCESS_UNVERIFIED", "Runner process status could not be verified",
            detail=runner.get("detail", ""))

    successful_trails = {
        (str(e.get("position")), str(e.get("completed_bar_time")))
        for e in events if e.get("event") == "TRAIL_UPDATE"
        and e.get("success") is True and e.get("position") is not None
        and e.get("completed_bar_time") is not None
    }
    delivered_signals = {
        str(e.get("signal_id")) for e in events
        if e.get("event") == "TELEGRAM_SIGNAL" and e.get("signal_id") is not None
        and (e.get("success") is True or
             (isinstance(e.get("telegram"), dict) and e["telegram"].get("success") is True))
    }

    for event in events:
        kind = event.get("event")
        result = event.get("result") if isinstance(event.get("result"), dict) else {}
        telegram = event.get("telegram") if isinstance(event.get("telegram"), dict) else {}
        detail = " · ".join(
            f"{k}={event[k]}" for k in (
                "reason", "retcode", "comment", "last_error", "attempt_number",
                "retry_scheduled", "completed_bar_time"
            ) if event.get(k) is not None
        )
        if kind == "ORDER_RESULT" and result.get("ok") is False:
            # A false result may be a pre-send guard outcome. Never infer broker-send failure.
            add("INFO", "ORDER_RESULT_NOT_ACCEPTED",
                "Order result was not successful; correlate with ORDER_ATTEMPT and EXECUTION_BLOCKED",
                event, "result.ok=false · not classified as broker submission failure")
        elif kind == "EXECUTION_BLOCKED":
            add("INFO", "EXECUTION_BLOCKED", "Execution guard blocked this candidate (not a broker failure)",
                event, str(event.get("reason", "")))
        elif kind == "TRAIL_UPDATE" and event.get("success") is False:
            key = (str(event.get("position")), str(event.get("completed_bar_time")))
            if event.get("completed_bar_time") is not None and key in successful_trails:
                add("INFO", "TRAIL_UPDATE_RECOVERED", "A later update succeeded for the same position/bar", event, detail)
            elif event.get("retry_scheduled") is True:
                add("WARNING", "TRAIL_UPDATE_RETRY_PENDING", "Trailing update failed; retry is scheduled", event, detail)
            else:
                add("ERROR", "TRAIL_UPDATE_UNRESOLVED", "Trailing update failed without a recorded retry/recovery", event, detail)
        elif kind == "TRAIL_DEFERRED":
            key = (str(event.get("position")), str(event.get("completed_bar_time")))
            if event.get("completed_bar_time") is not None and key in successful_trails:
                add("INFO", "TRAIL_DEFERRED_RECOVERED", "Deferred update was later applied for the same position/bar", event, detail)
            else:
                add("WARNING", "TRAIL_DEFERRED", "Trailing update was deferred; inspect subsequent attempts", event, detail)
        elif kind == "MT5_DEAL_HISTORY_QUERY_FAILED":
            add("WARNING", "DEAL_HISTORY_QUERY", "Runner could not query deal history; this is a telemetry/data-quality issue", event, detail)
        elif kind == "TELEGRAM_SIGNAL_RETRY":
            sid = event.get("signal_id")
            if sid is not None and str(sid) in delivered_signals:
                add("INFO", "TELEGRAM_RETRY_RECOVERED", "Later event confirms signal delivery", event, detail)
            else:
                add("WARNING", "TELEGRAM_SIGNAL_RETRY", "Signal notification retry has no confirmed delivery in this event window", event, detail)
        elif kind == "TELEGRAM_SIGNAL" and (event.get("success") is False or telegram.get("success") is False):
            sid = event.get("signal_id")
            if sid is not None and str(sid) in delivered_signals:
                add("INFO", "TELEGRAM_SIGNAL_RECOVERED", "Later event confirms signal delivery", event, detail)
            else:
                add("WARNING", "TELEGRAM_SIGNAL_DELIVERY", "Signal notification delivery failed or is unconfirmed", event, detail)
        elif kind == "START_TELEGRAM" and event.get("success") is False:
            add("WARNING", "TELEGRAM_START", "Startup notification failed", event, detail)
        elif kind == "TELEGRAM_DEAL_LIFECYCLE" and telegram.get("success") is False:
            add("WARNING", "TELEGRAM_DEAL_NOTIFY", "Deal notification failed; deal lifecycle event remains recorded", event, detail)
        elif isinstance(kind, str) and (kind.endswith("_ERROR") or kind.endswith("_FAILED")):
            add("WARNING", kind, f"Runner emitted {kind}", event, detail)

    return list(reversed(items[-150:]))


def _snapshot():
    events, health = source._read_events_with_health(EVENT_LIMIT)
    state = source._read_json(source.STATE_FILE)
    runner = source._runner_status()
    try:
        state_age = max(0.0, time.time() - source.STATE_FILE.stat().st_mtime)
    except OSError:
        state_age = None
    try:
        state_mtime = datetime.fromtimestamp(source.STATE_FILE.stat().st_mtime, timezone.utc).isoformat()
    except OSError:
        state_mtime = None
    try:
        event_stat = source.EVENTS.stat()
        event_age = max(0.0, time.time() - event_stat.st_mtime)
        event_meta = {"exists": True, "bytes": event_stat.st_size, "age_seconds": event_age,
                      "mtime_utc": datetime.fromtimestamp(event_stat.st_mtime, timezone.utc).isoformat()}
    except OSError:
        event_meta = {"exists": False, "bytes": None, "age_seconds": None, "mtime_utc": None}
    metrics = _metrics(events)
    diagnostics = _diagnostics(events, health, runner, state_age)
    latest = next((e for e in reversed(events) if e.get("event")), None)
    return {
        "runner": runner, "events": events, "health": health, "state": state,
        "state_age_seconds": state_age, "state_mtime_utc": state_mtime,
        "event_meta": event_meta, "metrics": metrics, "diagnostics": diagnostics,
        "latest": latest,
    }


def _table_rows(events):
    rows = []
    for e in reversed(events[-300:]):
        kind = e.get("event", "UNKNOWN")
        result = e.get("result") if isinstance(e.get("result"), dict) else {}
        summary = e.get("detail") or e.get("outcome") or e.get("reason") or ""
        if kind == "ORDER_RESULT":
            summary = f"result.ok={result.get('ok')} · retcode={result.get('retcode', '—')} · order={result.get('order', '—')}"
        elif kind == "TRAIL_UPDATE":
            summary = (f"position={e.get('position')} · SL {e.get('old_sl')} → {e.get('new_sl')} · "
                       f"success={e.get('success')} · retry={e.get('retry_scheduled', '—')}")
        elif kind == "TELEGRAM_DEAL_LIFECYCLE":
            summary = f"deal={e.get('deal')} · position={e.get('position')} · net={e.get('net', '—')}"
        elif kind == "PENDING_ORDER_LIFECYCLE":
            summary = f"order={e.get('order', '—')} · state={e.get('state', '—')} · reason={e.get('reason', '—')}"
        rows.append({
            "time": _tehran_time(e), "event": kind, "id": _event_id(e),
            "symbol": e.get("symbol", source.SYMBOL), "summary": str(summary),
            "raw": e,
        })
    return rows



def _order_lifecycle(events: list[dict], state: dict) -> list[dict]:
    """Group Runner-recorded order events; never represents live broker inventory."""
    grouped: dict[str, list[dict]] = {}
    state_orders = state.get("orders", []) if isinstance(state, dict) else []
    if isinstance(state_orders, dict):
        state_orders = list(state_orders.values())
    if not isinstance(state_orders, list):
        state_orders = []

    def order_id(event: dict):
        result = event.get("result") if isinstance(event.get("result"), dict) else {}
        for value in (
            event.get("order"), event.get("tracked_order"), event.get("ticket"),
            result.get("order"),
        ):
            if value not in (None, "", 0, "0"):
                return str(value)
        return None

    for event in events:
        key = order_id(event)
        if key:
            grouped.setdefault(key, []).append(event)
    for item in state_orders:
        if not isinstance(item, dict):
            continue
        key = next((str(item[k]) for k in ("ticket", "order", "order_id", "tracked_order")
                    if item.get(k) not in (None, "", 0, "0")), None)
        if key:
            grouped.setdefault(key, [])

    rows = []
    for key, rows_for_order in grouped.items():
        ordered = sorted(rows_for_order, key=lambda e: _stamp(e) or datetime.min.replace(tzinfo=timezone.utc))
        last = ordered[-1] if ordered else {}
        lifecycle = next(
            (e for e in reversed(ordered) if e.get("event") == "PENDING_ORDER_LIFECYCLE"),
            None,
        )
        result = last.get("result") if isinstance(last.get("result"), dict) else {}
        rows.append({
            "order_id": key,
            "lifecycle_status": (
                lifecycle.get("state") or lifecycle.get("status") or lifecycle.get("reason")
                if lifecycle else last.get("state") or last.get("status") or "RECORDED_ONLY"
            ),
            "event_count": len(ordered),
            "last_event": last.get("event", "STATE_ONLY"),
            "last_time": _tehran_time(last) if last else "—",
            "last_retcode": result.get("retcode", last.get("retcode")),
            "event_types": [e.get("event", "UNKNOWN") for e in ordered[-12:]],
            "source": "runner_state_and_event_log",
            "broker_reconciled": False,
        })
    rows.sort(key=lambda row: row["last_time"], reverse=True)
    return rows[:500]


def _trailing_diagnostics(events: list[dict]) -> list[dict]:
    """Group trailing attempts by position/completed bar and preserve raw outcomes."""
    grouped: dict[tuple[str, str], list[dict]] = {}
    for event in events:
        if event.get("event") not in ("TRAIL_UPDATE", "TRAIL_DEFERRED"):
            continue
        position = str(event.get("position") or "UNKNOWN")
        bar = str(event.get("completed_bar_time") or "UNKNOWN_BAR")
        grouped.setdefault((position, bar), []).append(event)

    rows = []
    for (position, bar), attempts in grouped.items():
        attempts.sort(key=lambda e: _stamp(e) or datetime.min.replace(tzinfo=timezone.utc))
        updates = [e for e in attempts if e.get("event") == "TRAIL_UPDATE"]
        last = attempts[-1]
        last_update = updates[-1] if updates else {}
        if last.get("event") == "TRAIL_DEFERRED":
            status = "DEFERRED"
        elif last_update.get("success") is True and (
            last is last_update or (
                _stamp(last_update) is not None and _stamp(last) is not None
                and _stamp(last_update) >= _stamp(last)
            )
        ):
            status = "SUCCEEDED"
        elif last_update.get("success") is False and last_update.get("retry_scheduled") is True:
            status = "RETRY_PENDING"
        elif last_update.get("success") is False:
            status = "FAILED_UNRESOLVED"
        else:
            status = "UNRESOLVED"
        rows.append({
            "position": position,
            "completed_bar_time": bar,
            "status": status,
            "attempts": len(attempts),
            "last_time": _tehran_time(last),
            "old_sl": last.get("old_sl"),
            "new_sl": last.get("new_sl"),
            "retcode": last.get("retcode"),
            "comment": last.get("comment"),
            "last_error": last.get("last_error"),
            "retry_scheduled": last.get("retry_scheduled"),
            "history": [{
                "event": e.get("event"),
                "time": _tehran_time(e),
                "success": e.get("success"),
                "old_sl": e.get("old_sl"),
                "new_sl": e.get("new_sl"),
                "retcode": e.get("retcode"),
                "comment": e.get("comment"),
                "reason": e.get("reason"),
                "retry_scheduled": e.get("retry_scheduled"),
            } for e in attempts],
        })
    rows.sort(key=lambda row: row["last_time"], reverse=True)
    return rows[:500]


def _history_failures(events: list[dict]) -> list[dict]:
    """Expose history-query failures without interpreting them as empty history."""
    rows = []
    for event in events:
        if event.get("event") != "MT5_DEAL_HISTORY_QUERY_FAILED":
            continue
        result = event.get("result") if isinstance(event.get("result"), dict) else {}
        rows.append({
            "time": _tehran_time(event),
            "ticket": event.get("ticket") or event.get("order") or event.get("tracked_order"),
            "position": event.get("position"),
            "query": event.get("query") or event.get("operation") or event.get("function"),
            "error": event.get("error") or event.get("last_error") or event.get("detail"),
            "last_error": event.get("last_error"),
            "attempt": event.get("attempt_number"),
            "raw_event": event,
        })
    return list(reversed(rows[-500:]))


def _file_fingerprint(path) -> dict:
    """On-demand SHA-256; intentionally not called during the five-second refresh."""
    try:
        before = path.stat()
        digest = hashlib.sha256()
        size = 0
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
                size += len(chunk)
        after = path.stat()
        stable = before.st_size == after.st_size and before.st_mtime_ns == after.st_mtime_ns
        return {
            "exists": True, "bytes": size, "sha256": digest.hexdigest(),
            "mtime_utc": datetime.fromtimestamp(after.st_mtime, timezone.utc).isoformat(),
            "stable_during_hash": stable,
        }
    except OSError as exc:
        return {"exists": False, "bytes": None, "sha256": None, "error": f"{type(exc).__name__}: {exc}"}



def _render():
    d = _snapshot()
    runner = d["runner"]
    alive = runner.get("alive")
    runner_text = "ACTIVE" if alive is True else "NOT FOUND" if alive is False else "UNVERIFIED"
    runner_class = "good" if alive is True else "bad" if alive is False else "warn"
    age = d["state_age_seconds"]
    state_fresh = f"{age:.0f}s ago" if age is not None else "unavailable"
    counts = Counter(x["level"] for x in d["diagnostics"])
    m = d["metrics"]["today"]
    allm = d["metrics"]["all_time_read_window"]
    tracked_orders = len(d["state"].get("orders", [])) if isinstance(d["state"].get("orders", []), list) else "—"
    tracked_positions = len(d["state"].get("positions", [])) if isinstance(d["state"].get("positions", []), list) else "—"
    alerts = []
    for item in reversed(d["diagnostics"]):
        if item["level"] not in ("ERROR", "WARNING"):
            continue
        alerts.append(
            f'<article class="alert {item["level"].lower()}"><b>{_esc(item["level"])} · {_esc(item["code"])}</b>'
            f'<span>{_esc(item["time"])}</span><p>{_esc(item["message"])}</p>'
            f'<small>{_esc(item["id"])} · {_esc(item["detail"])}</small></article>'
        )
        if len(alerts) >= 10:
            break
    if not alerts:
        alerts = ['<article class="alert clear"><b>No unresolved error/warning in the readable evidence window</b>'
                  '<small>Does not mean broker state has been independently verified.</small></article>']
    latest = d["latest"]
    latest_text = f'{_tehran_time(latest)} · {latest.get("event")}' if latest else "No event recorded"
    event_rows = _table_rows(d["events"])
    event_json = json.dumps(event_rows, ensure_ascii=False, default=str).replace("</", "<\\/")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="{REFRESH_SECONDS}">
<title>{VERSION}</title>
<style>
:root{{--bg:#0a1220;--panel:#121e30;--panel2:#0e1929;--line:#293b53;--text:#e8eff8;--muted:#9aabc0;--green:#68e0b7;--red:#ff8b9b;--amber:#f3c66d;--blue:#8dbdff}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:14px Segoe UI,Arial,sans-serif}}
main{{max-width:1500px;margin:auto;padding:22px}}header{{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}}
h1{{font-size:24px;margin:0}}h2{{font-size:16px;margin:0 0 13px}}p{{color:var(--muted);margin:6px 0}}
.status{{padding:8px 13px;border:1px solid var(--line);border-radius:24px;font-weight:800}}.good{{color:var(--green)}}.bad{{color:var(--red)}}.warn{{color:var(--amber)}}
.panel{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:17px;margin-top:14px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:10px}}
.metric{{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:13px;min-width:0}}
.metric span{{display:block;color:var(--muted);font-size:11px}}.metric b{{display:block;font-size:23px;margin-top:5px;overflow-wrap:anywhere}}
.alert{{background:var(--panel2);border:1px solid var(--line);border-left:4px solid var(--amber);padding:11px;border-radius:8px;margin:8px 0}}
.alert.error{{border-left-color:var(--red)}}.alert.clear{{border-left-color:var(--green)}}.alert span{{float:right;color:var(--muted);font-size:11px}}small{{display:block;color:var(--muted);overflow-wrap:anywhere;margin-top:5px}}
table{{width:100%;border-collapse:collapse;font-size:12px}}th,td{{padding:9px 7px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{color:var(--blue)}}td{{overflow-wrap:anywhere}}
.tools{{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 12px}}input,select{{background:#0b1626;color:var(--text);border:1px solid var(--line);border-radius:7px;padding:9px;min-width:160px}}
.tablewrap{{overflow:auto;max-height:620px}}.muted{{color:var(--muted)}}.foot{{font-size:11px;color:var(--muted);line-height:1.6}}
@media(max-width:650px){{main{{padding:11px}}.panel{{padding:12px}}}}
</style></head><body><main>
<header><div><h1>SP2L V3.1 · XAUUSD Forward Monitor</h1>
<p>{VERSION} · local · filesystem-only · refresh {REFRESH_SECONDS}s · Tehran time UTC+03:30</p></div>
<div class="status {runner_class}">RUNNER {runner_text}</div></header>

<section class="panel"><h2>System health</h2><div class="grid">
<div class="metric"><span>Runner process match</span><b class="{runner_class}">{runner_text}</b></div>
<div class="metric"><span>Process IDs (not process count)</span><b>{_esc(runner.get("pids", []))}</b></div>
<div class="metric"><span>Errors</span><b class="{'bad' if counts['ERROR'] else 'good'}">{counts['ERROR']}</b></div>
<div class="metric"><span>Warnings</span><b class="{'warn' if counts['WARNING'] else 'good'}">{counts['WARNING']}</b></div>
<div class="metric"><span>State freshness</span><b>{_esc(state_fresh)}</b></div>
<div class="metric"><span>Event file freshness</span><b>{_esc(f'{d["event_meta"]["age_seconds"]:.0f}s ago' if d["event_meta"]["age_seconds"] is not None else 'unavailable')}</b></div>
</div><p>Last recorded event: {_esc(latest_text)} · state file mtime UTC: {_esc(d["state_mtime_utc"])}</p>
<p>Runner process detection uses the exact configured script path. A launcher/child pair is not treated as two independent Runners.</p></section>

<section class="panel"><h2>Account & performance · Runner-recorded evidence</h2><div class="grid">
<div class="metric"><span>Today's closed deal events</span><b>{m['closed_deals']}</b></div>
<div class="metric"><span>Today's wins / losses / BE</span><b>{m['wins']} / {m['losses']} / {m['breakeven']}</b></div>
<div class="metric"><span>Today's reported net</span><b class="{'good' if m['net'] >= 0 else 'bad'}">{m['net']:+.2f}</b></div>
<div class="metric"><span>All-time window net</span><b>{allm['net']:+.2f}</b></div>
<div class="metric"><span>Signals today</span><b>{m['signals']}</b></div>
<div class="metric"><span>Accepted send responses</span><b>{m['accepted_send_responses']}</b></div>
</div><p>Deal counts are deduplicated by deal ID from TELEGRAM_DEAL_LIFECYCLE. Net is Runner-reported; no independent MT5 reconciliation. Today is the Tehran calendar day.</p></section>

<section class="panel"><h2>Orders & positions · recorded lifecycle, not live broker inventory</h2><div class="grid">
<div class="metric"><span>Pending lifecycle events</span><b>{m['pending_lifecycle_events']}</b></div>
<div class="metric"><span>Order attempts</span><b>{m['order_attempts']}</b></div>
<div class="metric"><span>Order result records</span><b>{m['order_results']}</b></div>
<div class="metric"><span>Runner-tracked order IDs</span><b>{_esc(tracked_orders)}</b></div>
<div class="metric"><span>Runner-tracked position IDs</span><b>{_esc(tracked_positions)}</b></div>
<div class="metric"><span>Execution guards</span><b>{m['execution_blocked']}</b></div>
</div><p>Lifecycle event totals and remembered IDs are not current active pending-order or open-position counts. MT5 is intentionally not queried.</p></section>

<section class="panel"><h2>Trade management · trailing</h2><div class="grid">
<div class="metric"><span>Successful SL updates</span><b class="good">{m['trail_success']}</b></div>
<div class="metric"><span>Failed update attempts</span><b>{m['trail_failed_attempts']}</b></div>
<div class="metric"><span>Deferred updates</span><b>{m['trail_deferred']}</b></div>
<div class="metric"><span>History query errors</span><b>{m['history_query_errors']}</b></div>
</div><p>Deferred/retry/recovered/terminal-failure states are distinguished in diagnostics. History-query errors indicate telemetry/data-quality gaps, not failed trades.</p></section>

<section class="panel"><h2>Alerts & action center · {counts['ERROR'] + counts['WARNING']} item(s)</h2>{''.join(alerts)}</section>

<section class="panel"><h2>Event timeline · latest {len(event_rows)} of {len(d['events'])} readable events</h2>
<div class="tools"><input id="q" type="search" placeholder="Search event, ticket, reason, symbol…">
<select id="kind"><option value="">All event types</option></select>
<select id="limit"><option>50</option><option selected>100</option><option>200</option><option>300</option></select></div>
<div class="tablewrap"><table><thead><tr><th>Tehran time</th><th>Event</th><th>ID</th><th>Symbol</th><th>Summary</th></tr></thead><tbody id="events"></tbody></table></div>
</section>


<section class="panel"><h2>Operational inspectors</h2>
<p>These inspectors use Runner state/event evidence only. They do not query MT5 or infer live broker status.</p>
<div class="tools">
<button id="load-orders" type="button">Load order lifecycle</button>
<button id="load-trailing" type="button">Load trailing diagnostics</button>
<button id="load-history" type="button">Load History failures</button>
<button id="load-evidence" type="button">Compute file SHA-256</button>
</div>
<div id="orders-result" class="tablewrap"><p class="muted">Order lifecycle explorer has not been loaded.</p></div>
<div id="trailing-result" class="tablewrap"><p class="muted">Trailing diagnostics have not been loaded.</p></div>
<div id="history-result" class="tablewrap"><p class="muted">History failure inspector has not been loaded.</p></div>
<div id="evidence-result"><p class="muted">File fingerprints are computed only when requested.</p></div>
</section>

<section class="panel"><h2>Evidence & data quality</h2><div class="grid">
<div class="metric"><span>Parsed events</span><b>{len(d['events'])}</b></div>
<div class="metric"><span>Total lines in event file</span><b>{d['health'].get('total_lines', 0)}</b></div>
<div class="metric"><span>Malformed lines</span><b class="{'bad' if d['health'].get('malformed_lines') else 'good'}">{d['health'].get('malformed_lines', 0)}</b></div>
<div class="metric"><span>Event file size</span><b>{_esc(d['event_meta']['bytes'])}</b></div>
<div class="metric"><span>State file</span><b>{'readable' if d['state_mtime_utc'] else 'unavailable'}</b></div>
<div class="metric"><span>MT5 access</span><b class="good">NOT USED</b></div>
</div><p>Runner root: {_esc(source.RUNNER_ROOT)} · source: {_esc(source.RUNNER_ROOT_SOURCE)}</p>
<p>Event file: {_esc(source.EVENTS)} · State file: {_esc(source.STATE_FILE)}</p>
<p>Event read error: {_esc(d['health'].get('read_error') or 'none')}</p>
<p>Event SHA-256 is not computed by the dashboard on every refresh; use a separate snapshot for immutable evidence hashing.</p></section>

<p class="foot">Read-only local dashboard. No MetaTrader5 import/initialize/shutdown, no order API, no Runner state/event/config writes. It does not send BUY/SELL decisions. Runner state IDs are not broker inventory. Dashboard binds to 127.0.0.1 only.</p>
</main>
<script id="event-data" type="application/json">{event_json}</script>
<script>
const rows=JSON.parse(document.getElementById('event-data').textContent);
const q=document.getElementById('q'), kind=document.getElementById('kind'), limit=document.getElementById('limit'), body=document.getElementById('events');
[...new Set(rows.map(r=>r.event))].sort().forEach(k=>{{const o=document.createElement('option');o.value=k;o.textContent=k;kind.appendChild(o)}});
function draw(){{const query=q.value.toLowerCase(), selected=kind.value, n=Number(limit.value);
 const filtered=rows.filter(r=>(!selected||r.event===selected)&&(!query||JSON.stringify(r).toLowerCase().includes(query))).slice(0,n);
 body.replaceChildren();
 for(const r of filtered){{const tr=document.createElement('tr');[r.time,r.event,r.id,r.symbol,r.summary].forEach(v=>{{const td=document.createElement('td');td.textContent=v??'—';tr.appendChild(td)}});body.appendChild(tr)}}
 if(!filtered.length){{const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=5;td.textContent='No matching events';tr.appendChild(td);body.appendChild(tr)}}
}}
[q,kind,limit].forEach(el=>el.addEventListener('input',draw));draw();

async function getJson(url) {
 const response=await fetch(url,{cache:'no-store'});
 if(!response.ok) throw new Error('HTTP '+response.status);
 return response.json();
}
function tableInto(target, headers, rows) {
 const root=document.getElementById(target); root.replaceChildren();
 if(!rows.length){root.textContent='No records in the current readable evidence window.';return;}
 const table=document.createElement('table'),thead=document.createElement('thead'),hr=document.createElement('tr');
 headers.forEach(h=>{const th=document.createElement('th');th.textContent=h;hr.appendChild(th)});
 thead.appendChild(hr);table.appendChild(thead);
 const tbody=document.createElement('tbody');
 rows.forEach(row=>{const tr=document.createElement('tr');row.forEach(value=>{const td=document.createElement('td');td.textContent=value===null||value===undefined?'—':String(value);tr.appendChild(td)});tbody.appendChild(tr)});
 table.appendChild(tbody);root.appendChild(table);
}
document.getElementById('load-orders').addEventListener('click',async()=>{
 const root='orders-result';try{const d=await getJson('/api/orders');tableInto(root,
 ['Order ID','Recorded status','Events','Last event','Last time','Retcode'],
 d.orders.map(x=>[x.order_id,x.lifecycle_status,x.event_count,x.last_event,x.last_time,x.last_retcode]));}
 catch(e){document.getElementById(root).textContent='Load failed: '+e.message;}
});
document.getElementById('load-trailing').addEventListener('click',async()=>{
 const root='trailing-result';try{const d=await getJson('/api/trailing');tableInto(root,
 ['Position','Completed bar','Status','Attempts','Last SL','Retcode','Comment'],
 d.trailing.map(x=>[x.position,x.completed_bar_time,x.status,x.attempts,
 (x.old_sl??'—')+' → '+(x.new_sl??'—'),x.retcode,x.comment]));}
 catch(e){document.getElementById(root).textContent='Load failed: '+e.message;}
});
document.getElementById('load-history').addEventListener('click',async()=>{
 const root='history-result';try{const d=await getJson('/api/history-failures');tableInto(root,
 ['Time','Ticket','Position','Query','Error','Last error'],
 d.failures.map(x=>[x.time,x.ticket,x.position,x.query,x.error,JSON.stringify(x.last_error)]));}
 catch(e){document.getElementById(root).textContent='Load failed: '+e.message;}
});
document.getElementById('load-evidence').addEventListener('click',async()=>{
 const root=document.getElementById('evidence-result');root.textContent='Computing SHA-256…';
 try{const d=await getJson('/api/evidence');tableInto('evidence-result',
 ['File','Exists','Bytes','SHA-256','Modified UTC'],
 Object.entries(d.files).map(([name,x])=>[name,x.exists,x.bytes,x.sha256,x.mtime_utc]));}
 catch(e){root.textContent='Fingerprint failed: '+e.message;}
});

</script></body></html>"""


@APP.get("/")
def index():
    return Response(_render(), mimetype="text/html")


@APP.get("/api/status")
def api_status():
    d = _snapshot()
    return jsonify({
        "version": VERSION, "runner": d["runner"], "metrics": d["metrics"],
        "diagnostics": d["diagnostics"], "event_health": d["health"],
        "event_meta": d["event_meta"], "state_age_seconds": d["state_age_seconds"],
        "event_count_read": len(d["events"]), "mt5_queried": False,
        "data_root": str(source.RUNNER_ROOT),
    })



@APP.get("/api/health")
def api_health():
    d = _snapshot()
    return jsonify({
        "runner": d["runner"],
        "state_age_seconds": d["state_age_seconds"],
        "state_mtime_utc": d["state_mtime_utc"],
        "event_meta": d["event_meta"],
        "event_health": d["health"],
        "diagnostic_counts": dict(Counter(item["level"] for item in d["diagnostics"])),
        "latest_event": d["latest"],
        "mt5_queried": False,
        "broker_state_verified": False,
    })


@APP.get("/api/events")
def api_events():
    d = _snapshot()
    query = request.args.get("q", "").strip().lower()
    event_type = request.args.get("event", "").strip()
    try:
        limit = max(1, min(500, int(request.args.get("limit", "100"))))
        offset = max(0, int(request.args.get("offset", "0")))
    except ValueError:
        return jsonify({"error": "limit and offset must be integers"}), 400
    rows = _table_rows(d["events"])
    if event_type:
        rows = [row for row in rows if row["event"] == event_type]
    if query:
        rows = [row for row in rows if query in json.dumps(row, ensure_ascii=False, default=str).lower()]
    total = len(rows)
    page = rows[offset:offset + limit]
    return jsonify({"total": total, "offset": offset, "limit": limit, "events": page})


@APP.get("/api/orders")
def api_orders():
    d = _snapshot()
    return jsonify({
        "orders": _order_lifecycle(d["events"], d["state"]),
        "source": "runner_state_and_event_log",
        "broker_reconciled": False,
    })


@APP.get("/api/trailing")
def api_trailing():
    d = _snapshot()
    rows = _trailing_diagnostics(d["events"])
    return jsonify({
        "trailing": rows,
        "counts": dict(Counter(row["status"] for row in rows)),
        "source": "runner_event_log",
    })


@APP.get("/api/history-failures")
def api_history_failures():
    d = _snapshot()
    rows = _history_failures(d["events"])
    return jsonify({"failures": rows, "count": len(rows), "source": "runner_event_log"})


@APP.get("/api/evidence")
def api_evidence():
    # Explicit on-demand hashing; never performed during routine dashboard refresh.
    return jsonify({
        "files": {
            "events": _file_fingerprint(source.EVENTS),
            "state": _file_fingerprint(source.STATE_FILE),
        },
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
    })



def main():
    print(f"{VERSION}: http://127.0.0.1:{PORT}", flush=True)
    APP.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    main()
