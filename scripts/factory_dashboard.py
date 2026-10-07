from __future__ import annotations

"""SP2L Research Factory - read-only space-station research control room.

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


def lifecycle_html(worker: dict) -> str:
    """Render a telemetry-derived Queue → Lab → Evidence → Complete track."""
    state = str(worker.get("state") or "IDLE").upper()
    artifact = bool(worker.get("output_artifact"))
    if state == "QUEUED":
        active = "queue"
    elif state in {"RUNNING", "HEARTBEAT"}:
        active = "lab"
    elif state == "COMPLETED" and artifact:
        active = "complete"
    elif state == "COMPLETED":
        active = "evidence"
    elif state == "FAILED":
        active = "failed"
    else:
        active = "idle"

    labels = (("queue", "QUEUE"), ("lab", "LAB"), ("evidence", "EVIDENCE"), ("complete", "COMPLETE"))
    steps = []
    for key, label in labels:
        cls = " lifecycle-step-active" if key == active else ""
        steps.append(f'<span class="lifecycle-step{cls}"><i></i>{label}</span>')
    if active == "failed":
        steps.append('<span class="lifecycle-step lifecycle-step-failed"><i></i>FAILED</span>')
    elif active == "idle":
        steps.append('<span class="lifecycle-step lifecycle-step-idle"><i></i>IDLE</span>')
    return '<div class="lifecycle" aria-label="Telemetry-backed job lifecycle">' + '<span class="lifecycle-track"></span>' + ''.join(steps) + '</div>'


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
    room_class = "room-active" if active else "room-idle"
    return f"""
    <section class="station {room_class}">
      <div class="station-sign"><span class="station-code">{code}</span><div><b>{title}</b><small>{subtitle}</small></div><i class="room-lamp"></i></div>
      <div class="station-floor">
        <div class="machine"></div>
        <div class="conveyor"><span></span><span></span><span></span><span></span><span></span></div>
        <div class="station-units">{units}</div>
      </div>
      <div class="station-status">{len(active)} assigned <span>• TELEMETRY LINK</span></div>
    </section>
    """



def station_world(workers: list[dict]) -> str:
    """Render a StarNet-inspired industrial pixel world from real telemetry."""
    payload = json.dumps([{"id":str(w.get("worker_id") or ""),"job":str(w.get("job_id") or ""),"state":str(w.get("state") or "IDLE").upper(),"station":station_for(w),"progress":float(w.get("progress") or 0)} for w in workers], ensure_ascii=False).replace("</","<\\/")
    return f'''\n    <section class="station-world panel">\n      <div class="world-head"><div><h2>STATION WORLD · LIVE TELEMETRY</h2><span>Industrial world view • agents follow worker state</span></div><b>PIXEL DECK / 12px GRID</b></div>\n      <div class="world-viewport"><canvas id="stationWorld" width="1180" height="590"></canvas></div>\n      <div class="world-legend"><span><i class="legend-agent"></i>AGENT</span><span><i class="legend-live"></i>LIVE</span><span><i class="legend-queue"></i>QUEUED</span><span><i class="legend-fail"></i>FAILED</span><span class="world-lock">RESEARCH ONLY · PRODUCTION LOCKED</span></div>\n      <script>\n      (() => {{\n        const workers = {payload}; const canvas=document.getElementById("stationWorld"); if(!canvas)return; const ctx=canvas.getContext("2d"); ctx.imageSmoothingEnabled=false; const W=1180,H=590;\n        const rooms={{discovery:{{x:70,y:95,w:300,h:175,label:"DISCOVERY LAB",code:"D01"}},stability:{{x:440,y:95,w:300,h:175,label:"STABILITY LAB",code:"S01"}},robustness:{{x:810,y:95,w:300,h:175,label:"ROBUSTNESS LAB",code:"R01"}},holdout:{{x:250,y:340,w:300,h:175,label:"HOLDOUT VAULT",code:"H01"}},forward:{{x:620,y:340,w:300,h:175,label:"FORWARD OPS",code:"F01"}},idle:{{x:950,y:340,w:180,h:175,label:"WORKER BAY",code:"W01"}}}};\n        const C={{wall:"#27343b",wall2:"#1a242b",floor:"#10191f",floor2:"#16232a",cyan:"#5bd5e6",green:"#63d39a",red:"#df6e75",amber:"#c79b4d"}};\n        function room(r){{ctx.fillStyle=C.floor;ctx.fillRect(r.x,r.y,r.w,r.h);ctx.fillStyle=C.floor2;for(let x=r.x+8;x<r.x+r.w-8;x+=24)for(let y=r.y+45;y<r.y+r.h-8;y+=24)ctx.fillRect(x,y,1,1);ctx.fillStyle=C.wall2;ctx.fillRect(r.x,r.y,r.w,11);ctx.fillRect(r.x,r.y,11,r.h);ctx.fillStyle=C.wall;ctx.fillRect(r.x,r.y,r.w,3);ctx.fillRect(r.x,r.y,3,r.h);ctx.fillStyle="#080e13";ctx.fillRect(r.x+11,r.y+11,r.w-22,30);ctx.strokeStyle="#34454e";ctx.strokeRect(r.x+10.5,r.y+10.5,r.w-21,r.h-21);ctx.fillStyle="#c2cbd0";ctx.font="bold 11px monospace";ctx.fillText(r.label,r.x+18,r.y+28);ctx.fillStyle=C.cyan;ctx.font="9px monospace";ctx.fillText(r.code,r.x+r.w-34,r.y+28);ctx.fillStyle="#2e3d45";ctx.fillRect(r.x+52,r.y+84,38,25);ctx.fillRect(r.x+126,r.y+84,38,25);ctx.fillStyle="#52636c";ctx.fillRect(r.x+57,r.y+88,28,11);ctx.fillRect(r.x+131,r.y+88,28,11)}}\n        function corridors(){{ctx.fillStyle="#1b282f";ctx.fillRect(370,210,70,22);ctx.fillRect(740,210,70,22);ctx.fillRect(500,315,120,28);ctx.fillRect(745,340,20,28);ctx.fillStyle="#455760";ctx.fillRect(370,219,70,2);ctx.fillRect(740,219,70,2);ctx.fillRect(532,328,55,2)}}\n        function agent(w,i,t){{const r=rooms[w.station]||rooms.idle,a=w.state==="RUNNING"||w.state==="HEARTBEAT",q=w.state==="QUEUED",d=w.state==="COMPLETED",bad=w.state==="FAILED",p=t/420+i*1.7;let x=r.x+45+(i*63)%(Math.max(90,r.w-95)),y=r.y+120+Math.sin(p)*2;if(q){{x=r.x+24;y=r.y+61}}if(d){{x=r.x+r.w-50;y=r.y+61}}ctx.save();ctx.translate(Math.round(x),Math.round(y));ctx.fillStyle="rgba(0,0,0,.4)";ctx.fillRect(-9,18,19,4);ctx.fillStyle=bad?C.red:(a?C.cyan:"#9ba8ae");ctx.fillRect(-6,-11,12,10);ctx.fillStyle="#18232a";ctx.fillRect(-3,-8,2,3);ctx.fillRect(3,-8,2,3);ctx.fillStyle=a?"#657780":"#4b5a62";ctx.fillRect(-9,0,18,13);ctx.fillStyle=a?C.cyan:"#73828a";ctx.fillRect(-11,2,3,8);ctx.fillRect(9,2,3,8);ctx.fillStyle="#202c33";ctx.fillRect(-7,13,5,6);ctx.fillRect(2,13,5,6);if(a){{ctx.fillStyle=C.green;ctx.fillRect(10,-12,3,3)}}ctx.restore();ctx.fillStyle="#9ba9b0";ctx.font="8px monospace";ctx.textAlign="center";ctx.fillText(w.id,x,y+31);if(w.job){{ctx.fillStyle="#667681";ctx.font="7px monospace";ctx.fillText(w.job.slice(0,18),x,y+42)}}}}\n        function draw(t){{ctx.clearRect(0,0,W,H);ctx.fillStyle="#080e12";ctx.fillRect(0,0,W,H);ctx.strokeStyle="#132027";for(let x=0;x<W;x+=24){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke()}}for(let y=0;y<H;y+=24){{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke()}}Object.values(rooms).forEach(room);corridors();workers.forEach((w,i)=>agent(w,i,t));ctx.fillStyle="#070b0e";ctx.fillRect(18,18,300,45);ctx.strokeStyle="#33454f";ctx.strokeRect(18.5,18.5,299,44);ctx.fillStyle=C.cyan;ctx.font="bold 11px monospace";ctx.textAlign="left";ctx.fillText("SP2L RESEARCH STATION",31,37);ctx.fillStyle="#687984";ctx.font="8px monospace";ctx.fillText("WORLD STATE ← WORKER TELEMETRY",31,52);ctx.fillStyle="#070b0e";ctx.fillRect(900,540,250,30);ctx.strokeStyle="#33454f";ctx.strokeRect(900.5,540.5,249,29);ctx.fillStyle=C.amber;ctx.font="8px monospace";ctx.fillText("PRODUCTION LOCKED",915,559);requestAnimationFrame(draw)}}\n        function resize(){{const w=Math.min(canvas.parentElement.clientWidth,W);canvas.style.width=w+"px";canvas.style.height=(w/W*H)+"px"}}resize();window.addEventListener("resize",resize);requestAnimationFrame(draw);\n      }})();\n      </script>\n    </section>\n    '''\n\n
def telemetry_panels(workers: list[dict]) -> str:
    queued = [w for w in workers if str(w.get("state") or "").upper() == "QUEUED"]
    active = [w for w in workers if str(w.get("state") or "").upper() in {"RUNNING", "HEARTBEAT"}]
    artifacts = [w for w in workers if w.get("output_artifact")]
    feed = sorted(workers, key=lambda w: str(w.get("heartbeat_utc") or ""), reverse=True)

    queue_rows = "".join(
        f'<div class="queue-row"><span class="mono">{escape(str(w.get("worker_id") or "—"))}</span>'
        f'<b>{escape(str(w.get("job_id") or "NO JOB"))}</b>'
        f'<span>{escape(str(w.get("detail") or "QUEUED"))}</span></div>'
        for w in queued[:8]
    ) or '<div class="empty-row">QUEUE EMPTY — no queued worker telemetry</div>'

    active_rows = "".join(
        f'<div class="job-row"><span class="mono">{escape(str(w.get("worker_id") or "—"))}</span>'
        f'<span>{escape(str(w.get("job_id") or "NO JOB"))}</span>'
        f'<span class="job-state {status_class(str(w.get("state") or ""))}">{escape(str(w.get("state") or "UNKNOWN").upper())}</span>'
        f'<b>{float(w.get("progress") or 0):.0f}%</b></div>'
        for w in active[:8]
    ) or '<div class="empty-row">NO ACTIVE JOB TELEMETRY</div>'

    feed_rows = "".join(
        f'<div class="feed-row"><span class="feed-time">{escape(str(w.get("heartbeat_utc") or "—").replace("T"," ")[:19])}</span>'
        f'<span class="feed-id">{escape(str(w.get("worker_id") or "—"))}</span>'
        f'<span>{escape(str(w.get("state") or "UNKNOWN").upper())}</span>'
        f'<span>{escape(str(w.get("detail") or "No detail"))}</span></div>'
        for w in feed[:10]
    ) or '<div class="empty-row">NO TELEMETRY FEED</div>'

    artifact_rows = "".join(
        f'<div class="artifact-row"><span class="mono">{escape(str(w.get("worker_id") or "—"))}</span>'
        f'<span>{escape(str(w.get("job_id") or "—"))}</span>'
        f'<span class="artifact">{escape(str(w.get("output_artifact")))}</span></div>'
        for w in artifacts[:8]
    ) or '<div class="empty-row">NO OUTPUT ARTIFACT REPORTED</div>'

    return f"""
    <section class="ops-grid">
      <div class="panel ops-panel"><h2>ACTIVE JOBS</h2>{active_rows}</div>
      <div class="panel ops-panel"><h2>JOB QUEUE</h2>{queue_rows}</div>
      <div class="panel ops-panel wide"><h2>TELEMETRY FEED · LATEST HEARTBEATS</h2>{feed_rows}</div>
      <div class="panel ops-panel wide"><h2>OUTPUT ARTIFACTS</h2>{artifact_rows}</div>
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
<title>SP2L Research Station</title>
<style>
:root{{--bg:#070b10;--panel:#0d141c;--line:#27343f;--text:#e7edf2;--muted:#71808c;--accent:#d6aa4d;--green:#63d39a;--red:#df6e75;--yellow:#d8b55b;--blue:#72b8d9;--cyan:#5bd5e6;--violet:#9b82dc}}
*{{box-sizing:border-box}}
body{{margin:0;background:radial-gradient(circle at 50% 0%,#101b26 0,#080c11 42%,#05080b 100%);color:var(--text);font:13px "Segoe UI",Arial,sans-serif}}
body:after{{content:"";position:fixed;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,rgba(255,255,255,.012) 0,rgba(255,255,255,.012) 1px,transparent 1px,transparent 4px);opacity:.28}}
main{{max-width:1580px;margin:auto;padding:20px 24px;position:relative;z-index:1}}
.top{{display:flex;justify-content:space-between;gap:18px;align-items:end;flex-wrap:wrap;border-bottom:1px solid var(--line);padding-bottom:16px}}
h1{{margin:0;font-size:25px;letter-spacing:2.2px;font-weight:800;text-shadow:0 0 18px rgba(91,213,230,.08)}}h1 span{{color:#f0f3f5}}.sub{{color:var(--muted);margin-top:6px;font-size:11px;letter-spacing:.7px;text-transform:uppercase}}
.state{{padding:8px 12px;border:1px solid var(--line);background:#0d1319;border-radius:4px;font-size:11px;font-weight:700;letter-spacing:.7px}}
.ok{{color:var(--green)}}.warn{{color:var(--yellow)}}.bad{{color:var(--red)}}
.stats{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:14px 0}}.stat,.panel{{background:var(--panel);border:1px solid var(--line);border-radius:5px}}.stat{{padding:12px 14px}}.stat b{{font-size:22px;display:block;letter-spacing:.6px}}.stat small{{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.8px}}
.floor{{position:relative;background:linear-gradient(145deg,#0b131b,#081017);border:1px solid #33434f;border-radius:8px;padding:16px;overflow:hidden;box-shadow:inset 0 0 60px rgba(91,213,230,.025),0 12px 40px rgba(0,0,0,.22)}}.floor:before{{content:"";position:absolute;inset:0;background-image:linear-gradient(#1b2a34 1px,transparent 1px),linear-gradient(90deg,#1b2a34 1px,transparent 1px);background-size:32px 32px;opacity:.32}}.floor:after{{content:"";position:absolute;left:50%;top:70px;bottom:18px;width:1px;background:linear-gradient(transparent,#33444f,transparent);opacity:.5}}
.sign{{position:relative;z-index:1;display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;color:var(--muted);font-size:10px;letter-spacing:.7px;text-transform:uppercase}}.sign b{{color:var(--text);font-size:12px}}
.stations{{position:relative;z-index:1;display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}.station{{min-height:145px;background:linear-gradient(145deg,rgba(15,24,32,.98),rgba(9,15,21,.98));border:1px solid #344551;border-radius:6px;padding:10px;position:relative;overflow:hidden}}.station:before{{content:"";position:absolute;inset:6px;border:1px solid rgba(91,213,230,.06);border-radius:4px;pointer-events:none}}.room-active{{box-shadow:inset 0 0 28px rgba(99,211,154,.035)}}.room-idle{{opacity:.86}}
.station-sign{{display:flex;gap:9px;align-items:center;border-bottom:1px solid var(--line);padding-bottom:8px;position:relative;z-index:2}}.station-code{{font:700 9px Consolas,monospace;color:var(--cyan);border:1px solid #27515a;padding:4px 5px;border-radius:3px;background:#0a151b}}.station-sign b{{display:block;font-size:10px;letter-spacing:.8px}}.station-sign small{{color:var(--muted);font-size:9px}}.room-lamp{{margin-left:auto;width:6px;height:6px;border-radius:50%;background:#4b5862}}.room-active .room-lamp{{background:var(--green);box-shadow:0 0 10px rgba(99,211,154,.7)}}
.station-floor{{height:68px;display:flex;align-items:center;justify-content:center;gap:8px;position:relative}}.machine{{width:26px;height:34px;border:1px solid #44545f;background:#151f27;border-radius:3px;box-shadow:inset 0 0 8px rgba(114,184,217,.08)}}.machine:before{{content:"";display:block;width:10px;height:10px;margin:6px auto;border:1px solid #5d6c77;border-radius:2px}}.machine:after{{content:"";display:block;width:16px;height:2px;margin:4px auto;background:#3c4b56}}.conveyor{{height:18px;width:78px;border:1px solid #34444f;border-radius:3px;background:#0a1015;display:flex;align-items:center;justify-content:space-around;overflow:hidden}}.conveyor span{{width:8px;height:8px;background:#26343e;border:1px solid #52616b;transform:rotate(45deg)}}.room-active .conveyor span{{animation:belt .9s linear infinite}}.room-active .conveyor span:nth-child(2){{animation-delay:.18s}}.room-active .conveyor span:nth-child(3){{animation-delay:.36s}}.room-active .conveyor span:nth-child(4){{animation-delay:.54s}}.room-active .conveyor span:nth-child(5){{animation-delay:.72s}}@keyframes belt{{to{{transform:translateX(12px) rotate(45deg)}}}}.station-units{{display:flex;gap:7px}}.station-unit{{width:27px;height:19px;border:1px solid #4a5864;border-radius:3px;background:#18212a;position:relative}}.station-unit:before{{content:"";position:absolute;left:6px;top:5px;width:9px;height:6px;background:#56636e}}.station-unit:after{{content:"";position:absolute;right:5px;top:5px;width:4px;height:6px;background:#2d3943}}.station-unit.active{{border-color:#527d68;box-shadow:0 0 10px rgba(105,195,154,.18)}}.station-unit.active:after{{background:var(--green)}}.empty-unit{{color:#3e4b56}}
.station-status{{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.7px}}
.panel{{padding:14px;margin-top:12px}}.panel h2{{font-size:11px;letter-spacing:1px;margin:0 0 11px;color:#c5cdd4}}.crew{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:9px}}
.worker-card{{background:#0d141b;border:1px solid #2b3843;border-radius:4px;padding:11px}}.worker-head,.worker-foot{{display:flex;justify-content:space-between;gap:8px;align-items:center}}.worker-id{{font:700 11px Consolas,monospace;color:#dce4ea}}
.status-dot{{width:7px;height:7px;border-radius:50%;background:#53606a}}.status-dot.ok{{background:var(--green);box-shadow:0 0 7px rgba(105,195,154,.45)}}.status-dot.warn{{background:var(--yellow)}}.status-dot.bad{{background:var(--red)}}
.agent-row{{display:flex;align-items:center;gap:12px;padding:12px 0 8px}}.agent-glyph{{width:42px;height:42px;position:relative;border:1px solid #33444f;border-radius:4px;background:linear-gradient(145deg,#101b23,#0b1218);image-rendering:pixelated;box-shadow:inset 0 0 12px rgba(91,213,230,.05)}}.agent-glyph:before{{content:"";position:absolute;left:12px;top:7px;width:15px;height:15px;border:2px solid #6c7b86;border-radius:2px;box-shadow:0 0 0 2px #111920}}.agent-glyph:after{{content:"";position:absolute;left:7px;bottom:6px;width:25px;height:12px;border:2px solid #566773;border-bottom:0;border-radius:4px 4px 0 0}}.agent-glyph span:before{{content:"";position:absolute;left:16px;top:13px;width:3px;height:3px;background:var(--cyan);box-shadow:8px 0 var(--cyan)}}.agent-glyph span{{position:absolute;right:5px;top:5px;width:4px;height:4px;border-radius:50%;background:var(--green)}}
.worker-info{{display:grid;gap:3px}}.worker-info b{{font-size:11px}}.worker-info span{{color:var(--muted);font-size:10px}}.worker-info strong{{font-size:9px;letter-spacing:.8px}}.meter{{height:4px;background:#25303a;border-radius:2px;overflow:hidden}}.meter i{{display:block;height:100%;background:var(--green);border-radius:2px}}.worker-foot{{color:var(--muted);font:10px Consolas,monospace;margin-top:6px}}.worker-job{{font:10px Consolas,monospace;color:var(--blue);margin-top:7px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}.station-world.panel{{padding:14px}}.world-head{{display:flex;justify-content:space-between;align-items:end;gap:12px;margin-bottom:10px}}.world-head h2{{margin:0 0 4px;font-size:11px;letter-spacing:1px}}.world-head span,.world-head>b{{color:var(--muted);font:9px Consolas,monospace;letter-spacing:.5px}}.world-head>b{{color:var(--accent)}}.world-viewport{{overflow:hidden;border:1px solid #33444e;background:#080e12;border-radius:5px;box-shadow:inset 0 0 45px rgba(0,0,0,.5)}}#stationWorld{{display:block;width:100%;height:auto;image-rendering:pixelated}}.world-legend{{display:flex;gap:16px;align-items:center;flex-wrap:wrap;padding-top:9px;color:#71808b;font:9px Consolas,monospace}}.world-legend i{{display:inline-block;width:8px;height:8px;margin-right:5px;border:1px solid #596873;vertical-align:-1px}}.legend-agent{{background:var(--cyan)}}.legend-live{{background:var(--green)}}.legend-queue{{background:var(--yellow)}}.legend-fail{{background:var(--red)}}.world-lock{{margin-left:auto;color:var(--accent)}}.lifecycle{{position:relative;display:flex;justify-content:space-between;gap:4px;margin-top:10px;padding-top:9px;border-top:1px solid #202b35}}.lifecycle-track{{position:absolute;left:7%;right:7%;top:12px;height:1px;background:#34424d}}.lifecycle-step{{position:relative;z-index:1;display:grid;justify-items:center;gap:4px;min-width:48px;color:#53616c;font:8px Consolas,monospace;letter-spacing:.4px}}.lifecycle-step i{{width:7px;height:7px;border-radius:50%;border:1px solid #4a5863;background:#111820}}.lifecycle-step-active{{color:var(--cyan);font-weight:700}}.lifecycle-step-active i{{background:var(--cyan);border-color:var(--cyan);box-shadow:0 0 9px rgba(91,213,230,.65)}}.lifecycle-step-failed{{color:var(--red)}}.lifecycle-step-failed i{{background:var(--red);border-color:var(--red);box-shadow:0 0 9px rgba(223,110,117,.45)}}.lifecycle-step-idle{{color:#66737d}}
.pipeline{{display:grid;grid-template-columns:repeat(6,1fr);gap:6px}}.phase{{background:#0d141b;border:1px solid var(--line);border-radius:3px;padding:9px;min-height:50px;display:flex;flex-direction:column;justify-content:space-between;gap:5px}}.phase b{{font-size:9px;letter-spacing:.7px}}.phase span{{font-size:10px;color:#c1cbd2}}
.meta{{color:var(--muted);font-size:10px;margin-top:12px;display:flex;gap:14px;flex-wrap:wrap}}.lock{{color:var(--accent)!important}}.empty-crew{{border:1px dashed #33414d;border-radius:4px;padding:25px;text-align:center;display:grid;gap:7px;color:var(--muted)}}.empty-mark{{font:700 11px Consolas,monospace;color:#56636d}}
@media(max-width:900px){{.stats{{grid-template-columns:repeat(2,1fr)}}.stations{{grid-template-columns:1fr 1fr}}.pipeline{{grid-template-columns:1fr 1fr}}@media(max-width:560px){{main{{padding:12px}}.stations{{grid-template-columns:1fr}}.stats{{grid-template-columns:1fr 1fr}}
.ops-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px}}.ops-panel{{margin-top:0}}.ops-panel.wide{{grid-column:span 2}}
.job-row,.queue-row,.feed-row,.artifact-row{{display:grid;gap:10px;align-items:center;border-top:1px solid #202b35;padding:8px 2px;font-size:10px}}
.job-row{{grid-template-columns:70px 1fr 80px 45px}}.queue-row{{grid-template-columns:70px 180px 1fr}}.feed-row{{grid-template-columns:145px 80px 90px 1fr}}.artifact-row{{grid-template-columns:70px 180px 1fr}}
.job-row:first-of-type,.queue-row:first-of-type,.feed-row:first-of-type,.artifact-row:first-of-type{{border-top:0}}
.job-state{{font-weight:700;letter-spacing:.5px}}.mono,.feed-time{{font:10px Consolas,monospace;color:#9aa7b2}}.artifact{{color:var(--blue);font-family:Consolas,monospace;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}.empty-row{{padding:13px 2px;color:#596773;font-size:10px}}
@media(max-width:900px){{.ops-grid{{grid-template-columns:1fr}}.ops-panel.wide{{grid-column:span 1}}.feed-row{{grid-template-columns:125px 70px 70px 1fr}}
@media(max-width:560px){{.job-row{{grid-template-columns:55px 1fr 60px}}.job-row b{{display:none}}.queue-row{{grid-template-columns:55px 120px 1fr}}.feed-row{{grid-template-columns:1fr 55px 60px}}.feed-row span:last-child{{grid-column:1/-1}}.artifact-row{{grid-template-columns:55px 110px 1fr}}
</style></head>
<body><main>
  <div class="top">
    <div><h1><span>SP2L RESEARCH STATION</span></h1><div class="sub">AI research agent deck • telemetry-backed • research only</div></div>
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
    <div class="sign"><div><b>RESEARCH STATION / FACTORY DECK</b><span> • agent motion is telemetry-backed</span></div><span>AUTO REFRESH · 5s</span></div>
    <div class="stations">
      {station_card("discovery", workers)}
      {station_card("stability", workers)}
      {station_card("robustness", workers)}
      {station_card("holdout", workers)}
      {station_card("forward", workers)}
      {station_card("idle", workers)}
    </div>
  </section>

  {station_world(workers)}\n\n  <section class="panel">
    <h2>AGENTS & CURRENT JOBS · TELEMETRY LINKED</h2>
    <div class="crew">{crew_html}</div>
  </section>

  {telemetry_panels(workers)}

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
