#!/usr/bin/env python
"""Read-only, isolated Strategy B forward-test dashboard.

Binds only to 127.0.0.1:8791. This module has no order-send/modify/cancel code.
"""
from __future__ import annotations

import html
import json
import os
import subprocess
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "runtime"
HOST = "127.0.0.1"
PORT = 8791
SYMBOL = os.environ.get("STRATEGY_B_SYMBOL", "XAUUSD.ecn")
TERMINAL = os.environ.get(
    "STRATEGY_B_MT5_TERMINAL_PATH",
    r"C:\Program Files\Otet Group MT5 Terminal\terminal64.exe",
)
MAGICS = {8, 9}
LOG_PATTERN = "strategy_b_*.log"
STARTED_AT = datetime.now().astimezone().isoformat(timespec="seconds")

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Strategy B | Read-only Monitor</title>
<style>
:root{color-scheme:dark;font-family:Inter,Segoe UI,Arial,sans-serif;background:#0b1220;color:#e7edf7}
body{margin:0;padding:20px;max-width:1200px;margin:auto}.top{display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap}
h1{font-size:24px;margin:0}.muted{color:#91a1ba}.pill{border:1px solid #34435d;border-radius:999px;padding:6px 10px;font-size:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:18px 0}
.card{background:#121d30;border:1px solid #263650;border-radius:14px;padding:16px;min-width:0}
.label{font-size:12px;color:#91a1ba;text-transform:uppercase;letter-spacing:.08em}.value{font-size:24px;font-weight:650;margin-top:8px;overflow-wrap:anywhere}
h2{font-size:16px;margin:0 0 12px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;line-height:1.55;max-height:430px;overflow:auto;margin:0;color:#c9d5e8}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:9px 7px;border-bottom:1px solid #263650;overflow-wrap:anywhere}th{color:#91a1ba}
.good{color:#72e0ad}.bad{color:#ff9292}.warn{color:#ffd37a}.section{margin:12px 0}.footer{font-size:12px;color:#91a1ba;margin:18px 0}
@media(max-width:600px){body{padding:12px}.value{font-size:20px}table{font-size:12px}}
</style></head><body>
<div class="top"><div><h1>Strategy B <span class="muted">/ PythonTraderBot</span></h1><div class="muted">Independent forward-test monitor · read-only</div></div><span class="pill">TAILNET ACCESS ONLY · NO TRADE CONTROLS</span></div>
<div class="grid">
<div class="card"><div class="label">Runner process</div><div class="value" id="runner">Loading…</div><div class="muted" id="runnerDetail"></div></div>
<div class="card"><div class="label">MT5 account</div><div class="value" id="account">Loading…</div><div class="muted" id="server"></div></div>
<div class="card"><div class="label">Balance</div><div class="value" id="balance">—</div><div class="muted">Account currency</div></div>
<div class="card"><div class="label">Equity</div><div class="value" id="equity">—</div><div class="muted" id="floating"></div></div>
<div class="card"><div class="label">B positions</div><div class="value" id="positions">—</div><div class="muted">Magic 8 / 9</div></div>
<div class="card"><div class="label">B pending orders</div><div class="value" id="orders">—</div><div class="muted">Magic 8 / 9</div></div>
</div>
<div class="grid">
<div class="card"><h2>Configuration reference</h2><pre id="config">Loading…</pre></div>
<div class="card"><h2>Log freshness</h2><pre id="logs">Loading…</pre></div>
</div>
<div class="card section"><h2>Strategy B positions</h2><div id="positionTable" class="muted">Loading…</div></div>
<div class="card section"><h2>Strategy B pending orders</h2><div id="orderTable" class="muted">Loading…</div></div>
<div class="card section"><h2>Recent runner output</h2><pre id="tail">Loading…</pre></div>
<div class="footer">Auto-refresh: 5 seconds · Started: <span id="started"></span> · Dashboard never submits, changes, or cancels trades.</div>
<script>
document.getElementById('started').textContent = new Date().toLocaleString();
function esc(x){return String(x??'—').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function money(x,cur){return x==null?'—':Number(x).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})+(cur?' '+cur:'');}
function table(rows,cols){if(!rows||!rows.length)return '<div class="muted">None currently detected</div>';return '<div style="overflow:auto"><table><thead><tr>'+cols.map(c=>'<th>'+esc(c[1])+'</th>').join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+cols.map(c=>'<td>'+esc(r[c[0]])+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';}
const apiPath = window.location.pathname.replace(/\/?$/, '/') + 'api';
async function refresh(){try{let r=await fetch(apiPath,{cache:'no-store'});let d=await r.json();
let runner=document.getElementById('runner');runner.textContent=d.runner.running?'RUNNING':'NOT DETECTED';runner.className='value '+(d.runner.running?'good':'bad');
document.getElementById('runnerDetail').textContent=d.runner.pids.length?'PID(s): '+d.runner.pids.join(', '):'No matching runner process';
document.getElementById('account').textContent=d.mt5.ok?(d.mt5.demo?'DEMO':'NON-DEMO'):'UNAVAILABLE';
document.getElementById('account').className='value '+(d.mt5.ok&&d.mt5.demo?'good':'warn');
document.getElementById('server').textContent=d.mt5.ok?d.mt5.server+' · '+d.mt5.login:d.mt5.error||'MT5 data unavailable';
document.getElementById('balance').textContent=d.mt5.ok?money(d.mt5.balance,d.mt5.currency):'—';
document.getElementById('equity').textContent=d.mt5.ok?money(d.mt5.equity,d.mt5.currency):'—';
document.getElementById('floating').textContent=d.mt5.ok?'Equity − balance: '+money(d.mt5.equity-d.mt5.balance,d.mt5.currency):'';
document.getElementById('positions').textContent=d.mt5.ok?d.mt5.positions.length:'—';
document.getElementById('orders').textContent=d.mt5.ok?d.mt5.orders.length:'—';
document.getElementById('config').textContent=JSON.stringify(d.config,null,2);
document.getElementById('logs').textContent=d.logs.map(x=>x.name+'\n  '+x.modified+' · '+x.bytes+' bytes').join('\n\n')||'No matching logs';
document.getElementById('tail').textContent=d.tail.join('\n')||'No stdout log content';
document.getElementById('positionTable').innerHTML=table(d.mt5.positions,[['ticket','Ticket'],['type','Type'],['volume','Lots'],['price_open','Open price'],['sl','SL'],['tp','TP'],['profit','Floating P/L'],['magic','Magic'],['comment','Comment']]);
document.getElementById('orderTable').innerHTML=table(d.mt5.orders,[['ticket','Ticket'],['type','Type'],['volume_initial','Lots'],['price_open','Entry'],['sl','SL'],['tp','TP'],['magic','Magic'],['comment','Comment']]);
}catch(e){document.getElementById('runner').textContent='DASHBOARD API ERROR';document.getElementById('runnerDetail').textContent=String(e)}}
refresh();setInterval(refresh,5000);
</script></body></html>"""


def _stamp(ts: float) -> str:
    return datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")


def _runner_processes() -> list[dict]:
    script_name = "SP2L_Advanced_Bot_Optimized.py"
    ps = (
        "$needle = '" + script_name + "'; "
        "Get-CimInstance Win32_Process | Where-Object { "
        "$_.CommandLine -and $_.CommandLine.Contains($needle) } | "
        "Select-Object ProcessId,ParentProcessId,Name,CreationDate | "
        "ConvertTo-Json -Compress"
    )
    try:
        p = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps],
            capture_output=True, text=True, timeout=5, check=False,
        )
        raw = json.loads(p.stdout.strip() or "[]")
        if isinstance(raw, dict):
            raw = [raw]
        return [
            {"pid": int(x["ProcessId"]), "parent": int(x["ParentProcessId"]),
             "name": x.get("Name", ""), "created": x.get("CreationDate", "")}
            for x in raw
        ]
    except Exception as exc:
        return [{"error": str(exc)}]


def _mt5_snapshot() -> dict:
    result = {"ok": False, "error": "MT5 read-only query not yet available",
              "positions": [], "orders": []}
    try:
        import MetaTrader5 as mt5
    except Exception as exc:
        result["error"] = "MetaTrader5 import failed: " + str(exc)
        return result
    initialized = False
    try:
        if not Path(TERMINAL).is_file():
            result["error"] = "Configured terminal path not found: " + TERMINAL
            return result
        if not mt5.initialize(path=TERMINAL, timeout=5000):
            result["error"] = "MT5 initialize failed: " + repr(mt5.last_error())
            return result
        initialized = True
        ti = mt5.terminal_info()
        ai = mt5.account_info()
        if ti is None or ai is None:
            result["error"] = "MT5 terminal/account info unavailable: " + repr(mt5.last_error())
            return result
        if str(getattr(ai, "server", "")) != os.environ.get("STRATEGY_B_EXPECTED_SERVER", "OtetGroup-MT5"):
            result["error"] = "Server mismatch; refusing to display account details"
            return result
        info = mt5.symbol_info(SYMBOL)
        positions = mt5.positions_get(symbol=SYMBOL)
        orders = mt5.orders_get(symbol=SYMBOL)
        if positions is None or orders is None:
            result["error"] = "MT5 positions/orders query failed: " + repr(mt5.last_error())
            return result
        def pos(p):
            if int(p.magic) not in MAGICS:
                return None
            return {"ticket": int(p.ticket), "type": "BUY" if int(p.type) == 0 else "SELL",
                    "volume": float(p.volume), "price_open": float(p.price_open),
                    "sl": float(p.sl), "tp": float(p.tp), "profit": float(p.profit),
                    "magic": int(p.magic), "comment": str(p.comment)}
        def order(o):
            if int(o.magic) not in MAGICS:
                return None
            return {"ticket": int(o.ticket), "type": str(o.type), "volume_initial": float(o.volume_initial),
                    "price_open": float(o.price_open), "sl": float(o.sl), "tp": float(o.tp),
                    "magic": int(o.magic), "comment": str(o.comment)}
        result = {
            "ok": True, "server": str(ai.server), "login": int(ai.login),
            "demo": int(ai.trade_mode) == int(mt5.ACCOUNT_TRADE_MODE_DEMO),
            "balance": float(ai.balance), "equity": float(ai.equity),
            "currency": str(ai.currency), "symbol": SYMBOL,
            "point": float(info.point) if info else None,
            "positions": [x for p in positions if (x := pos(p)) is not None],
            "orders": [x for o in orders if (x := order(o)) is not None],
        }
    except Exception as exc:
        result["error"] = "MT5 read-only query error: " + str(exc)
    finally:
        if initialized:
            try:
                mt5.shutdown()
            except Exception:
                pass
    return result


def _snapshot() -> dict:
    procs = _runner_processes()
    logfiles = sorted(
        RUNTIME.glob(LOG_PATTERN),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    logs = []
    for p in logfiles[:6]:
        try:
            st = p.stat()
            logs.append({"name": p.name, "bytes": st.st_size, "modified": _stamp(st.st_mtime)})
        except OSError:
            pass
    tail = []
    stdout = next((p for p in logfiles if "stdout" in p.name.lower()), None)
    if stdout:
        try:
            with stdout.open("r", encoding="utf-8", errors="replace") as f:
                tail = f.readlines()[-45:]
            tail = [line.rstrip("\r\n") for line in tail]
        except OSError as exc:
            tail = ["Could not read stdout log: " + str(exc)]
    return {
        "timestamp": _stamp(time.time()),
        "runner": {"running": any("pid" in p for p in procs), "pids": [p["pid"] for p in procs if "pid" in p], "processes": procs},
        "mt5": _mt5_snapshot(),
        "logs": logs, "tail": tail,
        "config": {
            "symbol": SYMBOL, "magic": 8, "second_entry_magic": 9,
            "spike_body_multiplier": 1.5, "p_gap_points": 100,
            "max_sl_distance_points": 1000, "tp_r": 0.9,
            "second_entry_enabled": False, "ema_filter": True, "ema_period": 60,
            "trend_filter": True, "max_opposite_moves": 1,
            "range_filter": False, "adx_period": 14, "min_adx": 20.0,
            "adx_rising_filter": False, "session_filter": False,
            "lot": 0.01, "timeframe": "M1", "config_note": "Reference values from runner source; read-only display.",
        },
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "StrategyBReadOnly/1.0"

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api":
            body = json.dumps(_snapshot(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)

    def log_message(self, fmt, *args):
        print("[strategy-b-dashboard] " + (fmt % args), flush=True)


if __name__ == "__main__":
    RUNTIME.mkdir(parents=True, exist_ok=True)
    print(f"Strategy B read-only dashboard: http://{HOST}:{PORT}", flush=True)
    print("No order submission/modification/cancellation routes exist.", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
