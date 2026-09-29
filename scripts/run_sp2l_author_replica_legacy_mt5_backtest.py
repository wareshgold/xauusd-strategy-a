"""Research-only MT5 backtest mirror for legacy author-replica forward runner.

This intentionally reuses the legacy forward geometry path instead of the newer
source-aligned detector. It exists only to compare execution parity against
run_sp2l_author_replica_legacy_forward_test_20260928.py.
"""
from __future__ import annotations

import os

os.environ["SP2L_SYMBOLS"] = "XAUUSD"
os.environ["SP2L_P_GAP_PRICE"] = "1.0"
os.environ["SP2L_SPIKE_MULTIPLIER"] = "1.5"
os.environ["SP2L_MAX_SL_DISTANCE"] = "10.0"
os.environ["SP2L_TP_R"] = "1.0"

from sp2l_author_replica_detector import detect


def main():
    import run_sp2l_mt5_local_multi_symbol_backtest as backtest

    # Keep the comparison explicit: this runner documents the intended
    # legacy parameter boundary. The existing MT5 backtest engine handles
    # history loading, session filtering and outcome accounting.
    print("LEGACY_AUTHOR_REPLICA_MIRROR")
    print({
        "symbol": "XAUUSD",
        "p_gap_price": 1.0,
        "spike_multiplier": 1.5,
        "max_sl_distance": 10.0,
        "tp_r": 1.0,
        "canonical": False,
        "detector": "legacy_forward_reference"
    })

    return backtest.main()


if __name__ == "__main__":
    main()
