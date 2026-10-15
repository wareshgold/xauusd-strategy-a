"""Read-only live dashboard for the SP2L forward-test session.

Serves one auto-refreshing page (default http://127.0.0.1:8790) so the
operator can SEE the session working without touching logs:

  - V3 state/event freshness, runner PID and read-only process CPU delta
  - execution flags with an explicit source/verification status
  - MT5 account + per-symbol live tick prices
  - today's signals / fills / W-L / net USD (from the event log)
  - today's orders (fills, cancels, expiry outcomes)
  - the last 40 events, newest first

Read-only by construction: it never places orders, never writes journal or
state files, and binds to 127.0.0.1 only. Telegram is never used here.

Usage:
    python scripts/live_dashboard.py                 # foreground, port 8790
    SP2L_DASHBOARD_PORT=9000 python scripts/live_dashboard.py

Run it in a second terminal next to the session (or detached the same way).
"""
from __future__ import annotations

import html
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, Response

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import MetaTrader5 as mt5  # noqa: E402
from mt5_terminal_resolver import find_mt5_terminal  # noqa: E402

from live_mt5_gateway import effective_mode  # noqa: E402  (gateway env truth)


def _runner_mode_from_process() -> tuple[str, str] | None:
    """True session mode: read the live runner's own env from process memory.

    Windows-only best effort (the whole live setup is Windows); returns the
    raw flag values so the dashboard reports what the session actually runs
    with, not what the dashboard process happens to have.
    """
    if os.name != "nt" or not RUNNER_LOCK.exists():
        return None
    try:
        import ctypes

        pid = int(RUNNER_LOCK.read_text(encoding="utf-8").strip() or 0)
        k32 = ctypes.windll.kernel32
        ntdll = ctypes.windll.ntdll
        h = k32.OpenProcess(0x1000 | 0x0010, False, pid)
        if not h:
            return None

        class PBI(ctypes.Structure):
            _fields_ = [(n, ctypes.c_void_p) for n in ("a", "b", "c", "d", "uid", "ppid")]

        pbi = PBI()
        rl = ctypes.c_ulong()
        if ntdll.NtQueryInformationProcess(h, 0, ctypes.byref(pbi), ctypes.sizeof(pbi), ctypes.byref(rl)):
            return None

        def rp(addr):
            v = ctypes.c_ulonglong()
            n = ctypes.c_size_t()
            if k32.ReadProcessMemory(h, ctypes.c_void_p(addr), ctypes.byref(v), 8, ctypes.byref(n)):
                return v.value
            return None

        params = rp((pbi.b or 0) + 0x20)
        envp = rp((params or 0) + 0x80)
        es = ctypes.c_ulonglong()
        n = ctypes.c_size_t()
        k32.ReadProcessMemory(h, ctypes.c_void_p((params or 0) + 0x3F0), ctypes.byref(es), 8, ctypes.byref(n))
        size = min(es.value or 16384, 262144)
        buf = ctypes.create_string_buffer(size)
        if not k32.ReadProcessMemory(h, ctypes.c_void_p(envp), buf, size, ctypes.byref(n)):
            return None
        blob = buf.raw[: n.value].decode("utf-16-le", errors="ignore")
        flags = {}
        for line in blob.split("\x00"):
            for key in ("LIVE_TRADING_ENABLE", "ALLOW_REAL_EXECUTION"):
                if line.startswith(key + "="):
                    flags[key] = line.split("=", 1)[1]
        if not flags:
            return None
        return (
            flags.get("LIVE_TRADING_ENABLE", "false").lower(),
            flags.get("ALLOW_REAL_EXECUTION", "false").lower(),
        )
    except Exception:
        return None

STATE_FILE = ROOT / "runtime" / "sp2l_v3_xauusd_rr2_trail4_forward_state.json"
RUNNER_LOCK = ROOT / "runtime" / "sp2l_multi_symbol_forward_runner.lock"
WATCHDOG_PID = ROOT / "runtime" / "forward_watchdog.pid"
EVENTS = ROOT / "artifacts" / "forward-test" / "SP2L_V3_XAUUSD_RR2_TRAIL4_FORWARD_EVENTS.jsonl"

PORT = int(os.getenv("SP2L_DASHBOARD_PORT", "8790"))
REFRESH_SECONDS = 5
IRAN_TZ = timezone(__import__("datetime").timedelta(hours=3, minutes=30))

app = Flask(__name__)

_PG_UP = """<!doctype html><html><head><meta charset="utf-8">
<title>SP2L Live Dashboard</title><style>
body{font-family:Consolas,monospace;background:#0e1116;color:#d8dee9;margin:16px}
h1{font-size:20px;color:#88c0d0}h2{font-size:15px;color:#81a1c1;margin:18px 0 6px}
table{border-collapse:collapse;font-size:13px;width:100%}
td,th{border:1px solid #2e3440;padding:3px 8px;text-align:left}
th{background:#1b2129;color:#88c0d0}
.ok{color:#a3be8c}.bad{color:#bf616a}.warn{color:#ebcb8b}.dim{color:#7b88a1}
.big{font-size:15px}.nowrap{white-space:pre-wrap}
</style><meta http-equiv="refresh" content="5"></head><body>
<h1>🟢 SP2L Forward Test — Live Dashboard</h1><span class="dim">auto-refresh 5s · research/demo only · read-only</span>"""


def _proc_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        out = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
            capture_output=True, text=True, timeout=5,
        ).stdout
        return "python" in out.lower()
    except Exception:
        return False


def _read_pid(path: Path) -> int:
    try:
        return int(path.read_text(encoding="utf-8").strip() or 0)
    except Exception:
        return 0


def session_status() -> str:
    runner_pid = _read_pid(RUNNER_LOCK)
    watchdog_pid = _read_pid(WATCHDOG_PID)
    try:
        mtime = STATE_FILE.stat().st_mtime
        age = time.time() - mtime
        beat = (
            f'<span class="ok">ALIVE ({age:.0f}s ago)</span>'
            if age < 15
            else f'<span class="bad">STALE ({age:.0f}s ago)</span>'
        )
    except OSError:
        beat = '<span class="bad">NO STATE FILE</span>'
    runner = (
        f'<span class="ok">alive (pid {runner_pid})</span>'
        if _proc_alive(runner_pid)
        else '<span class="bad">DEAD</span>'
    )
    watchdog = (
        f'<span class="ok">alive (pid {watchdog_pid})</span>'
        if _proc_alive(watchdog_pid)
        else '<span class="dim">not running / not configured</span>'
    )
    flags = _runner_mode_from_process()
    if flags is None:
        live, allow = "unknown", "unknown"
        flag_source = "runner environment unavailable; dashboard environment is not substituted"
        mode = '<span class="warn">UNVERIFIED</span>'
    else:
        live, allow = flags
        flag_source = "best-effort read of runner process environment"
        if live == "true" and allow == "true":
            mode = '<span class="bad">EXECUTION FLAGS ENABLED</span>'
        elif live == "false" or allow == "false":
            mode = '<span class="warn">at least one execution flag is false</span>'
        else:
            mode = '<span class="warn">UNVERIFIED</span>'
    return (
        f"<h2>Session</h2><table>"
        f"<tr><th>State-file freshness (not a heartbeat)</th><td class='big'>{beat}</td></tr>"
        f"<tr><th>Runner</th><td>{runner}</td></tr>"
        f"<tr><th>Watchdog</th><td>{watchdog}</td></tr>"
        f"<tr><th>Execution mode</th><td class='big'>{mode} "
        f"<span class='dim'>(LIVE_TRADING_ENABLE={html.escape(live)} · "
        f"ALLOW_REAL_EXECUTION={html.escape(allow)} · source: {html.escape(flag_source)})</span></td></tr>"
        f"</table>"
    )


_CPU_SAMPLES: dict[int, tuple[float, float]] = {}


def _process_cpu_delta(pid: int) -> str:
    """Read cumulative CPU time for one process; report delta since last page render."""
    if os.name != "nt" or pid <= 0:
        return "unavailable"
    handle = None
    try:
        import ctypes

        class FILETIME(ctypes.Structure):
            _fields_ = [("low", ctypes.c_uint32), ("high", ctypes.c_uint32)]

            def seconds(self) -> float:
                return ((int(self.high) << 32) | int(self.low)) / 10_000_000.0

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return "unavailable"
        created, exited, kernel, user = FILETIME(), FILETIME(), FILETIME(), FILETIME()
        if not kernel32.GetProcessTimes(
            handle, ctypes.byref(created), ctypes.byref(exited),
            ctypes.byref(kernel), ctypes.byref(user)
        ):
            return "unavailable"
        now = time.monotonic()
        cpu = kernel.seconds() + user.seconds()
        previous = _CPU_SAMPLES.get(pid)
        _CPU_SAMPLES[pid] = (now, cpu)
        if previous is None:
            return "sampling…"
        elapsed = max(0.001, now - previous[0])
        delta = max(0.0, cpu - previous[1])
        return f"{delta:.3f}s CPU / {elapsed:.1f}s elapsed"
    except Exception:
        return "unavailable"
    finally:
        if handle:
            try:
                ctypes.windll.kernel32.CloseHandle(handle)
            except Exception:
                pass


def runner_health() -> str:
    """Show state and event freshness separately; a live PID is not proof of progress."""
    runner_pid = _read_pid(RUNNER_LOCK)
    alive = _proc_alive(runner_pid)
    cpu_delta = _process_cpu_delta(runner_pid) if alive else "process not alive"
    state_age = None
    event_age = None
    try:
        state_age = max(0.0, time.time() - STATE_FILE.stat().st_mtime)
    except OSError:
        pass
    try:
        event_age = max(0.0, time.time() - EVENTS.stat().st_mtime)
    except OSError:
        pass

    def freshness(age):
        if age is None:
            return '<span class="bad">FILE MISSING</span>'
        if age <= 30:
            return f'<span class="ok">{age:.0f}s ago</span>'
        if age <= 180:
            return f'<span class="warn">STALE ({age:.0f}s ago)</span>'
        return f'<span class="bad">STALE ({age:.0f}s ago)</span>'

    process_status = (
        f'<span class="ok">alive PID {runner_pid}</span>' if alive
        else f'<span class="bad">not confirmed alive (lock PID {runner_pid or "unknown"})</span>'
    )
    return (
        '<h2>V3 Runner Diagnostics</h2><table>'
        f'<tr><th>Runner process</th><td>{process_status}</td></tr>'
        f'<tr><th>CPU delta</th><td>{html.escape(cpu_delta)} · read-only sample</td></tr>'
        f'<tr><th>V3 state last write</th><td>{freshness(state_age)}</td></tr>'
        f'<tr><th>V3 event log last write</th><td>{freshness(event_age)}</td></tr>'
        '<tr><th>Progress interpretation</th><td class="warn">A running process or fresh state file alone does not prove a successful market poll. Compare state and event freshness.</td></tr>'
        '</table>'
    )


def mt5_status() -> str:
    rows = []
    path = find_mt5_terminal()
    initialized = mt5.initialize(path=str(path)) if path else mt5.initialize()
    if not initialized:
        return "<h2>MT5</h2><p class='bad'>terminal not connected</p>"
    try:
        acc = mt5.account_info()
        term = mt5.terminal_info()
        head = (
            f"<tr><th>Account</th><td>{acc.login} @ {acc.server} "
            f"({'DEMO' if acc.trade_mode == 0 else 'REAL?!'}) · balance {acc.balance:.2f}</td></tr>"
            if acc else "<tr><th>Account</th><td class='bad'>unavailable</td></tr>"
        )
        head += f"<tr><th>Terminal connected</th><td class='{'ok' if term and term.connected else 'bad'}'>{term.connected if term else '?'}</td></tr>"
        for sym in ("XAUUSD.ecn", "EURUSD.ecn", "BTCUSD.ecn"):
            tick = mt5.symbol_info_tick(sym)
            rows.append(
                f"<tr><td>{sym}</td><td>{tick.bid:.2f} / {tick.ask:.2f}</td></tr>"
                if tick else f"<tr><td>{sym}</td><td class='dim'>no tick</td></tr>"
            )
    finally:
        mt5.shutdown()
    return f"<h2>MT5 (read-only probe)</h2><table>{head}</table><h2>Live ticks</h2><table>{''.join(rows)}</table>"


def today_stats() -> tuple[str, str, str]:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    signals = fills = closes = 0
    wins = losses = 0
    net = 0.0
    per_symbol: dict[str, dict] = {}
    orders: list[dict] = []
    events: list[dict] = []
    try:
        with EVENTS.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    ev = json.loads(line)
                except Exception:
                    continue
                events.append(ev)
                if not str(ev.get("ts_utc", "")).startswith(today):
                    continue
                sym = str(ev.get("symbol") or "?")
                b = per_symbol.setdefault(sym, {"sig": 0, "w": 0, "l": 0, "net": 0.0})
                kind = ev.get("event")
                if kind == "TELEGRAM_SIGNAL":
                    signals += 1
                    b["sig"] += 1
                elif kind == "TELEGRAM_DEAL_LIFECYCLE":
                    net_ev = float(ev.get("net", 0.0) or 0.0)
                    net += net_ev
                    b["net"] += net_ev
                    if int(ev.get("entry", -1)) == getattr(mt5, "DEAL_ENTRY_IN", 0):
                        fills += 1
                    else:
                        closes += 1
                        if net_ev > 0:
                            wins += 1
                            b["w"] += 1
                        elif net_ev < 0:
                            losses += 1
                            b["l"] += 1
                elif kind == "ORDER_RESULT":
                    res = ev.get("result") or {}
                    orders.append({
                        "t": ev.get("ts_utc", "")[11:19],
                        "sym": sym,
                        "dir": str(ev.get("signal_id", "")).rsplit(":", 1)[-1],
                        "outcome": "FILLED/PLACED" if res.get("ok") else f"REJECT {res.get('reason') or res.get('retcode')}",
                    })
                elif kind == "PENDING_ORDER_EXPIRED":
                    orders.append({
                        "t": ev.get("ts_utc", "")[11:19],
                        "sym": sym,
                        "dir": "—",
                        "outcome": f"EXPIRED ({ev.get('outcome')})",
                    })
    except OSError:
        pass
    rows = [
        f"<tr><td>{html.escape(s)}</td><td>{b['sig']}</td><td>{b['w']}</td>"
        f"<td>{b['l']}</td><td>{b['net']:+.2f}</td></tr>"
        for s, b in sorted(per_symbol.items())
    ]
    stats = (
        f"<h2>Today (UTC {today})</h2><table>"
        f"<tr><th>Signals</th><th>Fills</th><th>Closed</th><th>✅</th><th>❌</th><th>Net USD</th></tr>"
        f"<tr><td class='big'>{signals}</td><td>{fills}</td><td>{closes}</td>"
        f"<td class='ok'>{wins}</td><td class='bad'>{losses}</td><td class='big'>{net:+.2f}</td></tr>"
        f"</table>"
        + (f"<table><tr><th>Symbol</th><th>Sig</th><th>✅</th><th>❌</th><th>Net</th></tr>{''.join(rows)}</table>" if rows else "")
    )
    order_rows = "".join(
        f"<tr><td>{o['t']}</td><td>{html.escape(o['sym'])}</td><td>{o['dir']}</td>"
        f"<td class='{'ok' if 'FILLED' in o['outcome'] or 'PLACED' in o['outcome'] else 'warn'}'>{html.escape(o['outcome'])}</td></tr>"
        for o in orders[-12:]
    )
    orders_html = (
        f"<h2>Today's orders</h2><table><tr><th>Time UTC</th><th>Symbol</th><th>Dir</th><th>Outcome</th></tr>{order_rows}</table>"
        if order_rows else "<h2>Today's orders</h2><p class='dim'>none yet today</p>"
    )
    return stats, orders_html, events




def recent_trade_ledger(events: list[dict]) -> str:
    """Render only lifecycle events actually present in the active V3 event log."""
    rows = []
    for ev in reversed(events):
        if ev.get("event") != "TELEGRAM_DEAL_LIFECYCLE":
            continue
        try:
            stamp = datetime.fromisoformat(str(ev.get("ts_utc", "")).replace("Z", "+00:00"))
            stamp_text = stamp.astimezone(IRAN_TZ).strftime("%H:%M:%S")
        except (ValueError, TypeError):
            stamp_text = "—"
        is_entry = int(ev.get("entry", -1)) == getattr(mt5, "DEAL_ENTRY_IN", 0)
        action = "OPEN / ENTRY" if is_entry else "CLOSE / EXIT"
        net = ev.get("net")
        if net is None:
            net = ev.get("profit")
        try:
            net_text = f"{float(net):+.2f}" if net is not None else "not recorded"
        except (TypeError, ValueError):
            net_text = "not recorded"
        direction = str(ev.get("direction") or ev.get("side") or "—")
        rows.append(
            f"<tr><td>{stamp_text}</td><td>{action}</td><td>{html.escape(str(ev.get('symbol') or '—'))}</td>"
            f"<td>{html.escape(str(ev.get('position') or '—'))}</td>"
            f"<td>{html.escape(direction)}</td><td>{html.escape(str(ev.get('price') or '—'))}</td>"
            f"<td>{html.escape(net_text)}</td><td>{html.escape(str(ev.get('deal') or '—'))}</td></tr>"
        )
        if len(rows) >= 20:
            break
    if not rows:
        rows_html = "<tr><td colspan='8' class='dim'>No lifecycle trade events recorded in the active V3 log.</td></tr>"
    else:
        rows_html = "".join(rows)
    return (
        "<h2>Latest V3 trade lifecycle events (event-log evidence)</h2><table>"
        "<tr><th>Time Tehran</th><th>Lifecycle</th><th>Symbol</th><th>Position</th>"
        "<th>Side</th><th>Price</th><th>Net/profit field</th><th>Deal ticket</th></tr>"
        + rows_html + "</table>"
    )

def render() -> str:
    stats, orders_html, events = today_stats()
    ev_rows = []
    for ev in reversed(events[-40:]):
        t = str(ev.get("ts_utc", ""))[11:19]
        kind = str(ev.get("event", "?"))
        sym = str(ev.get("symbol") or "")
        detail = ev.get("detail") or ev.get("outcome") or (
            f"retcode={ev['result'].get('retcode')}" if isinstance(ev.get("result"), dict) and ev["result"].get("retcode") else ""
        )
        ok = ev.get("success")
        cls = "ok" if ok is True else ("bad" if ok is False else "dim")
        ev_rows.append(
            f"<tr><td>{t}</td><td>{html.escape(kind)}</td><td>{html.escape(sym)}</td>"
            f"<td class='{cls}'>{html.escape(str(detail))}</td></tr>"
        )
    events_html = (
        "<h2>Last 40 events (newest first)</h2><table>"
        "<tr><th>Time UTC</th><th>Event</th><th>Symbol</th><th>Detail</th></tr>"
        + "".join(ev_rows) + "</table>"
    )
    return (
        _PG_UP + session_status() + runner_health() + mt5_status()
        + recent_trade_ledger(events) + stats + orders_html + events_html
        + f"<p class='dim'>{datetime.now(IRAN_TZ).strftime('%H:%M:%S')} Iran time · "
        + "read-only page · dashboard never places orders</p></body></html>"
    )


@app.get("/")
def index() -> Response:
    return Response(render(), mimetype="text/html")


def main() -> None:
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
