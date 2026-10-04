"""SP2L V3 historical trailing/2X/RR research matrix.

Research-only. Reuses the frozen V2 detector/entry geometry and replays the
same historical signal population across exit variants. It does not define
canonical source semantics or emit production decisions.

Matrix per window:
  6 activation values × 10 trailing values × 2X ON/OFF × RR1/RR2 = 240 variants.
Windows:
  1M: 2026-08-26 .. 2026-09-25 UTC
  3M: 2026-07-01 .. 2026-10-01 UTC
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5
import numpy as np

try:
    from mt5_terminal_resolver import find_mt5_terminal
    from sp2l_strategy_a_v2_detector import detect_setup, find_first_entry
except ImportError:
    from scripts.mt5_terminal_resolver import find_mt5_terminal
    from scripts.sp2l_strategy_a_v2_detector import detect_setup, find_first_entry

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "backtest-mt5-local"
OUT.mkdir(parents=True, exist_ok=True)

ACTIVATIONS = (0, 5, 10, 15, 20, 30)
TRAILS = (2, 3, 4, 5, 6, 8, 10, 12, 15, 20)
RRS = (1.0, 2.0)
PIP_SIZE = 0.01


def resolve_symbol(requested: str) -> str:
    names = [str(s.name) for s in (mt5.symbols_get() or [])]
    candidate = requested.upper()
    if candidate in names:
        return candidate
    for suffix in (".ecn", ".ECN", "m", ".m", "_ecn", "-ECN"):
        if candidate + suffix in names:
            return candidate + suffix
    norm = "".join(c for c in candidate if c.isalnum())
    matches = [
        n for n in names
        if "".join(c for c in n.upper() if c.isalnum()) == norm
        or "".join(c for c in n.upper() if c.isalnum()).startswith(norm)
    ]
    if matches:
        return sorted(matches, key=lambda x: (len(x), x))[0]
    raise RuntimeError(f"symbol discovery failed: {requested}")


def fetch_rates(symbol: str, start: datetime, end: datetime) -> np.ndarray:
    chunks = []
    cur = start.astimezone(timezone.utc)
    end = end.astimezone(timezone.utc)
    while cur < end:
        z = min(cur + timedelta(days=7), end)
        rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, cur, z)
        if rates is None or len(rates) == 0:
            raise RuntimeError(f"M1 history failed {cur.isoformat()}..{z.isoformat()}: {mt5.last_error()}")
        chunks.append(rates.copy())
        cur = z + timedelta(minutes=1)
    x = np.concatenate(chunks)
    x.sort(order="time")
    _, idx = np.unique(x["time"], return_index=True)
    return x[np.sort(idx)]


def build_signals(rates: np.ndarray) -> list[dict]:
    signals = []
    used_entry_indices: set[int] = set()
    for c_pos in range(2, len(rates) - 1):
        setup = detect_setup(rates[c_pos - 2:c_pos + 1])
        if setup is None:
            continue
        entry = find_first_entry(rates, c_pos, setup)
        if entry is None:
            continue
        idx = int(entry["entry_index"])
        if idx in used_entry_indices:
            continue
        used_entry_indices.add(idx)
        signals.append({
            **entry,
            "signal_time": int(entry["entry_time"]),
            "entry_index": idx,
        })
    signals.sort(key=lambda x: (x["entry_index"], x["direction"]))
    return signals


def replay(signal: dict, rates: np.ndarray, activation_pips: int,
           trail_pips: int, two_x: bool, tp_r: float) -> dict:
    entry = float(signal["entry"])
    sl0 = float(signal["sl"])
    risk = abs(entry - sl0)
    direction = signal["direction"]
    tp = entry + tp_r * risk if direction == "BUY" else entry - tp_r * risk
    entry_i = int(signal["entry_index"])
    trail = trail_pips * PIP_SIZE
    activation = activation_pips * PIP_SIZE

    active_sl = sl0
    trailing_active = False
    entry2 = False
    entry2_price = entry - 0.5 * risk if direction == "BUY" else entry + 0.5 * risk
    mfe = 0.0
    exit_price = None
    reason = None
    exit_i = None

    for i in range(entry_i + 1, len(rates)):
        b = rates[i]
        hi, lo = float(b["high"]), float(b["low"])

        if direction == "BUY":
            mfe = max(mfe, hi - entry)
            if two_x and not entry2 and lo <= entry2_price:
                entry2 = True
            if hi - entry >= activation:
                trailing_active = True
                active_sl = max(active_sl, hi - trail)
            hit_sl = lo <= active_sl
            hit_tp = hi >= tp
        else:
            mfe = max(mfe, entry - lo)
            if two_x and not entry2 and hi >= entry2_price:
                entry2 = True
            if entry - lo >= activation:
                trailing_active = True
                active_sl = min(active_sl, lo + trail)
            hit_sl = hi >= active_sl
            hit_tp = lo <= tp

        if hit_sl and hit_tp:
            reason = "AMBIGUOUS_SAME_BAR"
            exit_price = None
            exit_i = i
            break
        if hit_sl:
            reason = "TRAIL_SL" if trailing_active else "SL"
            exit_price = active_sl
            exit_i = i
            break
        if hit_tp:
            reason = "TP"
            exit_price = tp
            exit_i = i
            break

    if exit_price is None and reason is None:
        b = rates[-1]
        exit_price = float(b["close"])
        exit_i = len(rates) - 1
        reason = "END_OF_DATA_MARK"

    if reason == "AMBIGUOUS_SAME_BAR":
        rr = None
    else:
        weighted_entry = (
            (entry + entry2_price) / 2.0 if entry2 else entry
        )
        effective_risk = risk
        pnl = (
            exit_price - weighted_entry
            if direction == "BUY"
            else weighted_entry - exit_price
        )
        rr = pnl / effective_risk

    return {
        "entry_time": int(signal["entry_time"]),
        "exit_time": int(rates[exit_i]["time"]),
        "direction": direction,
        "entry": entry,
        "sl": sl0,
        "risk": risk,
        "tp_r": tp_r,
        "entry2_filled": entry2,
        "weighted_entry": (
            (entry + entry2_price) / 2.0 if entry2 else entry
        ),
        "trailing_activated": trailing_active,
        "final_sl": active_sl,
        "max_favorable_price": mfe,
        "reason": reason,
        "realized_R": rr,
    }


def summarize(rows: list[dict]) -> dict:
    decisive = [r for r in rows if r["realized_R"] is not None]
    wins = [r for r in decisive if r["realized_R"] > 0]
    losses = [r for r in decisive if r["realized_R"] < 0]
    gross_profit = sum(r["realized_R"] for r in wins)
    gross_loss = abs(sum(r["realized_R"] for r in losses))

    eq = peak = max_dd = 0.0
    max_loss_run = loss_run = 0
    for r in sorted(decisive, key=lambda x: x["entry_time"]):
        eq += r["realized_R"]
        peak = max(peak, eq)
        max_dd = max(max_dd, peak - eq)
        if r["realized_R"] <= 0:
            loss_run += 1
            max_loss_run = max(max_loss_run, loss_run)
        else:
            loss_run = 0

    return {
        "trades": len(rows),
        "decisive": len(decisive),
        "wins": len(wins),
        "losses": len(losses),
        "ambiguous": len(rows) - len(decisive),
        "win_rate_pct": 100.0 * len(wins) / len(decisive) if decisive else None,
        "net_R": sum(r["realized_R"] for r in decisive),
        "profit_factor": gross_profit / gross_loss if gross_loss else None,
        "max_drawdown_R": max_dd,
        "max_consecutive_losses": max_loss_run,
        "avg_R": sum(r["realized_R"] for r in decisive) / len(decisive) if decisive else None,
        "tp_hits": sum(r["reason"] == "TP" for r in rows),
        "sl_hits": sum(r["reason"] == "SL" for r in rows),
        "trail_exits": sum(r["reason"] == "TRAIL_SL" for r in rows),
        "end_marks": sum(r["reason"] == "END_OF_DATA_MARK" for r in rows),
        "entry2_filled": sum(bool(r["entry2_filled"]) for r in rows),
    }


def run_window(name: str, start: datetime, end: datetime, symbol: str):
    rates = fetch_rates(symbol, start, end)
    signals = build_signals(rates)
    matrix = []
    details = []

    for tp_r in RRS:
        for act in ACTIVATIONS:
            for trail in TRAILS:
                for two_x in (False, True):
                    rows = [
                        replay(s, rates, act, trail, two_x, tp_r)
                        for s in signals
                    ]
                    summary = summarize(rows)
                    method = (
                        f"RR{int(tp_r)}_ACT{act}_TRAIL{trail}_"
                        f"2X{'ON' if two_x else 'OFF'}"
                    )
                    matrix.append({
                        "window": name,
                        "method": method,
                        "tp_r": tp_r,
                        "activation_pips": act,
                        "trail_pips": trail,
                        "two_x": two_x,
                        **summary,
                    })
                    for row in rows:
                        details.append({
                            "window": name,
                            "method": method,
                            "tp_r": tp_r,
                            "activation_pips": act,
                            "trail_pips": trail,
                            "two_x": two_x,
                            **row,
                        })

    return rates, signals, matrix, details


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mt5-path", required=True)
    ap.add_argument("--symbol", default="XAUUSD")
    ap.add_argument("--start-1m", default="2026-08-26T00:00:00+00:00")
    ap.add_argument("--end-1m", default="2026-09-25T23:59:59+00:00")
    ap.add_argument("--start-3m", default="2026-07-01T00:00:00+00:00")
    ap.add_argument("--end-3m", default="2026-10-01T23:59:59+00:00")
    args = ap.parse_args()

    s1 = datetime.fromisoformat(args.start_1m.replace("Z", "+00:00"))
    e1 = datetime.fromisoformat(args.end_1m.replace("Z", "+00:00"))
    s3 = datetime.fromisoformat(args.start_3m.replace("Z", "+00:00"))
    e3 = datetime.fromisoformat(args.end_3m.replace("Z", "+00:00"))

    if not mt5.initialize(path=args.mt5_path):
        terminal = find_mt5_terminal()
        if terminal is None or not mt5.initialize(path=str(terminal)):
            raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        symbol = resolve_symbol(args.symbol)
        r1, sig1, m1, d1 = run_window("1M", s1, e1, symbol)
        r3, sig3, m3, d3 = run_window("3M", s3, e3, symbol)
        matrix = m1 + m3
        details = d1 + d3

        by_method = {}
        for row in matrix:
            by_method.setdefault(row["method"], {})[row["window"]] = row

        combined = []
        for method, windows in by_method.items():
            a, b = windows["1M"], windows["3M"]
            combined.append({
                "method": method,
                "tp_r": a["tp_r"],
                "activation_pips": a["activation_pips"],
                "trail_pips": a["trail_pips"],
                "two_x": a["two_x"],
                "net_R_1M": a["net_R"],
                "net_R_3M": b["net_R"],
                "max_dd_1M": a["max_drawdown_R"],
                "max_dd_3M": b["max_drawdown_R"],
                "pf_1M": a["profit_factor"],
                "pf_3M": b["profit_factor"],
                "win_rate_1M": a["win_rate_pct"],
                "win_rate_3M": b["win_rate_pct"],
                "trades_1M": a["trades"],
                "trades_3M": b["trades"],
                "net_R_total": a["net_R"] + b["net_R"],
                "dd_worst": max(a["max_drawdown_R"], b["max_drawdown_R"]),
                "rank_score": (
                    a["net_R"] + b["net_R"]
                    - 0.5 * max(a["max_drawdown_R"], b["max_drawdown_R"])
                ),
            })

        combined.sort(key=lambda x: x["rank_score"], reverse=True)
        top1m = sorted(m1, key=lambda x: x["net_R"], reverse=True)[:20]
        top3m = sorted(m3, key=lambda x: x["net_R"], reverse=True)[:20]
        top_combined = combined[:30]

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = OUT / f"SP2L_V3_HISTORICAL_TRAILING_MATRIX_{stamp}"

        def write_csv(path, rows):
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)

        write_csv(base.with_name(base.name + "_MATRIX.csv"), matrix)
        write_csv(base.with_name(base.name + "_COMBINED.csv"), combined)
        write_csv(base.with_name(base.name + "_TRADES.csv"), details)

        payload = {
            "status": "COMPLETE",
            "research_only": True,
            "symbol_requested": args.symbol,
            "symbol_used": symbol,
            "timeframe": "M1",
            "population": {
                "1M_signals": len(sig1),
                "3M_signals": len(sig3),
                "1M_bars": len(r1),
                "3M_bars": len(r3),
                "variants_per_window": 240,
                "variant_definition": "6 activation × 10 trailing × 2X ON/OFF × RR1/RR2",
            },
            "windows": {
                "1M": {"start_utc": s1.isoformat(), "end_utc": e1.isoformat()},
                "3M": {"start_utc": s3.isoformat(), "end_utc": e3.isoformat()},
            },
            "top_1M": top1m,
            "top_3M": top3m,
            "top_combined": top_combined,
            "matrix": matrix,
            "semantic_limits": [
                "Research-only comparator; not canonical Strategy A.",
                "Uses the existing V2 frozen research detector/entry geometry.",
                "Trailing is an M1 high/low replay.",
                "2X fill is an M1 touch counterfactual.",
                "Same-bar SL/TP is explicitly ambiguous, not invented as SL-first.",
                "No production BUY/SELL decision is emitted.",
            ],
        }
        base.with_suffix(".json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(json.dumps({
            "status": "COMPLETE",
            "symbol": symbol,
            "signals_1M": len(sig1),
            "signals_3M": len(sig3),
            "variants_per_window": 240,
            "matrix_csv": str(base.with_name(base.name + "_MATRIX.csv")),
            "combined_csv": str(base.with_name(base.name + "_COMBINED.csv")),
            "trades_csv": str(base.with_name(base.name + "_TRADES.csv")),
            "json": str(base.with_suffix(".json")),
            "top_1M": top1m[:10],
            "top_3M": top3m[:10],
            "top_combined": top_combined[:10],
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
