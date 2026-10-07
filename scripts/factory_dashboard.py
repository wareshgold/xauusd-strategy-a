from __future__ import annotations

"""SP2L Research Factory - read-only Tycoon-style control room.

The visual layer is intentionally game-like, but all worker/job activity is
telemetry-backed. No activity is invented, no candidate is promoted, and the
MT5 forward runner is not modified.
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
LIVE_STATUS_FILE = ROOT / "runtime" / "factory_worker_status.json"
DEMO_STATUS_FILE = ROOT / "runtime" / "factory_demo_status.json"
DEMO_MODE = os.getenv("SP2L_FACTORY_DEMO", "0") == "1"
STATUS_FILE = DEMO_STATUS_FILE if DEMO_MODE else LIVE_STATUS_FILE
PORT = int(os.getenv("SP2L_FACTORY_DASHBOARD_PORT", "8788"))

PHASES = [
    ("SOURCE", "Source resolution", "BLOCKED"),
    ("GEOMETRY", "Frozen geometry", "BLOCKED"),
    ("DISCOVERY", "Candidate discovery", "NEXT"),
    ("STABILITY", "Stability / robustness", "NEXT"),
    ("HOLDOUT", "Untouched / fresh holdout", "PLANNED"),
    ("FORWARD", "Forward validation", "SEPARATE"),
]

STATIONS = {
    "discovery": ("DISCOVERY LAB", "🔬", "Candidate discovery"),
    "stability": ("STABILITY LAB", "🧪", "Chronological stability"),
    "robustness": ("ROBUSTNESS LAB", "⚙️", "Robustness checks"),
    "holdout": ("HOLDOUT VAULT", "🔒", "Untouched validation"),
    "forward": ("FORWARD OPS", "📡", "Separate MT5 validation"),
    "idle": ("WORKER BAY", "🧰", "Waiting for a job"),
}


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


def _health(heartbeat: str) -> tuple[str, float | None]:
    if not heartbeat:
        return "UNKNOWN", None
    try:
        dt = datetime.fromisoformat(heartbeat.replace("Z", "+00:00"))
        age = max(0.0, time.time() - dt.timestamp())
    except ValueError:
        return "UNKNOWN", None
    if age <= 90:
        return "LIVE", age
    if age <= 300:
        return "STALE", age
    return "OFFLINE", age


def worker_state() -> tuple[list[dict], str]:
    try:
        raw = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return [], "NO TELEMETRY"

    if isinstance(raw, dict) and isinstance(raw.get("workers"), list):
        workers = raw["workers"]
    elif isinstance(raw, list):
        workers = raw
    elif isinstance(raw, dict):
        workers = [raw]
    else:
        return [], "INVALID TELEMETRY"

    out = []
    for item in workers:
        if not isinstance(item, dict):
            continue
        health, age = _health(str(item.get("heartbeat_utc") or ""))
        out.append({**item, "telemetry_health": health, "heartbeat_age_s": age})

    if not out:
        return [], "NO TELEMETRY"
    if any(w["telemetry_health"] == "LIVE" for w in out):
        return out, "LIVE"
    if any(w["telemetry_health"] == "STALE" for w in out):
        return out, "STALE"
    return out, "OFFLINE"


def status_class(value: str) -> str:
    v = value.upper()
    if v in {"LIVE", "RUNNING", "COMPLETED", "VERIFIED", "SEPARATE"}:
        return "ok"
    if v in {"BLOCKED", "OFFLINE", "FAILED", "NOT ELIGIBLE"}:
        return "bad"
    return "warn"


def station_for(worker: dict) -> str:
    text = " ".join(
        str(worker.get(k) or "").lower()
        for k in ("job_type", "detail", "station", "phase")
    )
    for key in ("holdout", "forward", "robust", "stability", "discovery"):
        if key in text:
            return key
    return "idle"


def worker_card(worker: dict, index: int) -> str:
    station = station_for(worker)
    title, code, subtitle = STATIONS.get(station, STATIONS["idle"])
    try:
        progress = max(0.0, min(100.0, float(worker.get("progress") or 0)))
    except (TypeError, ValueError):
        progress = 0.0
    state = str(worker.get("state") or "UNKNOWN").upper()
    health = str(worker.get("telemetry_health") or "UNKNOWN")
    age = worker.get("heartbeat_age_s")
    beat = "—" if age is None else f"{age:.0f}s"
    return f"""
    <article class="worker-card">
      <div class="worker-head"><span class="worker-id">{escape(str(worker.get("worker_id") or f"W-{index:02d}"))}</span><span class="status-dot {status_class(health)}"></span></div>
      <div class="agent-row">
        <div class="agent-glyph"><span></span></div>
        <div class="worker-info"><b>{escape(title)}</b><span>{escape(subtitle)}</span><strong class="{status_class(state)}">{escape(state)}</strong></div>
      </div>
      <div class="meter"><i style="width:{progress:.0f}%"></i></div>
      <div class="worker-foot"><span>{progress:.0f}%</span><span>HB {beat}</span></div>
      <div class="worker-job">{escape(str(worker.get("job_id") or "NO ACTIVE JOB"))}</div>
    </article>
    """


def station_card(key: str, workers: list[dict]) -> str:
    title, code, subtitle = STATIONS[key]
    active = [w for w in workers if station_for(w) == key]
    units = ""
    for worker in active[:5]:
        state = str(worker.get("state") or "UNKNOWN").upper()
        health = str(worker.get("telemetry_health") or "UNKNOWN")
        active_class = " active" if state in {"RUNNING", "HEARTBEAT"} and health == "LIVE" else ""
        units += f'<span class="station-unit{active_class}" title="{escape(str(worker.get("job_id") or "worker"))}"></span>'
    if not units:
        units = '<span class="empty-unit">—</span>'
    return f"""
    <section class="station">
      <div class="station-sign"><span class="station-code">{code}</span><div><b>{title}</b><small>{subtitle}</small></div></div>
      <div class="station-floor">{units}</div>
      <div class="station-status">{len(active)} assigned</div>
    </section>
    """


def html_page() -> str:
    git = git_state()
    workers, factory_health = worker_state()
    mode_label = "DEMO TELEMETRY" if DEMO_MODE else "LIVE TELEMETRY"
    live = sum(w["telemetry_health"] == "LIVE" for w in workers)
    running = sum(str(w.get("state") or "").upper() in {"RUNNING", "HEARTBEAT"} for w in workers)
    failed = sum(str(w.get("state") or "").upper() == "FAILED" for w in workers)

    if factory_health == "LIVE":
        headline = "FACTORY IS WORKING"
        headline_class = "ok"
    elif factory_health in {"STALE", "OFFLINE"}:
        headline = "FACTORY TELEMETRY NEEDS ATTENTION"
        headline_class = "bad"
    else:
        headline = "FACTORY WAITING FOR TELEMETRY"
        headline_class = "warn"

    if not workers:
        crew_html = """
        <div class="empty-crew">
          <div class="empty-mark">NO SIGNAL</div>
          <b>No worker telemetry yet</b>
          <span>The floor is real; workers appear when a Factory worker publishes heartbeat data.</span>
        </div>
        """
    else:
        crew_html = "".join(worker_card(w, i + 1) for i, w in enumerate(workers))

    phase_html = "".join(
        f'<div class="phase"><span>{escape(name)}</span><b class="{status_class(status)}">{escape(status)}</b></div>'
        for _, name, status in PHASES
    )

    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="5">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SP2L Research Factory</title>
<style>
:root{--bg:#090d12;--panel:#111820;--line:#293642;--text:#e6edf3;--muted:#82909d;--accent:#d5a84b;--green:#69c39a;--red:#d86b72;--yellow:#d6b45a;--blue:#79aeca}
*{box-sizing:border-box}
body{margin:0;background:linear-gradient(180deg,#0a0f14,#080b0f);color:var(--text);font:13px "Segoe UI",Arial,sans-serif}
main{max-width:1540px;margin:auto;padding:24px}
.top{display:flex;justify-content:space-between;gap:18px;align-items:end;flex-wrap:wrap;border-bottom:1px solid var(--line);padding-bottom:16px}
h1{margin:0;font-size:24px;letter-spacing:1.4px;font-weight:700}h1 span{color:#f0f3f5}.sub{color:var(--muted);margin-top:6px;font-size:12px;letter-spacing:.35px}
.state{padding:8px 12px;border:1px solid var(--line);background:#0d1319;border-radius:4px;font-size:11px;font-weight:700;letter-spacing:.7px}
.ok{color:var(--green)}.warn{color:var(--yellow)}.bad{color:var(--red)}
.stats{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:14px 0}.stat,.panel{background:var(--panel);border:1px solid var(--line);border-radius:5px}.stat{padding:12px 14px}.stat b{font-size:22px;display:block;letter-spacing:.6px}.stat small{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.8px}
.floor{position:relative;background:#0c1218;border:1px solid #303d49;border-radius:5px;padding:16px;overflow:hidden}.floor:before{content:"";position:absolute;inset:0;background-image:linear-gradient(#1c2730 1px,transparent 1px),linear-gradient(90deg,#1c2730 1px,transparent 1px);background-size:36px 36px;opacity:.35}
.sign{position:relative;z-index:1;display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;color:var(--muted);font-size:10px;letter-spacing:.7px;text-transform:uppercase}.sign b{color:var(--text);font-size:12px}
.stations{position:relative;z-index:1;display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.station{min-height:130px;background:rgba(16,23,30,.96);border:1px solid #33414d;border-radius:4px;padding:11px}
.station-sign{display:flex;gap:10px;align-items:center;border-bottom:1px solid var(--line);padding-bottom:9px}.station-code{font:700 10px Consolas,monospace;color:var(--accent);border:1px solid #65512b;padding:4px 5px;border-radius:3px}.station-sign b{display:block;font-size:11px;letter-spacing:.5px}.station-sign small{color:var(--muted);font-size:10px}
.station-floor{height:62px;display:flex;align-items:center;justify-content:center;gap:12px}.station-unit{width:30px;height:18px;border:1px solid #4a5864;border-radius:3px;background:#18212a;position:relative}.station-unit:before{content:"";position:absolute;left:6px;top:5px;width:9px;height:6px;background:#56636e}.station-unit:after{content:"";position:absolute;right:5px;top:5px;width:4px;height:6px;background:#2d3943}.station-unit.active{border-color:#527d68;box-shadow:0 0 10px rgba(105,195,154,.18)}.station-unit.active:after{background:var(--green)}.empty-unit{color:#3e4b56}
.station-status{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.7px}
.panel{padding:14px;margin-top:12px}.panel h2{font-size:11px;letter-spacing:1px;margin:0 0 11px;color:#c5cdd4}.crew{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:9px}
.worker-card{background:#0d141b;border:1px solid #2b3843;border-radius:4px;padding:11px}.worker-head,.worker-foot{display:flex;justify-content:space-between;gap:8px;align-items:center}.worker-id{font:700 11px Consolas,monospace;color:#dce4ea}
.status-dot{width:7px;height:7px;border-radius:50%;background:#53606a}.status-dot.ok{background:var(--green);box-shadow:0 0 7px rgba(105,195,154,.45)}.status-dot.warn{background:var(--yellow)}.status-dot.bad{background:var(--red)}
.agent-row{display:flex;align-items:center;gap:12px;padding:12px 0 8px}.agent-glyph{width:42px;height:42px;position:relative;border:1px solid #3a4752;border-radius:4px;background:#141d25}.agent-glyph:before{content:"";position:absolute;left:13px;top:8px;width:14px;height:14px;border:2px solid #75838e;border-radius:50%}.agent-glyph:after{content:"";position:absolute;left:8px;bottom:6px;width:24px;height:11px;border:2px solid #75838e;border-bottom:0;border-radius:12px 12px 0 0}.agent-glyph span{position:absolute;right:5px;top:5px;width:4px;height:4px;border-radius:50%;background:var(--green)}
.worker-info{display:grid;gap:3px}.worker-info b{font-size:11px}.worker-info span{color:var(--muted);font-size:10px}.worker-info strong{font-size:9px;letter-spacing:.8px}.meter{height:4px;background:#25303a;border-radius:2px;overflow:hidden}.meter i{display:block;height:100%;background:var(--green);border-radius:2px}.worker-foot{color:var(--muted);font:10px Consolas,monospace;margin-top:6px}.worker-job{font:10px Consolas,monospace;color:var(--blue);margin-top:7px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.pipeline{display:grid;grid-template-columns:repeat(6,1fr);gap:6px}.phase{background:#0d141b;border:1px solid var(--line);border-radius:3px;padding:9px;min-height:50px;display:flex;flex-direction:column;justify-content:space-between;gap:5px}.phase b{font-size:9px;letter-spacing:.7px}.phase span{font-size:10px;color:#c1cbd2}
.meta{color:var(--muted);font-size:10px;margin-top:12px;display:flex;gap:14px;flex-wrap:wrap}.lock{color:var(--accent)!important}.empty-crew{border:1px dashed #33414d;border-radius:4px;padding:25px;text-align:center;display:grid;gap:7px;color:var(--muted)}.empty-mark{font:700 11px Consolas,monospace;color:#56636d}
@media(max-width:900px){.stats{grid-template-columns:repeat(2,1fr)}.stations{grid-template-columns:1fr 1fr}.pipeline{grid-template-columns:1fr 1fr}}@media(max-width:560px){main{padding:12px}.stations{grid-template-columns:1fr}.stats{grid-template-columns:1fr 1fr}}
</style></head>
<body><main>
  <div class="top">
    <div><h1><span>SP2L RESEARCH FACTORY</span></h1><div class="sub">Research orchestration control room • telemetry-backed • research only</div></div>
    <div class="state {headline_class}">{mode_label} · {headline}</div>
  </div>

  <section class="stats">
    <div class="stat"><b>{len(workers)}</b><small>Workers</small></div>
    <div class="stat"><b>{live}</b><small>Live heartbeat</small></div>
    <div class="stat"><b>{running}</b><small>Jobs running</small></div>
    <div class="stat"><b>{failed}</b><small>Failed workers</small></div>
    <div class="stat"><b>LOCKED</b><small>Production authority</small></div>
  </section>

  <section class="floor">
    <div class="sign"><div><b>FACTORY FLOOR</b><span> • workers move only when telemetry says they are active</span></div><span>AUTO REFRESH · 5s</span></div>
    <div class="stations">
      {station_card("discovery", workers)}
      {station_card("stability", workers)}
      {station_card("robustness", workers)}
      {station_card("holdout", workers)}
      {station_card("forward", workers)}
      {station_card("idle", workers)}
    </div>
  </section>

  <section class="panel">
    <h2>WORKERS & CURRENT JOBS</h2>
    <div class="crew">{crew_html}</div>
  </section>

  <section class="panel">
    <h2>RESEARCH PIPELINE</h2>
    <div class="pipeline">{phase_html}</div>
    <div class="meta">
      <span>ROOT {escape(git["root"])}</span>
      <span>BRANCH {escape(git["branch"])}</span>
      <span>HEAD {escape(git["head"])}</span>
      <span>origin {escape(git["origin"])}</span>
      <span class="lock">PRODUCTION LOCKED · NO BUY/SELL GENERATION</span>
    </div>
  </section>
</main></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = html_page().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
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
