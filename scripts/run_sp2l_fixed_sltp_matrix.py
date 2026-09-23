"""RESEARCH-ONLY experiment: fixed symmetric SL/TP winrate matrix.

Does NOT modify Strategy A / SP2L rules. Signal DETECTION is imported
unchanged from the existing frozen author-replica replay
(`run-author-replica-mt5-api.py` -> `signal()`), but the EXPERIMENT replaces
the strategy's spike-extreme SL + 1R TP with fixed symmetric distances
(SL = TP = N pips from entry), which the user explicitly requested as a
separate research matrix. Nothing here is canonical; nothing places orders.

Session window (user request: London open -> New York close):
  Candidates are kept only when the decision minute falls between London
  open (08:00 London) and the NY close (17:00 America/New_York), evaluated
  in NY wall clock as 03:00..16:59 ET (London is 8h ahead of NY in both DST
  regimes, except the 2-3 week DST mismatch windows each year -> documented
  limitation, no invented broker-timezone conversion).
  All aggregation timestamps remain UTC.

Pip-size note: XAUUSD uses the repo convention pip=0.01 (matches the live
forward runner and the user's own reporting). Indices are evaluated in TWO
interpretations because they differ by 100x:
  REPO_PIP      pip=0.01 (repo pip_size_for convention -> 20 pips = 0.20 idx points)
  INDEX_POINT   pip=1.0  (practical broker-point reading -> 20 pips = 20 idx points)
Both are reported; neither promotes a rule.

Integrity guard: a candidate is only counted if its trigger candle (i-1) is
contiguous with the decision minute (60s gap), mirroring the live runner
which always evaluates a just-closed contiguous M1 stream.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import MetaTrader5 as mt5

NY_TZ = ZoneInfo("America/New_York")
SYMBOLS = {
    "XAUUSD.ecn": {"pip_size": 0.01, "pip_method": "REPO_POINT_FOR_NON_FX_DIGITS"},
    "USTEC.c.ecn": {"pip_size": 0.01, "pip_method": "REPO_POINT_FOR_NON_FX_DIGITS"},
    "DJ30.c.ecn": {"pip_size": 0.01, "pip_method": "REPO_POINT_FOR_NON_FX_DIGITS"},
}
WIDTHS_PIPS = [20, 40, 60]
INDEX_PIP_SIZES = {"REPO_PIP": 0.01, "INDEX_POINT": 1.0}
TRIGGER_CONTIGUITY_SECONDS = 60

REPLAY_SOURCE = Path("scripts/run-author-replica-mt5-api.py")
_spec = importlib.util.spec_from_file_location("sp2l_replica", REPLAY_SOURCE)
_replica = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_replica)
detect_signal = _replica.signal  # frozen author-replica detection, unchanged


def in_london_to_ny_session(epoch_seconds: int) -> bool:
    """True when the UTC minute falls between London open and NY close,
    evaluated in NY wall clock: Mon-Fri, 03:00 <= time <= 16:59 ET."""
    dt = datetime.fromtimestamp(int(epoch_seconds), NY_TZ)
    if dt.weekday() >= 5:
        return False
    return 3 <= dt.hour <= 16


def fixed_exit_outcome(candles, start_index, direction, sl, tp):
    """Walk candles after the entry minute; first touch decides.
    Returns "WIN" | "LOSS" | "AMBIGUOUS" | None (unresolved at data end)."""
    for j in range(start_index + 1, len(candles)):
        c = candles[j]
        if direction == "BUY":
            hit_sl, hit_tp = c["low"] <= sl, c["high"] >= tp
        else:
            hit_sl, hit_tp = c["high"] >= sl, c["low"] <= tp
        if hit_sl and hit_tp:
            return "AMBIGUOUS"
        if hit_sl:
            return "LOSS"
        if hit_tp:
            return "WIN"
    return None


def fetch_candles(symbol: str) -> list[dict]:
    # Same fetch pattern as the proven 3.5-month replay: anchor at the last
    # minute. Terminal hard limit verified live: 99,000 M1 bars max per call.
    end = datetime.now(timezone.utc)
    expected = 99_000
    rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M1, end, expected)
    if rates is None:
        raise SystemExit(f"copy_rates_from failed for {symbol}: {mt5.last_error()}")
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
    candles.sort(key=lambda c: c["time"])
    seen = set()
    deduped = []
    for c in candles:
        if c["time"] in seen:
            continue
        seen.add(c["time"])
        deduped.append(c)
    return deduped


def integrity_stats(candles):
    ts = [c["time"] for c in candles]
    gaps = [
        {"from_utc": datetime.fromtimestamp(a, timezone.utc).isoformat(),
         "to_utc": datetime.fromtimestamp(b, timezone.utc).isoformat(),
         "missing_minutes": int((b - a) // 60) - 1}
        for a, b in zip(ts, ts[1:]) if b - a > 60
    ]
    return {
        "bars": len(candles),
        "unique_timestamps": len(ts) == len(set(ts)),
        "chronological": all(b > a for a, b in zip(ts, ts[1:])),
        "gap_count": len(gaps),
        "first_utc": datetime.fromtimestamp(ts[0], timezone.utc).isoformat() if ts else None,
        "last_utc": datetime.fromtimestamp(ts[-1], timezone.utc).isoformat() if ts else None,
    }


def _width_cell(candles, candidates, dist: float) -> dict:
    """Aggregate outcomes for one fixed SL/TP distance (price units)."""
    cells = {"BUY": {"WIN": 0, "LOSS": 0, "AMBIGUOUS": 0, "UNRESOLVED": 0},
             "SELL": {"WIN": 0, "LOSS": 0, "AMBIGUOUS": 0, "UNRESOLVED": 0}}
    totals = {"WIN": 0, "LOSS": 0, "AMBIGUOUS": 0, "UNRESOLVED": 0}
    for cand in candidates:
        entry = cand["entry"]
        sl = entry - dist if cand["direction"] == "BUY" else entry + dist
        tp = entry + dist if cand["direction"] == "BUY" else entry - dist
        outcome = fixed_exit_outcome(candles, cand["index"], cand["direction"], sl, tp)
        key = outcome if outcome else "UNRESOLVED"
        cells[cand["direction"]][key] += 1
        totals[key] += 1
    decisive = totals["WIN"] + totals["LOSS"]
    return {
        "sl_tp_distance_price": dist,
        "wins": totals["WIN"],
        "losses": totals["LOSS"],
        "ambiguous": totals["AMBIGUOUS"],
        "unresolved": totals["UNRESOLVED"],
        "win_rate_decisive": round(totals["WIN"] / decisive, 4) if decisive else None,
        "profit_factor_decisive": round(totals["WIN"] / totals["LOSS"], 4) if totals["LOSS"] else None,
        "net_r": totals["WIN"] - totals["LOSS"],
        "by_direction": cells,
    }


def _mode_summary(candles, candidates, widths, pip_size: float) -> dict:
    per_width = {}
    for width in widths:
        cell = _width_cell(candles, candidates, width * pip_size)
        per_width[str(width)] = cell
    return {"pip_size": pip_size, "widths": per_width}


def evaluate_symbol(symbol: str, pip_modes: dict[str, float]) -> dict:
    candles = fetch_candles(symbol)
    integrity = integrity_stats(candles)

    candidates = []
    for i in range(4, len(candles)):
        t = candles[i]["time"]
        if not in_london_to_ny_session(t):
            continue
        if t - candles[i - 1]["time"] != TRIGGER_CONTIGUITY_SECONDS:
            continue  # trigger/candidate across a data gap: not live-faithful
        sig = detect_signal(candles, i)
        if not sig:
            continue
        direction, entry, strategy_sl = sig
        candidates.append(
            {"index": i, "time": t, "direction": direction, "entry": entry,
             "strategy_sl": strategy_sl}
        )

    by_mode = {
        mode: _mode_summary(candles, candidates, WIDTHS_PIPS, pip_size)
        for mode, pip_size in pip_modes.items()
    }

    return {
        "symbol": symbol,
        "data_integrity": integrity,
        "candidates_in_session": len(candidates),
        "candidates_by_direction": {
            "BUY": sum(1 for c in candidates if c["direction"] == "BUY"),
            "SELL": sum(1 for c in candidates if c["direction"] == "SELL"),
        },
        "fixed_sltp_modes": by_mode,
    }


def main():
    ap = argparse.ArgumentParser(description="RESEARCH-ONLY fixed SL/TP winrate matrix")
    ap.add_argument("--output", default="artifacts/backtest-multi/SP2L_fixed_sltp_matrix.json")
    args = ap.parse_args()

    if not mt5.initialize():
        from mt5_terminal_resolver import find_mt5_terminal
        path = find_mt5_terminal()
        if path is None or not mt5.initialize(path=str(path)):
            raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        results = {}
        for symbol in SYMBOLS:
            if not mt5.symbol_select(symbol, True):
                raise SystemExit(f"symbol_select failed for {symbol}")
            print(f"[matrix] evaluating {symbol} ...", flush=True)
            results[symbol] = evaluate_symbol(symbol, INDEX_PIP_SIZES)

        matrix = {
            "research_only": True,
            "canonical": False,
            "note": (
                "User-requested experiment: frozen author-replica signal detection "
                "with FIXED symmetric SL=TP widths (20/40/60 pips) instead of the "
                "strategy's spike-extreme SL + 1R TP. Session filter London open -> "
                "NY close evaluated in NY wall clock (03:00..16:59 ET). No orders "
                "placed; no strategy rule modified or promoted."
            ),
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "signal_detection_source": str(REPLAY_SOURCE),
            "strategy_parameters_frozen": {
                "pGapPrice": _replica.P_GAP,
                "spikeMultiplier": _replica.SPIKE_MULT,
                "note": "MAX_SL / TP_R do not apply: SL and TP are synthetic fixed widths for this matrix only",
            },
            "session_window": {
                "definition": "London open -> NY close",
                "ny_wall_clock": "03:00..16:59 America/New_York, Mon-Fri",
                "dst_limitation": "US/UK DST mismatch weeks shift London open by 1h relative to 03:00 ET",
            },
            "trigger_contiguity_guard_seconds": TRIGGER_CONTIGUITY_SECONDS,
            "both_touch_policy": "AMBIGUOUS (conservative)",
            "symbols": results,
        }

        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(matrix, indent=2), encoding="utf-8")
        print(f"Wrote {out}")

        for symbol, res in results.items():
            print(f"\n=== {symbol} · candidates={res['candidates_in_session']} "
                  f"(B={res['candidates_by_direction']['BUY']}, S={res['candidates_by_direction']['SELL']}) ===")
            for mode, m in res["fixed_sltp_modes"].items():
                for width, cell in m["widths"].items():
                    wr = cell["win_rate_decisive"]
                    pf = cell["profit_factor_decisive"]
                    print(f"  {mode:<12} {width:>3}p (dist={cell['sl_tp_distance_price']:>8}) "
                          f"W={cell['wins']:<4} L={cell['losses']:<4} A={cell['ambiguous']:<3} "
                          f"WR={'' if wr is None else format(wr * 100, '.1f') + '%':>6} "
                          f"PF={'' if pf is None else pf} netR={cell['net_r']}")
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
