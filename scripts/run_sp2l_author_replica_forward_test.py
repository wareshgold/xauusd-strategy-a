"""
Research-only SP2L author-replica forward test for MT5 DEMO.

This runner intentionally reproduces the repository's research implementation
geometry from research/harness/sp2l_author_replica_candidate.ts / v1:
- fixed -4/-3/-2/-1 candle window
- P-Gap price = 1.0
- spike multiplier = 1.5
- origin candle SL
- TP = 1R
- max SL distance = 10.0 price units

It is NOT canonical Strategy A and must never be used for real-money execution.

Execution note:
The research backtest exposes a completed trigger candle and its theoretical
trigger extreme as the entry. In live forward testing that exact historical
price is not knowable after the candle closes, so this runner records the
theoretical entry and executes a MARKET order at the first observed tick after
the completed trigger. This execution difference is explicitly experimental
and must not be promoted to canonical fill semantics.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1
P_GAP_PRICE = 1.0
SPIKE_MULTIPLIER = 1.5
MAX_SL_DISTANCE = 10.0
TP_R = 1.0
VOLUME = 0.01
MAGIC = 26091901
POLL_SECONDS = 2
MAX_OPEN_POSITIONS = 1
# Research-only source-aligned SL interpretation: the SL is anchored to the
# candle from which the spike originated. The exact body/wick/buffer semantics
# remain unresolved, so this is explicitly non-canonical.
SL_ANCHOR = "SPIKE_CANDLE_EXTREME_RESEARCH"
# Research-only demo execution: place a limit at the theoretical entry so the
# prior MARKET_AFTER_COMPLETED_TRIGGER crossed-entry/invalid-stops failure is
# not silently converted into a level change. Pending-order lifecycle remains
# unresolved and non-canonical.
DEMO_ORDER_MODE = "PENDING_LIMIT_RESEARCH"

# Set the execution mode BEFORE importing the gateway. The gateway reads its
# environment at module import time; setting it afterwards is too late.
os.environ.setdefault("MT5_FORWARD_ORDER_MODE", DEMO_ORDER_MODE)

from live_mt5_gateway import Signal, execute_signal
from telegram_client import send_telegram_message

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
ARTIFACTS = ROOT / "artifacts" / "forward-test"
RUNTIME.mkdir(parents=True, exist_ok=True)
ARTIFACTS.mkdir(parents=True, exist_ok=True)
EVENTS = ARTIFACTS / "SP2L_AUTHOR_REPLICA_FORWARD_EVENTS.jsonl"
STATE = RUNTIME / "sp2l_author_replica_forward_state.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(event: dict) -> None:
    event = {"ts_utc": utc_now(), **event}
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, separators=(",", ":")) + "\n")
    print(json.dumps(event, indent=2))


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


def init() -> None:
    mt5_path = _resolve_terminal_path()
    initialized = mt5.initialize(path=mt5_path) if mt5_path else mt5.initialize()
    if not initialized:
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    info = mt5.account_info()
    if info is None:
        raise RuntimeError(f"MT5 account_info failed: {mt5.last_error()}")
    if int(info.trade_mode) != 0:
        raise RuntimeError(
            f"DEMO-ONLY GUARD: account trade_mode={info.trade_mode}; expected DEMO(0)"
        )
    sym = mt5.symbol_info(SYMBOL)
    if sym is None:
        raise RuntimeError(f"Missing symbol {SYMBOL}")
    if not mt5.symbol_select(SYMBOL, True):
        raise RuntimeError(f"symbol_select failed: {mt5.last_error()}")
    if int(sym.trade_mode) not in (1, 2, 4):
        raise RuntimeError(f"Symbol not openable: trade_mode={sym.trade_mode}")
    log_event({
        "event": "START",
        "mode": "RESEARCH_AUTHOR_REPLICA_FORWARD_TEST",
        "canonical": False,
        "account_login": int(info.login),
        "account_server": str(info.server),
        "account_trade_mode": int(info.trade_mode),
        "symbol": SYMBOL,
        "config": {
            "pGapPrice": P_GAP_PRICE,
            "spikeMultiplier": SPIKE_MULTIPLIER,
            "maxSlDistance": MAX_SL_DISTANCE,
            "tpR": TP_R,
            "volume": VOLUME,
            "slAnchor": SL_ANCHOR,
            "demoOrderMode": DEMO_ORDER_MODE,
        },
    })


def rates(count: int = 10):
    data = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, count)
    if data is None or len(data) < 6:
        return None
    return data


def detect(candles):
    # Use the last FOUR COMPLETED M1 candles. The current forming candle is excluded.
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
        entry = float(trigger["low"])
        sl = float(spike["low"])
        risk = entry - sl
        if 0 < risk <= MAX_SL_DISTANCE:
            return {
                "direction": "BUY",
                "trigger_time": int(trigger["time"]),
                "theoretical_entry": entry,
                "sl": sl,
                "risk": risk,
                "tp": entry + TP_R * risk,
                "secondary_entry_2x": entry + 0.5 * (sl - entry),
            }

    if sell:
        entry = float(trigger["high"])
        sl = float(spike["high"])
        risk = sl - entry
        if 0 < risk <= MAX_SL_DISTANCE:
            return {
                "direction": "SELL",
                "trigger_time": int(trigger["time"]),
                "theoretical_entry": entry,
                "sl": sl,
                "risk": risk,
                "tp": entry - TP_R * risk,
                "secondary_entry_2x": entry + 0.5 * (sl - entry),
            }
    return None


def telegram_send(text: str) -> dict:
    result = send_telegram_message(text)
    return {"success": result.success, "detail": result.detail}


def format_order_status_message(candidate: dict, result: dict) -> str:
    direction = candidate["direction"]
    icon = "🟢" if direction == "BUY" else "🔴"
    entry = float(candidate["theoretical_entry"])
    sl = float(candidate["sl"])
    tp = float(candidate["tp"])
    risk = abs(entry - sl)
    risk_pips = risk / PIP_SIZE
    trigger_time = datetime.fromtimestamp(
        int(candidate["trigger_time"]), timezone.utc
    ).astimezone(timezone(timedelta(hours=3, minutes=30)))

    accepted = bool(result.get("ok")) and not bool(result.get("dry_run"))
    if accepted:
        title = f"{icon} <b>SP2L — XAUUSD {direction} — PENDING ORDER ACCEPTED</b>"
        order_line = f"📦 <b>Order</b>   Pending Limit accepted by MT5"
    else:
        title = f"⚠️ <b>SP2L — XAUUSD {direction} — ORDER REJECTED</b>"
        order_line = f"📦 <b>Order</b>   Not placed"

    reason = result.get("reason")
    reason_line = f"\n❗ <b>Reason</b>  {reason}" if reason else ""
    order_id = result.get("order")
    order_line += f"\n🆔 <b>Order ID</b> {order_id}" if order_id else ""

    return (
        f"{title}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Entry</b>   {entry:.2f}\n"
        f"🛑 <b>SL</b>      {sl:.2f}\n"
        f"🎯 <b>TP (1R)</b>  {tp:.2f}\n"
        f"📏 <b>Risk</b>    {risk:.2f}  ({risk_pips:.0f} pip)\n"
        f"{order_line}\n"
        f"🕒 <b>Signal</b>  {trigger_time.strftime('%H:%M:%S')} (UTC+3:30)\n"
        f"🆔 <code>{candidate['signal_id']}</code>"
        f"{reason_line}"
    )

def open_positions():
    return list(mt5.positions_get(symbol=SYMBOL) or [])


def send_demo_order(signal):
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        return {"ok": False, "reason": f"NO_TICK:{mt5.last_error()}"}

    direction = signal["direction"]
    market_price = float(tick.ask if direction == "BUY" else tick.bid)
    payload = Signal(
        direction=direction,
        symbol=SYMBOL,
        entry=float(signal["theoretical_entry"]),
        sl=float(signal["sl"]),
        tp=float(signal["tp"]),
        volume=VOLUME,
        signal_id=signal["signal_id"],
        source="AUTHOR_REPLICA_FORWARD_TEST",
        status="APPROVED",
    )
    result = execute_signal(payload)
    return {**result, "observed_market_price": market_price, "theoretical_entry": signal["theoretical_entry"]}


LIFECYCLE_STATE = RUNTIME / "sp2l_author_replica_telegram_lifecycle_state.json"
PIP_SIZE = float(os.getenv("XAUUSD_PIP_SIZE", "0.01"))


def load_lifecycle_state() -> dict:
    try:
        payload = json.loads(LIFECYCLE_STATE.read_text(encoding="utf-8"))
        return {
            "deals": {int(x) for x in payload.get("deals", [])},
            "orders": {int(x) for x in payload.get("orders", [])},
            "positions": {int(x) for x in payload.get("positions", [])},
        }
    except Exception:
        return {"deals": set(), "orders": set(), "positions": set()}


def save_lifecycle_state(state: dict) -> None:
    LIFECYCLE_STATE.parent.mkdir(parents=True, exist_ok=True)
    LIFECYCLE_STATE.write_text(json.dumps({
        "deals": sorted(state["deals"])[-500:],
        "orders": sorted(state["orders"])[-500:],
        "positions": sorted(state["positions"])[-500:],
    }, indent=2), encoding="utf-8")


def lifecycle_levels(deal) -> tuple[float | None, float | None]:
    sl = tp = None
    position_id = int(getattr(deal, "position_id", 0) or 0)
    if position_id:
        positions = mt5.positions_get(ticket=position_id) or []
        if positions:
            sl = float(getattr(positions[0], "sl", 0.0) or 0.0) or None
            tp = float(getattr(positions[0], "tp", 0.0) or 0.0) or None
    order_id = int(getattr(deal, "order", 0) or 0)
    if (sl is None or tp is None) and order_id:
        orders = mt5.history_orders_get(ticket=order_id) or []
        if orders:
            order = orders[0]
            sl = sl if sl is not None else (float(getattr(order, "sl", 0.0) or 0.0) or None)
            tp = tp if tp is not None else (float(getattr(order, "tp", 0.0) or 0.0) or None)
    return sl, tp


def lifecycle_reason(deal) -> str:
    reason = int(getattr(deal, "reason", -1))
    if reason == getattr(mt5, "DEAL_REASON_TP", -999):
        return "TAKE PROFIT"
    if reason == getattr(mt5, "DEAL_REASON_SL", -998):
        return "STOP LOSS"
    return "CLOSE"


def position_entry_price(deal, magic: int | None = None) -> float | None:
    """Recover the original position entry price for a closing deal.

    The ``position=`` form of ``history_deals_get`` must be called WITHOUT a
    date range: when a date range is passed alongside ``position=``, the
    terminal ignores the position filter and returns every deal in the range.
    Entry deals are additionally filtered to this runner's magic so unrelated
    positions can never leak into the computation; with no matching entry the
    caller defers the notification instead of reporting wrong numbers.
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


def result_pips(side: str, entry: float | None, exit_price: float) -> float | None:
    if entry is None:
        return None
    signed_move = exit_price - entry if side == "BUY" else entry - exit_price
    return signed_move / PIP_SIZE


def lifecycle_message(deal, magic: int | None = None) -> str:
    is_open = int(getattr(deal, "entry", -1)) == mt5.DEAL_ENTRY_IN
    deal_type = getattr(deal, "type", None)
    if is_open:
        side = "BUY" if deal_type == mt5.DEAL_TYPE_BUY else "SELL"
    else:
        side = "SELL" if deal_type == mt5.DEAL_TYPE_BUY else "BUY"
    price = float(deal.price)
    sl, tp = lifecycle_levels(deal)
    profit = float(getattr(deal, "profit", 0.0))
    commission = float(getattr(deal, "commission", 0.0))
    swap = float(getattr(deal, "swap", 0.0))
    net = profit + commission + swap
    iran_time = datetime.fromtimestamp(int(deal.time), timezone.utc).astimezone(
        timezone.utc
    ).astimezone(timezone(timedelta(hours=3, minutes=30)))
    reason = "" if is_open else f"\nReason: {lifecycle_reason(deal)}"
    sl_text = f"{sl:.2f}" if sl is not None else "NOT SET"
    tp_text = f"{tp:.2f}" if tp is not None else "NOT SET"
    entry_price = price if is_open else position_entry_price(deal, magic)
    pips = None if is_open else result_pips(side, entry_price, price)
    pips_text = f"{pips:+.0f} pips" if pips is not None else "N/A"
    title = (
        f"🟢 XAUUSD {side} — OPEN" if is_open else
        f"🔵 XAUUSD {side} — CLOSE" if pips is not None and pips > 0 else
        f"🟠 XAUUSD {side} — CLOSE"
    )
    result_line = f"Result: {pips_text}\n" if not is_open else ""
    entry_str = f"{entry_price:.2f}" if entry_price is not None else "n/a (unlinked)"
    return (
        f"{title}{reason}\n\n"
        f"Entry: {entry_str}\n"
        f"{'Fill' if is_open else 'Exit'}: {price:.2f}\n"
        f"SL: {sl_text}\n"
        f"TP: {tp_text}\n\n"
        f"{result_line}"
        f"Volume: {float(deal.volume):.2f}\n"
        f"Profit: {profit:.2f}\n"
        f"Net: {net:.2f}\n\n"
        f"Date: {iran_time.strftime('%Y-%m-%d')}\n"
        f"Time: {iran_time.strftime('%H:%M:%S')} (UTC+3:30)\n\n"
        f"Deal: {int(deal.ticket)}\n"
        f"Order: {int(deal.order)}\n"
        f"Position: {int(getattr(deal, 'position_id', 0) or 0)}\n"
        f"Mode: RESEARCH FORWARD MONITOR"
    )


def monitor_trade_lifecycle(state: dict) -> None:
    start = datetime.now(timezone.utc) - timedelta(minutes=5)
    deals = mt5.history_deals_get(start, datetime.now(timezone.utc))
    if deals is None:
        return

    for deal in sorted(deals, key=lambda x: (int(x.time), int(x.ticket))):
        ticket = int(deal.ticket)
        order = int(getattr(deal, "order", 0) or 0)
        position = int(getattr(deal, "position_id", 0) or 0)
        magic = int(getattr(deal, "magic", 0) or 0)

        linked = (
            magic == MAGIC
            or (order and order in state["orders"])
            or (position and position in state["positions"])
        )
        if not linked or ticket in state["deals"]:
            continue

        if order:
            state["orders"].add(order)
        if position:
            state["positions"].add(position)

        is_entry_deal = int(getattr(deal, "entry", -1)) == mt5.DEAL_ENTRY_IN
        entry_price = float(deal.price) if is_entry_deal else position_entry_price(deal, MAGIC)
        if not is_entry_deal and entry_price is None:
            # Exit whose own-position entry cannot be resolved yet: defer the
            # notification to the next poll instead of sending wrong numbers.
            continue
        telegram_result = telegram_send(lifecycle_message(deal, MAGIC))
        log_event({
            "event": "TELEGRAM_DEAL_LIFECYCLE",
            "deal": ticket,
            "order": order,
            "position": position,
            "entry": int(getattr(deal, "entry", -1)),
            "reason": int(getattr(deal, "reason", -1)),
            "profit": float(getattr(deal, "profit", 0.0)),
            "commission": float(getattr(deal, "commission", 0.0)),
            "swap": float(getattr(deal, "swap", 0.0)),
            "telegram": telegram_result,
            "canonical": False,
        })
        state["deals"].add(ticket)
        save_lifecycle_state(state)



def main():
    init()
    seen_trigger = None
    lifecycle_state = load_lifecycle_state()
    deadline = None
    seconds = os.getenv("FORWARD_TEST_SECONDS")
    if seconds:
        deadline = time.time() + int(seconds)

    try:
        while deadline is None or time.time() < deadline:
            data = rates()
            monitor_trade_lifecycle(lifecycle_state)
            if data is None:
                time.sleep(POLL_SECONDS)
                continue

            candidate = detect(data)
            if candidate is not None and candidate["trigger_time"] != seen_trigger:
                seen_trigger = candidate["trigger_time"]
                candidate["signal_id"] = f"AUTHOR_REPLICA_FT_{seen_trigger}_{candidate['direction']}"
                signal_id = f"AUTHOR_REPLICA_FT_{seen_trigger}_{candidate['direction']}"
                log_event({
                    "event": "CANDIDATE",
                    "signal_id": signal_id,
                    "candidate": candidate,
                    "f13_2x": {
                        "status": "SOURCE_CONFIRMED_RELATION_ONLY",
                        "secondary_entry": candidate["secondary_entry_2x"],
                        "formula": "Entry + 0.5 * (StopLoss - Entry)",
                        "execution": "NOT_EXECUTED_UNRESOLVED_LIFECYCLE",
                        "sl_anchor": SL_ANCHOR,
                    },
                    "execution_semantics": "PENDING_LIMIT_RESEARCH",
                })
                # Do not notify Telegram before the broker result. A candidate
                # is not a trade, and a rejected order must never look like one.
                tick_before_order = mt5.symbol_info_tick(SYMBOL)
                log_event({
                    "event": "ORDER_ATTEMPT",
                    "signal_id": signal_id,
                    "direction": candidate["direction"],
                    "order_mode": DEMO_ORDER_MODE,
                    "entry": candidate["theoretical_entry"],
                    "sl": candidate["sl"],
                    "tp": candidate["tp"],
                    "volume": VOLUME,
                    "bid": float(tick_before_order.bid) if tick_before_order else None,
                    "ask": float(tick_before_order.ask) if tick_before_order else None,
                    "mt5_last_error_before": mt5.last_error(),
                    "reason": "SIGNAL_APPROVED_FOR_RESEARCH_EXECUTION",
                    "canonical": False,
                })
                result = send_demo_order(candidate)
                log_event({
                    "event": "ORDER_RESULT",
                    "signal_id": signal_id,
                    "result": result,
                    "mt5_last_error_after": mt5.last_error(),
                    "demo_only": True,
                    "success": bool(result.get("ok")),
                })
                if not result.get("ok"):
                    log_event({
                        "event": "ORDER_REJECTED",
                        "signal_id": signal_id,
                        "direction": candidate["direction"],
                        "entry": candidate["theoretical_entry"],
                        "sl": candidate["sl"],
                        "tp": candidate["tp"],
                        "volume": VOLUME,
                        "bid": float(tick_before_order.bid) if tick_before_order else None,
                        "ask": float(tick_before_order.ask) if tick_before_order else None,
                        "reason": result.get("reason", "UNKNOWN_EXECUTION_FAILURE"),
                        "retcode": result.get("retcode"),
                        "comment": result.get("comment"),
                        "last_error": result.get("last_error", mt5.last_error()),
                        "order_mode": DEMO_ORDER_MODE,
                        "canonical": False,
                    })
                    telegram_result = telegram_send(format_order_status_message(candidate, result))
                    log_event({
                        "event": "TELEGRAM_ORDER_STATUS",
                        "signal_id": signal_id,
                        "status": "REJECTED",
                        "result": telegram_result,
                        "canonical": False,
                    })
                else:
                    log_event({
                        "event": "ORDER_PLACED",
                        "signal_id": signal_id,
                        "direction": candidate["direction"],
                        "entry": candidate["theoretical_entry"],
                        "sl": candidate["sl"],
                        "tp": candidate["tp"],
                        "volume": VOLUME,
                        "order": result.get("order"),
                        "deal": result.get("deal"),
                        "retcode": result.get("retcode"),
                        "comment": result.get("comment"),
                        "order_mode": DEMO_ORDER_MODE,
                        "dry_run": result.get("dry_run"),
                        "canonical": False,
                    })
                    if not result.get("dry_run"):
                        telegram_result = telegram_send(format_order_status_message(candidate, result))
                        log_event({
                            "event": "TELEGRAM_ORDER_STATUS",
                            "signal_id": signal_id,
                            "status": "PENDING_ORDER_ACCEPTED",
                            "result": telegram_result,
                            "canonical": False,
                        })

                # Do not retry or move the strategy levels when the theoretical
                # entry has already been crossed. Fill/activation semantics are
                # unresolved; this is recorded as an execution miss for research.
                if result.get("reason") == "INVALID_STOPS_AT_CURRENT_MARKET":
                    market = float(result["observed_market_price"])
                    theoretical = float(result["theoretical_entry"])
                    drift = (
                        market - theoretical
                        if candidate["direction"] == "BUY"
                        else theoretical - market
                    )
                    log_event({
                        "event": "EXECUTION_MISS",
                        "signal_id": signal_id,
                        "direction": candidate["direction"],
                        "theoretical_entry": theoretical,
                        "observed_market_price": market,
                        "entry_drift_in_favor": drift,
                        "reason": "MARKET_MOVED_PAST_THEORETICAL_ENTRY_BEFORE_EXECUTION",
                        "action": "NO_RETRY_NO_LEVEL_MOVE",
                        "canonical": False,
                        "note": "Execution/fill semantics remain unresolved; candidate retained for research audit.",
                    })

            time.sleep(POLL_SECONDS)
    finally:
        mt5.shutdown()
        log_event({"event": "STOP"})


if __name__ == "__main__":
    main()


