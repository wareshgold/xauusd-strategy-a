import json
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
OUTPUT = Path("artifacts/mt5_xauusd_symbol_spec.json")

if not mt5.initialize():
    raise SystemExit(json.dumps({
        "status": "MT5_INIT_FAILED",
        "last_error": mt5.last_error(),
    }, indent=2))

try:
    info = mt5.symbol_info(SYMBOL)
    if info is None:
        raise SystemExit(json.dumps({
            "status": "SYMBOL_NOT_FOUND",
            "symbol": SYMBOL,
            "last_error": mt5.last_error(),
        }, indent=2))

    tick = mt5.symbol_info_tick(SYMBOL)

    fields = {
        "name": info.name,
        "path": info.path,
        "description": info.description,
        "currency_base": info.currency_base,
        "currency_profit": info.currency_profit,
        "currency_margin": info.currency_margin,
        "digits": info.digits,
        "point": info.point,
        "trade_tick_size": info.trade_tick_size,
        "trade_tick_value": info.trade_tick_value,
        "trade_tick_value_profit": info.trade_tick_value_profit,
        "trade_tick_value_loss": info.trade_tick_value_loss,
        "trade_contract_size": info.trade_contract_size,
        "trade_calc_mode": info.trade_calc_mode,
        "trade_mode": info.trade_mode,
        "volume_min": info.volume_min,
        "volume_max": info.volume_max,
        "volume_step": info.volume_step,
        "filling_mode": info.filling_mode,
        "order_mode": info.order_mode,
        "spread": info.spread,
        "visible": info.visible,
        "select": info.select,
    }

    result = {
        "status": "ACQUIRED",
        "research_only": True,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": SYMBOL,
        "terminal": {
            "version": mt5.version(),
            "terminal_info": str(mt5.terminal_info()),
            "account_info": str(mt5.account_info()),
        },
        "symbol_spec": fields,
        "current_tick": {
            "time": getattr(tick, "time", None),
            "bid": getattr(tick, "bid", None),
            "ask": getattr(tick, "ask", None),
            "last": getattr(tick, "last", None),
        } if tick is not None else None,
        "guard": "METADATA_ONLY; DOES NOT DEFINE STRATEGY GEOMETRY OR EXECUTION RULES",
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "output": str(OUTPUT),
        "symbol_spec": fields,
    }, ensure_ascii=False, indent=2, default=str))
finally:
    mt5.shutdown()
