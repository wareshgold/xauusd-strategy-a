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
    title, icon, subtitle = STATIONS.get(station, STATIONS["idle"])
    progress = worker.get("progress")
    try:
        progress = max(0.0, min(100.0, float(progress)))
        progress_text = f"{progress:.0f}%"
    except (TypeError, ValueError):
        progress = 0.0
        progress_text = "—"

    state = str(worker.get("state") or "UNKNOWN").upper()
    health = str(worker.get("telemetry_health") or "UNKNOWN")
    heartbeat = worker.get("heartbeat_age_s")
    beat = "—" if heartbeat is None else f"{heartbeat:.0f}s"

    motion = "walking" if state in {"RUNNING", "HEARTBEAT"} and health == "LIVE" else "idle"
    return f"""
    <article class="worker-card {motion}" data-worker="{escape(str(worker.get("worker_id") or index))}">
      <div class="worker-head">
        <span class="worker-id">👷 {escape(str(worker.get("worker_id") or f"W-{index:02d}"))}</span>
        <span class="badge {status_class(health)}">{escape(health)}</span>
      </div>
      <div class="worker-avatar" aria-hidden="true">🧑‍🔬</div>
      <div class="worker-info">
        <b>{escape(title)}</b>
        <span>{escape(subtitle)}</span>
        <span class="{status_class(state)}">{escape(state)}</span>
      </div>
      <div class="meter"><i style="width:{progress:.0f}%"></i></div>
      <div class="worker-foot"><span>{progress_text}</span><span>♥ {beat}</span></div>
      <div class="worker-job">{escape(str(worker.get("job_id") or "No job"))}</div>
    </article>
    """


def station_card(key: str, workers: list[dict]) -> str:
    title, icon, subtitle = STATIONS[key]
    active = [w for w in workers if station_for(w) == key]
    bodies = ""
    if active:
        for i, worker in enumerate(active[:4]):
            state = str(worker.get("state") or "UNKNOWN").upper()
            health = str(worker.get("telemetry_health") or "UNKNOWN")
            moving = state in {"RUNNING", "HEARTBEAT"} and health == "LIVE"
            bodies += (
                f'<span class="mini-worker {"move" if moving else ""}" '
                f'title="{escape(str(worker.get("job_id") or "worker"))}">👷</span>'
            )
    else:
        bodies = '<span class="empty-worker">·</span>'

    return f"""
    <section class="station">
      <div class="station-sign"><span>{icon}</span><div><b>{title}</b><small>{subtitle}</small></div></div>
      <div class="station-floor">{bodies}</div>
      <div class="station-status">{len(active)} worker{"s" if len(active) != 1 else ""}</div>
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
:root{{--bg:#0b1020;--panel:#151d31;--panel2:#1c2740;--line:#33415f;--text:#eef3ff;--muted:#91a0bd;--gold:#f4c95d;--green:#6ee7b7;--red:#fb7185;--yellow:#fbbf24;--blue:#7dd3fc}}
*{{box-sizing:border-box}}
body{{margin:0;background:radial-gradient(circle at 50% -10%,#263655 0,#0b1020 42%);color:var(--text);font:14px Segoe UI,Arial,sans-serif}}
main{{max-width:1500px;margin:auto;padding:22px}}
.top{{display:flex;justify-content:space-between;gap:16px;align-items:end;flex-wrap:wrap}}
h1{{margin:0;font-size:28px;letter-spacing:.5px}} h1 span{{color:var(--gold)}}
.sub{{color:var(--muted);margin-top:5px}}
.state{{padding:9px 13px;border:1px solid var(--line);border-radius:12px;background:#11192b;font-weight:800}}
.ok{{color:var(--green)}} .warn{{color:var(--yellow)}} .bad{{color:var(--red)}}
.stats{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:18px 0}}
.stat,.panel{{background:linear-gradient(180deg,#19233a,#11192b);border:1px solid var(--line);border-radius:14px}}
.stat{{padding:13px}} .stat b{{font-size:25px;display:block}} .stat small{{color:var(--muted)}}
.floor{{position:relative;background:#10182a;border:1px solid #3a4968;border-radius:18px;padding:18px;overflow:hidden}}
.floor:before{{content:"";position:absolute;inset:0;background-image:linear-gradient(#263452 1px,transparent 1px),linear-gradient(90deg,#263452 1px,transparent 1px);background-size:44px 44px;opacity:.25}}
.sign{{position:relative;z-index:1;display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}}
.sign b{{font-size:18px}} .sign span{{color:var(--muted)}}
.stations{{position:relative;z-index:1;display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.station{{min-height:145px;background:rgba(21,29,49,.93);border:1px solid #405071;border-radius:14px;padding:12px;box-shadow:inset 0 -12px 0 rgba(255,255,255,.02)}}
.station-sign{{display:flex;gap:9px;align-items:center;border-bottom:1px solid var(--line);padding-bottom:8px}}
.station-sign>span{{font-size:25px}} .station-sign b{{display:block}} .station-sign small{{color:var(--muted)}}
.station-floor{{height:70px;display:flex;align-items:center;justify-content:center;gap:18px;font-size:32px}}
.station-status{{color:var(--muted);font-size:12px}}
.mini-worker{{display:inline-block}} .mini-worker.move{{animation:walk .9s infinite alternate ease-in-out}}
@keyframes walk{{from{{transform:translateY(3px) rotate(-5deg)}}to{{transform:translateY(-4px) rotate(5deg)}}}}
.empty-worker{{font-size:26px;color:#46536d}}
.panel{{padding:14px;margin-top:16px}}
.panel h2{{font-size:16px;margin:0 0 12px}}
.crew{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}}
.worker-card{{position:relative;background:#10182a;border:1px solid var(--line);border-radius:13px;padding:11px;overflow:hidden}}
.worker-head,.worker-foot{{display:flex;justify-content:space-between;gap:8px;align-items:center}}
.worker-id{{font-weight:800}} .badge{{font-size:10px;font-weight:800}}
.worker-avatar{{font-size:48px;line-height:1;text-align:center;margin:10px 0 2px}}
.worker-info{{display:grid;gap:2px;text-align:center}} .worker-info span{{color:var(--muted);font-size:12px}}
.meter{{height:7px;background:#28344d;border-radius:8px;overflow:hidden;margin-top:10px}} .meter i{{display:block;height:100%;background:var(--green);border-radius:8px}}
.worker-foot{{color:var(--muted);font-size:11px;margin-top:5px}} .worker-job{{font-family:Consolas,monospace;font-size:11px;color:var(--blue);margin-top:7px;text-align:center;overflow:hidden;text-overflow:ellipsis}}
.walking .worker-avatar{{animation:walk .9s infinite alternate ease-in-out}}
.pipeline{{display:grid;grid-template-columns:repeat(6,1fr);gap:8px}}
.phase{{background:#10182a;border:1px solid var(--line);border-radius:10px;padding:9px;min-height:55px;display:flex;flex-direction:column;justify-content:space-between;gap:6px}}
.phase b{{font-size:10px}} .phase span{{font-size:12px}}
.meta{{color:var(--muted);font-size:11px;margin-top:14px;display:flex;gap:14px;flex-wrap:wrap}}
.empty-crew{{border:1px dashed #46536d;border-radius:12px;padding:25px;text-align:center;display:grid;gap:5px;color:var(--muted)}}
.big-worker{{font-size:50px}}
@media(max-width:900px){{.stats{{grid-template-columns:repeat(2,1fr)}}.stations{{grid-template-columns:1fr 1fr}}.pipeline{{grid-template-columns:1fr 1fr}}}}
@media(max-width:560px){{main{{padding:12px}}.stations{{grid-template-columns:1fr}}.stats{{grid-template-columns:1fr 1fr}}}}
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
