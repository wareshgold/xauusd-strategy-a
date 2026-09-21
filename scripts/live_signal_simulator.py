"""Deterministic live-signal simulator (dry-run chain verification tool).

Given an integer seed, deterministically derives a synthetic APPROVED signal
and verifies the FULL gateway chain:

    approved_signal.json -> gateway poll -> Telegram -> MT5 request (dry-run,
    no order) -> signals.jsonl + trades.jsonl -> file archived to
    runtime/processed/.

Safety: the simulator only ever writes the APPROVED-signal file consumed by
the gateway; it computes no strategy geometry and can never place a real
order (the gateway's dry-run gates apply unchanged).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(os.path.dirname(os.path.abspath(__file__))))

try:  # direct-script compatibility (repo pattern)
    from live_journal import read_jsonl, SIGNALS, TRADES  # type: ignore
    from live_mt5_gateway import SIGNAL_FILE  # type: ignore
except ModuleNotFoundError:  # pytest / package mode
    from scripts.live_journal import read_jsonl, SIGNALS, TRADES  # type: ignore
    from scripts.live_mt5_gateway import SIGNAL_FILE  # type: ignore

JOURNAL_DIR = SIGNALS.parent

DEFAULT_SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
PROCESSED_DIR = SIGNAL_FILE.parent / "processed"
# Deterministic uniqueness for repeated test runs: an explicit test run ID
# (e.g. the run timestamp) namespaces the signal ID so re-running the same
# seed never collides with the gateway's duplicate protection. Duplicate
# protection itself is intentionally unchanged.


def signal_id_for(seed: int, *, run_id: str | None = None, explicit_id: str | None = None) -> str:
    """Deterministic signal ID: explicit_id wins; else [run_id-]seed form."""
    if explicit_id:
        return str(explicit_id)
    if run_id:
        return f"SIM-{run_id}-{seed:04d}"
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"SIM-{day}-{seed:04d}"


def simulate_signal(
    seed: int,
    symbol: str = DEFAULT_SYMBOL,
    *,
    signal_id: str | None = None,
) -> dict:
    """Deterministically derive a synthetic APPROVED signal from a seed.

    Pure integer arithmetic (module-level randomness is never used) so the
    same seed always produces the same signal values on every machine.
    `signal_id` only namespaces the ID (see `signal_id_for`); it never
    affects direction/entry/SL/TP derivation.
    """
    rng = (seed * 1103515245 + 12345) % (2**31)
    direction = "BUY" if (rng % 2) == 0 else "SELL"
    # Entry reference: last digits of the seeded stream, kept far from any
    # real market price; the gateway re-prices execution from the live tick.
    base = 1000.0 + (rng % 500) + (rng % 97) / 100.0
    sl_dist = 5.0 + (rng % 7)
    tp_dist = 8.0 + (rng % 13)
    entry = round(base, 2)
    sl = round(entry - sl_dist, 2) if direction == "BUY" else round(entry + sl_dist, 2)
    tp = round(entry + tp_dist, 2) if direction == "BUY" else round(entry - tp_dist, 2)
    return {
        "direction": direction,
        "symbol": symbol,
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "volume": 0.01,
        "signal_id": signal_id or signal_id_for(seed),
        "source": "SIMULATOR_TEST_ONLY",
        "status": "APPROVED",
    }


def place_signal(payload: dict, signal_file: Path | None = None) -> Path:
    target = Path(signal_file) if signal_file else SIGNAL_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target


def run_gateway(seconds: float = 8.0) -> int:
    """Run the bounded gateway as a subprocess (env already set)."""
    env = os.environ.copy()
    env["GATEWAY_MAX_SECONDS"] = str(seconds)
    completed = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("live_mt5_gateway.py"))],
        env=env,
        check=False,
    )
    return completed.returncode


def verify_chain(
    signal_id: str,
    *,
    journal_dir: Path | None = None,
    processed_dir: Path | None = None,
) -> dict:
    """Verify the recorded chain for signal_id. Pure filesystem inspection."""
    journal = Path(journal_dir) if journal_dir else JOURNAL_DIR
    processed = Path(processed_dir) if processed_dir else PROCESSED_DIR

    signals = [
        r for r in read_jsonl(journal / "signals.jsonl")
        if r.get("signal_id") == signal_id
    ]
    trades = [
        r for r in read_jsonl(journal / "trades.jsonl")
        if r.get("signal_id") == signal_id
    ]
    sig_ok = bool(signals) and signals[-1].get("status") == "APPROVED"
    trade = trades[-1] if trades else {}
    trade_ok = bool(trades) and trade.get("status") == "DRY_RUN"
    request = (trade.get("execution_json") or {}).get("request") or {}
    request_ok = bool(request) and request.get("symbol") == trade.get("symbol")

    archived = any(p.name.endswith("approved_signal.json") for p in processed.glob("*approved_signal.json")) if processed.exists() else False

    checks = {
        "signal_recorded_approved": sig_ok,
        "trade_recorded_dry_run": trade_ok,
        "mt5_request_built": request_ok,
        "signal_file_archived": archived,
    }
    return {
        "signal_id": signal_id,
        "checks": checks,
        "chain_ok": all(checks.values()),
        "trade_status": trade.get("status"),
        "request_symbol": request.get("symbol"),
        "journal_dir": str(journal),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic dry-run chain simulator")
    parser.add_argument("--seed", type=int, default=1, help="deterministic signal seed")
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL)
    parser.add_argument("--signal-id", default=None,
                        help="explicit signal ID (wins over seed/run-id naming)")
    parser.add_argument("--run-id", default=None,
                        help="deterministic run namespace, e.g. 20260921T091500Z: "
                        "produces SIM-<run-id>-<seed> so repeated test runs of the "
                        "same seed stay unique without bypassing duplicate protection")
    parser.add_argument("--unique-run", action="store_true",
                        help="namespace this run with the current UTC timestamp "
                        "(deterministic per second; keeps values seed-derived)")
    parser.add_argument("--gateway-seconds", type=float, default=8.0)
    parser.add_argument("--verify-only", action="store_true",
                        help="re-verify the chain for an existing signal id")
    parser.add_argument("--no-gateway", action="store_true",
                        help="only write the signal file (no gateway run)")
    args = parser.parse_args()

    if args.unique_run and args.run_id is None:
        args.run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    signal_id = args.signal_id or signal_id_for(args.seed, run_id=args.run_id)

    if args.verify_only:
        pass
    else:
        payload = simulate_signal(args.seed, args.symbol, signal_id=signal_id)
        target = place_signal(payload)
        print(json.dumps({"signal_placed": payload, "file": str(target)}, indent=2))
        if not args.no_gateway:
            rc = run_gateway(args.gateway_seconds)
            if rc != 0:
                print(f"gateway exited with {rc}", file=sys.stderr)

    result = verify_chain(signal_id)
    print(json.dumps(result, indent=2))
    return 0 if result["chain_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
