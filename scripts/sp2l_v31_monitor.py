"""SP2L V3.1 XAUUSD forward-test monitoring dashboard.

Read-only operator UI for the V3 RR2/Trail3 forward session.
It reads the V3.1 state/event files and probes MT5 without sending orders.
Binds to localhost only. It never changes strategy state or execution.

Usage:
    python scripts/sp2l_v31_monitor.py
    SP2L_DASHBOARD_PORT=8790 python scripts/sp2l_v31_monitor.py
"""
from __future__ import annotations
import html
import json
import os
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from flask import Flask, Response, jsonify

try:
    import MetaTrader5 as mt5
except Exception:
    mt5 = None

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / "runtime" / "sp2l_v3_xauusd_rr2_trail3_forward_state.json"
EVENTS = ROOT / "artifacts" / "forward-test" / "SP2L_V3_XAUUSD_RR2_TRAIL3_FORWARD_EVENTS.jsonl"
PORT = int(os.getenv("SP2L_DASHBOARD_PORT", "8790"))
REFRESH = 3
MT5_PATH = os.getenv("MT5_PATH", r"C:\Program Files\Otet Group MT5 Terminal\terminal64.exe")
IRAN_TZ = timezone(timedelta(hours=3, minutes=30))

app = Flask(__name__)

def read_state():
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def read_events(limit=200):
    out=[]
    try:
        with EVENTS.open("r", encoding="utf-8") as f:
            for line in f:
                try: out.append(json.loads(line))
                except Exception: pass
    except OSError:
        pass
    return out[-limit:]

def fmt_ts(value):
    if not value: return "—"
    s=str(value)
    return s.replace("T"," ")[:19] + " UTC"

def mt5_probe():
    result={"connected":False,"trade_allowed":False,"account":None,"tick":None,
            "orders":[],"positions":[],"error":None}
    if mt5 is None:
        result["error"]="MetaTrader5 package unavailable"; return result
    try:
        ok=mt5.initialize(path=MT5_PATH)
        if not ok:
            result["error"]=str(mt5.last_error()); return result
        term=mt5.terminal_info()
        acc=mt5.account_info()
        tick=mt5.symbol_info_tick("XAUUSD.ecn")
        result["connected"]=bool(term and term.connected)
        result["trade_allowed"]=bool(term and getattr(term,"trade_allowed",False))
        if acc:
            result["account"]={"login":acc.login,"server":acc.server,
                               "trade_mode":acc.trade_mode,
                               "balance":float(acc.balance),"equity":float(acc.equity)}
        if tick:
            result["tick"]={"bid":float(tick.bid),"ask":float(tick.ask)}
        for o in (mt5.orders_get(symbol="XAUUSD.ecn") or []):
            result["orders"].append({"ticket":int(o.ticket),"type":int(o.type),
                "price":float(getattr(o,"price_open",0) or 0),
                "sl":float(getattr(o,"sl",0) or 0),"tp":float(getattr(o,"tp",0) or 0),
                "volume":float(getattr(o,"volume_current",0) or 0)})
        for p in (mt5.positions_get(symbol="XAUUSD.ecn") or []):
            result["positions"].append({"ticket":int(p.ticket),"type":int(p.type),
                "volume":float(p.volume),"open":float(p.price_open),
                "current":float(p.price_current),"sl":float(p.sl or 0),
                "tp":float(p.tp or 0),"profit":float(p.profit)})
    except Exception as e:
        result["error"]=str(e)
    finally:
        try: mt5.shutdown()
        except Exception: pass
    return result

def stats(events):
    stats={"signals":0,"orders":0,"fills":0,"closed":0,"wins":0,"losses":0,
           "net":0.0,"trail_updates":0}
    for e in events:
        k=e.get("event")
        if k=="TELEGRAM_SIGNAL": stats["signals"]+=1
        elif k=="ORDER_RESULT":
            stats["orders"]+=1
            if (e.get("result") or {}).get("ok"): stats["fills"]+=1
        elif k=="TELEGRAM_DEAL_LIFECYCLE":
            stats["closed"]+=1
            net=float(e.get("net",0) or 0); stats["net"]+=net
            if net>0: stats["wins"]+=1
            elif net<0: stats["losses"]+=1
        elif k=="TRAIL_UPDATE" and e.get("success"): stats["trail_updates"]+=1
    decisive=stats["wins"]+stats["losses"]
    stats["win_rate"]=(100*stats["wins"]/decisive) if decisive else None
    return stats

def esc(x): return html.escape(str(x))

def render():
    state=read_state(); events=read_events()
    probe=mt5_probe(); s=stats(events)
    try:
        age=time.time()-STATE_FILE.stat().st_mtime
        heartbeat=f'<span class="ok">ALIVE · {age:.0f}s ago</span>' if age<15 else f'<span class="bad">STALE · {age:.0f}s ago</span>'
        state_time=datetime.fromtimestamp(STATE_FILE.stat().st_mtime, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except OSError:
        age=9999; heartbeat='<span class="bad">NO STATE FILE</span>'; state_time="—"
    acc=probe["account"] or {}
    tick=probe["tick"] or {}
    orders=probe["orders"]; positions=probe["positions"]
    cards=[
      ("Signals",s["signals"]),("Orders",len(orders)),("Positions",len(positions)),
      ("Closed deals",s["closed"]),("Wins",s["wins"]),("Losses",s["losses"]),
      ("Win rate",f'{s["win_rate"]:.2f}%' if s["win_rate"] is not None else "—"),
      ("Net USD",f'{s["net"]:+.2f}'),("Trail updates",s["trail_updates"])
    ]
    card_html="".join(f'<div class="card"><div class="label">{esc(k)}</div><div class="value">{esc(v)}</div></div>' for k,v in cards)
    order_rows="".join(f'<tr><td>{o["ticket"]}</td><td>{o["type"]}</td><td>{o["volume"]:.2f}</td><td>{o["price"]:.2f}</td><td>{o["sl"]:.2f}</td><td>{o["tp"]:.2f}</td></tr>' for o in orders) or '<tr><td colspan="6" class="dim">No XAUUSD.ecn pending orders</td></tr>'
    pos_rows="".join(f'<tr><td>{p["ticket"]}</td><td>{p["type"]}</td><td>{p["volume"]:.2f}</td><td>{p["open"]:.2f}</td><td>{p["current"]:.2f}</td><td>{p["sl"]:.2f}</td><td>{p["tp"]:.2f}</td><td>{p["profit"]:+.2f}</td></tr>' for p in positions) or '<tr><td colspan="8" class="dim">No open XAUUSD.ecn positions</td></tr>'
    ev_rows=""
    for e in reversed(events[-40:]):
        k=e.get("event","?")
        detail=e.get("detail") or e.get("outcome") or e.get("comment") or ""
        if k=="TRAIL_UPDATE": detail=f'position={e.get("position")} SL {e.get("old_sl")} → {e.get("new_sl")}'
        if k=="ORDER_RESULT": detail=f'ok={e.get("result",{}).get("ok")} retcode={e.get("result",{}).get("retcode")}'
        ev_rows += f'<tr><td>{esc(fmt_ts(e.get("ts_utc")))}</td><td>{esc(k)}</td><td>{esc(e.get("symbol",""))}</td><td>{esc(detail)}</td></tr>'
    if not ev_rows: ev_rows='<tr><td colspan="4" class="dim">No events yet</td></tr>'
    html_page=f"""<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="{REFRESH}">
<title>SP2L V3.1 Monitor</title><style>
body{{margin:18px;background:#0d1117;color:#d7dee8;font:14px Consolas,monospace}}
h1{{color:#8bd5ca;margin-bottom:4px}} h2{{color:#7aa2f7;font-size:15px;margin-top:20px}}
.grid{{display:grid;grid-template-columns:repeat(5,minmax(130px,1fr));gap:8px}}
.card{{background:#161b22;border:1px solid #30363d;padding:10px;border-radius:6px}}
.label{{color:#8b949e;font-size:11px}} .value{{font-size:20px;margin-top:5px}}
table{{width:100%;border-collapse:collapse;margin-top:6px}}th,td{{border:1px solid #30363d;padding:5px;text-align:left}}th{{color:#8bd5ca;background:#161b22}}
.ok{{color:#a8e6a3}} .bad{{color:#ff7b72}} .warn{{color:#e3b341}} .dim{{color:#8b949e}}
.badge{{display:inline-block;padding:4px 8px;border:1px solid #30363d;border-radius:5px;margin-right:6px}}
</style></head><body>
<h1>SP2L V3.1 — XAUUSD Forward Monitor</h1>
<div class="dim">RR2 · Trail3 · 0.30 XAU price · research-only · read-only · auto-refresh {REFRESH}s</div>
<h2>Session health</h2><p><span class="badge">{heartbeat}</span>
<span class="badge">state: {esc(state_time)}</span>
<span class="badge">MT5: <span class="{'ok' if probe['connected'] else 'bad'}">{'CONNECTED' if probe['connected'] else 'OFFLINE'}</span></span>
<span class="badge">Trade API: <span class="{'ok' if probe['trade_allowed'] else 'warn'}">{probe['trade_allowed']}</span></span></p>
<div class="grid">{card_html}</div>
<h2>Configuration</h2><table><tr><th>Symbol</th><th>P-Gap</th><th>Spike</th><th>Max SL</th><th>RR</th><th>Trail</th><th>Volume</th><th>Mode</th></tr>
<tr><td>XAUUSD.ecn</td><td>1.0</td><td>1.5x</td><td>10.0</td><td>2.0R</td><td>3 = 0.30</td><td>0.01</td><td>LIVE EXECUTION / canonical=false</td></tr></table>
<h2>MT5</h2><table><tr><th>Account</th><th>Server</th><th>Balance</th><th>Equity</th><th>Bid</th><th>Ask</th></tr>
<tr><td>{esc(acc.get("login","—"))}</td><td>{esc(acc.get("server","—"))}</td><td>{acc.get("balance","—")}</td><td>{acc.get("equity","—")}</td><td>{tick.get("bid","—")}</td><td>{tick.get("ask","—")}</td></tr></table>
<h2>Pending orders</h2><table><tr><th>Ticket</th><th>Type</th><th>Volume</th><th>Price</th><th>SL</th><th>TP</th></tr>{order_rows}</table>
<h2>Open positions</h2><table><tr><th>Ticket</th><th>Type</th><th>Volume</th><th>Open</th><th>Current</th><th>SL</th><th>TP</th><th>Profit</th></tr>{pos_rows}</table>
<h2>Last 40 events</h2><table><tr><th>UTC</th><th>Event</th><th>Symbol</th><th>Detail</th></tr>{ev_rows}</table>
<p class="dim">Dashboard only reads state/events and probes MT5. It never calls order_send and never writes strategy state.</p>
</body></html>"""
    return html_page

@app.get("/")
def index(): return Response(render(), mimetype="text/html")

@app.get("/api/status")
def api_status():
    events=read_events()
    return jsonify({"state":read_state(),"stats":stats(events),"mt5":mt5_probe(),
                    "state_mtime":STATE_FILE.stat().st_mtime if STATE_FILE.exists() else None})

def main():
    app.run(host="127.0.0.1",port=PORT,debug=False,use_reloader=False)

if __name__=="__main__": main()
