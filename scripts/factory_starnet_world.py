from __future__ import annotations
import json, mimetypes, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from strategy_factory.starnet_adapter import build_world_state

ROOT=Path(__file__).resolve().parents[1]
VENDOR=ROOT/"vendor"/"starnet-engine"/"frontend"
STATUS=ROOT/"runtime"/"factory_worker_status.json"
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
<div class="card"><div class="lock">RESEARCH ONLY · PRODUCTION LOCKED</div><div class="dim">BUY/SELL GENERATION: 0</div></div></div>
<div id="telemetry" class="card"><div class="dim" id="link">FACTORY WAITING FOR TELEMETRY</div><div id="workers"></div></div>

<script src="/starnet/js/util.js"></script>
<script src="/starnet/app/terrain.js"></script>
<script src="/starnet/app/authored-prop-content.js"></script>
<script src="/starnet/app/authored-prop-motion.js"></script>
<script src="/starnet/app/approved-sheet-effects.js"></script>
<script src="/starnet/app/projection-prop-effects.js"></script>
<script src="/starnet/app/propremaster.js"></script>
<script src="/starnet/app/authored-surface-mounts.js"></script>
<script src="/starnet/app/propsprites.js"></script>
<script src="/starnet/js/assets.js"></script>
<script src="/starnet/app/worldsurface.js"></script>
<script src="/starnet/app/worldlight.js"></script>
<script src="/starnet/app/worldrenderer.js"></script>
<script src="/starnet/app/worldmodel.js"></script>
<script src="/starnet/app/stationbake.js"></script>
<script src="/starnet/app/world.js"></script>
<script>
(()=> {
 const canvas=document.getElementById("world");
 function resize(){const dpr=Math.min(2,devicePixelRatio||1);canvas.width=Math.floor(innerWidth*dpr);canvas.height=Math.floor(innerHeight*dpr);canvas.style.width=innerWidth+"px";canvas.style.height=innerHeight+"px";}
 function stage(){
   const station=WorldModel.create(WorldModel.starterDoc());
   const rooms=station.doc().order.slice();
   if(rooms.length) station.setFloor(rooms[0],"oak");
   const add=(kind,rect)=>station.addRoom({kind,rect});
   add("lab",{x1:21,y1:0,x2:37,y2:10}); add("lab",{x1:40,y1:0,x2:56,y2:10});
   add("vault",{x1:9,y1:14,x2:25,y2:23}); add("lab",{x1:28,y1:14,x2:44,y2:23}); add("hab",{x1:47,y1:14,x2:56,y2:23});
   station.placeHallway({rects:[{x1:17,y1:4,x2:21,y2:6},{x1:37,y1:4,x2:40,y2:6},{x1:18,y1:10,x2:31,y2:14},{x1:44,y1:17,x2:47,y2:19}]});
   World.loadStation(station);
   const overseer={id:"sp2l-factory-overseer",name:"FACTORY OVERSEER",color:"#d7b66c",skin:"default"};\n   if(typeof World.spawn!=="function") throw new Error("World.spawn is not a function");\n   World.spawn.call(World,overseer);
   World.start();
 }
 addEventListener("resize",resize);resize();
 try{World.init(canvas);stage(); }catch(e){document.getElementById("link").textContent="ENGINE ERROR · "+e.message; const box=document.createElement("div"); box.className="card"; box.style.cssText="position:absolute;left:18px;bottom:70px;z-index:20;max-width:900px;color:#ff8b8b;white-space:pre-wrap"; box.textContent="STAR-NET BOOT ERROR\n"+(e&&e.stack||e); document.body.appendChild(box); console.error(e);}
 async function poll(){
   try{const r=await fetch("/api/world",{cache:"no-store"});const s=await r.json();
    document.getElementById("link").textContent=s.workers.length?"FACTORY TELEMETRY · LIVE":"FACTORY TELEMETRY · WAITING FOR JOB";
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
    ws=build_world_state([w for w in workers if isinstance(w,dict)])
    return {"workers":[{"id":w.worker_id,"station":w.station,"state":w.state,"progress":w.progress,"job":w.job_id or ""} for w in ws.workers],
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
