"""Operational V2 dashboard for the read-only SP2L V3.1 forward monitor.

Run from this worktree:
    python scripts/sp2l_v31_rr4_act40_dashboard_v2.py

Default URL: http://127.0.0.1:8792
This module reuses the filesystem-only monitor readers. It never connects to MT5
or changes Runner state, orders, positions, or event logs.
"""
from __future__ import annotations

import html
import time
from datetime import datetime, timezone

from flask import Flask, Response, jsonify

import sp2l_v31_rr4_act40_monitor as source

app = Flask(__name__)
VERSION = "SP2L V3.1 OPERATIONAL DASHBOARD V2"
PORT = 8792
REFRESH_SECONDS = 5


def _e(value) -> str:
    return html.escape(str(value if value is not None else "—"))


def _parsed_time(event: dict):
    raw = event.get("ts_utc")
    try:
        value = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
    except (TypeError, ValueError):
        return None


def _today(events: list[dict]) -> list[dict]:
    today = datetime.now(source.TEHRAN_TZ).date()
    return [
        event for event in events
        if (stamp := _parsed_time(event)) is not None
        and stamp.astimezone(source.TEHRAN_TZ).date() == today
    ]


def _deal_rows(events: list[dict]) -> list[dict]:
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
    day = _today(events)
    deals = _deal_rows(day)
    nets = []
    for event in deals:
        try:
            nets.append(float(event.get("net", 0) or 0))
        except (TypeError, ValueError):
            continue
    return {
        "signals": sum(e.get("event") == "TELEGRAM_SIGNAL" for e in day),
        "orders_ok": sum(
            e.get("event") == "ORDER_RESULT"
            and isinstance(e.get("result"), dict)
            and e["result"].get("ok") is True for e in day
        ),
        "closed_deals": len(deals),
        "wins": sum(value > 0 for value in nets),
        "losses": sum(value < 0 for value in nets),
        "net": sum(nets),
        "trail_ok": sum(
            e.get("event") == "TRAIL_UPDATE" and e.get("success") is True for e in day
        ),
        "trail_failed": sum(
            e.get("event") == "TRAIL_UPDATE" and e.get("success") is False for e in day
        ),
    }


def _event_time(event: dict) -> str:
    stamp = _parsed_time(event)
    return stamp.astimezone(source.TEHRAN_TZ).strftime("%H:%M:%S") + " Tehran" if stamp else "time unavailable"


def _event_summary(event: dict) -> str:
    kind = event.get("event", "UNKNOWN")
    if kind == "ORDER_RESULT":
        result = event.get("result") if isinstance(event.get("result"), dict) else {}
        return f'Order send {"succeeded" if result.get("ok") else "failed"} · ticket {result.get("order", "—")} · retcode {result.get("retcode", "—")}'
    if kind == "PENDING_ORDER_LIFECYCLE":
        return f'Pending order {event.get("order", "—")} · state {event.get("state", "unknown")} · reason {event.get("reason") or "not supplied"}'
    if kind == "TELEGRAM_DEAL_LIFECYCLE":
        return f'Deal {event.get("deal", "—")} · position {event.get("position", "—")} · net {event.get("net", "—")}'
    if kind == "TRAIL_UPDATE":
        return f'Position {event.get("position", "—")} · SL {event.get("old_sl", "—")} → {event.get("new_sl", "—")} · {"updated" if event.get("success") is True else "not updated"}'
    if kind == "TELEGRAM_SIGNAL":
        return f'Signal {event.get("signal_id", "—")} · delivery {event.get("success", "not recorded")}'
    return str(event.get("detail") or event.get("reason") or event.get("outcome") or kind)


def _snapshot() -> dict:
    events, health = source._read_events_with_health()
    runner = source._runner_status()
    diagnostics = source._build_diagnostics(events, runner, health)
    state = source._read_json(source.STATE_FILE)
    metrics = _metrics(events)
    latest = next((e for e in reversed(events) if e.get("event")), None)
    state_age = None
    try:
        state_age = max(0, time.time() - source.STATE_FILE.stat().st_mtime)
    except OSError:
        pass
    counts = {
        level: sum(item.get("level") == level for item in diagnostics)
        for level in ("ERROR", "WARNING", "INFO")
    }
    return {
        "runner": runner, "events": events, "health": health,
        "diagnostics": diagnostics, "state": state, "metrics": metrics,
        "latest": latest, "state_age_seconds": state_age,
        "diagnostic_counts": counts,
    }


def _status_label(runner: dict) -> tuple[str, str]:
    if runner.get("alive") is True:
        return "RUNNER ACTIVE", "good"
    if runner.get("alive") is False:
        return "RUNNER NOT FOUND", "bad"
    return "RUNNER STATUS UNVERIFIED", "warn"


def _render() -> str:
    data = _snapshot()
    runner, metrics = data["runner"], data["metrics"]
    label, status_class = _status_label(runner)
    latest = data["latest"]
    last_activity = _event_time(latest) if latest else "No event recorded"
    age = data["state_age_seconds"]
    freshness = f"State updated {age:.0f}s ago" if age is not None else "State file unavailable"
    counts = data["diagnostic_counts"]
    attention = counts["ERROR"] + counts["WARNING"]

    alert_items = []
    for item in reversed(data["diagnostics"]):
        if item.get("level") not in ("ERROR", "WARNING"):
            continue
        ident = " · ".join(
            f'{key} {item[key]}' for key in ("order", "position", "deal") if item.get(key)
        )
        alert_items.append(
            '<article class="alert ' + ("critical" if item["level"] == "ERROR" else "caution") + '">'
            f'<div class="alerttop"><b>{_e(item["level"])} · {_e(item["code"])}</b><span>{_e(item["time_tehran"])}</span></div>'
            f'<div>{_e(item["message"])}</div><small>{_e(ident)} {_e(item.get("detail") or "")}</small></article>'
        )
        if len(alert_items) == 6:
            break
    if not alert_items:
        alert_items = ['<article class="alert clear"><b>No unresolved error/warning detected in the readable event window</b><small>This is not a live broker-state check.</small></article>']

    recent = []
    important = {
        "ORDER_RESULT", "PENDING_ORDER_LIFECYCLE", "TELEGRAM_DEAL_LIFECYCLE",
        "TRAIL_UPDATE", "TRAIL_DEFERRED", "TELEGRAM_SIGNAL",
        "MT5_DEAL_HISTORY_QUERY_FAILED", "PENDING_ORDER_TTL_SKIPPED",
    }
    for event in reversed(data["events"]):
        if event.get("event") not in important:
            continue
        recent.append(
            f'<tr><td>{_e(_event_time(event))}</td><td>{_e(event.get("event"))}</td>'
            f'<td>{_e(event.get("order") or event.get("position") or event.get("deal") or "—")}</td>'
            f'<td>{_e(event.get("symbol") or source.SYMBOL)}</td><td>{_e(_event_summary(event))}</td></tr>'
        )
        if len(recent) == 10:
            break
    if not recent:
        recent = ['<tr><td colspan="5" class="muted">No operational events recorded yet.</td></tr>']

    last_line = (
        f'{_event_time(latest)} · {_e(latest.get("event"))} · {_e(_event_summary(latest))}'
        if latest else "No events yet"
    )
    state_counts = (
        f'IDs remembered by Runner: {len(data["state"].get("orders", []))} orders · '
        f'{len(data["state"].get("positions", []))} positions'
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="{REFRESH_SECONDS}"><title>{VERSION}</title>
<style>
:root{{--bg:#0b1220;--panel:#121d2e;--line:#26364c;--text:#e8eef7;--muted:#9aabc0;--green:#6ee7b7;--red:#fca5a5;--amber:#fcd34d;--blue:#93c5fd}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px system-ui,Segoe UI,sans-serif}}
main{{max-width:1440px;margin:auto;padding:22px}}h1{{font-size:25px;margin:0}}h2{{font-size:17px;margin:0 0 13px}}p{{margin:6px 0;color:var(--muted)}}
.top{{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:18px}}
.pill{{padding:8px 12px;border:1px solid var(--line);border-radius:30px;font-weight:700}}.good{{color:var(--green)}}.bad{{color:var(--red)}}.warn{{color:var(--amber)}}
.panel{{background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:17px;margin:14px 0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:10px}}
.metric{{background:#0e1828;border:1px solid var(--line);border-radius:10px;padding:14px}}.metric span{{display:block;color:var(--muted);font-size:12px}}.metric strong{{display:block;font-size:25px;margin-top:5px}}
.alert{{border:1px solid var(--line);border-left:4px solid var(--amber);border-radius:9px;padding:12px;margin:8px 0;background:#0e1828}}
.alert.critical{{border-left-color:var(--red)}}.alert.clear{{border-left-color:var(--green)}}.alerttop{{display:flex;justify-content:space-between;gap:10px;margin-bottom:5px}}small{{display:block;color:var(--muted);margin-top:5px;overflow-wrap:anywhere}}
table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{padding:10px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{color:var(--blue);font-weight:600}}td{{overflow-wrap:anywhere}}
.muted{{color:var(--muted)}}details{{margin-top:12px}}summary{{cursor:pointer;color:var(--blue)}}.foot{{font-size:12px;color:var(--muted);margin-top:16px}}
@media(max-width:700px){{main{{padding:12px}}td,th{{padding:8px 5px}}}}
</style></head><body><main>
<div class="top"><div><h1>SP2L V3.1 · XAUUSD</h1><p>{VERSION} · read-only · refresh {REFRESH_SECONDS}s · research/demo</p></div>
<div class="pill {status_class}">{label}</div></div>
<section class="panel"><h2>Right now</h2><div class="grid">
<div class="metric"><span>Runner</span><strong class="{status_class}">{_e("ACTIVE" if runner.get("alive") is True else "NOT FOUND" if runner.get("alive") is False else "UNKNOWN")}</strong></div>
<div class="metric"><span>Errors</span><strong class="{'bad' if counts['ERROR'] else 'good'}">{counts['ERROR']}</strong></div>
<div class="metric"><span>Warnings</span><strong class="{'warn' if counts['WARNING'] else 'good'}">{counts['WARNING']}</strong></div>
<div class="metric"><span>Last activity</span><strong style="font-size:16px">{_e(last_activity)}</strong></div>
<div class="metric"><span>Data freshness</span><strong style="font-size:16px">{_e(freshness)}</strong></div>
</div><p>{_e(last_line)}</p></section>
<section class="panel"><h2>{'Action needed' if attention else 'System attention' } · {attention} item(s)</h2>{''.join(alert_items)}</section>
<section class="panel"><h2>Today's recorded trading results · Tehran day</h2><div class="grid">
<div class="metric"><span>Closed deals recorded</span><strong>{metrics['closed_deals']}</strong></div>
<div class="metric"><span>Wins / losses by net</span><strong>{metrics['wins']} / {metrics['losses']}</strong></div>
<div class="metric"><span>Recorded net</span><strong class="{'good' if metrics['net'] >= 0 else 'bad'}">{metrics['net']:+.2f}</strong></div>
<div class="metric"><span>Signals logged</span><strong>{metrics['signals']}</strong></div>
<div class="metric"><span>Successful order sends</span><strong>{metrics['orders_ok']}</strong></div>
<div class="metric"><span>Trailing updates OK / failed</span><strong>{metrics['trail_ok']} / {metrics['trail_failed']}</strong></div>
</div><p>Results count unique TELEGRAM_DEAL_LIFECYCLE deal IDs from today's event log. Net is the Runner-reported value, not independently reconciled broker P&amp;L.</p></section>
<section class="panel"><h2>Latest important activity</h2><table><thead><tr><th>Time</th><th>Event</th><th>ID</th><th>Symbol</th><th>What happened</th></tr></thead><tbody>{''.join(recent)}</tbody></table></section>
<section class="panel"><h2>Technical details</h2>
<p>Runner process: {_e(runner.get("detail"))}</p><p>{_e(state_counts)} (not live broker inventory)</p>
<p>MT5 is deliberately not queried. Pending-order and position tables are not represented as live status.</p>
<details><summary>Show diagnostic/file/session details</summary>
<p>Data root: {_e(source.RUNNER_ROOT)} · {_e(source.RUNNER_ROOT_SOURCE)}</p>
<p>Event file: {_e(source._file_health(source.EVENTS))}</p><p>State file: {_e(source._file_health(source.STATE_FILE))}</p>
<p>Event rows read: {len(data['events'])} · malformed JSON rows: {data['health'].get('malformed_lines', 0)}</p>
<p>Runner PIDs: {_e(runner.get('pids', []))} · State age seconds: {_e(data['state_age_seconds'])}</p>
<p>Diagnostic totals: errors {counts['ERROR']} · warnings {counts['WARNING']} · info {counts['INFO']}</p>
</details></section>
<div class="foot">Filesystem-only dashboard. No MT5 initialize/shutdown, no trading API calls, no Runner state/event writes. Dashboard V2 uses port {PORT}; existing monitor remains on its own port.</div>
</main></body></html>"""


@app.get("/")
def index() -> Response:
    return Response(_render(), mimetype="text/html")


@app.get("/api/status")
def api_status():
    data = _snapshot()
    return jsonify({
        "version": VERSION,
        "runner": data["runner"],
        "metrics_today": data["metrics"],
        "diagnostic_counts": data["diagnostic_counts"],
        "last_event": data["latest"],
        "state_age_seconds": data["state_age_seconds"],
        "event_count_read": len(data["events"]),
        "event_read_health": data["health"],
        "mt5_queried": False,
    })


def main() -> None:
    print(f"{VERSION}: http://127.0.0.1:{PORT}", flush=True)
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    main()
