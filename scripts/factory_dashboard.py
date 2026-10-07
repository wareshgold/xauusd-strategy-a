from __future__ import annotations

"""Read-only SP2L Research Factory floor dashboard.

This dashboard is deliberately separate from scripts/live_dashboard.py.
It observes Factory research state; it does not launch jobs, select a
candidate, modify the forward runner, or place orders.

Live worker telemetry is optional and must be written by the worker to:
    runtime/factory_worker_status.json

No telemetry is fabricated: missing/stale telemetry is shown explicitly.
"""

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from html import escape

ROOT = Path(__file__).resolve().parents[1]
STATUS_FILE = ROOT / "runtime" / "factory_worker_status.json"
PORT = int(os.getenv("SP2L_FACTORY_DASHBOARD_PORT", "8788"))

PHASES = [
    ("P1", "Orchestration boundary", "VERIFIED", 100),
    ("P2", "Synthetic execution", "VERIFIED", 100),
    ("P3", "Historical data adapter", "VERIFIED", 100),
    ("P4", "Deterministic execution kernel", "VERIFIED", 100),
    ("P5", "Source resolution / frozen geometry", "BLOCKED", 45),
    ("P6", "Test Factory", "IN PROGRESS", 25),
    ("P7", "Stability / robustness", "NEXT", 10),
    ("P8", "Untouched validation", "PLANNED", 0),
    ("P9", "Fresh holdout", "PLANNED", 0),
    ("P10", "Forward validation / reconciliation", "SEPARATE", 60),
    ("P11", "Production eligibility", "NOT ELIGIBLE", 0),
]


def _run(*args: str) -> str:
    try:
        return subprocess.run(
            args, cwd=ROOT, capture_output=True, text=True, timeout=3
        ).stdout.strip()
    except Exception:
        return ""


def git_state() -> dict[str, str]:
    return {
        "branch": _run("git", "branch", "--show-current") or "unknown",
        "head": _run("git", "rev-parse", "--short", "HEAD") or "unknown",
        "origin": _run("git", "rev-parse", "--short", "@{u}") or "unknown",
        "root": str(ROOT),
    }


def worker_state() -> dict:
    try:
        raw = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {
            "state": "NO TELEMETRY",
            "worker_id": None,
            "job_id": None,
            "job_type": None,
            "started_utc": None,
            "heartbeat_utc": None,
            "progress": None,
            "detail": "Factory worker has not published runtime telemetry.",
        }

    heartbeat = str(raw.get("heartbeat_utc") or "")
    age = None
    if heartbeat:
        try:
            dt = datetime.fromisoformat(heartbeat.replace("Z", "+00:00"))
            age = max(0.0, time.time() - dt.timestamp())
        except ValueError:
            pass

    declared = str(raw.get("state") or "UNKNOWN").upper()
    if age is None:
        health = "UNKNOWN"
    elif age <= 90:
        health = "LIVE"
    elif age <= 300:
        health = "STALE"
    else:
        health = "OFFLINE"

    return {
        **raw,
        "state": declared,
        "telemetry_health": health,
        "heartbeat_age_s": age,
    }


def phase_rows() -> str:
    return "".join(
        f"<tr><td>{pid}</td><td>{escape(name)}</td>"
        f"<td class='{status_class(status)}'>{escape(status)}</td>"
        f"<td><div class='bar'><span style='width:{pct}%'></span></div>"
        f"<span class='pct'>{pct}%</span></td></tr>"
        for pid, name, status, pct in PHASES
    )


def status_class(value: str) -> str:
    v = value.upper()
    if v in {"VERIFIED", "LIVE", "RUNNING", "COMPLETED"}:
        return "ok"
    if v in {"BLOCKED", "OFFLINE", "FAILED", "NOT ELIGIBLE"}:
        return "bad"
    return "warn"


def worker_html(w: dict) -> str:
    health = str(w.get("telemetry_health") or "UNKNOWN")
    progress = w.get("progress")
    progress_text = "—" if progress is None else f"{float(progress):.1f}%"
    age = w.get("heartbeat_age_s")
    age_text = "—" if age is None else f"{age:.0f}s ago"
    return f"""
    <h2>Factory worker</h2>
    <table>
      <tr><th>Health</th><td class="{status_class(health)} big">{escape(health)}</td></tr>
      <tr><th>Worker</th><td>{escape(str(w.get("worker_id") or "—"))}</td></tr>
      <tr><th>State</th><td class="{status_class(str(w.get("state") or ""))}">{escape(str(w.get("state") or "—"))}</td></tr>
      <tr><th>Busy with</th><td>{escape(str(w.get("job_type") or "—"))}</td></tr>
      <tr><th>Job ID</th><td>{escape(str(w.get("job_id") or "—"))}</td></tr>
      <tr><th>Progress</th><td>{progress_text}</td></tr>
      <tr><th>Heartbeat</th><td>{age_text}</td></tr>
      <tr><th>Detail</th><td>{escape(str(w.get("detail") or "—"))}</td></tr>
    </table>
    """


def html_page() -> str:
    g = git_state()
    w = worker_state()
    overall = "FACTORY OBSERVING"
    if w.get("telemetry_health") == "LIVE":
        overall = "FACTORY WORKER ACTIVE"
    elif w.get("telemetry_health") in {"STALE", "OFFLINE"}:
        overall = "FACTORY WORKER NOT HEALTHY"

    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="5">
<title>SP2L Research Factory</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;background:#111827;color:#e5e7eb;margin:28px}}
h1{{margin-bottom:4px}} h2{{margin-top:24px}}
table{{border-collapse:collapse;width:100%;background:#172033}}
th,td{{border:1px solid #2b3850;padding:9px;text-align:left}}
th{{color:#9ca3af;width:220px}}
.ok{{color:#6ee7b7}} .warn{{color:#fbbf24}} .bad{{color:#f87171}}
.dim{{color:#94a3b8}} .big{{font-size:18px;font-weight:700}}
.bar{{display:inline-block;width:220px;height:10px;background:#263247;border-radius:6px;vertical-align:middle;margin-right:8px}}
.bar span{{display:block;height:100%;background:#60a5fa;border-radius:6px}}
.pct{{color:#94a3b8}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
code{{color:#93c5fd}}
@media(max-width:900px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body>
<h1>🏭 SP2L Strategy Research Factory</h1>
<p class="dim">Read-only · refresh 5s · no BUY/SELL generation · no order execution</p>

<div class="grid">
<section>
<h2>Factory state</h2>
<table>
<tr><th>Overall</th><td class="big {status_class(overall)}">{overall}</td></tr>
<tr><th>Repository</th><td><code>{escape(g["root"])}</code></td></tr>
<tr><th>Branch</th><td>{escape(g["branch"])}</td></tr>
<tr><th>HEAD</th><td><code>{escape(g["head"])}</code></td></tr>
<tr><th>Origin</th><td><code>{escape(g["origin"])}</code></td></tr>
<tr><th>Telemetry file</th><td><code>{escape(str(STATUS_FILE))}</code></td></tr>
</table>
</section>
<section>
{worker_html(w)}
</section>
</div>

<h2>Factory roadmap</h2>
<table>
<tr><th>Phase</th><th>Work</th><th>Status</th><th>Progress estimate</th></tr>
{phase_rows()}
</table>

<h2>Current gate interpretation</h2>
<p>
The percentages above are <b>implementation-roadmap estimates</b>, not
statistical confidence, strategy quality, or probability of profitability.
P5 remains source-blocked; P7 is the next research-engineering target.
A candidate is never promoted because a dashboard score is high.
</p>

<p class="dim">Dashboard time: {datetime.now(timezone.utc).isoformat()}</p>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = html_page().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        return


def main() -> None:
    print(f"SP2L Factory Dashboard: http://127.0.0.1:{PORT}/")
    print(f"Repository: {ROOT}")
    print(f"Worker telemetry: {STATUS_FILE}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
