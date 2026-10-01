"""SP2L V3 XAUUSD balanced two-day forward test profile.

Research-only fixed profile:
- RR 2
- Trail 3 pips = 0.30 XAU price
- XAUUSD.ecn, 0.01 lot
- Frozen V3 geometry
- Clean run isolation inherited from the V3 forward runner
"""
from __future__ import annotations
import os
import sp2l_v3_config as cfg
import run_sp2l_v3_xauusd_forward_test as base

cfg.VERSION = "SP2L_V3_XAUUSD_RR2_TRAIL3_20261001"
cfg.TP_R = 2.0
cfg.TRAIL_PIPS = 3.0
cfg.TRAIL_DISTANCE_PRICE = cfg.TRAIL_PIPS * cfg.XAU_PIP_SIZE_PRICE

os.environ["SP2L_TP_R"] = "2.0"
os.environ["SP2L_VOLUME"] = "0.01"
os.environ["MT5_FORWARD_ORDER_MODE"] = cfg.ORDER_MODE
os.environ["SP2L_PENDING_TTL_MINUTES"] = str(cfg.PENDING_TTL_MINUTES)
os.environ["LIVE_TRADING_ENABLE"] = "true"
os.environ["ALLOW_REAL_EXECUTION"] = "true"

base.runner.EVENTS = base.runner.ARTIFACTS / "SP2L_V3_XAUUSD_RR2_TRAIL3_FORWARD_EVENTS.jsonl"
base.runner.STATE_FILE = base.runner.RUNTIME / "sp2l_v3_xauusd_rr2_trail3_forward_state.json"

if __name__ == "__main__":
    base.runner.main()
