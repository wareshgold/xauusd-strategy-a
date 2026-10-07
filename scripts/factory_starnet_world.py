from __future__ import annotations

"""SP2L Research Station world renderer v0.3.

A renderer-only presentation shell for the validated Factory world contract.
It deliberately does not execute Strategy A, create signals, or invent worker
activity. The browser polls the real Factory telemetry file and renders only
workers that exist in that telemetry.

This is the visual integration spike before replacing the existing dashboard
surface with a full StarNet-derived renderer.
"""

import json
import time
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from strategy_factory.starnet_adapter import build_world_state

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "runtime" / "factory_worker_status.json"
PORT = 8789


def read_world() -> dict:
    try:
        raw = json.loads(STATUS.read_text(encoding="utf-8"))
    except Exception:
        raw = {"workers": []}
    workers = raw.get("workers", []) if isinstance(raw, dict) else []
    if not isinstance(workers, list):
        workers = []
    state = build_world_state([w for w in workers if isinstance(w, dict)])
    return {
        "workers": [
            {
                "id": w.worker_id,
                "station": w.station,
                "state": w.state,
                "progress": w.progress,
                "job": w.job_id or "",
                "detail": w.detail or "",
            }
            for w in state.workers
        ],
        "locked": state.production_locked,
        "buy_sell": state.buy_sell_generation,
        "ts": time.time(),
    }


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SP2L Research Station</title>
<style>
@font-face{font-family:vt;src:url('/vendor/starnet-engine/frontend/assets/fonts/vt323.woff2') format('woff2')}
:root{--bg:#05070b;--ink:#d8e4e8;--dim:#60717b;--cyan:#54d7e8;--green:#72e2a0;--amber:#e4b85d;--red:#e86f78;--steel:#30424c}
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;background:#020409;color:var(--ink);overflow:hidden;font-family:vt,Consolas,monospace}
body:before{content:"";position:fixed;inset:0;pointer-events:none;background:radial-gradient(ellipse at center,transparent 35%,rgba(0,0,0,.65) 100%),repeating-linear-gradient(0deg,rgba(255,255,255,.018) 0 1px,transparent 1px 3px);z-index:5;mix-blend-mode:screen}
#top{height:68px;border-bottom:1px solid #1c3039;background:linear-gradient(#0b1117,#05090d);display:flex;align-items:center;justify-content:space-between;padding:0 22px;position:relative;z-index:10}
.brand{letter-spacing:3px;color:var(--cyan);font-size:25px;text-shadow:0 0 12px rgba(84,215,232,.25)}
.sub{font-size:13px;color:var(--dim);letter-spacing:1px}.lock{color:var(--amber);font-size:13px;letter-spacing:1px}
#stage{position:absolute;left:0;right:0;top:68px;bottom:0;background:#05080c}
canvas{width:100%;height:100%;display:block;image-rendering:pixelated}
#hud{position:absolute;left:20px;bottom:18px;right:20px;height:70px;border:1px solid #29404a;background:rgba(5,10,14,.88);box-shadow:0 0 28px rgba(0,0,0,.55),inset 0 0 18px rgba(84,215,232,.035);padding:10px 14px;display:grid;grid-template-columns:180px 1fr 260px;gap:18px;align-items:center;z-index:8}
.hbig{font-size:18px;color:var(--cyan);letter-spacing:2px}.small{font-size:12px;color:var(--dim);letter-spacing:.8px}
#workers{display:flex;gap:12px;overflow:hidden}.chip{border-left:2px solid var(--cyan);padding-left:8px;min-width:150px}.chip b{display:block;font-size:14px}.chip span{display:block;font-size:11px;color:var(--dim)}
#right{text-align:right}.danger{color:var(--red)}.ok{color:var(--green)}
</style>
</head>
<body>
<header id="top"><div><div class="brand">SP2L / RESEARCH STATION</div><div class="sub">TELEMETRY WORLD · FACTORY CONTROL DECK · CEO: ALI</div></div><div class="lock">RESEARCH ONLY · PRODUCTION LOCKED · BUY/SELL: 0</div></header>
<main id="stage"><canvas id="world"></canvas></main>
<section id="hud"><div><div class="hbig" id="count">0 WORKERS</div><div class="small" id="link">TELEMETRY LINK · WAITING</div></div><div id="workers"></div><div id="right"><div class="small">SOURCE</div><div class="small">runtime/factory_worker_status.json</div></div></section>
<script>
const cv=document.getElementById('world'),ctx=cv.getContext('2d');ctx.imageSmoothingEnabled=false;
let data={workers:[]}; let t=0;
const rooms={
 discovery:{x:.07,y:.16,w:.25,h:.27,code:'D01',name:'DISCOVERY LAB',sub:'CANDIDATE DISCOVERY'},
 stability:{x:.375,y:.16,w:.25,h:.27,code:'S01',name:'STABILITY LAB',sub:'CHRONOLOGICAL STABILITY'},
 robustness:{x:.68,y:.16,w:.25,h:.27,code:'R01',name:'ROBUSTNESS LAB',sub:'ROBUSTNESS CHECKS'},
 holdout:{x:.22,y:.58,w:.25,h:.27,code:'H01',name:'HOLDOUT VAULT',sub:'UNTOUCHED / FRESH'},
 forward:{x:.525,y:.58,w:.25,h:.27,code:'F01',name:'FORWARD OPS',sub:'SEPARATE MT5 VALIDATION'},
 idle:{x:.82,y:.58,w:.14,h:.27,code:'W01',name:'WORKER BAY',sub:'WAITING'}
};
function fit(){cv.width=Math.max(960,innerWidth*devicePixelRatio);cv.height=Math.max(600,(innerHeight-68)*devicePixelRatio)}
addEventListener('resize',fit);fit();
function rect(x,y,w,h,f,s){ctx.fillStyle=f;ctx.fillRect(x,y,w,h);if(s){ctx.strokeStyle=s;ctx.strokeRect(x+.5,y+.5,w-1,h-1)}}
function tx(s,x,y,n,c,a='left',bold=false){ctx.fillStyle=c;ctx.font=(bold?'700 ':'')+n+'px vt,monospace';ctx.textAlign=a;ctx.fillText(s,x,y)}
function room(key,r,W,H){
 const x=r.x*W,y=r.y*H,w=r.w*W,h=r.h*H,active=data.workers.some(a=>a.station===key);
 rect(x,y,w,h,'#101920','#3b505b');rect(x+2,y+2,w-4,9,active?'#355b64':'#24323a');
 tx(r.name,x+18,y+34,18,'#dbe5e8');tx(r.code,x+w-18,y+34,15,'#54d7e8','right',true);tx(r.sub,x+18,y+53,11,'#60717b');
 for(let i=0;i<5;i++){rect(x+18+i*22,y+70,13,3,i<2&&active?'#54d7e8':'#293941')}
 for(let i=0;i<3;i++){let dx=x+28+i*(w-76)/2,dy=y+h*.50;rect(dx,dy,Math.min(92,w/3.3),34,'#17252d','#40535e');rect(dx+14,dy-24,42,21,'#070d12','#536873');rect(dx+19,dy-19,32,10,key==='holdout'?'#e4b85d':key==='forward'?'#72b8d9':'#2b5962')}
 for(let i=0;i<8;i++)rect(x+20+i*(w-55)/8,y+h-23,25,3,'#26363e');
 rect(x+w/2-24,y+h-10,48,10,'#080e12','#53656f');rect(x+w/2-9,y+h-10,18,3,key==='holdout'?'#e4b85d':'#54d7e8');
}
function corridor(a,b,W,H){let x=a[0]*W,y=a[1]*H,w=a[2]*W,h=a[3]*H;rect(x,y,w,h,'#091117','#263a44');for(let i=0;i<Math.max(2,w/28);i++)rect(x+8+i*28,y+h/2-1,14,2,'#31505a')}
function background(W,H){
 rect(0,0,W,H,'#05090d');
 ctx.strokeStyle='#0c1a21';ctx.lineWidth=1;for(let x=0;x<W;x+=28){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke()}for(let y=0;y<H;y+=28){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke()}
 // perspective deck
 ctx.fillStyle='#081016';ctx.beginPath();ctx.moveTo(0,H*.9);ctx.lineTo(W,H*.9);ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.fill();
 for(let y=H*.91;y<H;y+=12){ctx.strokeStyle='#10242c';ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke()}
 for(let x=-W;x<W*2;x+=80){ctx.strokeStyle='#10242c';ctx.beginPath();ctx.moveTo(W/2,H*.72);ctx.lineTo(x,H);ctx.stroke()}
}
function agent(a,i,W,H){
 const r=rooms[a.station]||rooms.idle;let x=r.x*W+(.16+.62*((i*0.27+(t/6500))%1))*r.w*W,y=r.y*H+r.h*H*.70;
 if(a.state==='QUEUED'){x=r.x*W+r.w*W*.12;y=r.y*H+r.h*H*.26}
 if(a.state==='COMPLETED'){x=r.x*W+r.w*W*.88;y=r.y*H+r.h*H*.26}
 if(a.state==='FAILED'){x=r.x*W+r.w*W*.5;y=r.y*H+r.h*H*.84}
 const live=a.state==='RUNNING'||a.state==='HEARTBEAT', pulse=live?Math.sin(t/180+i):0;
 ctx.save();ctx.translate(Math.round(x),Math.round(y+Math.sin(t/700+i)*2));
 rect(-11,16,22,4,'#030608');rect(-2,-24,4,7,live?'#54d7e8':'#63747d');rect(-4,-29,8,4,a.state==='FAILED'?'#e86f78':live?'#72e2a0':'#e4b85d');
 rect(-8,-20,16,13,a.state==='FAILED'?'#8c3943':live?'#54d7e8':'#71818a','#091116');rect(-4,-16,3,3,'#061016');rect(3,-16,3,3,'#061016');
 rect(-12,-5,24,20,live?'#294b54':'#26343b','#5a6b74');rect(9,-2,6,12,'#17262d','#53656f');
 rect(-15,-3,4,12,live?'#54d7e8':'#667680');rect(11,-3,4,12,live?'#54d7e8':'#667680');
 let step=live&&(Math.floor(t/180+i)%2)?2:-2;rect(-7,15,5,8,'#3a4b54');rect(2+step,15,5,8,'#3a4b54');ctx.restore();
 tx(a.id,x,y+31,11,'#dbe5e8','center',true);tx((a.job||a.state).slice(0,18),x,y+44,9,'#60717b','center');
 if(live&&pulse>.7){ctx.strokeStyle='rgba(84,215,232,.7)';ctx.strokeRect(x-24,y-36,48,52)}
}
function draw(){
 const W=cv.width,H=cv.height;t+=16;background(W,H);
 Object.entries(rooms).forEach(([k,r])=>room(k,r,W,H));
 corridor([.32,.29,.055,.025],null,W,H);corridor([.625,.29,.055,.025],null,W,H);
 corridor([.43,.43,.025,.15],null,W,H);corridor([.74,.43,.025,.15],null,W,H);corridor([.47,.70,.055,.025],null,W,H);
 // command console
 rect(28,24,360,66,'#071017','#304750');tx('COMMAND / FACTORY LINK',45,50,15,'#54d7e8','left',true);tx('CEO ALI',45,73,12,'#e4b85d');tx('STATE: '+(data.workers.length?'LIVE TELEMETRY':'WAITING FOR TELEMETRY'),375,73,10,data.workers.length?'#72e2a0':'#60717b','right');
 Object.entries(rooms).forEach(([k,r])=>{});
 data.workers.forEach((a,i)=>agent(a,i,W,H));
 rect(W-330,24,302,66,'#071017','#304750');tx('AUTHORITY',W-313,50,12,'#60717b');tx('PRODUCTION LOCKED',W-313,72,16,'#e4b85d','left',true);tx('BUY/SELL 0',W-42,72,12,'#72e2a0','right',true);
 requestAnimationFrame(draw)
}
async function poll(){
 try{const r=await fetch('/api/world',{cache:'no-store'});data=await r.json();renderHud()}catch(e){document.getElementById('link').textContent='TELEMETRY LINK · OFFLINE'}
 setTimeout(poll,1000)
}
function renderHud(){
 document.getElementById('count').textContent=data.workers.length+' WORKERS';
 document.getElementById('link').textContent=data.workers.length?'TELEMETRY LINK · LIVE':'FACTORY WAITING FOR TELEMETRY';
 document.getElementById('workers').innerHTML=data.workers.slice(0,5).map(w=>'<div class="chip"><b>'+esc(w.id)+' · '+esc(w.state)+'</b><span>'+esc(w.station.toUpperCase())+' · '+Math.round(w.progress)+'%</span></div>').join('');
}
function esc(s){return String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}
draw();poll();
</script>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/world":
            body=json.dumps(read_world(),ensure_ascii=False).encode()
            self.send_response(200);self.send_header("Content-Type","application/json");self.send_header("Cache-Control","no-store");self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body);return
        body=PAGE.encode()
        self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.send_header("Cache-Control","no-store");self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
    def log_message(self,*args): return


if __name__ == "__main__":
    print(f"SP2L Research Station World: http://127.0.0.1:{PORT}/")
    print(f"Telemetry: {STATUS}")
    ThreadingHTTPServer(("127.0.0.1",PORT),Handler).serve_forever()
