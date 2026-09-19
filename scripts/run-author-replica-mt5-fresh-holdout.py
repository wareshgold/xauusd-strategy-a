"""Research-only untouched Fresh Holdout runner for SP2L Author-Replica.

Frozen boundary: 2026-09-19 00:00:00 UTC.
Frozen configuration: P-Gap=1.0, spike multiplier=1.5, max SL=10.0, TP=1.0R.
This runner performs exactly one configuration. It does not tune, sweep, or select
parameters from holdout results. It imports the existing signal implementation and
records data-integrity and per-trade evidence.

Important: MT5 timestamp/session semantics are recorded as observations; this runner
does not silently reinterpret terminal timestamps as historically verified UTC.
"""

from __future__ import annotations

import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
TIMEFRAME = mt5.TIMEFRAME_M1
BOUNDARY_UTC = datetime(2026, 9, 19, 0, 0, 0, tzinfo=timezone.utc)
END_UTC = datetime.now(timezone.utc)

P_GAP = 1.0
SPIKE_MULT = 1.5
MAX_SL = 10.0
TP_R = 1.0

SOURCE = Path("scripts/run-author-replica-mt5-nonoverlap-stability.py")
OUT = Path("artifacts/SP2L_fresh_holdout_2026-09-19.json")


def load_source_module():
    spec = importlib.util.spec_from_file_location("sp2l_replica", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load source module: {SOURCE}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def utc_iso(ts: int) -> str:
    return datetime.fromtimestamp(int(ts), timezone.utc).isoformat()


def main() -> None:
    mod = load_source_module()

    if END_UTC <= BOUNDARY_UTC:
        raise SystemExit("Current time is not after the frozen holdout boundary.")

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"symbol_select failed: {mt5.last_error()}")

        rates = mt5.copy_rates_range(
            SYMBOL,
            TIMEFRAME,
            BOUNDARY_UTC,
            END_UTC,
        )
        acquisition_error = None if rates is not None else str(mt5.last_error())

        if rates is None or len(rates) == 0:
            result = {
                "research_only": True,
                "status": "HOLDOUT_DATA_UNAVAILABLE",
                "requested_start_utc": BOUNDARY_UTC.isoformat(),
                "requested_end_utc": END_UTC.isoformat(),
                "symbol": SYMBOL,
                "timeframe": "M1",
                "acquisition_source": "MetaTrader5.copy_rates_range",
                "acquisition_error": acquisition_error,
                "frozen_config": {
                    "pGapPrice": P_GAP,
                    "spikeMultiplier": SPIKE_MULT,
                    "maxSlPrice": MAX_SL,
                    "tpR": TP_R,
                },
                "code_revision_note": "Run from the committed repository revision; record git SHA externally with the artifact.",
            }
            OUT.parent.mkdir(exist_ok=True)
            OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(json.dumps(result, indent=2))
            return

        candles = [
            {
                "time": int(r[0]),
                "open": float(r[1]),
                "high": float(r[2]),
                "low": float(r[3]),
                "close": float(r[4]),
            }
            for r in rates
        ]

        # The existing author-replica signal function uses four preceding candles.
        # Only signals whose trigger timestamp is inside the frozen holdout are eligible.
        signals = []
        for i in range(4, len(candles)):
            detected = mod.signal(candles, i)
            if not detected:
                continue

            direction, entry, sl = detected
            signal_ts = candles[i - 1]["time"]
            if signal_ts < int(BOUNDARY_UTC.timestamp()):
                continue

            risk = abs(entry - sl)
            if risk <= 0 or risk > MAX_SL:
                continue

            tp = entry + TP_R * risk if direction == "BUY" else entry - TP_R * risk
            signals.append(
                {
                    "index": i,
                    "signal_time_utc": utc_iso(signal_ts),
                    "direction": direction,
                    "entry": entry,
                    "sl": sl,
                    "tp": tp,
                    "risk": risk,
                }
            )

        for sig in signals:
            outcome = "OPEN_OR_UNRESOLVED"
            outcome_time_utc = None

            for j in range(sig["index"] + 1, len(candles)):
                x = candles[j]
                if sig["direction"] == "BUY":
                    hit_sl = x["low"] <= sig["sl"]
                    hit_tp = x["high"] >= sig["tp"]
                else:
                    hit_sl = x["high"] >= sig["sl"]
                    hit_tp = x["low"] <= sig["tp"]

                if hit_sl and hit_tp:
                    outcome = "AMBIGUOUS"
                    outcome_time_utc = utc_iso(x["time"])
                    break
                if hit_sl:
                    outcome = "LOSS"
                    outcome_time_utc = utc_iso(x["time"])
                    break
                if hit_tp:
                    outcome = "WIN"
                    outcome_time_utc = utc_iso(x["time"])
                    break

            sig["outcome"] = outcome
            sig["outcome_time_utc"] = outcome_time_utc

        wins = sum(s["outcome"] == "WIN" for s in signals)
        losses = sum(s["outcome"] == "LOSS" for s in signals)
        ambiguous = sum(s["outcome"] == "AMBIGUOUS" for s in signals)
        unresolved = sum(s["outcome"] == "OPEN_OR_UNRESOLVED" for s in signals)
        decisive = wins + losses

        result = {
            "research_only": True,
            "status": "HOLDOUT_PARTIAL_OR_COMPLETE",
            "holdout_boundary_utc": BOUNDARY_UTC.isoformat(),
            "requested_start_utc": BOUNDARY_UTC.isoformat(),
            "requested_end_utc": END_UTC.isoformat(),
            "actual_first_returned_timestamp_utc": utc_iso(candles[0]["time"]),
            "actual_last_returned_timestamp_utc": utc_iso(candles[-1]["time"]),
            "returned_bars": len(candles),
            "symbol": SYMBOL,
            "timeframe": "M1",
            "acquisition_source": "MetaTrader5.copy_rates_range",
            "acquisition_error": None,
            "frozen_config": {
                "pGapPrice": P_GAP,
                "spikeMultiplier": SPIKE_MULT,
                "maxSlPrice": MAX_SL,
                "tpR": TP_R,
            },
            "signals_detected": len(signals),
            "wins": wins,
            "losses": losses,
            "ambiguous": ambiguous,
            "open_or_unresolved": unresolved,
            "decisive_win_rate": wins / decisive if decisive else None,
            "total_R": wins - losses,
            "profit_factor": wins / losses if losses else None,
            "per_trade": signals,
            "holdout_integrity": {
                "parameter_sweep": False,
                "parameter_tuning": False,
                "post_result_subperiod_selection": False,
                "source_geometry_changed": False,
                "fill_semantics_changed": False,
                "unresolved_abcd_defined_from_holdout": False,
                "leg1_equals_leg2_promoted": False,
            },
            "limitations": [
                "Current-day MT5 history may be incomplete at execution time.",
                "An unresolved/open trade at the end of the returned data is not counted as a decisive outcome.",
                "MT5 timestamp/session semantics are observations and are not independently historically verified here.",
                "This artifact does not authorize live trading.",
            ],
        }

        OUT.parent.mkdir(exist_ok=True)
        OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))
        print(f"\\nWrote {OUT}")

    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
