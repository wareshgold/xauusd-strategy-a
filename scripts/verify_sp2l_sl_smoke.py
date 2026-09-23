"""Safe MT5 gateway SL/TP smoke test.

Default mode is DRY-RUN and never sends an order.
Use --place-cancel-test only for a demo account and only after explicitly
enabling both execution gates. The test creates a synthetic pending limit
away from the current market, verifies broker-stored Entry/SL/TP, then
cancels the pending order before it can be used as a strategy signal.

This validates execution plumbing only; it does not define Strategy A geometry.
"""

from __future__ import annotations

import argparse
import os

import MetaTrader5 as mt5

from live_mt5_gateway import Signal, execute_signal
from mt5_terminal_resolver import find_mt5_terminal


def _synthetic_signal(symbol: str, direction: str, tick, point: float) -> Signal:
    direction = direction.upper()
    if direction == "BUY":
        entry = float(tick.ask) - max(100 * point, 0.50)
        sl = entry - max(50 * point, 0.25)
        tp = entry + max(50 * point, 0.25)
    else:
        entry = float(tick.bid) + max(100 * point, 0.50)
        sl = entry + max(50 * point, 0.25)
        tp = entry - max(50 * point, 0.25)
    return Signal(direction=direction, symbol=symbol, entry=entry, sl=sl, tp=tp,
                  volume=0.01, signal_id="SL-SMOKE-TEST",
                  source="EXECUTION_PLUMBING_SMOKE", status="APPROVED")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--place-cancel-test", action="store_true")
    ap.add_argument("--direction", choices=["BUY", "SELL"], default="BUY")
    args = ap.parse_args()

    symbol = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
    os.environ["MT5_FORWARD_ORDER_MODE"] = "PENDING_LIMIT_RESEARCH"

    terminal = find_mt5_terminal()
    if terminal is None:
        raise RuntimeError("MT5 terminal not found; set MT5_TERMINAL_PATH if needed")
    print(f"MT5_TERMINAL={terminal}")

    if not mt5.initialize(path=str(terminal), timeout=10000):
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        info = mt5.symbol_info(symbol)
        tick = mt5.symbol_info_tick(symbol)
        if info is None or tick is None:
            raise RuntimeError(f"MT5 symbol/tick unavailable: {symbol}")
        signal = _synthetic_signal(symbol, args.direction, tick, float(info.point))

        print("SMOKE_TEST=EXECUTION_PLUMBING")
        print(f"symbol={symbol}")
        print(f"direction={signal.direction}")
        print(f"entry={signal.entry}")
        print(f"sl={signal.sl}")
        print(f"tp={signal.tp}")
        print(f"trade_mode={info.trade_mode}")
        print(f"account_trade_mode={getattr(mt5.account_info(), 'trade_mode', None)}")

        if not args.place_cancel_test:
            os.environ["LIVE_TRADING_ENABLE"] = "false"
            os.environ["ALLOW_REAL_EXECUTION"] = "false"
            result = execute_signal(signal)
            print("mode=DRY_RUN")
            print(result)
            return 0 if result.get("ok") and result.get("dry_run") else 1

        if os.getenv("LIVE_TRADING_ENABLE", "").lower() != "true":
            raise RuntimeError("--place-cancel-test requires LIVE_TRADING_ENABLE=true")
        if os.getenv("ALLOW_REAL_EXECUTION", "").lower() != "true":
            raise RuntimeError("--place-cancel-test requires ALLOW_REAL_EXECUTION=true")

        result = execute_signal(signal)
        print("mode=PLACE_THEN_CANCEL")
        print(result)

        if result.get("ok") and result.get("order"):
            ticket = int(result["order"])
            active = mt5.orders_get(ticket=ticket) or []
            if active:
                cancel = mt5.order_send({
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order": ticket,
                    "symbol": symbol,
                    "magic": int(os.getenv("MT5_MAGIC", "26091901")),
                    "comment": "SP2L-SL-SMOKE-CANCEL"[:31],
                })
                print({"cancel_retcode": getattr(cancel, "retcode", None),
                       "cancel_comment": getattr(cancel, "comment", None)})
            verification = result.get("verification") or {}
            return 0 if verification.get("verified") else 1
        return 1
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
