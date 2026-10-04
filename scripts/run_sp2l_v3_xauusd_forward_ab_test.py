"""SP2L V3 XAUUSD forward A/B trailing experiment.

Research-only launcher. Does not change canonical geometry or source semantics.
Profiles are isolated by magic number, event file, and state file.
"""
from __future__ import annotations

import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--profile", choices=("A", "B", "C"), required=True)
args = parser.parse_args()

PROFILES = {
    "A": {"activation_pips": 10.0, "trail_pips": 2.0, "magic_base": 26092210},
    "B": {"activation_pips": 15.0, "trail_pips": 2.0, "magic_base": 26092211},
    "C": {"activation_pips": 0.0, "trail_pips": 4.0, "magic_base": 26092212},
}
profile = PROFILES[args.profile]

# These must be set before importing the base runner because its config/magic
# values are read at import time.
os.environ["SP2L_SYMBOLS"] = "XAUUSD"
os.environ["SP2L_TP_R"] = "2.0"
os.environ["SP2L_VOLUME"] = "0.01"
os.environ["SP2L_MAGIC_BASE"] = str(profile["magic_base"])
os.environ["LIVE_TRADING_ENABLE"] = "true"
os.environ["ALLOW_REAL_EXECUTION"] = "true"

import MetaTrader5 as mt5
import sp2l_v3_config as cfg
import run_sp2l_v3_xauusd_forward_test as base

runner = base.runner

cfg.VERSION = (
    f"SP2L_V3_XAUUSD_AB_{args.profile}_"
    f"ACT{int(profile['activation_pips'])}_"
    f"TRAIL{int(profile['trail_pips'])}_20261003"
)
cfg.TP_R = 2.0
cfg.TRAIL_PIPS = float(profile["trail_pips"])
cfg.TRAIL_DISTANCE_PRICE = cfg.TRAIL_PIPS * cfg.XAU_PIP_SIZE_PRICE
cfg.ACTIVATION_PIPS = float(profile["activation_pips"])
cfg.ACTIVATION_DISTANCE_PRICE = cfg.ACTIVATION_PIPS * cfg.XAU_PIP_SIZE_PRICE

os.environ["SP2L_P_GAP_PRICE"] = str(cfg.P_GAP_PRICE)
os.environ["SP2L_SPIKE_MULTIPLIER"] = str(cfg.SPIKE_MULTIPLIER)
os.environ["SP2L_MAX_SL_DISTANCE"] = str(cfg.MAX_SL_DISTANCE)
os.environ["SP2L_TP_R"] = str(cfg.TP_R)
os.environ["SP2L_VOLUME"] = str(cfg.VOLUME)
os.environ["MT5_FORWARD_ORDER_MODE"] = cfg.ORDER_MODE
os.environ["SP2L_PENDING_TTL_MINUTES"] = str(cfg.PENDING_TTL_MINUTES)

runner.EVENTS = runner.ARTIFACTS / f"SP2L_V3_XAUUSD_AB_{args.profile}_FORWARD_EVENTS.jsonl"
runner.STATE_FILE = runner.RUNTIME / f"sp2l_v3_xauusd_ab_{args.profile.lower()}_forward_state.json"
runner.session_gate_status = lambda trigger_ts: (True, "V3_ALL_MARKET_HOURS")

_original_monitor = runner.monitor_position_lifecycle

def _ab_monitor(cfg_runtime, state):
    _original_monitor(cfg_runtime, state)

    symbol = cfg_runtime["symbol"]
    magic = cfg_runtime["magic"]
    info = mt5.symbol_info(symbol)
    if info is None:
        return

    trail_seen = state.setdefault("ab_trail_seen", {})
    bars = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 1, 1)
    if bars is None or len(bars) != 1:
        return

    b = bars[0]
    completed_bar_time = int(b["time"])
    high = float(b["high"])
    low = float(b["low"])

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return
    bid = float(getattr(tick, "bid", 0.0) or 0.0)
    ask = float(getattr(tick, "ask", 0.0) or 0.0)
    point = float(getattr(info, "point", 0.0) or 0.0)
    min_stop_distance = int(getattr(info, "trade_stops_level", 0) or 0) * point

    for p in (mt5.positions_get(symbol=symbol) or []):
        if int(getattr(p, "magic", 0) or 0) != magic:
            continue

        ticket = int(getattr(p, "ticket", 0) or 0)
        entry = float(getattr(p, "price_open", 0.0) or 0.0)
        old_sl = float(getattr(p, "sl", 0.0) or 0.0)
        tp = float(getattr(p, "tp", 0.0) or 0.0)
        if ticket <= 0 or entry <= 0:
            continue

        seen_key = f"{ticket}:{completed_bar_time}"
        if seen_key in trail_seen:
            continue

        if int(p.type) == mt5.POSITION_TYPE_BUY:
            if high - entry < cfg.ACTIVATION_DISTANCE_PRICE:
                continue
            new_sl = cfg.trail_stop("BUY", high)
            if new_sl <= old_sl or new_sl >= high:
                continue
            if new_sl >= bid - min_stop_distance:
                trail_seen[seen_key] = {"status": "SKIPPED_INVALID_STOPS"}
                continue
            direction = "BUY"
        else:
            if entry - low < cfg.ACTIVATION_DISTANCE_PRICE:
                continue
            new_sl = cfg.trail_stop("SELL", low)
            if old_sl > 0 and new_sl >= old_sl:
                continue
            if new_sl <= low:
                continue
            if new_sl <= ask + min_stop_distance:
                trail_seen[seen_key] = {"status": "SKIPPED_INVALID_STOPS"}
                continue
            direction = "SELL"

        send = mt5.order_send({
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": symbol,
            "position": ticket,
            "sl": float(new_sl),
            "tp": tp,
        })
        ok = bool(send and send.retcode == mt5.TRADE_RETCODE_DONE)
        trail_seen[seen_key] = {
            "status": "UPDATED" if ok else "FAILED",
            "new_sl": float(new_sl),
            "retcode": int(send.retcode) if send else None,
        }
        runner.log_event({
            "event": "AB_TRAIL_UPDATE",
            "version": cfg.VERSION,
            "profile": args.profile,
            "symbol": symbol,
            "position": ticket,
            "magic": magic,
            "direction": direction,
            "completed_bar_time": completed_bar_time,
            "entry": entry,
            "old_sl": old_sl,
            "new_sl": float(new_sl),
            "tp": tp,
            "activation_pips": cfg.ACTIVATION_PIPS,
            "trail_pips": cfg.TRAIL_PIPS,
            "success": ok,
            "retcode": int(send.retcode) if send else None,
            "comment": str(send.comment) if send else None,
            "canonical": False,
        })

runner.monitor_position_lifecycle = _ab_monitor

runner.log_event({
    "event": "AB_PROFILE_START",
    "version": cfg.VERSION,
    "profile": args.profile,
    "symbol": "XAUUSD.ecn",
    "magic": 26092211 if args.profile == "A" else 26092212 if args.profile == "B" else 26092213,
    "activation_pips": cfg.ACTIVATION_PIPS,
    "activation_distance_price": cfg.ACTIVATION_DISTANCE_PRICE,
    "trail_pips": cfg.TRAIL_PIPS,
    "trail_distance_price": cfg.TRAIL_DISTANCE_PRICE,
    "tp_r": cfg.TP_R,
    "two_x": False,
    "canonical": False,
    "source_semantics_resolved": False,
})

if __name__ == "__main__":
    runner.main()
