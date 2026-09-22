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

BASE_SYMBOLS = ("XAUUSD", "EURUSD", "BTCUSD")
TIMEFRAME = mt5.TIMEFRAME_M1
P_GAP_PRICE = float(os.getenv("SP2L_P_GAP_PRICE", "1.0"))
SPIKE_MULTIPLIER = float(os.getenv("SP2L_SPIKE_MULTIPLIER", "1.5"))
MAX_SL_DISTANCE = float(os.getenv("SP2L_MAX_SL_DISTANCE", "10.0"))
TP_R = float(os.getenv("SP2L_TP_R", "1.0"))
VOLUME = float(os.getenv("SP2L_VOLUME", "0.01"))
POLL_SECONDS = float(os.getenv("SP2L_POLL_SECONDS", "2"))
ORDER_MODE = os.getenv("MT5_FORWARD_ORDER_MODE", "PENDING_LIMIT_RESEARCH")
MAGIC_BASE = int(os.getenv("SP2L_MAGIC_BASE", "26092200"))
IRAN_TZ = timezone(timedelta(hours=3, minutes=30))

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "forward-test"
RUNTIME = ROOT / "runtime"
ARTIFACTS.mkdir(parents=True, exist_ok=True)
RUNTIME.mkdir(parents=True, exist_ok=True)
EVENTS = ARTIFACTS / "SP2L_MULTI_SYMBOL_FORWARD_EVENTS.jsonl"
STATE_FILE = RUNTIME / "sp2l_multi_symbol_forward_state.json"

SL_ANCHOR = "SPIKE_CANDLE_EXTREME_RESEARCH"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


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
            "deals": {int(k) for k in raw.get("deals", [])},
            "orders": {int(k) for k in raw.get("orders", [])},
            "positions": {int(k) for k in raw.get("positions", [])},
        }
    except Exception:
        return {"seen": {}, "deals": set(), "orders": set(), "positions": set()}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps({
        "seen": state["seen"],
        "deals": sorted(state["deals"])[-1000:],
        "orders": sorted(state["orders"])[-1000:],
        "positions": sorted(state["positions"])[-1000:],
    }, indent=2), encoding="utf-8")


def position_entry_price(deal) -> float | None:
    position_id = int(getattr(deal, "position_id", 0) or 0)
    if not position_id:
        return None
    start = datetime.fromtimestamp(int(deal.time), timezone.utc) - timedelta(days=7)
    end = datetime.fromtimestamp(int(deal.time), timezone.utc) + timedelta(seconds=1)
    history = mt5.history_deals_get(start, end, position=position_id) or []
    entries = [d for d in history if int(getattr(d, "entry", -1)) == mt5.DEAL_ENTRY_IN]
    if not entries:
        return None
    return float(sorted(entries, key=lambda x: (int(x.time), int(x.ticket)))[0].price)


def lifecycle_message(deal, symbol: str, pip_size: float) -> str:
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

    entry = price if is_open else position_entry_price(deal)
    pips = None
    if not is_open and entry is not None and pip_size > 0:
        signed_move = price - entry if side == "BUY" else entry - price
        pips = signed_move / pip_size

    if is_open:
        icon = "🟢" if side == "BUY" else "🔴"
    else:
        icon = "🔵" if pips is not None and pips > 0 else "🟠"

    dt = display_time_from_mt5(int(deal.time))
    result = f"Result: {pips:+.0f} pips\n" if pips is not None else ""
    return (
        f"{icon} {symbol} {side} — {'OPEN' if is_open else 'CLOSE'}"
        f"{'' if is_open else chr(10) + 'Reason: ' + lifecycle_reason(deal)}\n\n"
        f"Entry: {entry:.{max(2, int(mt5.symbol_info(symbol).digits))}f}\n"
        f"{'Fill' if is_open else 'Exit'}: {price:.{max(2, int(mt5.symbol_info(symbol).digits))}f}\n"
        f"\n{result}"
        f"Volume: {float(deal.volume):.2f}\n"
        f"Profit: {profit:.2f}\n"
        f"Net: {net:.2f}\n\n"
        f"Date: {dt:%Y-%m-%d}\nTime: {dt:%H:%M:%S} (UTC+3:30)\n\n"
        f"Deal: {int(deal.ticket)}\nOrder: {int(deal.order)}\n"
        f"Position: {int(getattr(deal, 'position_id', 0) or 0)}\n"
        f"Mode: RESEARCH FORWARD MONITOR"
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


def send_signal(candidate: dict, pip_size: float) -> None:
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
        f"⚖️ <b>Volume</b>  {VOLUME:.2f}\n"
        f"🕒 <b>Signal</b>  {t:%H:%M:%S} (UTC+3:30)\n\n"
        f"🆔 <code>AUTHOR_REPLICA_MULTI_{candidate['trigger_time']}_{symbol}_{candidate['direction']}</code>\n"
        f"⚠️ <i>RESEARCH / DEMO ONLY — NOT CANONICAL</i>"
    )
    gateway.send_telegram_message(text, parse_mode="HTML")


def execute_candidate(candidate: dict, magic: int) -> dict:
    symbol = candidate["symbol"]
    gateway.SYMBOL = symbol
    gateway.MAGIC = magic
    payload = gateway.Signal(
        direction=candidate["direction"], symbol=symbol,
        entry=float(candidate["theoretical_entry"]), sl=float(candidate["sl"]),
        tp=float(candidate["tp"]), volume=VOLUME,
        signal_id=f"AUTHOR_REPLICA_MULTI_{candidate['trigger_time']}_{symbol}_{candidate['direction']}",
        source="AUTHOR_REPLICA_MULTI_FORWARD_TEST", status="APPROVED",
    )
    return gateway.execute_signal(payload)


def monitor_symbol_lifecycle(cfg: dict, state: dict) -> None:
    symbol, magic, pip = cfg["symbol"], cfg["magic"], cfg["pip_size"]
    start = datetime.now(timezone.utc) - timedelta(hours=24)
    deals = mt5.history_deals_get(start, datetime.now(timezone.utc)) or []
    for deal in sorted(deals, key=lambda x: (int(x.time), int(x.ticket))):
        ticket = int(deal.ticket)
        if ticket in state["deals"]:
            continue
        order = int(getattr(deal, "order", 0) or 0)
        position = int(getattr(deal, "position_id", 0) or 0)
        deal_magic = int(getattr(deal, "magic", 0) or 0)
        linked = (
            deal_magic == magic
            or order in state["orders"]
            or position in state["positions"]
        )
        if not linked:
            continue
        state["orders"].add(order) if order else None
        state["positions"].add(position) if position else None
        text = lifecycle_message(deal, symbol, pip)
        result = gateway.send_telegram_message(text)
        log_event({
            "event": "TELEGRAM_DEAL_LIFECYCLE", "symbol": symbol,
            "deal": ticket, "order": order, "position": position,
            "entry": int(getattr(deal, "entry", -1)),
            "reason": int(getattr(deal, "reason", -1)),
            "profit": float(getattr(deal, "profit", 0.0)),
            "telegram": {"success": result.success, "detail": result.detail},
            "canonical": False,
        })
        state["deals"].add(ticket)
    save_state(state)


def main() -> None:
    if not mt5.initialize():
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
            "symbols": configs,
        },
    })

    state = load_state()
    deadline = None
    seconds = os.getenv("FORWARD_TEST_SECONDS")
    if seconds:
        deadline = time.time() + int(seconds)
    seen_trigger = state["seen"]

    try:
        while deadline is None or time.time() < deadline:
            for cfg in configs:
                symbol = cfg["symbol"]
                monitor_symbol_lifecycle(cfg, state)
                data = rates(symbol)
                if data is None:
                    continue
                candidate = detect(data, symbol)
                trigger_key = f"{symbol}:{candidate['trigger_time']}:{candidate['direction']}" if candidate else None
                if candidate is None or seen_trigger.get(symbol) == trigger_key:
                    continue

                seen_trigger[symbol] = trigger_key
                candidate["signal_id"] = trigger_key
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
                send_signal(candidate, cfg["pip_size"])
                tick = mt5.symbol_info_tick(symbol)
                log_event({
                    "event": "ORDER_ATTEMPT", "symbol": symbol,
                    "signal_id": trigger_key, "direction": candidate["direction"],
                    "entry": candidate["theoretical_entry"], "sl": candidate["sl"],
                    "tp": candidate["tp"], "volume": VOLUME,
                    "bid": float(tick.bid) if tick else None,
                    "ask": float(tick.ask) if tick else None,
                    "magic": cfg["magic"], "canonical": False,
                })
                result = execute_candidate(candidate, cfg["magic"])
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
                save_state(state)
            time.sleep(POLL_SECONDS)
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
