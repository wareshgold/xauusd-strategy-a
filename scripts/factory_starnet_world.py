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
<script src="/starnet/app/worldsurface.js"></script>
<script src="/starnet/app/worldrenderer.js"></script>
<script src="/starnet/app/worldmodel.js"></script>
<script src="/starnet/app/stationbake.js"></script>
<script>
(()=> {
 const canvas=document.getElementById("world"),ctx=canvas.getContext("2d");ctx.imageSmoothingEnabled=false;
 let state={workers:[]},station=null,baked=null;
 function buildStation(){
   station=WorldModel.create(WorldModel.defaultDoc());
   for(const id of station.doc().order.slice()) station.removeRoom(id);
   const rooms=[
    ["hab",{x1:4,y1:3,x2:20,y2:11}],["lab",{x1:23,y1:3,x2:39,y2:11}],["lab",{x1:42,y1:3,x2:58,y2:11}],
    ["vault",{x1:13,y1:17,x2:29,y2:25}],["lab",{x1:32,y1:17,x2:48,y2:25}],["hab",{x1:51,y1:17,x2:58,y2:25}],
    ["corridor",{x1:20,y1:6,x2:23,y2:8}],["corridor",{x1:39,y1:6,x2:42,y2:8}],
    ["corridor",{x1:28,y1:11,x2:34,y2:17}],["corridor",{x1:48,y1:20,x2:51,y2:22}]
   ];
   for(const [kind,rect] of rooms) station.addRoom({kind,rect});
   baked=StationBake.bake(station.projectGeometry());
 }
 function fit(){const dpr=Math.min(2,devicePixelRatio||1);canvas.width=Math.floor(innerWidth*dpr);canvas.height=Math.floor(innerHeight*dpr);canvas.style.width=innerWidth+"px";canvas.style.height=innerHeight+"px";}
 function labels(geo,s,ox,oy){
   const names=["DISCOVERY LAB","STABILITY LAB","ROBUSTNESS LAB","HOLDOUT VAULT","FORWARD OPS","WORKER BAY"],codes=["D01","S01","R01","H01","F01","W01"];
   (geo.rooms||[]).filter(r=>r.kind!=="corridor").slice(0,6).forEach((r,i)=>{
     const x=ox+r.x1*12*s,y=oy+r.y1*12*s,w=(r.x2-r.x1+1)*12*s;
     ctx.fillStyle="rgba(8,12,14,.76)";ctx.fillRect(x+5*s,y+5*s,Math.min(190*s,w-10*s),25*s);
     ctx.fillStyle="#d7b66c";ctx.font=Math.max(9,10*s)+"px monospace";ctx.fillText(names[i],x+10*s,y+16*s);
     ctx.fillStyle="#718078";ctx.font=Math.max(7,8*s)+"px monospace";ctx.fillText(codes[i],x+10*s,y+26*s);
   });
 }
 function render(){
   if(!baked)return;
   const pad=20,s=Math.min((canvas.width-pad*2)/baked.W,(canvas.height-pad*2)/baked.H),ox=(canvas.width-baked.W*s)/2,oy=(canvas.height-baked.H*s)/2;
   ctx.clearRect(0,0,canvas.width,canvas.height);ctx.save();ctx.translate(ox,oy);ctx.scale(s,s);
   StationBake.drawBase(ctx,baked,0,0);StationBake.drawLight(ctx,baked,0,0);ctx.restore();
   labels(station.projectGeometry(),s,ox,oy);requestAnimationFrame(render);
 }
 async function poll(){
   try{const r=await fetch("/api/world",{cache:"no-store"});state=await r.json();
    document.getElementById("link").textContent=state.workers.length?"FACTORY TELEMETRY · LIVE":"FACTORY WAITING FOR TELEMETRY";
    document.getElementById("workers").innerHTML=state.workers.map(w=>"<span class='worker "+(w.state==="FAILED"?"fail":(w.state==="RUNNING"||w.state==="HEARTBEAT"?"live":""))+"'>"+esc(w.id)+" · "+esc(w.station)+" · "+esc(w.state)+" · "+Math.round(w.progress)+"%</span>").join("");
   }catch(_){document.getElementById("link").textContent="FACTORY TELEMETRY · OFFLINE"}
   setTimeout(poll,1000);
 }
 function esc(s){return String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]))}
 addEventListener("resize",fit);fit();buildStation();poll();render();
})();
</script></body></html>"""

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
