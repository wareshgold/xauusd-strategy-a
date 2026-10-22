"""Read-only Strategy B forward observer.

This process can read M1 rates from an already installed MT5 terminal, but
contains no order_send / order-placement / order-modification code. It writes
only to Strategy B-specific state and event paths. It is a research observer,
not an execution-equivalent replica or production trading bot.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import MetaTrader5 as mt5
except ImportError as exc:  # no fallback to another execution/data provider
    raise SystemExit("MetaTrader5 package is required; no orders are supported.") from exc

from strategy_b_pythontraderbot_core import (
    Setup,
    StrategyBConfig,
    detect_setup,
    evaluate_pending_entry,
)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "strategy-b-forward"
RUNTIME_DIR = ROOT / "runtime"
EVENTS_FILE = ARTIFACT_DIR / "STRATEGY_B_FORWARD_EVENTS.jsonl"
STATE_FILE = RUNTIME_DIR / "strategy_b_forward_observer_state.json"
LOCK_FILE = RUNTIME_DIR / "strategy_b_forward_observer.lock"
_LOCK_TOKEN: str | None = None

# Fail closed: require an explicit opt-in even for this read-only observer.
OBSERVER_ENABLE = os.getenv("STRATEGY_B_OBSERVER_ENABLE", "false").lower() == "true"
# Source strategy default and broker-specific symbol are deliberately distinct.
SOURCE_SYMBOL = "XAUUSD"
# Current terminal only exposes XAUUSD.ecn; this explicit adapter does not alter strategy parameters.
SYMBOL = os.getenv("STRATEGY_B_SYMBOL", "XAUUSD.ecn").strip()
BARS = int(os.getenv("STRATEGY_B_BARS", "500"))
POLL_SECONDS = float(os.getenv("STRATEGY_B_POLL_SECONDS", "0.5"))
TERMINAL_PATH = os.getenv("STRATEGY_B_MT5_TERMINAL_PATH", "").strip()
CONFIG = StrategyBConfig()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_event(event: dict) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    row = {"observed_at_utc": utc_now(), "strategy": "B", "canonical": False, **event}
    with EVENTS_FILE.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, separators=(",", ":"), sort_keys=True) + "\n")


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"schema_version": 1, "strategy": "B", "pending_setup": None, "seen_candidate_ids": []}
    payload = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    if payload.get("strategy") != "B" or payload.get("schema_version") != 1:
        raise RuntimeError("Strategy B state identity/schema mismatch; refusing to reuse it.")
    return payload


def save_state(state: dict) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(STATE_FILE)


def acquire_lock() -> bool:
    """Exclusive lock; stale locks require deliberate operator inspection."""
    global _LOCK_TOKEN
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    token = f"{os.getpid()} {utc_now()}\\n"
    try:
        with LOCK_FILE.open("x", encoding="utf-8") as handle:
            handle.write(token)
        _LOCK_TOKEN = token
        return True
    except FileExistsError:
        print(f"BLOCKED: observer lock exists at {LOCK_FILE}; inspect its PID before removing it.")
        return False


def release_lock() -> None:
    if _LOCK_TOKEN is None:
        return
    try:
        if LOCK_FILE.read_text(encoding="utf-8") == _LOCK_TOKEN:
            LOCK_FILE.unlink()
    except OSError:
        pass


def setup_from_json(value: dict | None) -> Setup | None:
    if value is None:
        return None
    return Setup(
        direction=value["direction"],
        setup_time=value["setup_time"],
        setup_pos=int(value["setup_pos"]),
        sl=float(value["sl"]),
        spike_body=float(value["spike_body"]),
    )


def setup_to_json(value: Setup) -> dict:
    return {
        "direction": value.direction,
        "setup_time": value.setup_time,
        "setup_pos": value.setup_pos,
        "sl": value.sl,
        "spike_body": value.spike_body,
    }


def attach_source_ema(candles: list[dict], ema_by_time: dict[int, float]) -> None:
    """Mirror source EMA initialization and forming-candle update semantics."""
    if not candles:
        return
    alpha = 2.0 / (CONFIG.ema_period + 1.0)
    times = [int(row["time"]) for row in candles]

    if not ema_by_time or not any(stamp in ema_by_time for stamp in times):
        ema = float(candles[0]["close"])
        ema_by_time.clear()
        ema_by_time[times[0]] = ema
        candles[0]["ema"] = ema
        for row, stamp in zip(candles[1:], times[1:]):
            ema = alpha * float(row["close"]) + (1.0 - alpha) * ema
            ema_by_time[stamp] = ema
            row["ema"] = ema
        return

    for i, (row, stamp) in enumerate(zip(candles, times)):
        if stamp in ema_by_time:
            row["ema"] = ema_by_time[stamp]
        elif i > 0 and times[i - 1] in ema_by_time:
            ema = alpha * float(row["close"]) + (1.0 - alpha) * ema_by_time[times[i - 1]]
            ema_by_time[stamp] = ema
            row["ema"] = ema
        else:
            # Unexpected history discontinuity: re-seed as a fresh source process.
            ema_by_time.clear()
            ema = float(candles[0]["close"])
            ema_by_time[times[0]] = ema
            candles[0]["ema"] = ema
            for seed_row, seed_stamp in zip(candles[1:], times[1:]):
                ema = alpha * float(seed_row["close"]) + (1.0 - alpha) * ema
                ema_by_time[seed_stamp] = ema
                seed_row["ema"] = ema
            return

    # Recalculate the forming candle from the previous candle's cached EMA
    # on every poll, rather than compounding its prior forming EMA.
    if len(candles) >= 2:
        previous_ema = ema_by_time[times[-2]]
        current_ema = alpha * float(candles[-1]["close"]) + (1.0 - alpha) * previous_ema
        ema_by_time[times[-1]] = current_ema
        candles[-1]["ema"] = current_ema

    active = set(times)
    for stamp in list(ema_by_time):
        if stamp not in active:
            del ema_by_time[stamp]



def exact_terminal_process_running() -> bool:
    """Fail closed unless the exact configured MT5 executable is already running."""
    if os.name != "nt" or not TERMINAL_PATH or not Path(TERMINAL_PATH).is_absolute():
        print("BLOCKED: set STRATEGY_B_MT5_TERMINAL_PATH to an absolute Windows terminal64.exe path.")
        return False
    executable = Path(TERMINAL_PATH)
    if executable.name.lower() != "terminal64.exe" or not executable.is_file():
        print("BLOCKED: configured MT5 terminal executable is missing or is not terminal64.exe.")
        return False
    script = String.raw`$expected = [System.IO.Path]::GetFullPath($env:STRATEGY_B_MT5_TERMINAL_PATH); $matches = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'terminal64.exe' -and $_.ExecutablePath -eq $expected }); if ($matches.Count -gt 0) { exit 0 } else { exit 1 }`
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"BLOCKED: could not verify existing MT5 process: {exc}")
        return False
    if result.returncode != 0:
        print("BLOCKED: exact MT5 terminal process is not already running; observer will not launch it.")
        return False
    return True


def main() -> int:
    if not OBSERVER_ENABLE:
        print("BLOCKED: set STRATEGY_B_OBSERVER_ENABLE=true to start the read-only observer.")
        return 2
    if SYMBOL not in (SOURCE_SYMBOL, "XAUUSD.ecn"):
        print(f"BLOCKED: unsupported broker symbol mapping {SYMBOL!r}; allowed mappings are XAUUSD or XAUUSD.ecn.")
        return 2
    if BARS < 100 or POLL_SECONDS <= 0:
        print("BLOCKED: STRATEGY_B_BARS must be >=100 and poll interval must be >0.")
        return 2

    if not exact_terminal_process_running():
        return 3

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    if not acquire_lock():
        return 4
    try:
        state = load_state()
    except Exception:
        release_lock()
        raise

    # Exact process path was checked above. Attach using that explicit path; never use bare initialize().
    if not mt5.initialize(path=TERMINAL_PATH, timeout=10000):
        print(json.dumps({"status": "MT5_INITIALIZE_FAILED", "last_error": mt5.last_error()}))
        release_lock()
        return 3

    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        info = mt5.symbol_info(SYMBOL)
        expected_terminal_dir = os.path.normcase(os.path.realpath(str(Path(TERMINAL_PATH).parent)))
        actual_terminal_dir = os.path.normcase(os.path.realpath(str(getattr(terminal, "path", "")))) if terminal is not None else ""
        if terminal is None or account is None:
            print(json.dumps({"status": "MT5_SESSION_METADATA_UNAVAILABLE"}))
            return 3
        if actual_terminal_dir != expected_terminal_dir:
            print(json.dumps({"status": "MT5_TERMINAL_PATH_MISMATCH", "expected_directory": expected_terminal_dir, "actual_directory": actual_terminal_dir}))
            return 3
        if info is None:
            print(json.dumps({"status": "EXACT_SOURCE_SYMBOL_UNAVAILABLE", "symbol": SYMBOL}))
            return 3
        # Do not mutate Market Watch selection; preflight confirmed this symbol is visible.

        identity = {
            "server": getattr(account, "server", None),
            "account_login": int(account.login) if getattr(account, "login", None) is not None else None,
            "account_trade_mode": getattr(account, "trade_mode", None),
            "source_symbol": SOURCE_SYMBOL,
            "symbol": SYMBOL,
            "symbol_mapping": "SOURCE_NAME_MATCH" if SYMBOL == SOURCE_SYMBOL else "EXPLICIT_BROKER_SUFFIX_ADAPTER",
            "point": float(info.point),
            "digits": int(info.digits),
            "contract_size": float(getattr(info, "trade_contract_size", 0.0)),
            "trade_calc_mode": int(getattr(info, "trade_calc_mode", -1)),
            "filling_mode": int(getattr(info, "filling_mode", -1)),
            "order_mode": int(getattr(info, "order_mode", -1)),
            "currency_base": getattr(info, "currency_base", None),
            "currency_profit": getattr(info, "currency_profit", None),
            "currency_margin": getattr(info, "currency_margin", None),
            "volume_min": float(info.volume_min),
            "volume_step": float(info.volume_step),
            "trade_mode": int(info.trade_mode),
            "observer_only": True,
        }
        if state.get("terminal_identity") not in (None, identity):
            append_event({"event": "SESSION_IDENTITY_CHANGED", "previous": state.get("terminal_identity"), "current": identity})
            # State is not automatically reused across accounts/servers/spec changes.
            state["pending_setup"] = None
            state["seen_candidate_ids"] = []
        state["terminal_identity"] = identity
        save_state(state)
        append_event({"event": "OBSERVER_STARTED", "identity": identity, "config": CONFIG.__dict__, "source_symbol": SOURCE_SYMBOL, "broker_symbol": SYMBOL, "symbol_mapping": identity["symbol_mapping"]})
        print(json.dumps({"status": "READ_ONLY_OBSERVER_STARTED", "identity": identity, "source_symbol": SOURCE_SYMBOL, "broker_symbol": SYMBOL, "symbol_mapping": identity["symbol_mapping"], "orders_sent": False}, sort_keys=True))

        ema_by_time: dict[int, float] = {}
        while True:
            rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M1, 0, BARS)
            if rates is None or len(rates) < 100:
                append_event({"event": "RATES_UNAVAILABLE", "count": 0 if rates is None else len(rates), "last_error": mt5.last_error()})
                time.sleep(POLL_SECONDS)
                continue

            # Keep epoch seconds from MT5; no timezone guessing or rewriting.
            candles = []
            for row in rates:
                candles.append({
                    "time": int(row["time"]),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "tick_volume": int(row["tick_volume"]),
                    "spread": int(row["spread"]),
                    "real_volume": int(row["real_volume"]),
                })

            attach_source_ema(candles, ema_by_time)

            pending = setup_from_json(state.get("pending_setup"))
            # Preserve source loop ordering: evaluate a pre-existing setup before
            # looking for a new one in this poll.
            if pending is not None:
                result = evaluate_pending_entry(candles, pending, broker_point=float(info.point), config=CONFIG)
                if result == "INVALID":
                    append_event({"event": "PENDING_SETUP_INVALIDATED_MAX_SL", "setup": setup_to_json(pending), "max_sl_distance_points": CONFIG.max_sl_distance_points})
                    state["pending_setup"] = None
                    save_state(state)
                elif result is not None:
                    candidate_id = f"{result.direction}:{result.setup_time}:{result.entry_time}"
                    if candidate_id not in state["seen_candidate_ids"]:
                        append_event({
                            "event": "ENTRY_CANDIDATE_OBSERVED_NOT_SENT",
                            "candidate_id": candidate_id,
                            "direction": result.direction,
                            "setup_time": result.setup_time,
                            "entry_time": result.entry_time,
                            "entry": result.entry,
                            "sl": result.sl,
                            "tp": result.tp,
                            "risk_price": result.risk,
                            "risk_points": result.risk / float(info.point),
                            "source_tp_r": CONFIG.tp_r,
                            "order_sent": False,
                            "reason": "OBSERVER_HAS_NO_ORDER_EXECUTION_PATH",
                        })
                        state["seen_candidate_ids"].append(candidate_id)
                        state["seen_candidate_ids"] = state["seen_candidate_ids"][-5000:]
                        state["pending_setup"] = None
                        save_state(state)

            if state.get("pending_setup") is None:
                setup = detect_setup(candles, broker_point=float(info.point), config=CONFIG)
                if setup is not None:
                    # Persist the setup before reporting; restart cannot lose the
                    # observer's record of the newly found candidate setup.
                    state["pending_setup"] = setup_to_json(setup)
                    save_state(state)
                    append_event({"event": "SETUP_OBSERVED", "setup": setup_to_json(setup), "p_gap_points": CONFIG.p_gap_points, "broker_point": float(info.point)})

            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        append_event({"event": "OBSERVER_STOPPED", "reason": "KEYBOARD_INTERRUPT"})
        return 0
    finally:
        mt5.shutdown()
        release_lock()


if __name__ == "__main__":
    raise SystemExit(main())
