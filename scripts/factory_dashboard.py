from __future__ import annotations

"""Read-only SP2L Research Factory floor dashboard.

Separate from scripts/live_dashboard.py. It observes Factory research state;
it does not launch jobs, select candidates, modify the forward runner, or
place orders.

Live worker telemetry is optional and must be written by the worker to:
    runtime/factory_worker_status.json

Missing/stale telemetry is shown explicitly; activity is never fabricated.
"""

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_FILE = ROOT / "runtime" / "factory_worker_status.json"
PORT = int(os.getenv("SP2L_FACTORY_DASHBOARD_PORT", "8788"))

PHASES = [
    ("P1", "Orchestration boundary", "VERIFIED"),
    ("P2", "Synthetic execution", "VERIFIED"),
    ("P3", "Historical data adapter", "VERIFIED"),
    ("P4", "Deterministic execution kernel", "VERIFIED"),
    ("P5", "Source resolution / frozen geometry", "BLOCKED"),
    ("P6", "Test Factory", "PLANNED"),
    ("P7", "Stability / robustness", "NEXT"),
    ("P8", "Untouched validation", "PLANNED"),
    ("P9", "Fresh holdout", "PLANNED"),
    ("P10", "Forward validation / reconciliation", "SEPARATE"),
    ("P11", "Production eligibility", "NOT ELIGIBLE"),
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
            "detail": "No Factory worker telemetry has been published yet.",
        }

    heartbeat = str(raw.get("heartbeat_utc") or "")
    age = None
    if heartbeat:
        try:
            dt = datetime.fromisoformat(heartbeat.replace("Z", "+00:00"))
            age = max(0.0, time.time() - dt.timestamp())
        except ValueError:
            pass

    if age is None:
        health = "UNKNOWN"
    elif age <= 90:
        health = "LIVE"
    elif age <= 300:
        health = "STALE"
    else:
        health = "OFFLINE"

    return {**raw, "telemetry_health": health, "heartbeat_age_s": age}


def status_class(value: str) -> str:
    v = value.upper()
    if v in {"VERIFIED", "LIVE", "RUNNING", "COMPLETED", "SEPARATE"}:
        return "ok"
    if v in {"BLOCKED", "OFFLINE", "FAILED", "NOT ELIGIBLE"}:
        return "bad"
    return "warn"


def roadmap_summary() -> dict[str, int]:
    counts = {"VERIFIED": 0, "ACTIVE": 0, "PLANNED": 0, "OTHER": 0}
    for _, _, status in PHASES:
        if status == "VERIFIED":
            counts["VERIFIED"] += 1
        elif status in {"NEXT", "BLOCKED"}:
            counts["ACTIVE"] += 1
        elif status == "PLANNED":
            counts["PLANNED"] += 1
        else:
            counts["OTHER"] += 1
    return counts


def phase_rows() -> str:
    return "".join(
        f"<tr><td>{pid}</td><td>{escape(name)}</td>"
        f"<td class='{status_class(status)}'>{escape(status)}</td></tr>"
        for pid, name, status in PHASES
    )


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
    s = roadmap_summary()

    if w.get("telemetry_health") == "LIVE":
        overall = "FACTORY WORKER ACTIVE"
    elif w.get("telemetry_health") in {"STALE", "OFFLINE"}:
        overall = "FACTORY WORKER NOT HEALTHY"
    else:
        overall = "FACTORY OBSERVING"

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
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
code{{color:#93c5fd}}
.card{{background:#172033;border:1px solid #2b3850;padding:16px;border-radius:8px}}
.num{{font-size:28px;font-weight:700}}
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

<h2>How much is built?</h2>
<div class="grid">
<div class="card"><div class="num">{s["VERIFIED"]}/11</div><div>roadmap phases verified</div></div>
<div class="card"><div class="num">{s["ACTIVE"]}</div><div>source/stability work active or next</div></div>
<div class="card"><div class="num">{s["PLANNED"]}</div><div>later validation phases planned</div></div>
<div class="card"><div class="num">{s["OTHER"]}</div><div>separate / governance phases</div></div>
</div>
<p class="dim">
This is phase coverage, not a profitability score or statistical confidence.
It intentionally does not convert research performance into a production
decision.
</p>

<h2>Factory roadmap</h2>
<table>
<tr><th>Phase</th><th>Work</th><th>Status</th></tr>
{phase_rows()}
</table>

<h2>Current research path</h2>
<p>
<b>SOURCE RESOLUTION → FROZEN GEOMETRY → RESEARCH → STABILITY →
FRESH HOLDOUT → FORWARD</b>
</p>
<p>
P5 is still source-blocked. P7 is the next engineering target: independent
sub-window stability for RR1–RR5 and trailing candidates. The active MT5
forward runner remains outside this dashboard and is not modified by it.
</p>

<p class="dim">Dashboard UTC: {datetime.now(timezone.utc).isoformat()}</p>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = html_page().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args) -> None:
        return


def main() -> None:
    print(f"SP2L Factory Dashboard: http://127.0.0.1:{PORT}/")
    print(f"Repository: {ROOT}")
    print(f"Worker telemetry: {STATUS_FILE}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
