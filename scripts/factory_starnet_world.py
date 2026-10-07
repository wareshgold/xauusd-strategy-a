from __future__ import annotations
import json, mimetypes, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from strategy_factory.starnet_adapter import build_world_state
from strategy_factory.job_events import FactoryJobEventLedger

ROOT=Path(__file__).resolve().parents[1]
VENDOR=ROOT/"vendor"/"starnet-engine"/"frontend"
STATUS=ROOT/"runtime"/"factory_worker_status.json"
JOB_EVENTS=ROOT/"runtime"/"factory_job_events.jsonl"
PORT=8789

PAGE=r"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SP2L Research Station</title>
<style>
html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#050709;color:#d9d4c5;font:13px monospace}
#world{position:absolute;inset:0;width:100%;height:100%;background:#070d10}
#hud{position:absolute;left:18px;right:18px;top:16px;display:flex;justify-content:space-between;align-items:flex-start;pointer-events:none;z-index:5}
.card{background:rgba(9,13,15,.88);border:1px solid #49483e;padding:10px 13px;box-shadow:0 5px 25px rgba(0,0,0,.35)}
.title{color:#d7b66c;font-weight:700;letter-spacing:1.8px}.dim{color:#8e948e;font-size:10px;margin-top:4px}.lock{color:#d6aa4d}
#telemetry{position:absolute;left:18px;bottom:16px;max-width:700px;z-index:5;pointer-events:none}
.worker{display:inline-block;margin:4px 5px 0 0;padding:5px 7px;background:rgba(10,15,17,.88);border:1px solid #34413e;color:#b9c3bd;font-size:10px}
.live{border-color:#5b9b78;color:#77d09a}.fail{border-color:#a35d62;color:#df7c82}
</style></head><body>
<canvas id="world"></canvas>
<div id="hud"><div class="card"><div class="title">SP2L / RESEARCH STATION</div><div class="dim">STAR-NET WORLD ENGINE · SP2L TELEMETRY ADAPTER · CEO: ALI</div></div>
<div class="card"><div class="lock">RESEARCH ONLY · PRODUCTION LOCKED</div><div class="dim">BUY/SELL GENERATION: 0 · HANDOFF NETWORK: READY</div></div></div>
<div id="telemetry" class="card"><div class="dim" id="link">FACTORY WAITING FOR TELEMETRY</div><div class="dim">HANDOFF ROUTE · DISCOVERY → STABILITY → ROBUSTNESS → HOLDOUT → FORWARD</div><div id="workers"></div></div>

<script src="/starnet/js/util.js"></script>
<script src="/starnet/app/asciifx.js"></script>
<script src="/starnet/js/audio.js"></script>
<script src="/starnet/js/arcade.js"></script>
<script src="/starnet/app/backdrop-bake.js"></script>
<script src="/starnet/app/spacebg.js"></script>
<script src="/starnet/app/terrain.js"></script>
<script src="/starnet/app/industrialtextures.js"></script>
<script src="/starnet/app/authored-prop-content.js"></script>
<script src="/starnet/app/authored-service-content.js"></script>
<script src="/starnet/app/authored-prop-motion.js"></script>
<script src="/starnet/app/authored-machine-config.js"></script>
<script src="/starnet/app/approved-sheet-effects.js"></script>
<script src="/starnet/app/projection-prop-effects.js"></script>
<script src="/starnet/app/propremaster.js"></script>
<script src="/starnet/app/authored-surface-mounts.js"></script>
<script src="/starnet/app/propsprites.js"></script>
<script src="/starnet/app/propsearch.js"></script>
<script src="/starnet/app/conveyor.js"></script>
<script src="/starnet/app/pipeline.js"></script>
<script src="/starnet/app/workflowline.js"></script>
<script src="/starnet/app/ghostline.js"></script>
<script src="/starnet/app/propanchor.js"></script>
<script src="/starnet/app/waitanchor.js"></script>
<script src="/starnet/app/data-shim.js"></script>
<script src="/starnet/js/sprite-load-plan.js"></script>
<script src="/starnet/app/skinstage.js"></script>
<script src="/starnet/app/skin-study-tone.js"></script>
<script src="/starnet/app/skin-study-preview.js"></script>
<script src="/starnet/js/assets.js"></script>
<script src="/starnet/app/zones.js"></script>
<script src="/starnet/app/toolprops.js"></script>
<script src="/starnet/app/worldsurface.js"></script>
<script src="/starnet/app/worldlight.js"></script>
<script src="/starnet/app/worldrenderer.js"></script>
<script src="/starnet/app/arrival.js"></script>
<script src="/starnet/app/world.js"></script>
<script src="/starnet/app/worldmodel.js"></script>
<script src="/starnet/app/roomstyles.js"></script>
<script src="/starnet/app/stationbuilder.js"></script>
<script src="/starnet/app/planpreview.js"></script>
<script src="/starnet/app/linelayout.js"></script>
<script src="/starnet/app/lineedit.js"></script>
<script src="/starnet/app/stationbake.js"></script>
<script>
(()=> {
 const canvas=document.getElementById("world");
 let telemetryWorkers = new Map();
 let activeRunIds = new Map();
 function factoryBus(){return (typeof U!=="undefined" && U.bus && typeof U.bus.emit==="function") ? U.bus : null;}
 function syncTelemetryToWorld(workers){
   const bus=factoryBus();
   if(!bus) return;
   for(const w of workers){
     if(!w || !w.id) continue;
     const prev=telemetryWorkers.get(w.id);
     const live=(w.state==="RUNNING"||w.state==="HEARTBEAT");
     const wasLive=prev==="RUNNING"||prev==="HEARTBEAT";
     if(live && !wasLive){
       const runId="factory:"+w.id+":"+String(w.job||"unknown");
       activeRunIds.set(w.id,runId);
       bus.emit("agent.run.start",{agentId:w.id,runId,trigger:"event",factory:true,jobId:w.job||null});
     }else if(!live && wasLive && (w.state==="COMPLETED"||w.state==="FAILED"||w.state==="IDLE")){
       bus.emit("agent.run.end",{agentId:w.id,runId:activeRunIds.get(w.id)||null,reason:w.state==="FAILED"?"error":"done",factory:true});
       activeRunIds.delete(w.id);
     }
     telemetryWorkers.set(w.id,w.state);
   }
 }

 function resize(){const dpr=Math.min(2,devicePixelRatio||1);canvas.width=Math.floor(innerWidth*dpr);canvas.height=Math.floor(innerHeight*dpr);canvas.style.width=innerWidth+"px";canvas.style.height=innerHeight+"px";}
 function stage(){
   const station=WorldModel.create(WorldModel.starterDoc());
   const rooms=station.doc().order.slice();
   if(rooms.length){
     const hub=station.doc().rooms[rooms[0]];
     hub.name="DISCOVERY LAB";
     hub.kind="lab";
     hub.rects=[{x1:2,y1:2,x2:17,y2:11}];
     station.setFloor(rooms[0],"oak");
   }
   const add=(kind,rect,name)=>station.addRoom({kind,rect,name});
   add("lab",{x1:25,y1:2,x2:40,y2:11},"STABILITY LAB");
   add("lab",{x1:48,y1:2,x2:63,y2:11},"ROBUSTNESS LAB");
   add("vault",{x1:11,y1:18,x2:26,y2:28},"HOLDOUT VAULT");
   add("lab",{x1:42,y1:18,x2:57,y2:28},"FORWARD OPS");
   // Authored workflow spine: real StarNet corridor decks + real belt topology.
   // The belts are a visual handoff map only; they do not fabricate jobs or runtime activity.
   station.placeHallway({rects:[
     {x1:17,y1:5,x2:25,y2:7},
     {x1:40,y1:5,x2:48,y2:7},
     {x1:54,y1:10,x2:56,y2:16},
     {x1:25,y1:15,x2:56,y2:17},
     {x1:24,y1:16,x2:26,y2:23},
     {x1:25,y1:22,x2:43,y2:24}
   ]});

   const handoffRun=(a,b)=>station.placeBeltRun({tx:a[0],ty:a[1]},{tx:b[0],ty:b[1]});
   const handoffs=[
     // DISCOVERY → STABILITY
     [[17,6],[25,6]],
     // STABILITY → ROBUSTNESS
     [[40,6],[48,6]],
     // ROBUSTNESS → central workflow spine
     [[55,10],[55,16]],
     [[55,16],[25,16]],
     // spine → HOLDOUT
     [[25,16],[25,22]],
     // HOLDOUT → FORWARD OPS
     [[25,23],[43,23]]
   ];
   for(const [a,b] of handoffs) handoffRun(a,b);

   World.loadStation(station);
   const roster=telemetryWorkers.size?[...telemetryWorkers.keys()].sort():[];
   const heroId=roster[0]||"sp2l-factory-overseer";
   const overseer={id:heroId,name:heroId==="sp2l-factory-overseer"?"FACTORY OVERSEER":heroId,color:"#d7b66c",skin:"default"};
   if(typeof World.spawn!=="function") throw new Error("World.spawn is not a function");
   World.spawn.call(World,overseer);
   World.start();
 }
 addEventListener("resize",resize);resize();
 async function boot(){
   try{const r=await fetch("/api/world",{cache:"no-store"});const s=await r.json();for(const w of (s.workers||[])) if(w&&w.id) telemetryWorkers.set(w.id,w.state);}
   catch(_){/* telemetry may be unavailable; the world still boots as a neutral overseer */}
   stage();
 }
 try{World.init(canvas);boot(); }catch(e){document.getElementById("link").textContent="ENGINE ERROR · "+e.message; const box=document.createElement("div"); box.className="card"; box.style.cssText="position:absolute;left:18px;bottom:70px;z-index:20;max-width:900px;color:#ff8b8b;white-space:pre-wrap"; box.textContent="STAR-NET BOOT ERROR\n"+(e&&e.stack||e); document.body.appendChild(box); console.error(e);}
 async function poll(){
   try{const r=await fetch("/api/world",{cache:"no-store"});const s=await r.json();
    syncTelemetryToWorld(s.workers);
    const latest=s.handoffs&&s.handoffs.length?s.handoffs[s.handoffs.length-1]:null;
    document.getElementById("link").textContent=latest ? "FACTORY TELEMETRY · HANDOFF ACCEPTED · "+latest.source.toUpperCase()+" → "+latest.destination.toUpperCase() : (s.workers.length?"FACTORY TELEMETRY · LIVE":"FACTORY TELEMETRY · WAITING FOR JOB");
    document.getElementById("workers").innerHTML=s.workers.map(w=>"<span class='worker "+(w.state==="FAILED"?"fail":(w.state==="RUNNING"||w.state==="HEARTBEAT"?"live":""))+"'>"+esc(w.id)+" · "+esc(w.station)+" · "+esc(w.state)+" · "+Math.round(w.progress)+"%</span>").join("");
   }catch(_){document.getElementById("link").textContent="FACTORY TELEMETRY · OFFLINE"}
   setTimeout(poll,1000);
 }
 function esc(s){return String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]))}
 poll();
})();
</script></script></body></html>"""

def world_payload():
    try: raw=json.loads(STATUS.read_text(encoding="utf-8"))
    except Exception: raw={"workers":[]}
    workers=raw.get("workers",[]) if isinstance(raw,dict) else []
    events=FactoryJobEventLedger(path=JOB_EVENTS).entries()
    ws=build_world_state([w for w in workers if isinstance(w,dict)], events=events)
    return {"workers":[{"id":w.worker_id,"station":w.station,"state":w.state,"progress":w.progress,"job":w.job_id or ""} for w in ws.workers],
            "handoffs":[{"sequence":h.sequence,"job":h.job_id,"source":h.source_station,"destination":h.destination_station,"artifact":h.output_artifact,"event_fingerprint":h.event_fingerprint} for h in ws.handoffs],
            "production_locked":ws.production_locked,"buy_sell_generation":ws.buy_sell_generation,"ts":time.time()}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path=self.path.split("?",1)[0]
        if path=="/api/world":
            body=json.dumps(world_payload()).encode();self.send_response(200);self.send_header("Content-Type","application/json");self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(body);return
        if path=="/":
            body=PAGE.encode();self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(body);return
        if path.startswith("/starnet/"):
            rel=path[len("/starnet/"):];target=(VENDOR/rel).resolve()
            if VENDOR.resolve() not in target.parents:self.send_error(403);return
            if not target.is_file():self.send_error(404);return
            data=target.read_bytes();ctype=mimetypes.guess_type(str(target))[0] or "application/octet-stream"
            self.send_response(200);self.send_header("Content-Type",ctype);self.send_header("Cache-Control","public, max-age=3600");self.end_headers();self.wfile.write(data);return
        self.send_error(404)
    def log_message(self,*args):pass

if __name__=="__main__":
    print(f"SP2L StarNet World: http://127.0.0.1:{PORT}/")
    print(f"Pinned engine: {VENDOR}")
    ThreadingHTTPServer(("127.0.0.1",PORT),Handler).serve_forever()
