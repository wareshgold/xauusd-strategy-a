"""Offline Tick replay for the 27 one-entry/two-leg partial-close variants.

One 0.02-lot entry is modeled as two 0.01-lot legs. The first leg exits at
1R; the second exits at 2R, 3R, or the V3.1 4R/trailing profile.
Research-only: no MT5 imports, terminal access, network, or order APIs.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import heapq
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from research.capital_matrix.matrix import BrokerSpec, INITIAL_CAPITAL
from research.capital_matrix.partial_matrix import (
    build_partial_matrix, size_partial_run, TRAIL_ACTIVATION, TRAIL_DISTANCE,
)
from research.capital_matrix.replay_v31_tick_matrix import (
    EXPECTED_MANIFEST_SHA256, EXPECTED_M1_SHA256, EXPECTED_POPULATION_SHA256,
    EXPECTED_SYMBOL_SPECS_SHA256, EXPECTED_TICK_SHA256, POP_FIELDS, TICK_FIELDS,
    INITIAL_EQUITY, PENDING_TTL_SECONDS, parse_utc_epoch, round_price, sha256_file,
    load_inputs,
)

BROKER = BrokerSpec(Decimal("0.01"), Decimal("1"), Decimal("0.01"),
                    Decimal("100"), Decimal("0.01"))
TP1_R = 1.0


@dataclass
class PartialPortfolio:
    run: object
    equity: Decimal = INITIAL_EQUITY
    entry_index: int = 0
    state: str = "FLAT"
    pending: dict | None = None
    position: dict | None = None
    rows: list = field(default_factory=list)
    counts: dict = field(default_factory=lambda: {
        "FILLED_AND_CLOSED": 0, "PARTIAL_LEG_CLOSED": 0,
        "UNFILLED_EXPIRED": 0, "REJECTED_NOT_PLACEABLE": 0,
        "REJECTED_EXPOSURE_BUSY": 0, "INFEASIBLE_SIZE": 0,
        "AMBIGUOUS_DATA": 0,
    })


def candidate(p, row, status, **extra):
    item = {
        "run_id": p.run.run_id, "family": "PARTIAL_CLOSE",
        "candidate_entry_time_utc": row["entry_time_utc"],
        "direction": row["direction"], "status": status,
        "theoretical_entry": float(row["entry_proxy"]),
        "initial_sl": float(row["sl_initial"]),
        "risk_price": float(row["risk_price"]),
        "equity_before": float(p.equity),
    }
    item.update(extra)
    p.rows.append(item)
    p.counts[status] = p.counts.get(status, 0) + 1


def close_leg(p, now_ms, exit_price, reason, lots, leg_name, final=False):
    pos = p.position
    row = pos["row"]
    direction = row["direction"]
    signed = exit_price - pos["fill_price"]
    if direction == "SELL":
        signed = -signed
    pnl = (Decimal(str(signed)) / BROKER.tick_size *
           BROKER.tick_value_per_lot * Decimal(str(lots)))
    before = p.equity
    p.equity += pnl
    item = {
        "run_id": p.run.run_id, "family": "PARTIAL_CLOSE",
        "candidate_entry_time_utc": row["entry_time_utc"],
        "direction": direction,
        "status": "FILLED_AND_CLOSED" if final else "PARTIAL_LEG_CLOSED",
        "leg": leg_name, "submission_time_utc": datetime.fromtimestamp(
            pos["submission_ms"]/1000, timezone.utc).isoformat(),
        "fill_time_utc": datetime.fromtimestamp(pos["fill_ms"]/1000, timezone.utc).isoformat(),
        "fill_price": pos["fill_price"], "theoretical_entry": pos["theoretical_entry"],
        "initial_sl": pos["initial_sl"], "final_sl": pos["sl"],
        "exit_time_utc": datetime.fromtimestamp(now_ms/1000, timezone.utc).isoformat(),
        "exit_price": exit_price, "exit_reason": reason, "lots": lots,
        "gross_pnl_usd": float(pnl),
        "r_multiple": signed / pos["actual_initial_risk_price"] if pos["actual_initial_risk_price"] else 0,
        "requested_risk_usd": pos["requested_risk_usd"],
        "sizing_actual_risk_usd": pos["sizing_actual_risk_usd"],
        "equity_before": float(before), "equity_after": float(p.equity),
        "trail_activated": pos["trail_active"], "tick_gap_exposed": pos["gap_exposed"],
        "commission": "NOT_PROVIDED", "swap": "NOT_PROVIDED",
        "slippage": "NOT_CALIBRATED",
    }
    p.rows.append(item)
    p.counts[item["status"]] += 1
    return pnl


def submit_candidate(p, row, now_ms, bid, ask):
    if p.state != "FLAT":
        candidate(p, row, "REJECTED_EXPOSURE_BUSY",
                  rejection_reason="MAX_OPEN_POSITIONS_1")
        return
    direction = row["direction"]
    entry = float(row["entry_proxy"])
    if not (entry < ask if direction == "BUY" else entry > bid):
        candidate(p, row, "REJECTED_NOT_PLACEABLE",
                  rejection_reason="LIMIT_ENTRY_NOT_PLACEABLE_AT_SUBMISSION_QUOTE",
                  submission_time_utc=datetime.fromtimestamp(now_ms/1000, timezone.utc).isoformat())
        return
    p.pending = {"row": row, "submit_ms": now_ms,
                 "expires_ms": now_ms + int(PENDING_TTL_SECONDS*1000)}
    p.state = "PENDING"


def fill_pending(p, now_ms, bid, ask):
    q = p.pending
    if q is None:
        return
    row = q["row"]
    direction = row["direction"]
    theoretical = float(row["entry_proxy"])
    fillable = ask <= theoretical if direction == "BUY" else bid >= theoretical
    if now_ms >= q["expires_ms"]:
        candidate(p, row, "UNFILLED_EXPIRED",
                  submission_time_utc=datetime.fromtimestamp(q["submit_ms"]/1000, timezone.utc).isoformat(),
                  expiry_time_utc=datetime.fromtimestamp(q["expires_ms"]/1000, timezone.utc).isoformat())
        p.pending = None
        p.state = "FLAT"
        return
    if not fillable:
        return
    stop = float(row["sl_initial"])
    if (direction == "BUY" and stop >= theoretical) or (direction == "SELL" and stop <= theoretical):
        candidate(p, row, "AMBIGUOUS_DATA", ambiguity="INVALID_INITIAL_STOP_GEOMETRY")
        p.pending = None
        p.state = "FLAT"
        return
    sizing = size_partial_run(
        p.run, initial_capital=INITIAL_EQUITY, current_equity=p.equity,
        stop_distance_price=Decimal(str(abs(theoretical-stop))), broker=BROKER,
    )
    if not sizing.feasible:
        candidate(p, row, "INFEASIBLE_SIZE", sizing_reason=sizing.reason,
                  requested_risk_usd=float(sizing.requested_risk_usd))
        p.pending = None
        p.state = "FLAT"
        return
    fill = ask if direction == "BUY" else bid
    risk = float(row["risk_price"])
    tp1 = theoretical + TP1_R*risk if direction == "BUY" else theoretical - TP1_R*risk
    tp2 = theoretical + float(p.run.tp2_r)*risk if direction == "BUY" else theoretical - float(p.run.tp2_r)*risk
    p.position = {
        "row": row, "fill_ms": now_ms, "fill_price": fill,
        "theoretical_entry": theoretical, "initial_sl": stop, "sl": stop,
        "tp1": tp1, "tp2": tp2, "first_lots": float(sizing.leg_lots),
        "remaining_lots": float(sizing.total_lots), "first_done": False,
        "actual_initial_risk_price": abs(fill-stop),
        "requested_risk_usd": float(sizing.requested_risk_usd),
        "sizing_actual_risk_usd": float(sizing.actual_risk_usd),
        "submission_ms": q["submit_ms"], "trail_active": False,
        "favorable_extreme": fill, "gap_exposed": False,
        "is_runner": p.run.is_runner,
    }
    p.pending = None
    p.state = "OPEN"


def process_bar_close(p, bar, bid, ask):
    pos = p.position
    if not pos or not pos["is_runner"]:
        return
    if bar["time"]*1000 <= pos["fill_ms"]:
        return
    direction = pos["row"]["direction"]
    if direction == "BUY":
        pos["favorable_extreme"] = max(pos["favorable_extreme"], bar["high"])
        move = pos["favorable_extreme"] - pos["fill_price"]
    else:
        pos["favorable_extreme"] = min(pos["favorable_extreme"], bar["low"])
        move = pos["fill_price"] - pos["favorable_extreme"]
    if move + 1e-12 < float(TRAIL_ACTIVATION):
        return
    pos["trail_active"] = True
    raw = (pos["favorable_extreme"] - float(TRAIL_DISTANCE) if direction == "BUY"
           else pos["favorable_extreme"] + float(TRAIL_DISTANCE))
    proposed = round_price(raw, 0.01, direction)
    placeable = proposed < bid - 1e-9 if direction == "BUY" else proposed > ask + 1e-9
    better = proposed > pos["sl"] if direction == "BUY" else proposed < pos["sl"]
    if placeable and better:
        pos["sl"] = proposed


def process_tick(p, now_ms, bid, ask):
    if p.pending:
        fill_pending(p, now_ms, bid, ask)
    pos = p.position
    if not pos:
        return
    direction = pos["row"]["direction"]
    quote = bid if direction == "BUY" else ask
    sl_hit = quote <= pos["sl"] if direction == "BUY" else quote >= pos["sl"]
    tp1_hit = quote >= pos["tp1"] if direction == "BUY" else quote <= pos["tp1"]
    tp2_hit = quote >= pos["tp2"] if direction == "BUY" else quote <= pos["tp2"]
    # Stop is conservatively first on a quote touching conflicting levels.
    if sl_hit:
        close_leg(p, now_ms, quote, "SL_OR_TRAILING_SL",
                  pos["remaining_lots"], "REMAINDER", final=True)
        if not pos["first_done"]:
            # Both legs remain intact before TP1.
            pos["remaining_lots"] = 0.0
        p.position = None
        p.state = "FLAT"
        return
    if not pos["first_done"] and tp1_hit:
        close_leg(p, now_ms, quote, "TP1_1R", pos["first_lots"], "TP1", final=False)
        pos["first_done"] = True
        pos["remaining_lots"] = pos["first_lots"]
        # A quote can leap through TP1 and TP2; process the second leg on this tick.
    if pos["first_done"] and tp2_hit:
        close_leg(p, now_ms, quote, "TP2_OR_RUNNER_TP", pos["remaining_lots"],
                  "TP2_OR_RUNNER", final=True)
        p.position = None
        p.state = "FLAT"


def run_replay(entries, bars, tick_path: Path, latency_seconds: float):
    portfolios = [PartialPortfolio(run) for run in build_partial_matrix()]
    latency_ms = int(latency_seconds*1000)
    bar_i = 0
    previous_ms = -1
    previous_tick_ms = None
    tick_count = 0
    gaps_gt_60 = 0
    first_tick_ms = None
    due_heap = []
    for idx in range(len(portfolios)):
        due = parse_utc_epoch(entries[0]["entry_time_utc"])*1000 + 60_000 + latency_ms
        heapq.heappush(due_heap, (due, idx))
    active = {}
    with gzip.open(tick_path, "rt", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != TICK_FIELDS:
            raise ValueError(f"unexpected Tick header: {reader.fieldnames}")
        for line, tick in enumerate(reader, 2):
            now_ms = int(tick["time_msc"])
            bid, ask = float(tick["bid"]), float(tick["ask"])
            if now_ms < previous_ms or not all(math.isfinite(x) and x > 0 for x in (bid,ask)) or ask < bid:
                raise ValueError(f"invalid/out-of-order tick at line {line}")
            gap_now = previous_tick_ms is not None and now_ms-previous_tick_ms > 60_000
            if gap_now:
                gaps_gt_60 += 1
            if first_tick_ms is None:
                first_tick_ms = now_ms
            previous_ms = now_ms
            previous_tick_ms = now_ms
            tick_count += 1
            while bar_i < len(bars) and (bars[bar_i]["time"]+60)*1000 <= now_ms:
                bar = bars[bar_i]
                for p in active.values():
                    process_bar_close(p, bar, bid, ask)
                bar_i += 1
            for idx, p in list(active.items()):
                if gap_now and p.position:
                    p.position["gap_exposed"] = True
                process_tick(p, now_ms, bid, ask)
                if p.state == "FLAT":
                    del active[idx]
            while due_heap and due_heap[0][0] <= now_ms:
                _, idx = heapq.heappop(due_heap)
                p = portfolios[idx]
                row = entries[p.entry_index]
                p.entry_index += 1
                was_flat = p.state == "FLAT"
                submit_candidate(p, row, now_ms, bid, ask)
                if p.state != "FLAT":
                    active[idx] = p
                if p.entry_index < len(entries):
                    due = parse_utc_epoch(entries[p.entry_index]["entry_time_utc"])*1000 + 60_000 + latency_ms
                    heapq.heappush(due_heap, (due, idx))
    last_ms = previous_ms
    for p in portfolios:
        while p.entry_index < len(entries):
            row = entries[p.entry_index]
            candidate(p, row, "AMBIGUOUS_DATA", ambiguity="NO_TICK_AT_OR_AFTER_SCHEDULED_SUBMISSION")
            p.entry_index += 1
        if p.pending:
            candidate(p, p.pending["row"], "AMBIGUOUS_DATA",
                      ambiguity="TICK_SOURCE_ENDED_BEFORE_PENDING_RESOLUTION")
            p.pending = None
        if p.position:
            pos = p.position
            candidate(p, pos["row"], "AMBIGUOUS_DATA",
                      ambiguity="TICK_SOURCE_ENDED_WITH_OPEN_POSITION",
                      fill_time_utc=datetime.fromtimestamp(pos["fill_ms"]/1000, timezone.utc).isoformat(),
                      last_tick_utc=datetime.fromtimestamp(last_ms/1000, timezone.utc).isoformat())
            p.position = None
    return portfolios, {"tick_rows": tick_count, "tick_gaps_gt_60s": gaps_gt_60,
                        "first_tick_ms": first_tick_ms, "last_tick_ms": last_ms,
                        "latency_seconds": latency_seconds}


def summarize(p):
    closed = [r for r in p.rows if r.get("status") in ("PARTIAL_LEG_CLOSED", "FILLED_AND_CLOSED")]
    final = [r for r in p.rows if r.get("status") == "FILLED_AND_CLOSED"]
    pnls = [float(r["gross_pnl_usd"]) for r in closed]
    wins = [x for x in pnls if x > 0]
    losses = [x for x in pnls if x < 0]
    gp, gl = sum(wins), abs(sum(losses))
    peak = equity = float(INITIAL_EQUITY)
    max_dd = 0.0
    for r in closed:
        equity = float(r["equity_after"])
        peak = max(peak, equity)
        max_dd = max(max_dd, (peak-equity)/peak if peak else 0.0)
    return {
        "run_id": p.run.run_id, "family": "PARTIAL_CLOSE",
        "closed_trades": len(final), "closed_legs": len(closed),
        "gross_net_usd": sum(pnls), "profit_factor": gp/gl if gl else None,
        "win_rate": len(wins)/len(closed) if closed else None,
        "average_r": sum(float(r["r_multiple"]) for r in closed)/len(closed) if closed else None,
        "max_drawdown_fraction": max_dd, "ending_equity_gross": float(p.equity),
        "counts": p.counts,
        "cost_status": "GROSS_ONLY_COMMISSION_SWAP_SLIPPAGE_NOT_INCLUDED",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--population", required=True)
    ap.add_argument("--population-manifest", required=True)
    ap.add_argument("--m1-csv-gz", required=True)
    ap.add_argument("--ticks-csv-gz", required=True)
    ap.add_argument("--symbol-specs", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--latency-seconds", type=float, default=2.0)
    ap.add_argument("--population-sha256", default=EXPECTED_POPULATION_SHA256)
    ap.add_argument("--manifest-sha256", default=EXPECTED_MANIFEST_SHA256)
    ap.add_argument("--m1-sha256", default=EXPECTED_M1_SHA256)
    ap.add_argument("--ticks-sha256", default=EXPECTED_TICK_SHA256)
    ap.add_argument("--symbol-specs-sha256", default=EXPECTED_SYMBOL_SPECS_SHA256)
    args = ap.parse_args()
    if not 0 <= args.latency_seconds <= 30:
        raise ValueError("latency must be between 0 and 30 seconds")
    out = Path(args.output_dir).resolve()
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise FileExistsError(f"output directory must be new/empty: {out}")
    out.mkdir(parents=True, exist_ok=True)
    entries, bars, _ = load_inputs(
        Path(args.population), Path(args.population_manifest), Path(args.m1_csv_gz),
        Path(args.ticks_csv_gz), Path(args.symbol_specs),
        args.population_sha256, args.manifest_sha256, args.m1_sha256,
        args.ticks_sha256, args.symbol_specs_sha256,
    )
    portfolios, stats = run_replay(entries, bars, Path(args.ticks_csv_gz), args.latency_seconds)
    detail = out / "SP2L_PARTIAL_MATRIX_TRADE_REPLAY.csv"
    summary = out / "SP2L_PARTIAL_MATRIX_RUN_SUMMARY.csv"
    with detail.open("x", encoding="utf-8", newline="") as stream:
        fields = sorted({key for p in portfolios for row in p.rows for key in row})
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for p in portfolios:
            writer.writerows(p.rows)
    summaries = [summarize(p) for p in portfolios]
    with summary.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summaries[0]))
        writer.writeheader()
        for row in summaries:
            row = dict(row)
            row["counts"] = json.dumps(row["counts"], sort_keys=True)
            writer.writerow(row)
    code_dir = Path(__file__).resolve().parent
    code_hashes = {
        "partial_replay_script": sha256_file(Path(__file__).resolve()),
        "partial_matrix_definition": sha256_file(code_dir / "partial_matrix.py"),
        "base_replay_script": sha256_file(code_dir / "replay_v31_tick_matrix.py"),
        "matrix_definition": sha256_file(code_dir / "matrix.py"),
    }
    manifest = {
        "status": "COMPLETE_GROSS_ONLY", "research_only": True, "canonical": False,
        "mt5_accessed": False, "runner_accessed": False, "orders_possible": False,
        "population_rows": len(entries), "partial_matrix_runs": len(portfolios),
        "fixed_volume_references": 3, "risk_normalized_variants": 24,
        "execution_assumptions": {
            "latency_seconds": args.latency_seconds,
            "submission": "first_tick_at_or_after_trigger_bar_close_plus_latency",
            "pending_order": "BUY fills when Ask <= limit; SELL fills when Bid >= limit",
            "pending_ttl_seconds": PENDING_TTL_SECONDS,
            "portfolio_exposure_limit": 1,
            "entry": "one 0.02-lot position; 0.01 lot closed at TP1=1R; 0.01 lot remains",
            "second_leg_exit": "2R, 3R, or 4R target with V3.1 0.40/0.40 completed-M1 trailing",
            "sl_after_tp1": "initial stop retained; no break-even move",
            "same_tick_sl_tp": "SL prioritized conservatively",
            "end_of_source": "open/pending positions censored, not force-closed",
        },
        "input_sha256": {
            "population": args.population_sha256, "population_manifest": args.manifest_sha256,
            "m1": args.m1_sha256, "ticks": args.ticks_sha256,
            "symbol_specs": args.symbol_specs_sha256,
        },
        "code_sha256": code_hashes,
        "broker_contract": {"symbol": "XAUUSD.ecn", "digits": 2, "tick_size": 0.01,
            "tick_value_per_lot_usd": 1.0, "volume_min": 0.01,
            "volume_step": 0.01, "volume_max": 100.0},
        "cost_limitations": ["Commission not provided", "Swap not provided",
            "Slippage not calibrated", "Broker minimum stop distance unavailable; trailing assumes zero"],
        "tick_stats": stats,
        "output_sha256": {detail.name: sha256_file(detail), summary.name: sha256_file(summary)},
        "note": "Assumed historical execution replay, not proof of historical broker fills.",
    }
    manifest_path = out / "SP2L_PARTIAL_MATRIX_REPLAY_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "runs": len(portfolios),
        "fixed_volume_references": 3, "risk_normalized_variants": 24,
        "tick_rows": stats["tick_rows"], "latency_seconds": args.latency_seconds,
        "detail_csv": str(detail), "summary_csv": str(summary),
        "manifest": str(manifest_path), "summary": summaries},
        indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
