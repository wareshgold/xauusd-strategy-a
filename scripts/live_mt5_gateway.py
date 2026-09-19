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
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import MetaTrader5 as mt5

from live_journal import record_market_snapshot, record_signal, record_trade


SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
MAGIC = int(os.getenv("MT5_MAGIC", "26091901"))
DEVIATION = int(os.getenv("MT5_DEVIATION_POINTS", "30"))
POLL_SECONDS = float(os.getenv("POLL_SECONDS", "2"))
SIGNAL_FILE = Path(os.getenv("SIGNAL_FILE", "runtime/approved_signal.json"))
LIVE_TRADING_ENABLE = os.getenv("LIVE_TRADING_ENABLE", "false").lower() == "true"
MAX_OPEN_POSITIONS = int(os.getenv("MAX_OPEN_POSITIONS", "1"))

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
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    body = urlencode({"chat_id": TELEGRAM_CHAT_ID, "text": text}).encode()
    try:
        req = Request(url, data=body, method="POST")
        with urlopen(req, timeout=10) as response:
            return 200 <= response.status < 300
    except Exception as exc:
        print(f"[telegram] send failed: {exc}")
        return False


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
    lines = [
        f"SP2L SIGNAL — {signal.direction}",
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
    payload = json.loads(SIGNAL_FILE.read_text(encoding="utf-8"))
    return Signal.from_json(payload)


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
    last_status = None
    telegram_send(
        "SP2L Live Gateway started\n"
        f"Symbol: {SYMBOL}\n"
        f"Mode: {'LIVE' if LIVE_TRADING_ENABLE else 'DRY-RUN'}"
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
                    "LIVE" if LIVE_TRADING_ENABLE else "DRY-RUN",
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
                    "LIVE" if LIVE_TRADING_ENABLE else "DRY-RUN",
                    result,
                ))
                archive_signal()

            time.sleep(POLL_SECONDS)
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
