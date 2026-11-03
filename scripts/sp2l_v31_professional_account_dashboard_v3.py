r"""Isolated, read-only MT5 account observer and professional SP2L dashboard.

Safety contract:
- Requires a dedicated MT5 terminal executable path (portable copy).
- Refuses the known Forward Runner terminal path.
- Never imports or calls the Runner.
- Uses account_info, positions_get, orders_get, history_deals_get only.
- Binds Flask to localhost; no order/trade API is imported or called.
- MT5 is initialized and shut down only in this independent observer process.

Configure:
  SP2L_OBSERVER_TERMINAL_PATH=D:\MT5-Observer\terminal64.exe
  SP2L_RUNNER_TERMINAL_PATH=C:\Program Files\Otet Group MT5 Terminal\terminal64.exe
  SP2L_OBSERVER_PORT=8793
"""
from __future__ import annotations

import html
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Flask, Response, jsonify

APP = Flask(__name__)
VERSION = "SP2L PROFESSIONAL ACCOUNT DASHBOARD V3"
PORT = int(os.getenv("SP2L_OBSERVER_PORT", "8793"))
REFRESH_SECONDS = 10
HISTORY_DAYS = 90
MIN_TRADES_FOR_CURVE = 6
TEHRAN = timezone(timedelta(hours=3, minutes=30), name="Asia/Tehran")
DEFAULT_RUNNER_TERMINAL = r"C:\Program Files\Otet Group MT5 Terminal\terminal64.exe"


def _normal_path(value: str) -> str:
    return os.path.normcase(os.path.abspath(os.path.expandvars(os.path.expanduser(value))))


def validate_terminal_paths(observer_path: str | None, runner_path: str | None = None) -> str:
    """Fail closed unless observer uses a distinct, explicitly configured terminal binary."""
    if not observer_path:
        raise RuntimeError("SP2L_OBSERVER_TERMINAL_PATH is required; use a dedicated MT5 portable copy.")
    candidate = Path(observer_path).expanduser()
    if not candidate.is_file():
        raise RuntimeError(f"Observer terminal executable does not exist: {candidate}")
    runner = runner_path or os.getenv("SP2L_RUNNER_TERMINAL_PATH", DEFAULT_RUNNER_TERMINAL)
    if _normal_path(str(candidate)) == _normal_path(runner):
        raise RuntimeError("Observer terminal path matches the Forward Runner terminal; refusing shared connection.")
    return str(candidate.resolve())


def _number(value, default=0.0) -> float:
    try:
        result = float(value)
        return result if result == result and abs(result) != float("inf") else default
    except (TypeError, ValueError):
        return default


def _money(value, currency="") -> str:
    return f'{_number(value):,.2f} {currency}'.strip()


def _deal_value(deal) -> float:
    return sum(_number(getattr(deal, field, 0)) for field in ("profit", "commission", "swap", "fee"))


def build_closed_trades(deals, symbol: str) -> list[dict]:
    """Aggregate all symbol deals by position; keep only positions with an exit deal."""
    grouped = defaultdict(list)
    for deal in deals or ():
        if str(getattr(deal, "symbol", "") or "") != symbol:
            continue
        position_id = int(getattr(deal, "position_id", 0) or 0)
        if position_id <= 0:
            continue
        grouped[position_id].append(deal)
    rows = []
    for position_id, items in grouped.items():
        exits = [d for d in items if int(getattr(d, "entry", -1)) in (1, 3)]
        if not exits:
            continue
        close_deal = max(exits, key=lambda d: (int(getattr(d, "time", 0)), int(getattr(d, "ticket", 0))))
        rows.append({
            "position_id": position_id,
            "close_time": int(getattr(close_deal, "time", 0) or 0),
            "net": round(sum(_deal_value(d) for d in items), 8),
            "deals": len(items),
            "symbol": symbol,
        })
    return sorted(rows, key=lambda row: (row["close_time"], row["position_id"]))


def performance(trades: list[dict]) -> dict:
    curve, running, peak, max_dd = [], 0.0, 0.0, 0.0
    wins = losses = breakeven = 0
    gross_profit = gross_loss = 0.0
    for trade in trades:
        net = _number(trade.get("net"))
        running += net
        peak = max(peak, running)
        max_dd = max(max_dd, peak - running)
        curve.append({"time": trade.get("close_time"), "cumulative_net": round(running, 2)})
        if net > 0:
            wins += 1
            gross_profit += net
        elif net < 0:
            losses += 1
            gross_loss += abs(net)
        else:
            breakeven += 1
    count = len(trades)
    return {
        "closed_trades": count, "wins": wins, "losses": losses, "breakeven": breakeven,
        "win_rate": round(100 * wins / count, 2) if count else None,
        "net": round(running, 2), "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "profit_factor": round(gross_profit / gross_loss, 4) if gross_loss else (None if not gross_profit else "infinity"),
        "max_drawdown_currency": round(max_dd, 2), "curve": curve,
        "curve_ready": count >= MIN_TRADES_FOR_CURVE,
    }


def _safe_call(fn, **kwargs):
    if not callable(fn):
        raise RuntimeError("Required MT5 read function is unavailable")
    value = fn(**kwargs)
    if value is None:
        raise RuntimeError("MT5 read returned None; see terminal last_error")
    return value


class MT5Observer:
    def __init__(self, mt5_module=None):
        self.mt5 = mt5_module
        self.connected = False
        self.last_error = None
        self.last_success = None
        self.cache = {}

    def connect(self):
        terminal = validate_terminal_paths(
            os.getenv("SP2L_OBSERVER_TERMINAL_PATH"),
            os.getenv("SP2L_RUNNER_TERMINAL_PATH", DEFAULT_RUNNER_TERMINAL),
        )
        if self.mt5 is None:
            import MetaTrader5 as mt5
            self.mt5 = mt5
        ok = self.mt5.initialize(path=terminal, portable=True, timeout=10000)
        if not ok:
            self.last_error = f"initialize failed: {self.mt5.last_error()}"
            raise RuntimeError(self.last_error)
        self.connected = True

    def close(self):
        if self.connected:
            self.mt5.shutdown()
            self.connected = False

    def snapshot(self, symbol="XAUUSD.ecn"):
        try:
            if not self.connected:
                self.connect()
            account = _safe_call(self.mt5.account_info)
            positions = _safe_call(self.mt5.positions_get, symbol=symbol)
            orders = _safe_call(self.mt5.orders_get, symbol=symbol)
            now = datetime.now(timezone.utc)
            start = now - timedelta(days=HISTORY_DAYS)
            history = _safe_call(
                self.mt5.history_deals_get,
                date_from=start.replace(tzinfo=None),
                date_to=now.replace(tzinfo=None),
                group=f"*{symbol}*",
            )
            trades = build_closed_trades(history, symbol)
            stats = performance(trades)
            today = datetime.now(TEHRAN).date()
            today_trades = [
                t for t in trades
                if datetime.fromtimestamp(t["close_time"], timezone.utc).astimezone(TEHRAN).date() == today
            ]
            today_stats = performance(today_trades)
            self.cache = {
                "ok": True, "observed_at_utc": now.isoformat(),
                "account": {
                    "login": int(getattr(account, "login", 0) or 0),
                    "server": str(getattr(account, "server", "") or ""),
                    "currency": str(getattr(account, "currency", "") or ""),
                    "balance": _number(getattr(account, "balance", 0)),
                    "equity": _number(getattr(account, "equity", 0)),
                    "profit": _number(getattr(account, "profit", 0)),
                    "margin": _number(getattr(account, "margin", 0)),
                    "free_margin": _number(getattr(account, "margin_free", 0)),
                    "leverage": int(getattr(account, "leverage", 0) or 0),
                },
                "positions": [{
                    "ticket": int(getattr(p, "ticket", 0) or 0),
                    "type": int(getattr(p, "type", -1)),
                    "volume": _number(getattr(p, "volume", 0)),
                    "price_open": _number(getattr(p, "price_open", 0)),
                    "price_current": _number(getattr(p, "price_current", 0)),
                    "sl": _number(getattr(p, "sl", 0)),
                    "tp": _number(getattr(p, "tp", 0)),
                    "profit": _number(getattr(p, "profit", 0)),
                    "swap": _number(getattr(p, "swap", 0)),
                    "magic": int(getattr(p, "magic", 0) or 0),
                } for p in positions],
                "orders": [{
                    "ticket": int(getattr(o, "ticket", 0) or 0),
                    "type": int(getattr(o, "type", -1)),
                    "volume": _number(getattr(o, "volume_current", 0)),
                    "price": _number(getattr(o, "price_open", 0)),
                    "sl": _number(getattr(o, "sl", 0)),
                    "tp": _number(getattr(o, "tp", 0)),
                } for o in orders],
                "performance": stats, "today": today_stats,
                "history_days": HISTORY_DAYS, "symbol": symbol,
                "source": "MT5 read-only account/history API",
            }
            self.last_error = None
            self.last_success = now.isoformat()
            return self.cache
        except Exception as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            if self.cache:
                return {**self.cache, "ok": False, "stale": True, "error": self.last_error}
            return {"ok": False, "stale": False, "error": self.last_error,
                    "account": {}, "positions": [], "orders": [],
                    "performance": performance([]), "today": performance([]),
                    "symbol": symbol, "source": "unavailable"}


observer = MT5Observer()
_LAST_SNAPSHOT = {}
_LAST_POLL = 0.0


def get_snapshot(force=False):
    global _LAST_SNAPSHOT, _LAST_POLL
    if force or time.monotonic() - _LAST_POLL >= REFRESH_SECONDS:
        _LAST_SNAPSHOT = observer.snapshot()
        _LAST_POLL = time.monotonic()
    return _LAST_SNAPSHOT


def _e(value):
    return html.escape(str(value if value is not None else "—"))


def _curve_svg(stats):
    points = stats.get("curve") or []
    if not stats.get("curve_ready"):
        return '<div class="empty"><b>Performance curve unlocks after 6 closed trades</b><span>Current sample: ' + str(stats.get("closed_trades", 0)) + ' / 6</span></div>'
    values = [float(p["cumulative_net"]) for p in points]
    lo, hi = min([0.0] + values), max([0.0] + values)
    span = max(hi - lo, 1.0)
    coords = []
    for i, value in enumerate(values):
        x = 24 + (i * 752 / max(len(values) - 1, 1))
        y = 154 - ((value - lo) / span * 128)
        coords.append(f"{x:.1f},{y:.1f}")
    zero_y = 154 - ((0 - lo) / span * 128)
    return (f'<svg viewBox="0 0 800 180" role="img" aria-label="Cumulative realized net performance">'
            f'<line x1="24" y1="{zero_y:.1f}" x2="776" y2="{zero_y:.1f}" stroke="#40516a" stroke-dasharray="4 5"/>'
            f'<polyline points="{" ".join(coords)}" fill="none" stroke="#67e8c1" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{coords[-1].split(",")[0]}" cy="{coords[-1].split(",")[1]}" r="4" fill="#67e8c1"/></svg>')


def _render():
    data = get_snapshot()
    account = data.get("account") or {}
    stats = data.get("performance") or performance([])
    today = data.get("today") or performance([])
    currency = account.get("currency", "")
    status = "CONNECTED" if data.get("ok") else "STALE DATA" if data.get("stale") else "OBSERVER OFFLINE"
    status_class = "good" if data.get("ok") else "warn"
    chart = _curve_svg(stats)
    positions = "".join(
        f'<tr><td>{p["ticket"]}</td><td>{"BUY" if p["type"] == 0 else "SELL" if p["type"] == 1 else p["type"]}</td>'
        f'<td>{p["volume"]:.2f}</td><td>{p["price_open"]:.2f}</td><td>{p["price_current"]:.2f}</td>'
        f'<td class="{"pos" if p["profit"] >= 0 else "neg"}">{p["profit"]:+.2f}</td></tr>'
        for p in data.get("positions", [])
    ) or '<tr><td colspan="6" class="dim">No open positions</td></tr>'
    orders = "".join(
        f'<tr><td>{o["ticket"]}</td><td>{o["type"]}</td><td>{o["volume"]:.2f}</td><td>{o["price"]:.2f}</td><td>{o["sl"]:.2f}</td><td>{o["tp"]:.2f}</td></tr>'
        for o in data.get("orders", [])
    ) or '<tr><td colspan="6" class="dim">No pending orders</td></tr>'
    winrate = "—" if stats.get("win_rate") is None else f'{stats["win_rate"]:.1f}%'
    pf = "—" if stats.get("profit_factor") is None else str(stats["profit_factor"])
    error = f'<div class="notice">{_e(data.get("error"))}</div>' if data.get("error") else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="{REFRESH_SECONDS}"><title>{VERSION}</title>
<style>
:root{{--bg:#080f1d;--panel:#111d30;--panel2:#0c1728;--line:#263952;--text:#edf4ff;--muted:#91a5bf;--mint:#67e8c1;--blue:#8dbdff;--red:#ff8294;--amber:#f7c76a}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(ellipse at 15% -10%,#193454 0,transparent 42%),var(--bg);color:var(--text);font:14px Inter,Segoe UI,Arial,sans-serif}}
main{{max-width:1480px;margin:auto;padding:26px}}.head{{display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:22px}}
.brand{{display:flex;gap:13px;align-items:center}}.logo{{width:46px;height:46px;border-radius:14px;background:linear-gradient(140deg,#1f987d,#2463a4);display:grid;place-items:center;font-weight:900;font-size:18px;box-shadow:0 8px 26px #0b786b55}}
h1{{font-size:23px;margin:0;letter-spacing:.2px}}.sub{{color:var(--muted);margin-top:5px;font-size:12px}}.status{{border:1px solid var(--line);border-radius:30px;padding:9px 14px;font-weight:800;letter-spacing:.7px}}.good{{color:var(--mint)}}.warn{{color:var(--amber)}}.pos{{color:var(--mint)}}.neg{{color:var(--red)}}
.grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px}}.card{{background:linear-gradient(150deg,#15243a,#101a2b);border:1px solid var(--line);border-radius:16px;padding:17px;box-shadow:0 10px 28px #0002;min-width:0}}
.label{{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:1px}}.value{{font-size:25px;font-weight:750;margin-top:9px;letter-spacing:-.5px;overflow-wrap:anywhere}}.hint{{color:var(--muted);font-size:11px;margin-top:5px}}
.section{{background:var(--panel);border:1px solid var(--line);border-radius:17px;padding:19px;margin-top:16px;box-shadow:0 12px 32px #0002}}.sectionhead{{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:13px}}h2{{font-size:15px;margin:0}}.tag{{font-size:10px;color:var(--blue);border:1px solid #345477;border-radius:20px;padding:5px 9px}}
.chart{{background:linear-gradient(180deg,#0d1b2d,#0b1524);border:1px solid #20344d;border-radius:13px;padding:12px;min-height:210px}}svg{{width:100%;height:180px;display:block}}.empty{{height:180px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:8px;color:var(--muted)}}.empty b{{color:var(--text);font-size:14px}}.empty span{{font-size:12px}}
.stats{{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-top:13px}}.mini{{background:var(--panel2);border:1px solid var(--line);border-radius:11px;padding:12px}}.mini span{{display:block;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.7px}}.mini b{{display:block;font-size:17px;margin-top:6px}}
table{{width:100%;border-collapse:collapse;font-size:12px}}th,td{{padding:12px 10px;text-align:left;border-bottom:1px solid #24364d}}th{{color:var(--muted);font-weight:600;text-transform:uppercase;font-size:10px;letter-spacing:.7px}}.dim{{color:var(--muted)}}.notice{{padding:12px;border:1px solid #705b30;background:#332b1b;border-radius:10px;color:#ffda91;margin-top:14px;overflow-wrap:anywhere}}
.footer{{color:#71859e;font-size:11px;margin:18px 3px 4px;line-height:1.6}}
@media(max-width:900px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}.stats{{grid-template-columns:repeat(3,minmax(0,1fr))}}}}
@media(max-width:560px){{main{{padding:13px}}.grid{{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}}.card{{padding:12px}}.value{{font-size:19px}}.section{{padding:13px}}.stats{{grid-template-columns:repeat(2,minmax(0,1fr))}}table{{font-size:11px}}th,td{{padding:9px 6px}}}}
</style></head><body><main>
<header class="head"><div class="brand"><div class="logo">S2</div><div><h1>SP2L · Account Cockpit</h1><div class="sub">XAUUSD.ecn · Professional Dashboard V3 · live read-only observer</div></div></div><div class="status {status_class}">{status}</div></header>
<div class="grid">
<div class="card"><div class="label">Balance</div><div class="value">{_e(_money(account.get("balance"), currency))}</div><div class="hint">Broker account balance</div></div>
<div class="card"><div class="label">Equity</div><div class="value">{_e(_money(account.get("equity"), currency))}</div><div class="hint">Balance + floating P&amp;L</div></div>
<div class="card"><div class="label">Floating P&amp;L</div><div class="value {'pos' if _number(account.get('profit')) >= 0 else 'neg'}">{_e(_money(account.get("profit"), currency))}</div><div class="hint">Current open positions</div></div>
<div class="card"><div class="label">Free Margin</div><div class="value">{_e(_money(account.get("free_margin"), currency))}</div><div class="hint">Available margin</div></div>
</div>
<section class="section"><div class="sectionhead"><h2>Realized performance · last {HISTORY_DAYS} days</h2><span class="tag">{stats.get("closed_trades",0)} CLOSED TRADES</span></div>
<div class="chart">{chart}</div>
<div class="stats">
<div class="mini"><span>Net P&amp;L</span><b class="{'pos' if stats.get('net',0)>=0 else 'neg'}">{_e(_money(stats.get("net"),currency))}</b></div>
<div class="mini"><span>Win rate</span><b>{winrate}</b></div>
<div class="mini"><span>Profit factor</span><b>{_e(pf)}</b></div>
<div class="mini"><span>Max drawdown</span><b class="neg">{_e(_money(stats.get("max_drawdown_currency"),currency))}</b></div>
<div class="mini"><span>W / L / BE</span><b>{stats.get("wins",0)} / {stats.get("losses",0)} / {stats.get("breakeven",0)}</b></div>
</div><div class="hint">Curve is cumulative realized net by closed position (profit + commission + swap + fee), not a tick-by-tick broker equity curve. Sample is grouped by position ID.</div></section>
<section class="section"><div class="sectionhead"><h2>Today's performance</h2><span class="tag">TEHRAN DAY</span></div>
<div class="grid">
<div class="card"><div class="label">Closed trades</div><div class="value">{today.get("closed_trades",0)}</div></div>
<div class="card"><div class="label">Today's net</div><div class="value {'pos' if today.get('net',0)>=0 else 'neg'}">{_e(_money(today.get("net"),currency))}</div></div>
<div class="card"><div class="label">Win / Loss / BE</div><div class="value">{today.get("wins",0)} / {today.get("losses",0)} / {today.get("breakeven",0)}</div></div>
<div class="card"><div class="label">Today's win rate</div><div class="value">{'—' if today.get("win_rate") is None else str(today.get("win_rate"))+'%'}</div></div>
</div></section>
<section class="section"><div class="sectionhead"><h2>Open positions</h2><span class="tag">{len(data.get("positions",[]))} LIVE</span></div>
<div style="overflow-x:auto"><table><thead><tr><th>Ticket</th><th>Side</th><th>Lots</th><th>Entry</th><th>Current</th><th>Floating P&amp;L</th></tr></thead><tbody>{positions}</tbody></table></div></section>
<section class="section"><div class="sectionhead"><h2>Pending orders</h2><span class="tag">{len(data.get("orders",[]))} LIVE</span></div>
<div style="overflow-x:auto"><table><thead><tr><th>Ticket</th><th>Type</th><th>Volume</th><th>Entry</th><th>SL</th><th>TP</th></tr></thead><tbody>{orders}</tbody></table></div></section>
{error}
<div class="footer">Account: {_e(account.get("login","—"))} · {_e(account.get("server","—"))} · {_e(currency)} · leverage 1:{account.get("leverage","—")}<br>
Last observer read: {_e(data.get("observed_at_utc","not available"))} · Refresh {REFRESH_SECONDS}s · History {HISTORY_DAYS} days<br>
Independent terminal process in portable mode. Read-only API surface only. No Runner import, no trading requests, no Runner files modified.</div>
</main></body></html>"""


@APP.get("/")
def index():
    return Response(_render(), mimetype="text/html")


@APP.get("/api/status")
def api_status():
    return jsonify(get_snapshot())


def main():
    # Fail before opening the web server if isolation cannot be established.
    validate_terminal_paths(
        os.getenv("SP2L_OBSERVER_TERMINAL_PATH"),
        os.getenv("SP2L_RUNNER_TERMINAL_PATH", DEFAULT_RUNNER_TERMINAL),
    )
    print(f"{VERSION}: http://127.0.0.1:{PORT} (read-only observer)", flush=True)
    try:
        APP.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False, threaded=True)
    finally:
        observer.close()


if __name__ == "__main__":
    main()
