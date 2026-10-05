"""SP2L V3 XAUUSD research forward profile: RR2 / ACT10 / TRAIL2 / 2X OFF.

Research unit:
- ACT10 = 10 MT5 points
- TRAIL2 = 2 MT5 points

For XAUUSD.ecn, MT5 currently reports point=0.01, therefore:
- activation = 0.10 price
- trailing distance = 0.02 price

This is NOT a source-confirmed pip definition.
"""

from __future__ import annotations

import os
import sp2l_v3_config as cfg

cfg.VERSION = "SP2L_V3_XAUUSD_RR2_ACT10_TRAIL2_20261005"
cfg.TP_R = 2.0

# Labels only. Actual price conversion is performed by the live MT5
# symbol point inside the trailing runner.
cfg.TRAIL_PIPS = 2.0
cfg.TRAIL_ACTIVATION_PIPS = 10.0
cfg.TRAIL_DISTANCE_PRICE = 0.02
cfg.TRAIL_ACTIVATION_PRICE = 0.10

os.environ["SP2L_SYMBOLS"] = "XAUUSD"
os.environ["SP2L_P_GAP_PRICE"] = str(cfg.P_GAP_PRICE)
os.environ["SP2L_SPIKE_MULTIPLIER"] = str(cfg.SPIKE_MULTIPLIER)
os.environ["SP2L_MAX_SL_DISTANCE"] = str(cfg.MAX_SL_DISTANCE)
os.environ["SP2L_TP_R"] = "2.0"
os.environ["SP2L_VOLUME"] = "0.01"
os.environ["MT5_FORWARD_ORDER_MODE"] = cfg.ORDER_MODE
os.environ["SP2L_PENDING_TTL_MINUTES"] = str(cfg.PENDING_TTL_MINUTES)
os.environ["LIVE_TRADING_ENABLE"] = "true"
os.environ["ALLOW_REAL_EXECUTION"] = "true"

import run_sp2l_v3_xauusd_forward_test as base

base.runner.EVENTS = (
    base.runner.ARTIFACTS
    / "SP2L_V3_XAUUSD_RR2_ACT10_TRAIL2_FORWARD_EVENTS.jsonl"
)

base.runner.STATE_FILE = (
    base.runner.RUNTIME
    / "sp2l_v3_xauusd_rr2_act10_trail2_forward_state.json"
)

if __name__ == "__main__":
    base.runner.main()


