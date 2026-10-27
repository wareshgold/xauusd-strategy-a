"""Research-only SP2L break-even stop study: activation at 0.5R/1R, stop at entry or +/- $0.05.

Uses the existing V3 signal geometry and M1 bars. No canonical rules are changed.
Stops moved from a completed bar become active on the next bar. Same-bar SL/TP
collisions are ambiguous and excluded from decisive P&L. No MT5 terminal is used.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import run_sp2l_v3_xauusd_trailing_matrix as base

OUT = Path(__file__).resolve().parents[1] / "artifacts" / "v3"


def simulate(bars, candidate, entry_idx, activation_r, lock_price):
    direction = candidate["direction"]
    entry = float(candidate["theoretical_entry"])
    initial_sl = float(candidate["sl"])
    tp = float(candidate["tp"])
    risk = float(candidate["risk"])
    if risk <= 0:
        raise ValueError("Candidate risk must be positive")
    sl = initial_sl
    activated = False
    exit_price = exit_time = None
    reason = "OPEN_OR_UNRESOLVED"
    ambiguous = False
    for k in range(entry_idx + 1, len(bars)):
        b = bars[k]
        hi, lo, op = float(b["high"]), float(b["low"]), float(b["open"])
        hit_sl = lo <= sl if direction == "BUY" else hi >= sl
        hit_tp = hi >= tp if direction == "BUY" else lo <= tp
        if hit_sl and hit_tp:
            ambiguous, reason, exit_time = True, "SL_AND_TP_SAME_BAR", int(b["time"])
            break
        if hit_sl:
            fill = sl
            if direction == "BUY" and op < sl:
                fill = op
            if direction == "SELL" and op > sl:
                fill = op
            exit_price, exit_time = fill, int(b["time"])
            reason = "BREAK_EVEN_SL" if activated else "SL"
            break
        if hit_tp:
            exit_price, exit_time, reason = tp, int(b["time"]), "TP"
            break

        favorable = hi - entry if direction == "BUY" else entry - lo
        if favorable >= activation_r * risk:
            proposed = entry + lock_price if direction == "BUY" else entry - lock_price
            # Only move in the protective direction and only if the proposed
            # stop level was actually traversed by this bar. It is eligible
            # for fills starting on the next bar, never retroactively this bar.
            if direction == "BUY" and sl < proposed < hi:
                sl, activated = proposed, True
            elif direction == "SELL" and lo < proposed < sl:
                sl, activated = proposed, True

    realized_r = None
    gross_usd = None
    if exit_price is not None and not ambiguous:
        pnl_price = exit_price - entry if direction == "BUY" else entry - exit_price
        realized_r = pnl_price / risk
        gross_usd = pnl_price * 0.01 * 100.0  # 0.01 lot * 100 oz/lot
    return {
        "scenario": f"BE_{activation_r:g}R_LOCK_{lock_price:.2f}",
        "activation_R": activation_r, "lock_price": lock_price,
        "direction": direction, "trigger_time": int(candidate["trigger_time"]),
        "entry_time": int(candidate["trigger_time"]), "exit_time": exit_time,
        "entry": entry, "initial_sl": initial_sl, "initial_tp": tp,
        "risk_price": risk, "final_sl": sl, "stop_moved": activated,
        "exit_price": exit_price, "reason": reason, "ambiguous": ambiguous,
        "realized_R": realized_r, "gross_usd": gross_usd,
    }


def summarize(rows, bars_by_time, point_price, volume_lots, contract_size, commissions):
    groups = defaultdict(list)
    for r in rows:
        groups[(r["activation_R"], r["lock_price"])].append(r)
    out = []
    for (activation_r, lock_price), all_rows in groups.items():
        closed = [r for r in all_rows if r["exit_price"] is not None and not r["ambiguous"]]
        unresolved = sum(r["exit_price"] is None and not r["ambiguous"] for r in all_rows)
        ambiguous = sum(bool(r["ambiguous"]) for r in all_rows)
        gross = spread_cost = 0.0
        missing_spread = 0
        for r in closed:
            gross += float(r["realized_R"]) * r["risk_price"] * volume_lots * contract_size
            entry_bar = bars_by_time.get(int(r["entry_time"]))
            exit_bar = bars_by_time.get(int(r["exit_time"]))
            if entry_bar is None or exit_bar is None or int(entry_bar["spread"]) < 0 or int(exit_bar["spread"]) < 0:
                missing_spread += 1
                continue
            # Consistent with the previous audit's M1 spread proxy convention.
            spread_points = int(entry_bar["spread"]) if r["direction"] == "BUY" else int(exit_bar["spread"])
            spread_cost += spread_points * point_price * volume_lots * contract_size
        item = {
            "activation_R": activation_r, "lock_price": lock_price,
            "candidates": len(all_rows), "closed_decisive": len(closed),
            "ambiguous_excluded": ambiguous, "unresolved_at_dataset_end": unresolved,
            "stop_moved_count": sum(bool(r["stop_moved"]) for r in all_rows),
            "gross_usd": round(gross, 2), "spread_cost_usd": round(spread_cost, 2),
            "spread_missing_count": missing_spread,
        }
        for commission in commissions:
            comm_usd = commission * volume_lots * len(closed)
            item[f"net_usd_commission_{commission:g}_per_lot_rt"] = (
                round(gross - spread_cost - comm_usd, 2) if missing_spread == 0 else None
            )
        out.append(item)
    return sorted(out, key=lambda x: (x["activation_R"], x["lock_price"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv-path", required=True)
    ap.add_argument("--symbol", default="XAUUSD.ecn")
    ap.add_argument("--start", default="2026-08-21T00:00:00+00:00")
    ap.add_argument("--end", default="2026-09-19T00:00:00+00:00")
    ap.add_argument("--config-module", default="sp2l_v3_rr2_trail4_config")
    ap.add_argument("--point-price", type=float, default=0.01)
    ap.add_argument("--volume-lots", type=float, default=0.01)
    ap.add_argument("--contract-size", type=float, default=100.0)
    ap.add_argument("--commission-per-lot-round-turn", type=float, nargs="+", default=[0.0, 7.0, 14.0])
    ap.add_argument("--output-prefix", default="")
    a = ap.parse_args()
    start, end = datetime.fromisoformat(a.start), datetime.fromisoformat(a.end)
    if start.tzinfo is None or end.tzinfo is None or start >= end:
        raise ValueError("Use valid timezone-aware bounds")
    if min(a.point_price, a.volume_lots, a.contract_size) <= 0:
        raise ValueError("point price, volume and contract size must be positive")
    if any(x < 0 for x in a.commission_per_lot_round_turn):
        raise ValueError("Commission assumptions must be >= 0")
    cfg = __import__(a.config_module)
    bars = base.load_m1_csv(a.csv_path, start, end)
    candidates = base.collect_candidates(bars, cfg, a.symbol)
    if not candidates:
        raise RuntimeError("No candidates in requested window")
    bars_by_time = {int(b["time"]): b for b in bars}
    specs = [(0.5, 0.0), (0.5, 0.05), (1.0, 0.0), (1.0, 0.05)]
    trades = []
    for activation_r, lock_price in specs:
        for candidate, entry_idx in candidates:
            trades.append(simulate(bars, candidate, entry_idx, activation_r, lock_price))
    matrix = summarize(trades, bars_by_time, a.point_price, a.volume_lots, a.contract_size,
                       a.commission_per_lot_round_turn)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = Path(a.output_prefix) if a.output_prefix else OUT / f"SP2L_V3_BREAKEVEN_MATRIX_{stamp}"
    if root.suffix:
        root = root.with_suffix("")
    for suffix in (".json", "_matrix.csv", "_trades.csv", "_SNAPSHOT.md"):
        p = root.with_name(root.name + suffix) if suffix.startswith("_") else root.with_suffix(suffix)
        if p.exists():
            raise FileExistsError(f"Refusing to overwrite existing output: {p}")
    payload = {
        "status": "COMPLETE", "research_only": True, "canonical": False,
        "symbol": a.symbol, "timeframe": "M1",
        "window_utc": {"start": a.start, "end": a.end},
        "bars": len(bars), "bars_sha256": hashlib.sha256(bars.tobytes()).hexdigest(),
        "candidates": len(candidates), "scenario_count": 4,
        "config_module": a.config_module,
        "entry_geometry": {"version": cfg.VERSION, "p_gap_price": cfg.P_GAP_PRICE,
            "spike_multiplier": cfg.SPIKE_MULTIPLIER, "max_sl_distance": cfg.MAX_SL_DISTANCE,
            "configured_tp_R": cfg.TP_R, "session_policy": cfg.SESSION_POLICY},
        "management": "Keep original fixed TP; after 0.5R or 1R favorable excursion, move SL to entry or entry +/- 0.05 price; new stop is active from next bar.",
        "cost_model": {"spread_proxy": "M1 spread points; BUY entry spread, SELL exit spread",
            "point_price": a.point_price, "volume_lots": a.volume_lots, "contract_size": a.contract_size,
            "commission_per_lot_round_turn": a.commission_per_lot_round_turn,
            "commission_not_broker_confirmed": True,
            "excludes": ["swap", "slippage", "latency", "intrabar tick path"],
            "ambiguous_same_bar_SL_TP": "excluded, not guessed",
            "unresolved_at_dataset_end": "excluded, not assigned guessed outcome"},
        "matrix": matrix,
    }
    json_path = root.with_suffix(".json")
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    for suffix, rows in [("_matrix.csv", matrix), ("_trades.csv", trades)]:
        with root.with_name(root.name + suffix).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    snap = root.with_name(root.name + "_SNAPSHOT.md")
    snap.write_text("# Research-only break-even matrix\n\n"
        "Four scenarios only: 0.5R/1R activation x entry/entry +/- 0.05 price.\n"
        "Existing signal geometry and fixed TP are unchanged. New stop applies from next M1 bar.\n"
        "M1 spread is a proxy; commission is sensitivity only; swap/slippage/latency excluded.\n"
        "Not canonical and not a fresh holdout.\n", encoding="utf-8")
    print(json.dumps({"status": "COMPLETE", "json": str(json_path),
        "matrix_csv": str(root.with_name(root.name + "_matrix.csv")),
        "trades_csv": str(root.with_name(root.name + "_trades.csv")),
        "snapshot": str(snap), "bars": len(bars), "candidates": len(candidates),
        "matrix_rows": len(matrix), "matrix": matrix, "research_only": True, "canonical": False}, indent=2))


if __name__ == "__main__":
    main()
