"""Research-only fixed-distance R:R=1 sensitivity replay for existing SP2L signals.

This tool does NOT change detector geometry. It replays the same signal set with
fixed SL/TP distances expressed in pips. For XAUUSD.ecn the default pip size is
0.01 price units, so 20/40/60 pips correspond to 0.20/0.40/0.60 price units.

Ambiguous same-bar ordering remains quarantined. No canonical rule is promoted.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = ROOT / "artifacts/backtest-mt5-local/SP2L_MT5_LOCAL_MULTI_SYMBOL_20260926T124056Z.json"
OUT_DIR = ROOT / "artifacts/backtest-mt5-local"


def load_signals(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for base, result in data.get("outcomes", {}).items():
        if result.get("status") == "FAILED":
            continue
        for s in result.get("signals_detail", []):
            out.append({"base": base, **s})
    return sorted(out, key=lambda x: (int(x["signal_time"]), x["base"]))


def fetch_window(symbol: str, start_ts: int, end_ts: int):
    start = datetime.fromtimestamp(start_ts, timezone.utc) - timedelta(minutes=2)
    end = datetime.fromtimestamp(end_ts, timezone.utc) + timedelta(minutes=2)
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start, end)
    if rates is None or len(rates) == 0:
        raise RuntimeError(f"No M1 data for {symbol}: {mt5.last_error()}")
    return rates


def classify(symbol: str, signals: list[dict], pip_size: float, pip_distance: int):
    dist = pip_size * pip_distance
    rows = []

    # Use the signal's original trigger time as the signal timestamp. Entry is
    # considered eligible only from the following M1 bar, matching the existing
    # research replay. Fixed-distance SL/TP replace the detector's original
    # source-research SL/TP only for this sensitivity test.
    for s in signals:
        direction = s["direction"]
        entry = float(s["entry"])
        if direction == "BUY":
            sl = entry - dist
            tp = entry + dist
        else:
            sl = entry + dist
            tp = entry - dist

        rates = fetch_window(symbol, int(s["signal_time"]), int(s["signal_time"]) + 60 * 24 * 60)
        outcome = "OPEN_AT_END"
        exit_time = None

        for i, bar in enumerate(rates):
            if int(bar["time"]) <= int(s["signal_time"]):
                continue
            high, low = float(bar["high"]), float(bar["low"])

            if direction == "BUY":
                touched_entry = low <= entry
                hit_sl = low <= sl
                hit_tp = high >= tp
            else:
                touched_entry = high >= entry
                hit_sl = high >= sl
                hit_tp = low <= tp

            if not touched_entry:
                continue

            # Same-bar entry + SL/TP cannot be ordered from M1 OHLC.
            if hit_sl and hit_tp:
                outcome = "AMBIGUOUS"
                exit_time = int(bar["time"])
                break
            if hit_tp:
                outcome = "AMBIGUOUS"
                exit_time = int(bar["time"])
                break
            if hit_sl:
                outcome = "LOSS"
                exit_time = int(bar["time"])
                break

            for j in range(i + 1, len(rates)):
                b = rates[j]
                h, l = float(b["high"]), float(b["low"])
                hit_sl2 = l <= sl if direction == "BUY" else h >= sl
                hit_tp2 = h >= tp if direction == "BUY" else l <= tp
                if hit_sl2 and hit_tp2:
                    outcome = "AMBIGUOUS"
                    exit_time = int(b["time"])
                    break
                if hit_tp2:
                    outcome = "WIN"
                    exit_time = int(b["time"])
                    break
                if hit_sl2:
                    outcome = "LOSS"
                    exit_time = int(b["time"])
                    break
            break

        rows.append({
            "signal_time": int(s["signal_time"]),
            "direction": direction,
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "result": outcome,
            "exit_time": exit_time,
        })

    decisive = [r for r in rows if r["result"] in ("WIN", "LOSS")]
    wins = sum(r["result"] == "WIN" for r in decisive)
    losses = sum(r["result"] == "LOSS" for r in decisive)
    ambiguous = sum(r["result"] == "AMBIGUOUS" for r in rows)
    n = len(decisive)

    by_direction = {}
    for direction in ("BUY", "SELL"):
        sub = [r for r in decisive if r["direction"] == direction]
        w = sum(r["result"] == "WIN" for r in sub)
        l = sum(r["result"] == "LOSS" for r in sub)
        by_direction[direction] = {
            "decisive": len(sub),
            "wins": w,
            "losses": l,
            "win_rate_pct": (100.0 * w / len(sub)) if sub else None,
        }

    return {
        "pip_distance": pip_distance,
        "price_distance": dist,
        "signals": len(rows),
        "decisive": n,
        "wins": wins,
        "losses": losses,
        "ambiguous": ambiguous,
        "win_rate_pct_resolved_only": (100.0 * wins / n) if n else None,
        "net_r_resolved_only": wins - losses,
        "profit_factor_resolved_only": (wins / losses) if losses else None,
        "worst_case_all_ambiguous_loss_wr_pct": (
            100.0 * wins / len(rows) if rows else None
        ),
        "best_case_all_ambiguous_win_wr_pct": (
            100.0 * (wins + ambiguous) / len(rows) if rows else None
        ),
        "by_direction_resolved_only": by_direction,
        "rows": rows,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--artifact", default=str(DEFAULT_ARTIFACT))
    p.add_argument("--symbol", default="XAUUSD.ecn")
    p.add_argument("--pip-size", type=float, default=0.01)
    p.add_argument("--distances", default="20,40,60")
    p.add_argument("--mt5-path", default=None)
    args = p.parse_args()

    artifact = Path(args.artifact)
    signals = [s for s in load_signals(artifact) if s["base"] == "XAUUSD"]
    distances = [int(x) for x in args.distances.split(",")]

    if not mt5.initialize(path=args.mt5_path) if args.mt5_path else not mt5.initialize():
        print(json.dumps({"status": "MT5_INIT_FAILED", "error": mt5.last_error()}, indent=2))
        return 2

    try:
        matrix = [
            classify(args.symbol, signals, args.pip_size, d)
            for d in distances
        ]
        report = {
            "status": "COMPLETE",
            "research_only": True,
            "source_artifact": str(artifact),
            "symbol": args.symbol,
            "pip_size_price_units": args.pip_size,
            "distances_pips": distances,
            "rr": "1:1",
            "signal_set": {
                "base": "XAUUSD",
                "signals": len(signals),
                "signal_geometry_unchanged": True,
            },
            "matrix": [
                {k: v for k, v in x.items() if k != "rows"} for x in matrix
            ],
            "detailed_rows": {str(x["pip_distance"]): x["rows"] for x in matrix},
            "semantic_limits": [
                "This is a sensitivity replay only; it does not select canonical SL/TP.",
                "Same-bar entry/TP and same-bar SL/TP remain AMBIGUOUS at M1 OHLC resolution.",
                "No fill semantics are promoted or changed.",
                "For XAUUSD, 0.01 price units are treated as 1 pip by explicit test configuration.",
            ],
        }
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = OUT_DIR / f"SP2L_FIXED_RR1_PIP_MATRIX_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({
            "status": "COMPLETE",
            "report": str(path),
            "matrix": report["matrix"],
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
