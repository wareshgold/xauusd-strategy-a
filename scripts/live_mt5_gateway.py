"""Live MT5 execution gateway with Telegram/echo output.

IMPORTANT:
- This module does NOT discover or define Strategy A geometry.
- It accepts an externally produced/approved signal payload.
- LIVE_TRADING_ENABLE defaults to false.
- Keep strategy detection separate from execution.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

try:
    from live_journal import record_market_snapshot, record_signal, record_trade, read_jsonl, SIGNALS
    from telegram_client import send_telegram_message
except ModuleNotFoundError:
    from scripts.live_journal import record_market_snapshot, record_signal, record_trade, read_jsonl, SIGNALS
    from scripts.telegram_client import send_telegram_message


SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
MAGIC = int(os.getenv("MT5_MAGIC", "26091901"))
DEVIATION = int(os.getenv("MT5_DEVIATION_POINTS", "30"))
POLL_SECONDS = float(os.getenv("POLL_SECONDS", "2"))
SIGNAL_FILE = Path(os.getenv("SIGNAL_FILE", "runtime/approved_signal.json"))
LIVE_TRADING_ENABLE = os.getenv("LIVE_TRADING_ENABLE", "false").lower() == "true"
# Double gate: even with LIVE_TRADING_ENABLE=true, real order_send additionally
# requires ALLOW_REAL_EXECUTION=true. One forgotten flag can never go live.
ALLOW_REAL_EXECUTION = os.getenv("ALLOW_REAL_EXECUTION", "false").lower() == "true"
# Hard real-execution blocker (third layer): symbol trade modes that allow
# OPENING new positions (MetaTrader5 SYMBOL_TRADE_MODE_*: 1=LONGONLY,
# 2=SHORTONLY, 4=FULL). Anything else — DISABLED (0), CLOSEONLY (3), or
# unknown/unavailable — must never reach an open-order request. This is
# verified against the live terminal immediately before order_send,
# regardless of any operator flags (fail-closed).
OPENABLE_SYMBOL_TRADE_MODES = {1, 2, 4}
SYMBOL_TRADE_MODE_NAMES = {
    0: "DISABLED",
    1: "LONGONLY",
    2: "SHORTONLY",
    3: "CLOSEONLY",
    4: "FULL",
}
MAX_OPEN_POSITIONS = int(os.getenv("MAX_OPEN_POSITIONS", "1"))
# Optional bounded run (smoke tests). 0 / unset = run until stopped.
MAX_RUN_SECONDS = float(os.getenv("GATEWAY_MAX_SECONDS", "0")) or None

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


@dataclass(frozen=True)
class Signal:
    direction: str
    symbol: str
    entry: float
    sl: float
    tp: float
    volume: float
    signal_id: str
    source: str
    status: str

    @classmethod
    def from_json(cls, payload: dict) -> "Signal":
        required = ["direction", "symbol", "entry", "sl", "tp", "volume", "signal_id", "source", "status"]
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"Missing signal fields: {missing}")
        direction = str(payload["direction"]).upper()
        if direction not in {"BUY", "SELL"}:
            raise ValueError("direction must be BUY or SELL")
        if str(payload["status"]).upper() != "APPROVED":
            raise ValueError("signal status must be APPROVED")
        if str(payload["symbol"]) != SYMBOL:
            raise ValueError(f"signal symbol {payload['symbol']} != configured {SYMBOL}")
        for field in ("entry", "sl", "tp", "volume"):
            value = float(payload[field])
            if value <= 0:
                raise ValueError(f"{field} must be > 0")
        if float(payload["volume"]) <= 0:
            raise ValueError("volume must be > 0")
        return cls(
            direction=direction,
            symbol=SYMBOL,
            entry=float(payload["entry"]),
            sl=float(payload["sl"]),
            tp=float(payload["tp"]),
            volume=float(payload["volume"]),
            signal_id=str(payload["signal_id"]),
            source=str(payload["source"]),
            status="APPROVED",
        )


def telegram_send(text: str) -> bool:
    """Delegates to the shared Telegram client (same env vars, same behavior)."""
    result = send_telegram_message(text)
    if not result.success and result.detail != "NOT_CONFIGURED":
        print(f"[telegram] send failed: {result.detail}")
    return result.success


def mt5_initialize() -> None:
    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    if not mt5.symbol_select(SYMBOL, True):
        raise RuntimeError(f"symbol_select failed: {mt5.last_error()}")


def account_snapshot() -> dict:
    account = mt5.account_info()
    terminal = mt5.terminal_info()
    tick = mt5.symbol_info_tick(SYMBOL)
    return {
        "server": account.server if account else None,
        "login": account.login if account else None,
        "trade_allowed": bool(terminal.trade_allowed) if terminal else None,
        "connected": bool(terminal.connected) if terminal else None,
        "bid": float(tick.bid) if tick else None,
        "ask": float(tick.ask) if tick else None,
        "time_utc": datetime.now(timezone.utc).isoformat(),
    }


def open_positions() -> list:
    positions = mt5.positions_get(symbol=SYMBOL)
    return list(positions or [])


def format_signal(signal: Signal, mode: str, result: dict | None = None) -> str:
    title = "Nexora EXECUTION" if result is not None else "Nexora SIGNAL"
    lines = [
        f"{title} — {signal.direction}",
        f"Symbol: {signal.symbol}",
        f"Entry: {signal.entry}",
        f"SL: {signal.sl}",
        f"TP: {signal.tp}",
        f"Volume: {signal.volume}",
        f"Signal ID: {signal.signal_id}",
        f"Source: {signal.source}",
        f"Mode: {mode}",
    ]
    if result:
        lines.extend([
            f"MT5 retcode: {result.get('retcode')}",
            f"Order: {result.get('order')}",
            f"Deal: {result.get('deal')}",
            f"Comment: {result.get('comment')}",
        ])
    return "\n".join(lines)


def effective_mode() -> str:
    """Truthful mode label: LIVE only when BOTH real-execution keys are set."""
    return "LIVE" if (LIVE_TRADING_ENABLE and ALLOW_REAL_EXECUTION) else "DRY-RUN"


def execute_signal(signal: Signal) -> dict:
    positions = open_positions()
    if len(positions) >= MAX_OPEN_POSITIONS:
        return {"ok": False, "reason": "MAX_OPEN_POSITIONS", "open_positions": len(positions)}

    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        return {"ok": False, "reason": "NO_TICK"}

    price = float(tick.ask if signal.direction == "BUY" else tick.bid)
    order_type = mt5.ORDER_TYPE_BUY if signal.direction == "BUY" else mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": signal.volume,
        "type": order_type,
        "price": price,
        "sl": signal.sl,
        "tp": signal.tp,
        "deviation": DEVIATION,
        "magic": MAGIC,
        "comment": f"SP2L:{signal.signal_id}"[:31],
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    if not LIVE_TRADING_ENABLE:
        return {
            "ok": True,
            "dry_run": True,
            "request": request,
            "retcode": None,
            "reason": "LIVE_TRADING_ENABLE=false",
        }

    if not ALLOW_REAL_EXECUTION:
        return {
            "ok": True,
            "dry_run": True,
            "request": request,
            "retcode": None,
            "reason": "ALLOW_REAL_EXECUTION!=true",
        }

    # Demo-only blocker: this execution test must never submit to a real account.
    account = mt5.account_info()
    account_trade_mode = int(account.trade_mode) if account is not None else None
    if account_trade_mode != 0:  # MetaTrader5 ACCOUNT_TRADE_MODE_DEMO
        return {
            "ok": False,
            "reason": "DEMO_ACCOUNT_REQUIRED",
            "account_trade_mode": account_trade_mode,
        }

    # Hard real-execution blocker (layer 4): refuse open orders on symbols
    # whose live trade mode forbids opening (e.g. CLOSEONLY). Checked against
    # the terminal's CURRENT state, immediately before order_send; missing
    # symbol info fails closed.
    info = mt5.symbol_info(SYMBOL)
    trade_mode = int(info.trade_mode) if info is not None else None
    if trade_mode is None or trade_mode not in OPENABLE_SYMBOL_TRADE_MODES:
        return {
            "ok": False,
            "reason": "SYMBOL_NOT_OPENABLE",
            "symbol_trade_mode": trade_mode,
            "trade_mode_name": SYMBOL_TRADE_MODE_NAMES.get(trade_mode, "UNKNOWN")
            if trade_mode is not None
            else "UNAVAILABLE",
        }

    result = mt5.order_send(request)
    if result is None:
        return {"ok": False, "reason": "ORDER_SEND_NONE", "last_error": mt5.last_error()}

    return {
        "ok": result.retcode == mt5.TRADE_RETCODE_DONE,
        "dry_run": False,
        "retcode": result.retcode,
        "order": result.order,
        "deal": result.deal,
        "comment": result.comment,
    }


def read_signal() -> Signal | None:
    if not SIGNAL_FILE.exists():
        return None
    payload = json.loads(SIGNAL_FILE.read_text(encoding="utf-8-sig"))
    return Signal.from_json(payload)



def signal_already_seen(signal_id: str) -> bool:
    return any(str(row.get("signal_id")) == signal_id for row in read_jsonl(SIGNALS))

def archive_signal() -> None:
    if not SIGNAL_FILE.exists():
        return
    archive_dir = SIGNAL_FILE.parent / "processed"
    archive_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = archive_dir / f"{stamp}_{SIGNAL_FILE.name}"
    SIGNAL_FILE.replace(target)


def main() -> None:
    mt5_initialize()
    started_at = time.time()
    last_status = None
    telegram_send(
        "Nexora Gateway started\n"
        f"Symbol: {SYMBOL}\n"
        f"Mode: {effective_mode()}"
    )

    try:
        while True:
            snapshot = account_snapshot()
            status_key = (
                snapshot["server"],
                snapshot["connected"],
                snapshot["trade_allowed"],
            )
            if status_key != last_status:
                print(json.dumps({"gateway": snapshot}, indent=2))
                last_status = status_key
            record_market_snapshot(snapshot)

            signal = read_signal()
            if signal:
                if signal_already_seen(signal.signal_id):
                    duplicate = {
                        "signal_id": signal.signal_id,
                        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        "symbol": signal.symbol,
                        "direction": signal.direction,
                        "signal_entry": signal.entry,
                        "sl": signal.sl,
                        "tp": signal.tp,
                        "volume": signal.volume,
                        "source": signal.source,
                        "status": "DUPLICATE_REJECTED",
                        "reason": "DUPLICATE_SIGNAL_ID",
                    }
                    record_signal(duplicate)
                    print(json.dumps({"signal_id": signal.signal_id, "execution": {"ok": False, "reason": "DUPLICATE_SIGNAL_ID"}}, indent=2))
                    telegram_send(
                        format_signal(
                            signal,
                            effective_mode(),
                            {"retcode": None, "order": None, "deal": None, "comment": "DUPLICATE_SIGNAL_ID"},
                        )
                    )
                    archive_signal()
                    time.sleep(POLL_SECONDS)
                    continue
                record_signal({
                    "signal_id": signal.signal_id,
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "symbol": signal.symbol,
                    "direction": signal.direction,
                    "signal_entry": signal.entry,
                    "sl": signal.sl,
                    "tp": signal.tp,
                    "volume": signal.volume,
                    "source": signal.source,
                    "status": "APPROVED",
                })
                message = format_signal(
                    signal,
                    effective_mode(),
                )
                telegram_send(message)

                result = execute_signal(signal)
                record_trade({
                    "signal_id": signal.signal_id,
                    "symbol": signal.symbol,
                    "direction": signal.direction,
                    "signal_entry": signal.entry,
                    "sl": signal.sl,
                    "tp": signal.tp,
                    "volume": signal.volume,
                    "execution_timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "status": "DRY_RUN" if result.get("dry_run") else ("OPEN" if result.get("ok") else "EXECUTION_FAILED"),
                    "order_id": result.get("order"),
                    "deal_id": result.get("deal"),
                    "retcode": result.get("retcode"),
                    "comment": result.get("comment"),
                    "execution_json": result,
                })
                print(json.dumps({
                    "signal_id": signal.signal_id,
                    "execution": result,
                }, indent=2))

                telegram_send(format_signal(
                    signal,
                    effective_mode(),
                    result,
                ))
                archive_signal()

            if MAX_RUN_SECONDS and time.time() - started_at >= MAX_RUN_SECONDS:
                print(json.dumps({"gateway": "bounded_run_complete", "max_run_seconds": MAX_RUN_SECONDS}))
                break
            time.sleep(POLL_SECONDS)
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
