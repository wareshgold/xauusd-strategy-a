"""Clean V2 SP2L research forward-test entrypoint.

This entrypoint intentionally uses the recovered V2 geometry already implemented
by run_sp2l_author_replica_multi_symbol_forward_test.py. It does NOT install
the legacy four-candle detector and does NOT apply the London/New-York session
gate used by the old forward wrapper.

Research/demo execution only. Real-account execution remains impossible because
the underlying gateway requires a DEMO account.
"""

from __future__ import annotations

import os

# Match the recovered V2 reference backtest exactly.
os.environ["SP2L_SYMBOLS"] = "XAUUSD"
os.environ["SP2L_P_GAP_PRICE"] = "1.0"
os.environ["SP2L_SPIKE_MULTIPLIER"] = "1.5"
os.environ["SP2L_MAX_SL_DISTANCE"] = "10.0"
os.environ["SP2L_TP_R"] = "1.0"
os.environ["MT5_FORWARD_ORDER_MODE"] = "PENDING_LIMIT_RESEARCH"

# The V2 reference backtest had no session filter.
import run_sp2l_author_replica_multi_symbol_forward_test as runner

# The base runner's detector/find-first-entry are the recovered V2 geometry.
# Disable only the operational session gate so the forward population matches
# the reference V2 scope. This does not alter signal geometry.
runner._session_gate_safe = lambda trigger_ts, state: (True, "V2_REFERENCE_NO_SESSION_FILTER")

# Use a wider rolling window than the old 10-bar wrapper. This reduces missed
# first-trigger visibility while leaving setup/trigger geometry unchanged.
_original_rates = runner.rates

def rates(symbol: str, count: int = 10):
    return _original_rates(symbol, 120)

runner.rates = rates

# Explicitly enable demo execution when the operator has not supplied flags.
# The underlying gateway still hard-blocks non-demo accounts.
os.environ.setdefault("LIVE_TRADING_ENABLE", "true")
os.environ.setdefault("ALLOW_REAL_EXECUTION", "true")

if __name__ == "__main__":
    runner.main()
