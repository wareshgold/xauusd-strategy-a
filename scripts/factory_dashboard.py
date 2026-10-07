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

from strategy_factory.starnet_adapter import build_world_state

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
    """Render a telemetry-backed SP2L station world from the validated adapter."""
    world_state = build_world_state(workers)
    payload = json.dumps(
        [
            {
                "id": worker.worker_id,
                "job": str(worker.job_id or ""),
                "state": worker.state,
                "station": worker.station,
                "progress": worker.progress,
            }
            for worker in world_state.workers
        ],
        ensure_ascii=False,
    ).replace("</", "<\\/")

    world = """
    <section class="station-world panel">
      <div class="world-head">
        <div><h2>STATION WORLD · TELEMETRY IS THE GAME STATE</h2><span>Rooms are capabilities • corridors are handoff lanes • agents are real workers</span></div>
        <b>SP2L / RESEARCH DECK 01</b>
      </div>
      <div class="world-viewport"><canvas id="stationWorld" width="1280" height="650"></canvas></div>
      <div class="world-legend">
        <span><i class="legend-agent"></i>AGENT</span><span><i class="legend-live"></i>LIVE</span>
        <span><i class="legend-queue"></i>QUEUED</span><span><i class="legend-fail"></i>FAILED</span>
        <span class="world-lock">RESEARCH ONLY · PRODUCTION LOCKED · BUY/SELL: 0</span>
      </div>
      <script>
      (() => {
        const workers = __WORKERS__;
        const canvas = document.getElementById("stationWorld");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        ctx.imageSmoothingEnabled = false;
        const W = 1280, H = 650;
        const C = {
          bg:"#070b10", floor:"#111a20", floor2:"#17242b", wall:"#33434d",
          edge:"#52636e", text:"#dce5ea", muted:"#657681", cyan:"#5bd5e6",
          green:"#63d39a", amber:"#d6aa4d", red:"#df6e75", blue:"#72b8d9",
          dark:"#0a1015", glass:"#12202a"
        };
        const rooms = {
          discovery:{x:70,y:105,w:330,h:190,label:"DISCOVERY LAB",code:"D01",sub:"CANDIDATE DISCOVERY"},
          stability:{x:475,y:105,w:330,h:190,label:"STABILITY LAB",code:"S01",sub:"CHRONOLOGICAL STABILITY"},
          robustness:{x:880,y:105,w:330,h:190,label:"ROBUSTNESS LAB",code:"R01",sub:"ROBUSTNESS CHECKS"},
          holdout:{x:275,y:390,w:330,h:190,label:"HOLDOUT VAULT",code:"H01",sub:"UNTOUCHED / FRESH"},
          forward:{x:680,y:390,w:330,h:190,label:"FORWARD OPS",code:"F01",sub:"MT5 VALIDATION"},
          idle:{x:1050,y:390,w:160,h:190,label:"WORKER BAY",code:"W01",sub:"NO ACTIVE JOB"}
        };

        function rect(x,y,w,h,fill,stroke) {
          ctx.fillStyle=fill; ctx.fillRect(x,y,w,h);
          if(stroke){ctx.strokeStyle=stroke;ctx.strokeRect(x+.5,y+.5,w-1,h-1);}
        }
        function text(s,x,y,size,color,align="left",weight="400") {
          ctx.fillStyle=color;ctx.font=weight+" "+size+"px monospace";ctx.textAlign=align;ctx.fillText(s,x,y);
        }
        function panelBox(x,y,w,h) {
          rect(x,y,w,h,C.floor,C.edge);
          rect(x+6,y+6,w-12,h-12,"#0d151b","#26353f");
        }
        function room(r,key) {
          panelBox(r.x,r.y,r.w,r.h);
          rect(r.x+1,r.y+1,r.w-2,8,C.wall);
          rect(r.x+14,r.y+22,r.w-28,38,"#0a1116","#263943");
          text(r.label,r.x+24,r.y+38,12,C.text,"left","700");
          text(r.code,r.x+r.w-24,r.y+38,10,C.cyan,"right","700");
          text(r.sub,r.x+24,r.y+52,7,C.muted);
          // windows / status lights
          for(let i=0;i<6;i++){rect(r.x+18+i*18,r.y+72,11,4,i<3?C.cyan:"#263943");}
          // desks and terminals
          for(let i=0;i<3;i++){
            const dx=r.x+28+i*92, dy=r.y+112;
            rect(dx,dy,68,25,"#18252d","#3b4c57");
            rect(dx+12,dy-17,31,16,C.dark,"#465863");
            rect(dx+16,dy-13,23,8,key==="holdout"?C.amber:(key==="forward"?C.blue:"#31525b"));
            rect(dx+48,dy+6,8,8,"#283740");
            rect(dx+18,dy+28,8,5,"#4b5b65"); rect(dx+43,dy+28,8,5,"#4b5b65");
          }
          // floor strips
          for(let i=0;i<7;i++) rect(r.x+20+i*43,r.y+r.h-28,28,3,"#25333b");
          // door
          rect(r.x+r.w/2-22,r.y+r.h-10,44,10,"#0a1116",C.edge);
          rect(r.x+r.w/2-8,r.y+r.h-10,16,3,key==="holdout"?C.amber:C.cyan);
        }
        function vault() {
          const r=rooms.holdout;
          rect(r.x+104,r.y+84,122,72,"#0a1015","#697985");
          rect(r.x+114,r.y+94,102,52,"#121c23","#354954");
          rect(r.x+157,r.y+110,18,18,C.amber,"#e2bf6b");
          for(let i=0;i<4;i++) rect(r.x+123+i*21,r.y+103,12,3,"#263943");
          text("SEALED",r.x+165,r.y+141,7,C.amber,"center","700");
          rect(r.x+26,r.y+84,55,42,"#101a20","#3d4e59");
          text("LOCK",r.x+53,r.y+109,8,C.amber,"center","700");
        }
        function forwardConsole() {
          const r=rooms.forward;
          rect(r.x+35,r.y+78,260,48,"#0a1116","#3f5661");
          for(let i=0;i<8;i++) rect(r.x+48+i*28,r.y+91,17,19,i%2? "#18313a":"#15232b","#36515d");
          rect(r.x+40,r.y+145,250,12,"#0c1419","#34464f");
          text("MT5 VALIDATION BRIDGE",r.x+165,r.y+101,9,C.blue,"center","700");
          text("SEPARATE FROM RESEARCH PROMOTION",r.x+165,r.y+117,7,C.muted,"center");
        }
        function corridors() {
          // Authorized-looking handoff lanes are visualized, but no job is invented.
          const lanes=[
            [400,205,75,20],[805,205,75,20],[440,295,35,95],[605,475,75,20],
            [1008,475,42,20],[605,285,75,105]
          ];
          lanes.forEach(([x,y,w,h])=>{
            rect(x,y,w,h,"#0c151b","#2b3d47");
            if(w>h){for(let xx=x+8;xx<x+w-4;xx+=18)rect(xx,y+h/2-1,10,2,"#3c5662");}
            else{for(let yy=y+8;yy<y+h-4;yy+=18)rect(x+w/2-1,yy,2,10,"#3c5662");}
          });
        }
        function props() {
          // authored environmental props: server rack, plant, warning markers, cargo crates
          rect(28,30,180,48,"#0a1116","#2e424d");
          text("SP2L RESEARCH STATION",40,50,12,C.cyan,"left","700");
          text("LIVE WORLD / TELEMETRY LINK",40,66,7,C.muted);
          rect(1080,30,172,48,"#0a1116","#2e424d");
          text("PRODUCTION LOCKED",1166,51,9,C.amber,"center","700");
          text("BUY/SELL GENERATION: 0",1166,66,7,C.muted,"center");

          // server rack
          rect(16,415,70,126,"#0d171e","#465762");
          for(let i=0;i<5;i++){rect(24,428+i*20,54,12,"#16252e","#31464f");rect(30,433+i*20,8,3,i===0?C.green:"#38505b");}
          text("EVID.",51,557,7,C.muted,"center");

          // crates
          [[1020,570],[1080,570],[1140,570]].forEach((p,i)=>{
            rect(p[0],p[1],42,28,"#202a30","#5a6265");
            ctx.strokeStyle="#59666b";ctx.beginPath();ctx.moveTo(p[0]+4,p[1]+4);ctx.lineTo(p[0]+38,p[1]+24);ctx.moveTo(p[0]+38,p[1]+4);ctx.lineTo(p[0]+4,p[1]+24);ctx.stroke();
          });
          // caution stripes
          for(let x=110;x<250;x+=18) rect(x,360,12,5,x%36===0?C.amber:"#26313a");
          text("HANDOFF DECK",180,350,7,C.muted,"center");
        }
        function agent(w,i,t) {
          const r=rooms[w.station]||rooms.idle;
          const live=w.state==="RUNNING"||w.state==="HEARTBEAT";
          const queued=w.state==="QUEUED", done=w.state==="COMPLETED", fail=w.state==="FAILED";
          const phase=(t/9000+i*0.19)%1;
          const laneX=r.x+42+(i*71)%(Math.max(76,r.w-84));
          const laneY=r.y+126+(i%2)*34;
          let x=laneX, y=laneY+Math.sin(t/1500+i)*2;
          if(queued){x=r.x+22;y=r.y+67;}
          if(done){x=r.x+r.w-27;y=r.y+67;}
          if(fail){x=r.x+r.w/2;y=r.y+r.h-48;}
          // active workers patrol a short, deterministic route inside their assigned room
          if(live){
            const span=Math.max(48,r.w-92), eased=phase<0.5?phase*2:2-phase*2;
            x=r.x+46+eased*span; y=laneY+Math.sin(t/1500+i)*2;
          }
          ctx.save();ctx.translate(Math.round(x),Math.round(y));
          // shadow
          rect(-10,18,21,4,"#05090c");
          // antenna / status
          rect(-1,-17,2,5,live?C.cyan:"#52616a");
          rect(-3,-20,6,3,fail?C.red:(live?C.green:C.amber));
          // head
          rect(-7,-13,14,11,fail?C.red:(live?C.cyan:"#7d8b93"),"#10181d");
          rect(-4,-10,2,3,"#071016");rect(3,-10,2,3,"#071016");
          // body + backpack
          rect(-10,-1,20,15,live?"#284650":"#202c33","#61727c");
          rect(7,2,5,9,"#16232a","#465762");
          // arms
          rect(-14,1,4,10,live?C.cyan:"#566771");rect(10,1,4,10,live?C.cyan:"#566771");
          // legs, with a tiny walk-cycle offset
          const step=live&&Math.floor(t/420+i)%2?2:-2;
          rect(-7,14,5,7,"#354650");rect(2+step,14,5,7,"#354650");
          // progress chip
          if(live){rect(14,-13,4,4,C.green);rect(-18,-4,5,18,"#18262e");rect(-18,13,5,Math.max(1,17*(w.progress/100)),C.green);}
          ctx.restore();
          text(w.id,x,y+31,8,C.text,"center","700");
          if(w.job) text(w.job.slice(0,16),x,y+42,6,C.muted,"center");
        }
        function draw(t) {
          rect(0,0,W,H,C.bg);
          // floor grid
          ctx.strokeStyle="#142129";
          for(let x=0;x<W;x+=24){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}
          for(let y=0;y<H;y+=24){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}
          corridors();
          Object.entries(rooms).forEach(([k,r])=>room(r,k));
          vault();forwardConsole();props();
          workers.forEach((w,i)=>agent(w,i,t));
          // status footer
          rect(260,600,760,28,"#080e12","#2e414c");
          text("QUEUE → LAB → EVIDENCE → COMPLETE",640,618,9,C.cyan,"center","700");
          text("STATE SOURCE: runtime/factory_worker_status.json",640,625,6,C.muted,"center");
          requestAnimationFrame(draw);
        }
        function resize(){
          const w=Math.min(canvas.parentElement.clientWidth,W);
          canvas.style.width=w+"px";canvas.style.height=(w/W*H)+"px";
        }
        resize();window.addEventListener("resize",resize);requestAnimationFrame(draw);
      })();
      </script>
    </section>
    """
    return world.replace("__WORKERS__", payload)

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
    <div><h1><span>SP2L RESEARCH STATION</span></h1><div class="sub">CEO: ALI • AI research agent deck • telemetry-backed • research only</div></div>
    <div class="state {headline_class}">{mode_label} · {headline}<br><span style="font-size:9px;color:#71808c">COMMAND: CEO ALI</span></div>
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
