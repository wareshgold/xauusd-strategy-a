"""SP2L V3 XAUUSD research forward profile: RR2 / NO TRAILING / 2X OFF.

This profile is a research/forward-test variant only.
It preserves the existing V3 geometry and TP_R=2.0, but disables the
experimental trailing monitor so the forward test observes the original
SL/TP payoff without trailing intervention.

No-trailing is NOT canonical Strategy A.
"""

from __future__ import annotations

import os
import sp2l_v3_config as cfg

cfg.VERSION = "SP2L_V3_XAUUSD_RR2_NOTRAILING_20261007"
cfg.TP_R = 2.0

# Explicitly zeroed as labels only. The actual safety switch is the monitor
# override below, which restores the base runner's non-trailing lifecycle
# monitor captured before V3 trailing was installed.
cfg.TRAIL_PIPS = 0.0
cfg.TRAIL_ACTIVATION_PIPS = 0.0
cfg.TRAIL_DISTANCE_PRICE = 0.0
cfg.TRAIL_ACTIVATION_PRICE = 0.0

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

# Reuse the same signal/entry geometry and the same forward-only freshness
# guard. Only the trailing intervention is disabled.
base.runner.monitor_position_lifecycle = base.runner._original_monitor

base.runner.EVENTS = (
    base.runner.ARTIFACTS
    / "SP2L_V3_XAUUSD_RR2_NOTRAILING_FORWARD_EVENTS.jsonl"
)

base.runner.STATE_FILE = (
    base.runner.RUNTIME
    / "sp2l_v3_xauusd_rr2_notrailing_forward_state.json"
)

if __name__ == "__main__":
    base.runner.main()
