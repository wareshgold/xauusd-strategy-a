"""Clean V2 SP2L research forward-test entrypoint.

This entrypoint intentionally uses the recovered V2 geometry already implemented
by run_sp2l_author_replica_multi_symbol_forward_test.py. It does NOT install
the legacy four-candle detector and does NOT apply the London/New-York session
gate used by the old forward wrapper.

Research/demo execution only. Real-account execution remains impossible because
the underlying gateway requires a DEMO account.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

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


def _suppress_heartbeat_stdout() -> None:
    """Keep HEARTBEAT in the ledger but remove it from the runner console.

    This is display-only. The heartbeat JSON written by the base runner is
    preserved byte-for-byte in structure; all non-heartbeat logging remains
    untouched and continues through the original logger.
    """
    original_log_event = runner.log_event

    def log_event(event: dict) -> None:
        if event.get("event") != "HEARTBEAT":
            original_log_event(event)
            return

        payload = {"ts_utc": runner.now_utc(), **event}
        with runner.EVENTS.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, separators=(",", ":")) + "\n")

    runner.log_event = log_event


def _start_heartbeat_monitor() -> None:
    """Open a separate PowerShell window for display-only heartbeat telemetry.

    The monitor only tails the runner's existing event ledger. It never
    initializes MT5, evaluates candidates, or performs any trading action.
    """
    root = Path(__file__).resolve().parents[1]
    monitor = root / "scripts" / "monitor_sp2l_v2_forward_heartbeat.py"
    events = root / "artifacts" / "forward-test" / "SP2L_MULTI_SYMBOL_FORWARD_EVENTS.jsonl"
    command = (
        f'& "{sys.executable}" "{monitor}" '
        f'--events "{events}"'
    )
    subprocess.Popen(
        [
            "powershell.exe",
            "-NoProfile",
            "-NoExit",
            "-Command",
            command,
        ],
        creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
    )


if __name__ == "__main__":
    _suppress_heartbeat_stdout()
    _start_heartbeat_monitor()
    runner.main()
