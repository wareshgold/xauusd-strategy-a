"""One-command live-session runner (operator tool; executes nothing itself).

Tomorrow's single command shape:

    python scripts/run_live_session.py                 # dry-run session (default)
    python scripts/run_live_session.py --check-only    # pre-flight only, no gateway
    python scripts/run_live_session.py --mode real     # REAL orders (requires BOTH
                                                       # LIVE_TRADING_ENABLE=true AND
                                                       # ALLOW_REAL_EXECUTION=true)

What it does:
1. Runs the pre-flight readiness check (MT5 terminal/account/symbol, Telegram
   config, real-execution double gate).
2. In `real` mode REFUSES to start unless the readiness verdict is READY and
   both real-execution keys are set (defense against one forgotten flag).
3. Hands over to the existing gateway loop (scripts/live_mt5_gateway.py),
   which polls the approved-signal file and, for every signal:
       signal -> Telegram message + MT5 trade request -> execution -> Telegram.

No strategy rules, no geometry, no autonomous signals: the gateway only ever
consumes a human-approved signal file.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(os.path.dirname(os.path.abspath(__file__))))

try:  # direct-script compatibility (repo pattern)
    from live_readiness import check_live_readiness, format_readiness
except ModuleNotFoundError:  # pytest / package mode
    from scripts.live_readiness import check_live_readiness, format_readiness

GATEWAY = "live_mt5_gateway.py"


def _requested_real(args_mode: str) -> bool:
    return args_mode == "real"


def _env_real_keys() -> tuple[bool, bool]:
    live = os.getenv("LIVE_TRADING_ENABLE", "false").strip().lower() == "true"
    allow = os.getenv("ALLOW_REAL_EXECUTION", "false").strip().lower() == "true"
    return live, allow


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-flight + gateway session runner")
    parser.add_argument(
        "--mode",
        choices=("dry-run", "real"),
        default="dry-run",
        help="dry-run (default): gateway runs with dry-run gates; real: REAL orders",
    )
    parser.add_argument(
        "--check-only", action="store_true", help="run pre-flight only and exit"
    )
    parser.add_argument(
        "--seconds", type=float, default=0.0,
        help="bounded session length (0 = run until stopped)",
    )
    args = parser.parse_args()

    want_real = _requested_real(args.mode)
    live, allow = _env_real_keys()

    # Safety: requested real mode must be backed by BOTH environment keys.
    if want_real and not (live and allow):
        print(
            "REFUSED: --mode real requires BOTH environment keys set:\n"
            "  LIVE_TRADING_ENABLE=true\n"
            "  ALLOW_REAL_EXECUTION=true\n"
            "Nothing was started.",
            file=sys.stderr,
        )
        return 2

    report = check_live_readiness(probe_mt5=True)
    print(format_readiness(report))

    if args.check_only:
        return 0 if report["verdict"] == "READY" else 1

    if want_real and report["verdict"] != "READY":
        print(
            "\nREFUSED: --mode real requested but pre-flight verdict is "
            f"{report['verdict']} (blocking: {', '.join(report['blocking_items'])}).\n"
            "Nothing was started.",
            file=sys.stderr,
        )
        return 2

    mode_note = (
        "REAL ORDERS WILL BE SENT TO MT5"
        if want_real
        else "dry-run: every execution is journal-only (no order reaches MT5)"
    )
    print(f"\nStarting gateway ({GATEWAY}) — {mode_note}\n")

    env = os.environ.copy()
    cmd = [sys.executable, str(GATEWAY)]
    if args.seconds > 0:
        env["GATEWAY_MAX_SECONDS"] = str(args.seconds)
    try:
        completed = subprocess.run(cmd, env=env, check=False)
        return completed.returncode
    except KeyboardInterrupt:
        print("\nSession interrupted by operator; gateway subprocess terminated.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
