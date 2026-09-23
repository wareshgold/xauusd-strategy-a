"""Research-only multi-symbol SP2L author-replica forward runner.

Runs XAUUSD, EURUSD and BTCUSD concurrently in one MT5 Python process.
It does not define or promote canonical Strategy A geometry.

Symbol names are resolved from the connected MT5 terminal. Pip size is derived
from MT5 point/digits using the conventional FX rule (5/3 digits => 10 points)
and point for 2/1/0-digit instruments, with per-symbol environment overrides
available as PIP_SIZE_<BASE>, e.g. PIP_SIZE_EURUSD=0.0001.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

import live_mt5_gateway as gateway

# Symbol selection is configuration only (research/forward-test scope):
# override with SP2L_SYMBOLS="XAUUSD,GBPUSD,USTEC"; XAUUSD stays the default
# first entry. Order here defines the magic-number slot (MAGIC_BASE+index+1).
BASE_SYMBOLS = tuple(
    s.strip().upper()
    for s in os.getenv("SP2L_SYMBOLS", "XAUUSD,EURUSD,BTCUSD").split(",")
    if s.strip()
)
TIMEFRAME = mt5.TIMEFRAME_M1
P_GAP_PRICE = float(os.getenv("SP2L_P_GAP_PRICE", "1.0"))
SPIKE_MULTIPLIER = float(os.getenv("SP2L_SPIKE_MULTIPLIER", "1.5"))
MAX_SL_DISTANCE = float(os.getenv("SP2L_MAX_SL_DISTANCE", "10.0"))
TP_R = float(os.getenv("SP2L_TP_R", "1.0"))
VOLUME = float(os.getenv("SP2L_VOLUME", "0.01"))
POLL_SECONDS = float(os.getenv("SP2L_POLL_SECONDS", "2"))
ORDER_MODE = os.getenv("MT5_FORWARD_ORDER_MODE", "PENDING_LIMIT_RESEARCH")
# The gateway re-reads this variable at execution time (its own default is
# MARKET). Publish the runner's declared mode, otherwise orders silently
# execute as MARKET: the fill lands beyond the theoretical entry while
# SL/TP stay on the theoretical levels, destroying the 1R risk/reward
# relation (observed 2026-09-22 15:05: filled 4325.61 vs entry 4324.59,
# real R:R 0.34 instead of 1:1).
os.environ.setdefault("MT5_FORWARD_ORDER_MODE", ORDER_MODE)
MAGIC_BASE = int(os.getenv("SP2L_MAGIC_BASE", "26092200"))
# Per-symbol volume override (e.g. SP2L_VOLUME_US500=0.1 for index CFDs whose
# volume_min is 0.1; a volume below volume_min is rejected by the broker).
def _volume_for(base: str) -> float:
    override = os.getenv(f"SP2L_VOLUME_{base}")
    return float(override) if override else VOLUME
IRAN_TZ = timezone(timedelta(hours=3, minutes=30))

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "forward-test"
RUNTIME = ROOT / "runtime"
ARTIFACTS.mkdir(parents=True, exist_ok=True)
RUNTIME.mkdir(parents=True, exist_ok=True)
EVENTS = ARTIFACTS / "SP2L_MULTI_SYMBOL_FORWARD_EVENTS.jsonl"
STATE_FILE = RUNTIME / "sp2l_multi_symbol_forward_state.json"

SL_ANCHOR = "SPIKE_CANDLE_EXTREME_RESEARCH"
DAILY_SUMMARY_UTC_HOUR = int(os.getenv("SP2L_DAILY_SUMMARY_UTC_HOUR", "21"))
# Pending-order expiry: unfilled limit orders of this runner are cancelled
# after N minutes (0 disables). Research/infrastructure only — never touches
# open positions, foreign/manual orders, or SL/TP semantics.
PENDING_TTL_MINUTES = float(os.getenv("SP2L_PENDING_TTL_MINUTES", "30"))
RUNNER_LOCK = RUNTIME / "sp2l_multi_symbol_forward_runner.lock"


def acquire_runner_lock() -> int | None:
    """Single-instance guard: two concurrent runners would double every order."""
    RUNTIME.mkdir(parents=True, exist_ok=True)
    try:
        if RUNNER_LOCK.exists():
            pid = int(RUNNER_LOCK.read_text(encoding="utf-8").strip() or 0)
            if pid > 0 and pid != os.getpid():
                try:
                    os.kill(pid, 0)  # signal probe: raises if the process is gone
                    return pid
                except OSError:
                    pass  # stale lock file
        RUNNER_LOCK.write_text(str(os.getpid()), encoding="utf-8")
        return None
    except (OSError, ValueError):
        return None  # lock unavailable: never block the demo runner on FS errors


def release_runner_lock() -> None:
    try:
        if RUNNER_LOCK.exists() and RUNNER_LOCK.read_text(encoding="utf-8").strip() == str(os.getpid()):
            RUNNER_LOCK.unlink()
    except OSError:
        pass


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _utc_day_key(ts: int) -> str:
    return datetime.fromtimestamp(int(ts), timezone.utc).strftime("%Y-%m-%d")


def execution_mode_line() -> str:
    """Self-declared execution mode from this process's operator flags."""
    live = os.getenv("LIVE_TRADING_ENABLE", "false").lower()
    allow = os.getenv("ALLOW_REAL_EXECUTION", "false").lower()
    if live == "true" and allow == "true":
        return (
            "🟩 Execution: LIVE-DEMO\n"
            f"   LIVE_TRADING_ENABLE={live} · ALLOW_REAL_EXECUTION={allow}"
        )
    return (
        "🟨 Execution: DRY-RUN\n"
        f"   LIVE_TRADING_ENABLE={live} · ALLOW_REAL_EXECUTION={allow}"
    )


def build_daily_summary(state: dict) -> str | None:
    """Deterministic daily summary over the events already recorded today (UTC)."""
    if not EVENTS.exists():
        return None
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    signals = fills = closes = 0
    wins = losses = 0
    net = 0.0
    per_symbol: dict[str, dict] = {}
    with EVENTS.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                ev = json.loads(line)
            except Exception:
                continue
            if not str(ev.get("ts_utc", "")).startswith(today):
                continue
            symbol = str(ev.get("symbol") or "?")
            bucket = per_symbol.setdefault(symbol, {"signals": 0, "wins": 0, "losses": 0, "net": 0.0})
            event = ev.get("event")
            if event == "TELEGRAM_SIGNAL":
                signals += 1
                bucket["signals"] += 1
            elif event == "TELEGRAM_DEAL_LIFECYCLE":
                net_ev = float(ev.get("net", 0.0) or 0.0)
                if int(ev.get("entry", -1)) == getattr(mt5, "DEAL_ENTRY_IN", 0):
                    fills += 1
                    bucket["net"] += net_ev
                else:
                    closes += 1
                    bucket["net"] += net_ev
                    if net_ev > 0:
                        wins += 1
                        bucket["wins"] += 1
                    elif net_ev < 0:
                        losses += 1
                        bucket["losses"] += 1
    if signals == 0 and closes == 0:
        return None
    lines = [
        f"📊 SP2L Forward — Daily Summary (UTC {today})\n",
        f"Signals: {signals} · Fills: {fills} · Closed: {closes}",
        f"Closed results: ✅ {wins} · ❌ {losses}",
        f"Closed net: {net:+.2f} USD",
        "",
        "Per symbol:",
    ]
    for symbol in sorted(per_symbol):
        b = per_symbol[symbol]
        lines.append(f"- {symbol}: sig {b['signals']} · ✅ {b['wins']} · ❌ {b['losses']} · net {b['net']:+.2f}")
    lines += ["", execution_mode_line(), "⚠️ RESEARCH / DEMO ONLY — NOT CANONICAL"]
    return "\n".join(lines)


def maybe_send_daily_summary(state: dict) -> None:
    key = "last_daily_summary_utc_day"
    now = datetime.now(timezone.utc)
    if now.hour < DAILY_SUMMARY_UTC_HOUR:
        return
    today = now.strftime("%Y-%m-%d")
    if state.get(key) == today:
        return
    summary = build_daily_summary(state)
    if summary is None:
        state[key] = today
        return
    result = gateway.send_telegram_message(summary)
    log_event({
        "event": "DAILY_SUMMARY", "success": bool(getattr(result, "success", False)),
        "detail": getattr(result, "detail", None), "utc_day": today, "canonical": False,
    })
    if getattr(result, "success", False):
        state[key] = today
    save_state(state)


def log_event(event: dict) -> None:
    payload = {"ts_utc": now_utc(), **event}
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, separators=(",", ":")) + "\n")
    print(json.dumps(payload, indent=2))


def mt5_server_offset() -> timedelta:
    """Estimate MT5 broker-server offset for human-facing timestamps only."""
    tick_times = []
    for base in BASE_SYMBOLS:
        symbol = resolve_symbol(base)
        if symbol:
            tick = mt5.symbol_info_tick(symbol)
            if tick and getattr(tick, "time", None):
                tick_times.append(int(tick.time))
    if not tick_times:
        return timedelta(0)
    observed = sum(tick_times) / len(tick_times)
    offset_seconds = observed - time.time()
    offset_hours = max(-12, min(14, round(offset_seconds / 3600)))
    return timedelta(hours=offset_hours)


def display_time_from_mt5(timestamp: int) -> datetime:
    offset = mt5_server_offset()
    utc_time = datetime.fromtimestamp(int(timestamp), timezone.utc) - offset
    return utc_time.astimezone(IRAN_TZ)


def resolve_symbol(base: str) -> str | None:
    symbols = list(mt5.symbols_get() or [])
    names = {str(s.name): s for s in symbols}
    preferred = (base, f"{base}.ecn", f"{base}.ECN", f"{base}m")
    for name in preferred:
        if name in names:
            return name
    matches = sorted(
        name for name in names
        if name.upper().startswith(base.upper())
    )
    return matches[0] if matches else None


def pip_size_for(symbol: str, info) -> tuple[float, str]:
    base = symbol.upper().split(".")[0].rstrip("M")
    override = os.getenv(f"PIP_SIZE_{base}")
    point = float(getattr(info, "point", 0.0) or 0.0)
    digits = int(getattr(info, "digits", 0) or 0)
    if override:
        return float(override), "ENV_OVERRIDE"
    if digits in (3, 5):
        return point * 10.0, "DIGITS_3_5_X10_POINT"
    return point, "POINT_FOR_NON_FX_DIGITS"


def symbol_config(symbol: str) -> dict:
    info = mt5.symbol_info(symbol)
    if info is None:
        raise RuntimeError(f"symbol_info unavailable: {symbol}")
    pip, method = pip_size_for(symbol, info)
    return {
        "symbol": symbol,
        "point": float(info.point),
        "digits": int(info.digits),
        "pip_size": pip,
        "pip_method": method,
        "trade_mode": int(info.trade_mode),
        "volume_min": float(info.volume_min),
        "volume_max": float(info.volume_max),
        "volume_step": float(info.volume_step),
    }


def rates(symbol: str, count: int = 10):
    data = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, count)
    if data is None or len(data) < 6:
        return None
    return data


def detect(candles, symbol: str):
    a, spike, correction, trigger = candles[-5], candles[-4], candles[-3], candles[-2]
    spike_body_buy = float(spike["close"] - spike["open"])
    spike_body_sell = float(spike["open"] - spike["close"])

    buy = (
        trigger["low"] < correction["low"]
        and correction["close"] > spike["close"]
        and correction["open"] > spike["open"]
        and spike["close"] > a["close"]
        and spike["open"] > a["open"]
        and correction["close"] > correction["open"]
        and spike["close"] > spike["open"]
        and a["close"] > a["open"]
        and correction["low"] > a["high"] + P_GAP_PRICE
        and spike_body_buy > SPIKE_MULTIPLIER * (correction["close"] - correction["open"])
        and spike_body_buy > SPIKE_MULTIPLIER * (a["close"] - a["open"])
        and spike_body_buy > SPIKE_MULTIPLIER * (trigger["close"] - trigger["open"])
    )

    sell = (
        trigger["high"] > correction["high"]
        and correction["close"] < spike["close"]
        and correction["open"] < spike["open"]
        and spike["close"] < a["close"]
        and spike["open"] < a["open"]
        and correction["close"] < correction["open"]
        and spike["close"] < spike["open"]
        and a["close"] < a["open"]
        and correction["high"] < a["low"] - P_GAP_PRICE
        and spike_body_sell > SPIKE_MULTIPLIER * (correction["open"] - correction["close"])
        and spike_body_sell > SPIKE_MULTIPLIER * (a["open"] - a["close"])
        and spike_body_sell > SPIKE_MULTIPLIER * (trigger["open"] - trigger["close"])
    )

    if buy == sell:
        return None

    if buy:
        entry, sl = float(trigger["low"]), float(spike["low"])
        risk = entry - sl
        if 0 < risk <= MAX_SL_DISTANCE:
            return {
                "direction": "BUY", "trigger_time": int(trigger["time"]),
                "theoretical_entry": entry, "sl": sl, "risk": risk,
                "tp": entry + TP_R * risk,
                "secondary_entry_2x": entry + 0.5 * (sl - entry),
                "symbol": symbol,
            }

    if sell:
        entry, sl = float(trigger["high"]), float(spike["high"])
        risk = sl - entry
        if 0 < risk <= MAX_SL_DISTANCE:
            return {
                "direction": "SELL", "trigger_time": int(trigger["time"]),
                "theoretical_entry": entry, "sl": sl, "risk": risk,
                "tp": entry - TP_R * risk,
                "secondary_entry_2x": entry + 0.5 * (sl - entry),
                "symbol": symbol,
            }
    return None


def load_state() -> dict:
    try:
        raw = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return {
            "seen": {str(k): v for k, v in raw.get("seen", {}).items()},
            "notified": {str(k) for k in raw.get("notified", [])},
            "deals": {int(k) for k in raw.get("deals", [])},
            "orders": {int(k) for k in raw.get("orders", [])},
            "positions": {int(k) for k in raw.get("positions", [])},
            "position_orders": {str(k): {int(v) for v in vals} for k, vals in raw.get("position_orders", {}).items()},
            "order_states": {str(k) for k in raw.get("order_states", [])},
        }
    except Exception:
        return {"seen": {}, "notified": set(), "deals": set(), "orders": set(), "positions": set(), "position_orders": {}, "order_states": set()}


def reconcile_state_from_events(state: dict) -> None:
    """Recover execution truth after a restart, including pre-fix state."""
    if not EVENTS.exists():
        return
    successful = {}
    recovered_order_states = set()
    recovered_orders = set()
    recovered_positions = set()
    recovered_deals = set()
    try:
        for line in EVENTS.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            signal_id = event.get("signal_id")
            if event.get("event") == "ORDER_RESULT" and bool(event.get("success")):
                if signal_id:
                    successful[str(signal_id)] = str(signal_id)
                order_id = int(event.get("tracked_order") or 0)
                deal_id = int(event.get("tracked_deal") or 0)
                if order_id:
                    recovered_orders.add(order_id)
                if deal_id:
                    recovered_deals.add(deal_id)
            elif event.get("event") == "PENDING_ORDER_LIFECYCLE":
                order_id = int(event.get("order") or 0)
                state_name = str(event.get("state") or "")
                if order_id:
                    recovered_orders.add(order_id)
                    if state_name:
                        recovered_order_states.add(f"{order_id}:{state_name}")
                    position_id = int(event.get("position_id") or 0)
                    if position_id:
                        recovered_positions.add(position_id)
            elif event.get("event") == "TELEGRAM_DEAL_LIFECYCLE":
                deal_id = int(event.get("deal") or 0)
                order_id = int(event.get("order") or 0)
                position_id = int(event.get("position") or 0)
                if deal_id:
                    recovered_deals.add(deal_id)
                if order_id:
                    recovered_orders.add(order_id)
                if position_id:
                    recovered_positions.add(position_id)
            elif event.get("event") == "TELEGRAM_SIGNAL" and bool(event.get("success")):
                if signal_id:
                    state["notified"].add(str(signal_id))
    except OSError:
        return

    recovered_seen = {}
    for signal_id in successful:
        symbol = signal_id.split(":", 1)[0]
        recovered_seen[symbol] = signal_id
    state["seen"] = recovered_seen
    state["orders"].update(recovered_orders)
    state["positions"].update(recovered_positions)
    state["deals"].update(recovered_deals)
    state["order_states"].update(recovered_order_states)


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps({
        "seen": state["seen"],
        "notified": sorted(state["notified"])[-1000:],
        "deals": sorted(state["deals"])[-1000:],
        "orders": sorted(state["orders"])[-1000:],
        "positions": sorted(state["positions"])[-1000:],
        "position_orders": {k: sorted(v) for k, v in state.get("position_orders", {}).items()},
        "order_states": sorted(state["order_states"])[-2000:],
    }, indent=2), encoding="utf-8")


def position_entry_price(deal, magic: int | None = None) -> float | None:
    """Volume-weighted entry price of the deal's own position.

    The ``position=`` form of ``history_deals_get`` must be called WITHOUT a
    date range: when a date range is passed alongside ``position=``, the
    terminal silently ignores the position filter and returns every deal in
    the range. That leak produced a wrong result message on 2026-09-22 (an
    XAUUSD.ecn exit reported entry 4347.104 — the volume-weighted mean of
    nine unrelated entry deals). Entry deals are additionally filtered to
    this runner's magic so manual or foreign positions can never be mixed
    in; with no matching entry the function returns None and the caller
defers the notification instead of inventing numbers.
    """
    position_id = int(getattr(deal, "position_id", 0) or 0)
    if not position_id:
        return None
    history = mt5.history_deals_get(position=position_id) or []
    if not history:
        start = datetime.fromtimestamp(int(deal.time), timezone.utc) - timedelta(days=7)
        end = datetime.fromtimestamp(int(deal.time), timezone.utc) + timedelta(seconds=1)
        history = [
            d for d in (mt5.history_deals_get(start, end) or [])
            if int(getattr(d, "position_id", 0) or 0) == position_id
        ]
    entries = [
        d for d in history
        if int(getattr(d, "entry", -1)) == mt5.DEAL_ENTRY_IN
        and (magic is None or int(getattr(d, "magic", 0) or 0) == magic)
    ]
    if not entries:
        return None
    total_volume = sum(float(getattr(d, "volume", 0.0) or 0.0) for d in entries)
    if total_volume <= 0:
        return None
    return sum(
        float(d.price) * float(getattr(d, "volume", 0.0) or 0.0) for d in entries
    ) / total_volume


def lifecycle_message(deal, symbol: str, pip_size: float, magic: int | None = None) -> str:
    is_open = int(getattr(deal, "entry", -1)) == mt5.DEAL_ENTRY_IN
    deal_type = getattr(deal, "type", None)
    if is_open:
        side = "BUY" if deal_type == mt5.DEAL_TYPE_BUY else "SELL"
    else:
        side = "SELL" if deal_type == mt5.DEAL_TYPE_BUY else "BUY"

    price = float(deal.price)
    profit = float(getattr(deal, "profit", 0.0))
    commission = float(getattr(deal, "commission", 0.0))
    swap = float(getattr(deal, "swap", 0.0))
    net = profit + commission + swap

    entry = price if is_open else position_entry_price(deal, magic)
    pips = None
    if not is_open and entry is not None and pip_size > 0:
        signed_move = price - entry if side == "BUY" else entry - price
        pips = signed_move / pip_size

    if is_open:
        icon = "🟢" if side == "BUY" else "🔴"
    else:
        icon = "🔵" if pips is not None and pips > 0 else "🟠"

    dt = display_time_from_mt5(int(deal.time))
    digits = max(2, int(mt5.symbol_info(symbol).digits))
    entry_str = f"{entry:.{digits}f}" if entry is not None else "n/a (unlinked)"
    reason = lifecycle_reason(deal)
    reason_icon = {"TAKE PROFIT": "🎯", "STOP LOSS": "🛑"}.get(reason, "☑️")
    if is_open:
        head = f"{icon} <b>SP2L — {symbol} {side} — OPENED</b>"
        body = f"📌 <b>Fill</b>     {price:.{digits}f}"
    else:
        res_icon = "🟢" if pips is not None and pips > 0 else "🔴"
        res_line = f"{res_icon} <b>Result</b>  {pips:+.0f} pips · {net:+.2f} USD" if pips is not None else f"☑️ Result  {net:+.2f} USD"
        head = f"{res_icon} <b>SP2L — {symbol} {side} — CLOSED</b>"
        body = (
            f"📌 <b>Entry</b>   {entry_str}\n"
            f"🏁 <b>Exit</b>    {price:.{digits}f}\n"
            f"{reason_icon} <b>Reason</b>  {reason}"
        )
    pips_line = (
        f"📏 <b>Move</b>    {pips:+.0f} pips\n"
        if not is_open and pips is not None and entry is not None else ""
    )
    return (
        f"{head}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{body}\n"
        f"{pips_line}"
        f"⚖️ <b>Volume</b>  {float(deal.volume):.2f}\n"
        f"💰 <b>Profit</b>   {profit:+.2f} · Net {net:+.2f}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🕒 {dt:%H:%M:%S} (UTC+3:30) · {dt:%Y-%m-%d}\n"
        f"🆔 <code>{int(deal.ticket)}/{int(getattr(deal, 'position_id', 0) or 0)}</code>\n"
        f"⚠️ <i>RESEARCH / DEMO ONLY — NOT CANONICAL</i>"
    )


def lifecycle_reason(deal) -> str:
    reason = int(getattr(deal, "reason", -1))
    if reason == getattr(mt5, "DEAL_REASON_TP", -999):
        return "TAKE PROFIT"
    if reason == getattr(mt5, "DEAL_REASON_SL", -998):
        return "STOP LOSS"
    return "CLOSE"


def lifecycle_levels(deal, symbol: str):
    sl = tp = None
    position_id = int(getattr(deal, "position_id", 0) or 0)
    if position_id:
        positions = mt5.positions_get(ticket=position_id) or []
        if positions:
            sl = float(getattr(positions[0], "sl", 0.0) or 0.0) or None
            tp = float(getattr(positions[0], "tp", 0.0) or 0.0) or None
    order_id = int(getattr(deal, "order", 0) or 0)
    if sl is None or tp is None:
        orders = mt5.history_orders_get(ticket=order_id) or [] if order_id else []
        if orders:
            order = orders[0]
            sl = sl if sl is not None else (float(getattr(order, "sl", 0.0) or 0.0) or None)
            tp = tp if tp is not None else (float(getattr(order, "tp", 0.0) or 0.0) or None)
    return sl, tp


def send_signal(candidate: dict, pip_size: float):
    symbol = candidate["symbol"]
    digits = int(mt5.symbol_info(symbol).digits)
    t = display_time_from_mt5(candidate["trigger_time"])
    risk_pips = candidate["risk"] / pip_size if pip_size else 0.0
    icon = "🟢" if candidate["direction"] == "BUY" else "🔴"
    text = (
        f"{icon} <b>SP2L — {symbol} {candidate['direction']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Entry</b>   {candidate['theoretical_entry']:.{digits}f}\n"
        f"🛑 <b>SL</b>      {candidate['sl']:.{digits}f}\n"
        f"🎯 <b>TP (1R)</b>  {candidate['tp']:.{digits}f}\n"
        f"📏 <b>Risk</b>    {candidate['risk']:.{digits}f}  ({risk_pips:.0f} pip)\n"
        f"➕ <b>2X Entry</b> {candidate['secondary_entry_2x']:.{digits}f}  <i>(research)</i>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Order</b>   Pending Limit\n"
        f"⚖️ <b>Volume</b>  {candidate.get('volume', VOLUME):.2f}\n"
        f"🕒 <b>Signal</b>  {t:%H:%M:%S} (UTC+3:30)\n\n"
        f"🆔 <code>AUTHOR_REPLICA_MULTI_{candidate['trigger_time']}_{symbol}_{candidate['direction']}</code>\n"
        f"⚠️ <i>RESEARCH / DEMO ONLY — NOT CANONICAL</i>"
    )
    return gateway.send_telegram_message(text, parse_mode="HTML")


def execute_candidate(candidate: dict, magic: int) -> dict:
    symbol = candidate["symbol"]
    gateway.SYMBOL = symbol
    gateway.MAGIC = magic
    payload = gateway.Signal(
        direction=candidate["direction"], symbol=symbol,
        entry=float(candidate["theoretical_entry"]), sl=float(candidate["sl"]),
        tp=float(candidate["tp"]), volume=float(candidate.get("volume", VOLUME)),
        signal_id=f"AUTHOR_REPLICA_MULTI_{candidate['trigger_time']}_{symbol}_{candidate['direction']}",
        source="AUTHOR_REPLICA_MULTI_FORWARD_TEST", status="APPROVED",
    )
    return gateway.execute_signal(payload)


def order_state_name(order) -> str:
    state = int(getattr(order, "state", -1))
    names = {
        getattr(mt5, "ORDER_STATE_STARTED", 0): "STARTED",
        getattr(mt5, "ORDER_STATE_PLACED", 1): "PLACED",
        getattr(mt5, "ORDER_STATE_CANCELED", 2): "CANCELED",
        getattr(mt5, "ORDER_STATE_PARTIAL", 3): "PARTIAL",
        getattr(mt5, "ORDER_STATE_FILLED", 4): "FILLED",
        getattr(mt5, "ORDER_STATE_REJECTED", 5): "REJECTED",
        getattr(mt5, "ORDER_STATE_EXPIRED", 6): "EXPIRED",
        getattr(mt5, "ORDER_STATE_REQUEST_ADD", 7): "REQUEST_ADD",
        getattr(mt5, "ORDER_STATE_REQUEST_MODIFY", 8): "REQUEST_MODIFY",
        getattr(mt5, "ORDER_STATE_REQUEST_CANCEL", 9): "REQUEST_CANCEL",
    }
    return names.get(state, f"UNKNOWN_{state}")


def _cancel_pending_order(order, state: dict) -> None:
    """Cancel one stale pending order and notify Telegram with the outcome.

    Expiry policy (SP2L_PENDING_TTL_MINUTES): a limit order that did not fill
    within its window no longer reflects the research setup's intended
    immediate-entry premise. Cancellation is runner-side account hygiene:
    never touches positions, foreign/manual orders, or strategy semantics.
    In DRY-RUN the cancel request is logged but not sent (gateway-style
    dry_run result), so the observe-only contract stays intact.
    """
    ticket = int(getattr(order, "ticket", 0) or 0)
    symbol = str(getattr(order, "symbol", "") or "")
    setup_ts = int(getattr(order, "time_setup", 0) or 0)
    age_minutes = (time.time() - setup_ts) / 60.0 if setup_ts else 0.0
    digits_info = mt5.symbol_info(symbol)
    digits = max(2, int(getattr(digits_info, "digits", 2) or 2)) if digits_info else 2

    cancel_request = {
        "action": mt5.TRADE_ACTION_REMOVE,
        "order": ticket,
    }

    live_flag = os.getenv("LIVE_TRADING_ENABLE", "false").lower() == "true"
    allow_flag = os.getenv("ALLOW_REAL_EXECUTION", "false").lower() == "true"
    if not (live_flag and allow_flag):
        result = {
            "ok": True, "dry_run": True, "retcode": None,
            "reason": "LIVE_TRADING_ENABLE=false",
        }
    else:
        account = mt5.account_info()
        if account is None or int(account.trade_mode) != 0:
            result = {"ok": False, "reason": "DEMO_ACCOUNT_REQUIRED"}
        else:
            send = mt5.order_send(cancel_request)
            if send is None:
                result = {"ok": False, "reason": "ORDER_SEND_NONE", "last_error": mt5.last_error()}
            else:
                result = {
                    "ok": send.retcode == mt5.TRADE_RETCODE_DONE,
                    "dry_run": False,
                    "retcode": send.retcode,
                    "comment": send.comment,
                }

    outcome = "CANCELLED" if result.get("ok") else f"CANCEL_FAILED({result.get('reason') or result.get('retcode')})"
    log_event({
        "event": "PENDING_ORDER_EXPIRED",
        "symbol": symbol, "order": ticket,
        "age_minutes": round(age_minutes, 1),
        "price_open": float(getattr(order, "price_open", 0.0) or 0.0),
        "sl": float(getattr(order, "sl", 0.0) or 0.0),
        "tp": float(getattr(order, "tp", 0.0) or 0.0),
        "cancel": result,
        "outcome": outcome,
        "canonical": False,
    })

    dt = display_time_from_mt5(setup_ts)
    text = (
        f"🟠 <b>SP2L — {symbol} — EXPIRED</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Order</b>   Pending Limit (unfilled)\n"
        f"📌 <b>Entry</b>   {float(getattr(order, 'price_open', 0.0) or 0.0):.{digits}f}\n"
        f"🛑 <b>SL</b>      {float(getattr(order, 'sl', 0.0) or 0.0):.{digits}f}\n"
        f"🎯 <b>TP</b>      {float(getattr(order, 'tp', 0.0) or 0.0):.{digits}f}\n"
        f"⏳ <b>Age</b>     {age_minutes:.0f} min · TTL {PENDING_TTL_MINUTES:.0f} min\n"
        f"✔️ <b>Action</b>  {outcome}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🕒 {dt:%H:%M:%S} (UTC+3:30) · {dt:%Y-%m-%d}\n"
        f"🆔 <code>{ticket}</code>\n"
        f"⚠️ <i>RESEARCH / DEMO ONLY — NOT CANONICAL</i>"
    )
    tg = gateway.send_telegram_message(text, parse_mode="HTML")
    state["order_states"].add(f"{ticket}:EXPIRY_NOTIFIED:{outcome}")
    log_event({
        "event": "TELEGRAM_PENDING_EXPIRED", "symbol": symbol,
        "order": ticket, "outcome": outcome,
        "telegram": {"success": tg.success, "detail": tg.detail},
        "canonical": False,
    })


def enforce_pending_order_expiry(cfg: dict, state: dict) -> None:
    """Cancel this runner's pending limit orders older than PENDING_TTL_MINUTES."""
    if PENDING_TTL_MINUTES <= 0:
        return
    symbol, magic = cfg["symbol"], cfg["magic"]
    active = mt5.orders_get(symbol=symbol) or []
    for order in active:
        ticket = int(getattr(order, "ticket", 0) or 0)
        if not ticket:
            continue
        order_magic = int(getattr(order, "magic", 0) or 0)
        if order_magic != magic and ticket not in state["orders"]:
            continue  # never touch foreign/manual orders
        order_type = int(getattr(order, "type", -1))
        if order_type not in (mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_SELL_LIMIT):
            continue  # only the runner's own pending limits expire
        setup_ts = int(getattr(order, "time_setup", 0) or 0)
        if not setup_ts:
            continue
        age_minutes = (time.time() - setup_ts) / 60.0
        if age_minutes < PENDING_TTL_MINUTES:
            continue
        marker = f"{ticket}:EXPIRY_NOTIFIED:"
        if any(s.startswith(marker) for s in state["order_states"]):
            continue  # expiry already handled for this ticket
        _cancel_pending_order(order, state)


def monitor_pending_order_lifecycle(cfg: dict, state: dict) -> None:
    """Observe broker-side pending-order state without changing execution semantics."""
    symbol, magic = cfg["symbol"], cfg["magic"]
    start = datetime.now(timezone.utc) - timedelta(hours=24)
    end = datetime.now(timezone.utc)
    orders = mt5.history_orders_get(start, end, group=symbol) or []
    active = mt5.orders_get(symbol=symbol) or []
    orders = list(orders) + list(active)
    seen_local = set()
    for order in sorted(orders, key=lambda x: (int(getattr(x, "time_setup", 0) or 0), int(getattr(x, "ticket", 0) or 0))):
        ticket = int(getattr(order, "ticket", 0) or 0)
        if not ticket or ticket in seen_local:
            continue
        seen_local.add(ticket)
        order_magic = int(getattr(order, "magic", 0) or 0)
        if order_magic != magic and ticket not in state["orders"]:
            continue
        state_name = order_state_name(order)
        marker = f"{ticket}:{state_name}"
        if marker in state["order_states"]:
            continue
        state["orders"].add(ticket)
        state["order_states"].add(marker)
        log_event({
            "event": "PENDING_ORDER_LIFECYCLE",
            "symbol": symbol,
            "order": ticket,
            "state": state_name,
            "state_code": int(getattr(order, "state", -1)),
            "type": int(getattr(order, "type", -1)),
            "type_time": int(getattr(order, "type_time", -1)),
            "time_setup": int(getattr(order, "time_setup", 0) or 0),
            "time_done": int(getattr(order, "time_done", 0) or 0),
            "magic": order_magic,
            "position_id": int(getattr(order, "position_id", 0) or 0),
            "position_by_id": int(getattr(order, "position_by_id", 0) or 0),
            "volume_initial": float(getattr(order, "volume_initial", 0.0) or 0.0),
            "volume_current": float(getattr(order, "volume_current", 0.0) or 0.0),
            "price_open": float(getattr(order, "price_open", 0.0) or 0.0),
            "price_current": float(getattr(order, "price_current", 0.0) or 0.0),
            "sl": float(getattr(order, "sl", 0.0) or 0.0),
            "tp": float(getattr(order, "tp", 0.0) or 0.0),
            "canonical": False,
        })


def _remember_position_links(state: dict, deal) -> None:
    """Persist the broker position id and both entry/exit order ids for correlation."""
    position = int(getattr(deal, "position_id", 0) or 0)
    order = int(getattr(deal, "order", 0) or 0)
    if position:
        state["positions"].add(position)
        state.setdefault("position_orders", {}).setdefault(str(position), set())
        if order:
            state["position_orders"][str(position)].add(order)
    if order:
        state["orders"].add(order)


def _reconcile_history_position_links(state: dict, symbol: str, magic: int) -> None:
    """Build position->orders/deals links from broker history before lifecycle filtering."""
    start = datetime.now(timezone.utc) - timedelta(hours=24)
    deals = mt5.history_deals_get(start, datetime.now(timezone.utc), group=symbol) or []
    for deal in deals:
        order = int(getattr(deal, "order", 0) or 0)
        position = int(getattr(deal, "position_id", 0) or 0)
        deal_magic = int(getattr(deal, "magic", 0) or 0)
        if deal_magic == magic or order in state["orders"] or position in state["positions"]:
            _remember_position_links(state, deal)


def monitor_symbol_lifecycle(cfg: dict, state: dict) -> None:
    symbol, magic, pip = cfg["symbol"], cfg["magic"], cfg["pip_size"]
    _reconcile_history_position_links(state, symbol, magic)
    start = datetime.now(timezone.utc) - timedelta(hours=24)
    deals = mt5.history_deals_get(start, datetime.now(timezone.utc), group=symbol) or []
    for deal in sorted(deals, key=lambda x: (int(x.time), int(x.ticket))):
        ticket = int(deal.ticket)
        if ticket in state["deals"]:
            continue
        order = int(getattr(deal, "order", 0) or 0)
        position = int(getattr(deal, "position_id", 0) or 0)
        deal_magic = int(getattr(deal, "magic", 0) or 0)
        position_orders = state.get("position_orders", {}).get(str(position), set())
        linked = (
            deal_magic == magic
            or order in state["orders"]
            or position in state["positions"]
            or bool(position_orders)
        )
        if not linked:
            continue
        _remember_position_links(state, deal)
        is_entry_deal = int(getattr(deal, "entry", -1)) == mt5.DEAL_ENTRY_IN
        entry_price = float(deal.price) if is_entry_deal else position_entry_price(deal, magic)
        if not is_entry_deal and entry_price is None:
            # Exit whose own-position entry cannot be resolved yet: defer the
            # notification to the next poll instead of sending wrong numbers.
            continue
        text = lifecycle_message(deal, symbol, pip, magic)
        result = gateway.send_telegram_message(text, parse_mode="HTML")
        exit_price = float(deal.price)
        signed_move = None
        pips_result = None
        if int(getattr(deal, "entry", -1)) != mt5.DEAL_ENTRY_IN and entry_price is not None and pip > 0:
            deal_type = getattr(deal, "type", None)
            side = "SELL" if deal_type == mt5.DEAL_TYPE_BUY else "BUY"
            signed_move = exit_price - entry_price if side == "BUY" else entry_price - exit_price
            pips_result = signed_move / pip
        profit = float(getattr(deal, "profit", 0.0))
        commission = float(getattr(deal, "commission", 0.0))
        swap = float(getattr(deal, "swap", 0.0))
        net = profit + commission + swap
        log_event({
            "event": "TELEGRAM_DEAL_LIFECYCLE", "symbol": symbol,
            "deal": ticket, "order": order, "position": position,
            "entry": int(getattr(deal, "entry", -1)),
            "reason": int(getattr(deal, "reason", -1)),
            "entry_price": entry_price,
            "exit_price": exit_price,
            "pips_result": pips_result,
            "profit": profit,
            "commission": commission,
            "swap": swap,
            "net": net,
            "telegram": {"success": result.success, "detail": result.detail},
            "canonical": False,
        })
        state["deals"].add(ticket)
    save_state(state)


def _resolve_terminal_path() -> str | None:
    """Explicit env override first, then the repo terminal auto-resolver."""
    env = os.getenv("MT5_TERMINAL_PATH")
    if env:
        return env
    try:
        import mt5_terminal_resolver
    except ModuleNotFoundError:
        try:
            from scripts import mt5_terminal_resolver  # type: ignore
        except ModuleNotFoundError:
            return None
    found = mt5_terminal_resolver.find_mt5_terminal()
    return str(found) if found else None


def main() -> None:
    mt5_path = _resolve_terminal_path()
    initialized = mt5.initialize(path=mt5_path) if mt5_path else mt5.initialize()
    if not initialized:
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

    account = mt5.account_info()
    if account is None or int(account.trade_mode) != 0:
        raise RuntimeError("DEMO-ONLY GUARD: a DEMO MT5 account is required")

    configs = []
    for index, base in enumerate(BASE_SYMBOLS):
        symbol = resolve_symbol(base)
        if symbol is None:
            log_event({"event": "SYMBOL_UNAVAILABLE", "base": base})
            continue
        if not mt5.symbol_select(symbol, True):
            log_event({"event": "SYMBOL_SELECT_FAILED", "symbol": symbol, "error": str(mt5.last_error())})
            continue
        cfg = symbol_config(symbol)
        cfg["magic"] = MAGIC_BASE + index + 1
        cfg["volume"] = _volume_for(base.upper().split(".")[0])
        configs.append(cfg)

    if not configs:
        raise RuntimeError("None of XAUUSD/EURUSD/BTCUSD could be resolved in MT5")

    log_event({
        "event": "START",
        "mode": "RESEARCH_AUTHOR_REPLICA_MULTI_SYMBOL_FORWARD_TEST",
        "canonical": False,
        "account_login": int(account.login),
        "account_server": str(account.server),
        "account_trade_mode": int(account.trade_mode),
        "config": {
            "pGapPrice": P_GAP_PRICE, "spikeMultiplier": SPIKE_MULTIPLIER,
            "maxSlDistance": MAX_SL_DISTANCE, "tpR": TP_R, "volume": VOLUME,
            "orderMode": ORDER_MODE, "slAnchor": SL_ANCHOR,
            "pendingTtlMinutes": PENDING_TTL_MINUTES,
            "symbols": configs,
        },
    })

    volume_summary = ", ".join(
        "{}={:.2f}".format(c["symbol"], c.get("volume", VOLUME)) for c in configs
    )
    # Self-declared execution mode: the session's own operator flags, as seen
    # by this process. LIVE-DEMO still requires the DEMO-ONLY account guard.
    startup_banner = gateway.send_telegram_message(
        "🟢 SP2L Forward Test — started\n"
        f"Account: {account.login} ({account.server}, DEMO)\n"
        f"Symbols: {', '.join(c['symbol'] for c in configs)}\n"
        f"Order mode: {ORDER_MODE}\n"
        f"Volume: {volume_summary} · TP {TP_R:.1f}R\n"
        f"{execution_mode_line()}\n"
        "⚠️ RESEARCH / DEMO ONLY — NOT CANONICAL"
    )
    log_event({
        "event": "START_TELEGRAM",
        "success": bool(getattr(startup_banner, "success", False)),
        "detail": getattr(startup_banner, "detail", None),
        "canonical": False,
    })

    state = load_state()
    state.setdefault("position_orders", {})
    deadline = None
    seconds = os.getenv("FORWARD_TEST_SECONDS")
    if seconds:
        deadline = time.time() + int(seconds)
    reconcile_state_from_events(state)
    save_state(state)
    seen_trigger = state["seen"]

    holder_pid = acquire_runner_lock()
    if holder_pid is not None:
        raise RuntimeError(
            f"Another forward runner is already active (pid {holder_pid}). "
            "Stop it first — two runners would duplicate every order."
        )

    try:
        while deadline is None or time.time() < deadline:
            for cfg in configs:
                symbol = cfg["symbol"]
                enforce_pending_order_expiry(cfg, state)
                monitor_pending_order_lifecycle(cfg, state)
                monitor_symbol_lifecycle(cfg, state)
                data = rates(symbol)
                if data is None:
                    continue
                candidate = detect(data, symbol)
                trigger_key = f"{symbol}:{candidate['trigger_time']}:{candidate['direction']}" if candidate else None
                if candidate is None or seen_trigger.get(symbol) == trigger_key:
                    continue

                candidate["signal_id"] = trigger_key
                if trigger_key not in state["notified"]:
                    telegram_result = send_signal(candidate, cfg["pip_size"])
                    telegram_success = bool(getattr(telegram_result, "success", False))
                    log_event({
                        "event": "TELEGRAM_SIGNAL",
                        "symbol": symbol,
                        "signal_id": trigger_key,
                        "success": telegram_success,
                        "detail": getattr(telegram_result, "detail", None),
                        "canonical": False,
                    })
                    if telegram_success:
                        state["notified"].add(trigger_key)
                    save_state(state)
                log_event({
                    "event": "CANDIDATE", "symbol": symbol,
                    "signal_id": trigger_key, "candidate": candidate,
                    "pip_size": cfg["pip_size"], "pip_method": cfg["pip_method"],
                    "f13_2x": {
                        "status": "SOURCE_CONFIRMED_RELATION_ONLY",
                        "secondary_entry": candidate["secondary_entry_2x"],
                        "formula": "Entry + 0.5 * (StopLoss - Entry)",
                        "execution": "NOT_EXECUTED_UNRESOLVED_LIFECYCLE",
                    },
                    "execution_semantics": ORDER_MODE,
                })
                tick = mt5.symbol_info_tick(symbol)
                log_event({
                    "event": "ORDER_ATTEMPT", "symbol": symbol,
                    "signal_id": trigger_key, "direction": candidate["direction"],
                    "entry": candidate["theoretical_entry"], "sl": candidate["sl"],
                    "tp": candidate["tp"], "volume": candidate.get("volume", VOLUME),
                    "bid": float(tick.bid) if tick else None,
                    "ask": float(tick.ask) if tick else None,
                    "magic": cfg["magic"], "canonical": False,
                })
                try:
                    result = execute_candidate(candidate, cfg["magic"])
                except Exception as exc:
                    result = {
                        "ok": False,
                        "error": f"execute_candidate_exception: {type(exc).__name__}: {exc}",
                    }
                # Persist execution identifiers immediately. MT5 may report a
                # closing deal with a different identifier and some brokers
                # may not carry the original magic onto the closing deal.
                result_order = int(result.get("order", 0) or 0)
                result_deal = int(result.get("deal", 0) or 0)
                if result_order:
                    state["orders"].add(result_order)
                log_event({
                    "event": "ORDER_RESULT", "symbol": symbol,
                    "signal_id": trigger_key, "result": result,
                    "tracked_order": result_order or None,
                    "tracked_deal": result_deal or None,
                    "demo_only": True, "success": bool(result.get("ok")),
                })
                if bool(result.get("ok")):
                    seen_trigger[symbol] = trigger_key
                save_state(state)
            maybe_send_daily_summary(state)
            time.sleep(POLL_SECONDS)
    finally:
        release_runner_lock()
        mt5.shutdown()


if __name__ == "__main__":
    main()
