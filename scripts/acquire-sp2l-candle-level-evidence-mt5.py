"""Frozen MT5 candle-level evidence acquisition for archived SP2L research signals.

Research-only. Does not modify signal logic, parameters, source geometry, or execution.
Uses the same MT5 acquisition pattern as the archived weekly author-replica artifact:
copy_rates_from(XAUUSD.ecn, M1, 2026-09-18 23:59:59 UTC, 10000).
The returned raw MT5 epoch is preserved; UTC is only a display representation.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
TIMEFRAME = mt5.TIMEFRAME_M1
REQUESTED_BARS = 10000
END_UTC = datetime(2026, 9, 18, 23, 59, 59, tzinfo=timezone.utc)

SIGNAL_FILE = Path("artifacts/SP2L_author_replica_2026-09-14_2026-09-18.json")
OUT = Path("artifacts/SP2L_candle_level_evidence_2026-09-14_2026-09-18.json")


def iso_utc(raw_ts: int) -> str:
    return datetime.fromtimestamp(int(raw_ts), timezone.utc).isoformat()


def main() -> None:
    archived = json.loads(SIGNAL_FILE.read_text(encoding="utf-8"))
    expected = archived["signals"]

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"symbol_select failed: {mt5.last_error()}")

        retrieved_at = datetime.now(timezone.utc).isoformat()
        rates = mt5.copy_rates_from(SYMBOL, TIMEFRAME, END_UTC, REQUESTED_BARS)
        if rates is None or len(rates) == 0:
            raise SystemExit(f"MT5 returned no rates: {mt5.last_error()}")

        candles = []
        for idx, r in enumerate(rates):
            raw_ts = int(r[0])
            candles.append({
                "index": idx,
                "timestamp_raw_mt5_epoch": raw_ts,
                "timestamp_utc_display": iso_utc(raw_ts),
                "open": float(r[1]),
                "high": float(r[2]),
                "low": float(r[3]),
                "close": float(r[4]),
                "tick_volume": int(r[5]),
                "spread": int(r[6]),
                "real_volume": int(r[7]),
                "symbol": SYMBOL,
                "timeframe": "M1",
                "acquisition_method": "MetaTrader5.copy_rates_from",
            })

        by_display_time = {c["timestamp_utc_display"]: c for c in candles}

        mappings = []
        for sig_idx, sig in enumerate(expected):
            ts = sig["signal_time_utc"]
            candle = by_display_time.get(ts)
            if candle is None:
                mappings.append({
                    "archived_signal_index": sig_idx,
                    "signal_time_utc": ts,
                    "direction": sig["direction"],
                    "entry": sig["entry"],
                    "sl": sig["sl"],
                    "tp": sig["tp"],
                    "archived_outcome": sig["outcome"],
                    "mapping_status": "SIGNAL_CANDLE_NOT_FOUND",
                })
                continue

            i = candle["index"]
            context = {
                "a_index": i - 4,
                "s_index": i - 3,
                "correction_index": i - 2,
                "trigger_index": i - 1,
                "signal_index": i,
            }
            valid_context = min(context.values()) >= 0
            mappings.append({
                "archived_signal_index": sig_idx,
                "signal_time_utc": ts,
                "direction": sig["direction"],
                "entry": sig["entry"],
                "sl": sig["sl"],
                "tp": sig["tp"],
                "archived_outcome": sig["outcome"],
                "signal_candle_index": i,
                "detection_context_indices": context,
                "outcome_scan_start_index": i + 1,
                "mapping_status": "MAPPED" if valid_context else "INSUFFICIENT_PRECEDING_CONTEXT",
            })

        # Explicit raw timestamp sequence diagnostics; no synthetic filling.
        gaps = []
        for a, z in zip(candles, candles[1:]):
            delta = z["timestamp_raw_mt5_epoch"] - a["timestamp_raw_mt5_epoch"]
            if delta != 60:
                gaps.append({
                    "from_index": a["index"],
                    "from_timestamp_utc_display": a["timestamp_utc_display"],
                    "to_index": z["index"],
                    "to_timestamp_utc_display": z["timestamp_utc_display"],
                    "delta_seconds": delta,
                    "missing_m1_bars": max(0, delta // 60 - 1),
                })

        artifact = {
            "research_only": True,
            "artifact_type": "immutable_candle_level_evidence",
            "source_signal_artifact": str(SIGNAL_FILE).replace("\\", "/"),
            "source_signal_artifact_sha256": hashlib.sha256(SIGNAL_FILE.read_bytes()).hexdigest(),
            "symbol": SYMBOL,
            "timeframe": "M1",
            "frozen_signal_window_utc": {
                "start": archived["week_start_utc"],
                "end": archived["week_end_utc"],
            },
            "acquisition": {
                "method": "MetaTrader5.copy_rates_from",
                "requested_end_utc": END_UTC.isoformat(),
                "requested_bars": REQUESTED_BARS,
                "retrieved_at_utc": retrieved_at,
                "raw_mt5_timestamps_preserved": True,
                "historical_timezone_reinterpretation": False,
                "synthetic_candle_fill": False,
                "alternate_feed_substitution": False,
                "mt5_last_error": None,
            },
            "frozen_config": archived["config"],
            "repository_revision_note": "Record the git commit SHA used to execute this script in the companion integrity report.",
            "returned_bars": len(candles),
            "first_candle": candles[0],
            "last_candle": candles[-1],
            "gap_count": len(gaps),
            "gaps": gaps,
            "candles": candles,
            "signal_mappings": mappings,
            "mapping_summary": {
                "expected_signals": len(expected),
                "mapped": sum(x["mapping_status"] == "MAPPED" for x in mappings),
                "not_found": sum(x["mapping_status"] == "SIGNAL_CANDLE_NOT_FOUND" for x in mappings),
                "insufficient_context": sum(x["mapping_status"] == "INSUFFICIENT_PRECEDING_CONTEXT" for x in mappings),
            },
            "integrity_constraints": [
                "No parameter sweep or tuning.",
                "No source-geometry inference or promotion.",
                "No AB=CD anchor/tolerance inference.",
                "No fill-semantics inference.",
                "No pending-order lifecycle inference.",
                "No production BUY/SELL generation.",
                "Archived signal list is preserved as the mapping target.",
            ],
        }

        OUT.parent.mkdir(exist_ok=True)
        OUT.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
        artifact_sha = hashlib.sha256(OUT.read_bytes()).hexdigest()

        print(json.dumps({
            "status": "ACQUIRED",
            "output": str(OUT),
            "artifact_sha256": artifact_sha,
            "returned_bars": len(candles),
            "first_timestamp_utc_display": candles[0]["timestamp_utc_display"],
            "last_timestamp_utc_display": candles[-1]["timestamp_utc_display"],
            "gap_count": len(gaps),
            "mapping_summary": artifact["mapping_summary"],
        }, indent=2))

    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
