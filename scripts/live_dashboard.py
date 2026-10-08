"""Read-only live dashboard for the SP2L forward-test session.

Serves one auto-refreshing page (default http://127.0.0.1:8790) so the
operator can SEE the session working without touching logs:

  - session heartbeat (state-file mtime, runner/watchdog pids alive)
  - execution mode (LIVE-DEMO / DRY-RUN) with the raw operator flags
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
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

from flask import Flask, Response

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import MetaTrader5 as mt5  # noqa: E402
from mt5_terminal_resolver import find_mt5_terminal  # noqa: E402

from live_mt5_gateway import effective_mode  # noqa: E402  (gateway env truth)


def _runner_mode_from_process(lock_path: Path | None = None) -> tuple[str, str] | None:
    """True session mode: read the live runner's own env from process memory.

    Windows-only best effort (the whole live setup is Windows); returns the
    raw flag values so the dashboard reports what the session actually runs
    with, not what the dashboard process happens to have.
    """
    lock_path = lock_path or RUNNER_LOCK
    if os.name != "nt" or not lock_path.exists():
        return None
    try:
        import ctypes

        pid = int(lock_path.read_text(encoding="utf-8").strip() or 0)
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

STATE_FILE = ROOT / "runtime" / "sp2l_multi_symbol_forward_state.json"
HEALTH_FILE = ROOT / "runtime" / "sp2l_multi_symbol_forward_health.json"
RUNNER_LOCK = ROOT / "runtime" / "sp2l_multi_symbol_forward_runner.lock"
WATCHDOG_PID = ROOT / "runtime" / "forward_watchdog.pid"
EVENTS = ROOT / "artifacts" / "forward-test" / "SP2L_MULTI_SYMBOL_FORWARD_EVENTS.jsonl"

PORT = int(os.getenv("SP2L_DASHBOARD_PORT", "8790"))
REFRESH_SECONDS = 5
IRAN_TZ = ZoneInfo("Asia/Tehran")

def _profile_roots() -> list[Path]:
    """Return this checkout plus sibling SP2L worktrees used for research profiles."""
    roots = [ROOT]
    try:
        for p in ROOT.parent.glob("xauusd-strategy-a-*"):
            if p.is_dir() and (p / "artifacts" / "forward-test").is_dir():
                roots.append(p)
    except OSError:
        pass
    return list(dict.fromkeys(roots))

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

def _active_profile_root() -> Path:
    """Select the worktree whose runner lock currently belongs to a live process."""
    live = []
    for root in _profile_roots():
        lock = root / "runtime" / "sp2l_multi_symbol_forward_runner.lock"
        try:
            pid = int(lock.read_text(encoding="utf-8").strip() or 0)
        except (OSError, ValueError):
            pid = 0
        if _proc_alive(pid):
            live.append(root)
    if len(live) == 1:
        return live[0]
    if live:
        return max(live, key=lambda p: (p / "runtime" / "sp2l_multi_symbol_forward_runner.lock").stat().st_mtime)
    return ROOT

def _active_forward_paths() -> tuple[Path, Path]:
    """Resolve event/state files belonging to the currently running profile."""
    profile_root = _active_profile_root()
    artifacts = profile_root / "artifacts" / "forward-test"
    runtime = profile_root / "runtime"
    events = artifacts / "SP2L_MULTI_SYMBOL_FORWARD_EVENTS.jsonl"
    event_candidates = sorted(
        artifacts.glob("*_FORWARD_EVENTS.jsonl"),
        key=lambda p: p.stat().st_mtime if p.exists() else 0.0,
        reverse=True,
    )
    event = event_candidates[0] if event_candidates else events
    stem = event.stem[:-len("_FORWARD_EVENTS")]
    state = runtime / (stem.lower() + "_forward_state.json")
    if not state.exists():
        state_candidates = sorted(
            runtime.glob("*_forward_state.json"),
            key=lambda p: p.stat().st_mtime if p.exists() else 0.0,
            reverse=True,
        )
        state = state_candidates[0] if state_candidates else runtime / "sp2l_multi_symbol_forward_state.json"
    return event, state

def _mt5_server_offset_seconds(symbol: str = "XAUUSD.ecn") -> int:
    """Infer broker-server clock offset for display only."""
    initialized_here = False
    try:
        if not mt5.terminal_info():
            path = find_mt5_terminal()
            initialized_here = bool(mt5.initialize(path=str(path)) if path else mt5.initialize())
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            return 0
        offset = int(round(float(tick.time) - time.time()))
        return offset if abs(offset) <= 18 * 3600 else 0
    except Exception:
        return 0
    finally:
        if initialized_here:
            mt5.shutdown()

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


def runner_health() -> str:
    """Read-only operational health for the currently active forward profile."""
    profile_root = _active_profile_root()
    health_file = profile_root / "runtime" / "sp2l_multi_symbol_forward_health.json"
    try:
        raw = json.loads(health_file.read_text(encoding="utf-8"))
        ts = str(raw.get("ts_utc") or "")
        beat_dt = datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None
        age = time.time() - beat_dt.timestamp() if beat_dt else 999999.0
        pid = int(raw.get("pid") or 0)
        alive = _proc_alive(pid)
        mt5_ok = raw.get("mt5_connected") is True
        poll_ok = raw.get("poll_ok") is True
        cpu_delta = float(raw.get("process_cpu_delta") or 0.0)
        m1_ts = raw.get("m1_bar_time")
        m1_text = "—"
        if m1_ts:
            offset = _mt5_server_offset_seconds(str(raw.get("symbol") or "XAUUSD.ecn"))
            m1_text = datetime.fromtimestamp(int(m1_ts) - offset, timezone.utc).astimezone(IRAN_TZ).strftime("%H:%M:%S")
        if age <= 45 and alive:
            health = '<span class="ok">🟢 HEALTHY</span>'
        elif age <= 120 and alive:
            health = '<span class="warn">🟡 STALE</span>'
        else:
            health = '<span class="bad">🔴 OFFLINE / STALE</span>'
        poll = '<span class="ok">OK</span>' if poll_ok else '<span class="bad">FAILED</span>'
        mt5 = '<span class="ok">CONNECTED</span>' if mt5_ok else '<span class="bad">DISCONNECTED</span>'
        activity = '<span class="ok">ACTIVE</span>' if cpu_delta > 0 else '<span class="warn">NO CPU DELTA</span>'
        return (
            '<h2>Runner Health</h2><table>'
            f"<tr><th>Overall</th><td class='big'>{health}</td></tr>"
            f"<tr><th>Process</th><td>{'alive' if alive else 'dead'} (PID {pid})</td></tr>"
            f"<tr><th>MT5</th><td>{mt5}</td></tr>"
            f"<tr><th>Market poll</th><td>{poll} · M1 {m1_text} Tehran</td></tr>"
            f"<tr><th>CPU activity</th><td>{activity} · Δ {cpu_delta:.6f}s</td></tr>"
            f"<tr><th>Heartbeat</th><td>{age:.0f}s ago</td></tr>"
            '</table>'
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        try:
            _, active_state = _active_forward_paths()
            lock = profile_root / "runtime" / "sp2l_multi_symbol_forward_runner.lock"
            pid = _read_pid(lock)
            age = time.time() - active_state.stat().st_mtime
            alive = _proc_alive(pid)
            health = '<span class="ok">🟢 ACTIVE (fallback)</span>' if alive and age < 120 else (
                '<span class="warn">🟡 STALE STATE</span>' if alive else '<span class="bad">🔴 OFFLINE</span>'
            )
            return (
                '<h2>Runner Health</h2><table>'
                f"<tr><th>Overall</th><td class='big'>{health}</td></tr>"
                f"<tr><th>Process</th><td>{'alive' if alive else 'dead'} (PID {pid})</td></tr>"
                f"<tr><th>State</th><td>{age:.0f}s since last write</td></tr>"
                f"<tr><th>Profile</th><td>{html.escape(profile_root.name)}</td></tr>"
                '</table>'
            )
        except (OSError, ValueError, TypeError):
            return '<h2>Runner Health</h2><p class="bad">🔴 NO RUNNER TELEMETRY</p>'


def _health_heartbeat_age() -> float | None:
    """Heartbeat age from the runner's own health telemetry.

    V3 runs report their heartbeat in HEALTH_FILE; the legacy STATE_FILE
    belongs to the retired multi-symbol session. Fall back to active state
    only when health telemetry is unavailable.
    """
    try:
        profile_root = _active_profile_root()
        health_file = profile_root / "runtime" / "sp2l_multi_symbol_forward_health.json"
        raw = json.loads(health_file.read_text(encoding="utf-8"))
        ts = str(raw.get("ts_utc") or "")
        if not ts:
            return None
        beat_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return time.time() - beat_dt.timestamp()
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return None


def session_status() -> str:
    profile_root = _active_profile_root()
    runner_lock = profile_root / "runtime" / "sp2l_multi_symbol_forward_runner.lock"
    watchdog_pid_file = profile_root / "runtime" / "forward_watchdog.pid"
    runner_pid = _read_pid(runner_lock)
    watchdog_pid = _read_pid(watchdog_pid_file)

    hb_age = _health_heartbeat_age()
    if hb_age is not None:
        age = hb_age
    else:
        try:
            _, active_state = _active_forward_paths()
            age = time.time() - active_state.stat().st_mtime
        except OSError:
            age = None

    if age is None:
        beat = '<span class="bad">NO STATE FILE</span>'
    else:
        beat = (
            f'<span class="ok">ALIVE ({age:.0f}s ago)</span>'
            if age < 15
            else f'<span class="bad">STALE ({age:.0f}s ago)</span>'
        )
    runner = (
        f'<span class="ok">alive (pid {runner_pid})</span>'
        if _proc_alive(runner_pid)
        else '<span class="bad">DEAD</span>'
    )
    watchdog = (
        f'<span class="ok">alive (pid {watchdog_pid})</span>'
        if _proc_alive(watchdog_pid)
        else '<span class="dim">not running</span>'
    )
    flags = _runner_mode_from_process(runner_lock)
    if flags is None:
        flags = (
            os.getenv("LIVE_TRADING_ENABLE", "false").lower(),
            os.getenv("ALLOW_REAL_EXECUTION", "false").lower(),
        )
    live, allow = flags
    mode = (
        '<span class="ok">🟩 LIVE-DEMO</span>' if live == "true" and allow == "true"
        else '<span class="warn">🟨 DRY-RUN</span>'
    )
    return (
        f"<h2>Session</h2><table>"
        f"<tr><th>Heartbeat</th><td class='big'>{beat}</td></tr>"
        f"<tr><th>Runner</th><td>{runner}</td></tr>"
        f"<tr><th>Watchdog</th><td>{watchdog}</td></tr>"
        f"<tr><th>Execution mode</th><td class='big'>{mode} "
        f"<span class='dim'>(LIVE_TRADING_ENABLE={live} · "
        f"ALLOW_REAL_EXECUTION={allow} — read from the live runner process)</span></td></tr>"
        f"</table>"
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
    event_file, _ = _active_forward_paths()
    today = datetime.now(IRAN_TZ).strftime("%Y-%m-%d")
    signals = fills = closes = 0
    wins = losses = 0
    net = 0.0
    per_symbol: dict[str, dict] = {}
    orders: list[dict] = []
    events: list[dict] = []
    try:
        with event_file.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    ev = json.loads(line)
                except Exception:
                    continue
                events.append(ev)
                try:
                    ev_dt = datetime.fromisoformat(str(ev.get("ts_utc", "")).replace("Z", "+00:00")).astimezone(IRAN_TZ)
                except (ValueError, TypeError):
                    continue
                if ev_dt.strftime("%Y-%m-%d") != today:
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
                        "t": (datetime.fromisoformat(ev.get("ts_utc", "").replace("Z","+00:00")).astimezone(IRAN_TZ).strftime("%H:%M:%S") if ev.get("ts_utc") else "—"),
                        "sym": sym,
                        "dir": str(ev.get("signal_id", "")).rsplit(":", 1)[-1],
                        "outcome": "FILLED/PLACED" if res.get("ok") else f"REJECT {res.get('reason') or res.get('retcode')}",
                    })
                elif kind == "PENDING_ORDER_EXPIRED":
                    orders.append({
                        "t": (datetime.fromisoformat(ev.get("ts_utc", "").replace("Z","+00:00")).astimezone(IRAN_TZ).strftime("%H:%M:%S") if ev.get("ts_utc") else "—"),
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
        f"<h2>Today (Tehran {today})</h2><table>"
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
        f"<h2>Today's orders</h2><table><tr><th>Time Tehran</th><th>Symbol</th><th>Dir</th><th>Outcome</th></tr>{order_rows}</table>"
        if order_rows else "<h2>Today's orders</h2><p class='dim'>none yet today</p>"
    )
    return stats, orders_html, events


def trade_ledger() -> str:
    """Read-only MT5 trade ledger: current open positions and recently closed trades."""
    initialized_here = False
    open_rows = []
    closed_rows = []
    try:
        if not mt5.terminal_info():
            path = find_mt5_terminal()
            initialized_here = bool(mt5.initialize(path=str(path)) if path else mt5.initialize())
        if not mt5.terminal_info():
            return "<h2>Trades</h2><p class='bad'>MT5 unavailable</p>"

        magic = 26092201

        for pos in sorted(
            mt5.positions_get() or [],
            key=lambda p: int(getattr(p, "time", 0) or 0),
            reverse=True,
        ):
            if int(getattr(pos, "magic", 0) or 0) != magic:
                continue
            direction = "BUY" if int(pos.type) == 0 else "SELL"
            open_time = datetime.fromtimestamp(
                int(pos.time), timezone.utc
            ).astimezone(IRAN_TZ).strftime("%H:%M:%S")
            floating = float(pos.profit)
            open_rows.append(
                f"<tr><td>{open_time}</td><td>{html.escape(str(pos.symbol))}</td>"
                f"<td>{direction}</td><td>{int(pos.ticket)}</td><td>{pos.volume:g}</td>"
                f"<td>{pos.price_open:.2f}</td><td>{pos.sl:.2f}</td><td>{pos.tp:.2f}</td>"
                f"<td class='{'ok' if floating >= 0 else 'bad'}'>{floating:+.2f}</td></tr>"
            )

        # MT5 history_deals_get() in this broker environment expects the
        # broker/server-clock wall time, not runner UTC. Reuse the observed
        # server offset exactly as the lifecycle reconciliation does.
        offset = _mt5_server_offset_seconds("XAUUSD.ecn")
        end_server = datetime.now(timezone.utc) + timedelta(seconds=offset)
        start_server = end_server - timedelta(days=1)
        deals = mt5.history_deals_get(start_server, end_server) or []

        by_position = {}
        for deal in deals:
            if int(getattr(deal, "magic", 0) or 0) != magic:
                continue
            by_position.setdefault(int(deal.position_id), []).append(deal)

        for position_id, position_deals in by_position.items():
            exits = [
                d for d in position_deals
                if int(getattr(d, "entry", -1)) == getattr(mt5, "DEAL_ENTRY_OUT", 1)
            ]
            if not exits:
                continue
            entries = [
                d for d in position_deals
                if int(getattr(d, "entry", -1)) == getattr(mt5, "DEAL_ENTRY_IN", 0)
            ]
            if not entries:
                continue
            entry = min(
                entries,
                key=lambda d: (int(getattr(d, "time", 0) or 0), int(getattr(d, "ticket", 0) or 0)),
            )
            exit_deal = max(
                exits,
                key=lambda d: (int(getattr(d, "time", 0) or 0), int(getattr(d, "ticket", 0) or 0)),
            )
            direction = "BUY" if int(entry.type) == 0 else "SELL"
            net = sum(
                float(getattr(d, "profit", 0.0) or 0.0)
                + float(getattr(d, "commission", 0.0) or 0.0)
                + float(getattr(d, "swap", 0.0) or 0.0)
                + float(getattr(d, "fee", 0.0) or 0.0)
                for d in position_deals
            )
            close_time = datetime.fromtimestamp(
                int(exit_deal.time), timezone.utc
            ).astimezone(IRAN_TZ).strftime("%H:%M:%S")
            reason = str(getattr(exit_deal, "comment", "") or "").strip()
            closed_rows.append(
                (
                    int(exit_deal.time),
                    f"<tr><td>{close_time}</td><td>{html.escape(str(entry.symbol))}</td>"
                    f"<td>{direction}</td><td>{position_id}</td><td>{entry.volume:g}</td>"
                    f"<td>{entry.price:.2f}</td><td>{exit_deal.price:.2f}</td>"
                    f"<td class='{'ok' if net >= 0 else 'bad'}'>{net:+.2f}</td>"
                    f"<td>{html.escape(reason or '—')}</td></tr>",
                )
            )

        closed_html_rows = [
            row for _, row in sorted(closed_rows, reverse=True)[:20]
        ]
        open_html = "".join(open_rows) or (
            "<tr><td colspan='9' class='dim'>No open Strategy A trades</td></tr>"
        )
        closed_html = "".join(closed_html_rows) or (
            "<tr><td colspan='9' class='dim'>No closed Strategy A trades in the last 24h</td></tr>"
        )
        return (
            "<h2>Open trades</h2><table>"
            "<tr><th>Open Tehran</th><th>Symbol</th><th>Dir</th><th>Position</th><th>Vol</th>"
            "<th>Entry</th><th>SL</th><th>TP</th><th>Floating P/L</th></tr>"
            + open_html + "</table>"
            "<h2>Closed trades — last 24h</h2><table>"
            "<tr><th>Close Tehran</th><th>Symbol</th><th>Dir</th><th>Position</th><th>Vol</th>"
            "<th>Entry</th><th>Exit</th><th>Net USD</th><th>Broker comment</th></tr>"
            + closed_html + "</table>"
            "<p class='dim'>Source: MT5 positions/history · Strategy A magic 26092201 · read-only.</p>"
        )
    except Exception as exc:
        return f"<h2>Trades</h2><p class='bad'>MT5 trade ledger error: {html.escape(str(exc))}</p>"
    finally:
        if initialized_here:
            mt5.shutdown()

def render() -> str:
    stats, orders_html, events = today_stats()
    ev_rows = []
    for ev in reversed(events[-40:]):
        t = (datetime.fromisoformat(str(ev.get("ts_utc", "")).replace("Z","+00:00")).astimezone(IRAN_TZ).strftime("%H:%M:%S") if ev.get("ts_utc") else "—")
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
        "<tr><th>Time Tehran</th><th>Event</th><th>Symbol</th><th>Detail</th></tr>"
        + "".join(ev_rows) + "</table>"
    )
    return (
        _PG_UP + session_status() + runner_health() + mt5_status() + trade_ledger() + stats + orders_html + events_html
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
