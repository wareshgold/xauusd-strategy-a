"""Offline V3.1 tick replay for the executable 49-run capital matrix.

Research only. Standard-library implementation; no MT5 imports, network calls,
terminal access, or order APIs. Tick data is streamed once while all eligible
single-exposure portfolios are advanced in parallel.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN
from pathlib import Path

from research.capital_matrix.matrix import (
    INITIAL_CAPITAL, BrokerSpec, Family, build_matrix, size_run,
)

EXPECTED_TICK_SHA256 = "8fb7589922980df0bf0cf4ffe1babf6ad82768bedac784bf62ffa2a9d698386f"
EXPECTED_POPULATION_SHA256 = "f29879c837938e22a851dd967a33740ea7f4b781e741f4119a2dd25ef4c598c5"
EXPECTED_M1_SHA256 = "daf4eb26c47ef0dadc045c76b9a72b667751e1eac315697a6b024e81e355c402"
EXPECTED_MANIFEST_SHA256 = "0919987a69fbc403d064113c999664c5e4da309c3d9989254c300f2723fcbd09"
TICK_FIELDS = ["time_msc", "time_utc", "bid", "ask", "last", "volume", "flags"]
POP_FIELDS = ["strategy","variant","direction","setup_time_utc","entry_time_utc",
              "entry_proxy","sl_initial","target","risk_price","exit_time_utc",
              "exit_price","exit_reason","status","r_multiple"]
INITIAL_EQUITY = Decimal("1000")
BROKER = BrokerSpec(Decimal("0.01"), Decimal("1"), Decimal("0.01"),
                    Decimal("100"), Decimal("0.01"))
LATENCY_SECONDS = 2.0
PENDING_TTL_SECONDS = 1800.0
TRAIL_ACTIVATION = 0.40
TRAIL_DISTANCE = 0.40


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_utc_epoch(value: str) -> int:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"timestamp is not timezone-aware: {value}")
    return int(dt.timestamp())


def load_inputs(population_path: Path, population_manifest: Path,
                m1_path: Path, tick_path: Path,
                expected_population_sha: str, expected_manifest_sha: str,
                expected_m1_sha: str, expected_tick_sha: str):
    for path, expected, label in (
        (population_path, expected_population_sha, "population"),
        (population_manifest, expected_manifest_sha, "population manifest"),
        (m1_path, expected_m1_sha, "M1 source"),
        (tick_path, expected_tick_sha, "tick source"),
    ):
        actual = sha256_file(path)
        if actual.lower() != expected.lower():
            raise ValueError(f"{label} SHA-256 mismatch: expected {expected}, got {actual}")
    manifest = json.loads(population_manifest.read_text(encoding="utf-8"))
    if manifest.get("population_sha256", "").lower() != expected_population_sha.lower():
        raise ValueError("population manifest does not bind the expected CSV SHA")
    if manifest.get("source_sha256", "").lower() != expected_m1_sha.lower():
        raise ValueError("population manifest does not bind the expected M1 SHA")
    with population_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != POP_FIELDS:
            raise ValueError(f"unexpected population header: {reader.fieldnames}")
        entries = list(reader)
    if len(entries) != 1518:
        raise ValueError(f"expected 1518 frozen entries, got {len(entries)}")
    previous = -1
    for row in entries:
        ts = parse_utc_epoch(row["entry_time_utc"])
        if ts < previous:
            raise ValueError("population entries are not chronological")
        previous = ts
        if row["direction"] not in ("BUY", "SELL"):
            raise ValueError("invalid direction in population")
        for k in ("entry_proxy", "sl_initial", "risk_price"):
            if not math.isfinite(float(row[k])):
                raise ValueError(f"non-finite {k}")
    bars = []
    with gzip.open(m1_path, "rt", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        expected_header = ["time","time_utc","open","high","low","close",
                           "tick_volume","spread_points","real_volume"]
        if reader.fieldnames != expected_header:
            raise ValueError(f"unexpected M1 header: {reader.fieldnames}")
        for row in reader:
            bars.append({"time":int(row["time"]), "high":float(row["high"]),
                         "low":float(row["low"])})
    if len(bars) != 89866:
        raise ValueError(f"expected 89866 M1 bars, got {len(bars)}")
    return entries, bars, manifest


@dataclass
class Portfolio:
    run: object
    equity: Decimal = INITIAL_EQUITY
    entry_index: int = 0
    state: str = "FLAT"
    pending: dict | None = None
    position: dict | None = None
    rows: list = field(default_factory=list)
    counts: dict = field(default_factory=lambda: {
        "FILLED_AND_CLOSED":0, "UNFILLED_EXPIRED":0,
        "REJECTED_NOT_PLACEABLE":0, "REJECTED_EXPOSURE_BUSY":0,
        "INFEASIBLE_SIZE":0, "AMBIGUOUS_DATA":0,
    })


def emit_candidate(p: Portfolio, row: dict, status: str, **extra):
    out = {
        "run_id":p.run.run_id, "family":p.run.family.value,
        "candidate_entry_time_utc":row["entry_time_utc"],
        "direction":row["direction"], "status":status,
        "theoretical_entry":float(row["entry_proxy"]),
        "initial_sl":float(row["sl_initial"]),
        "risk_price":float(row["risk_price"]),
        "equity_before":float(p.equity),
    }
    out.update(extra)
    p.rows.append(out)
    p.counts[status] = p.counts.get(status, 0) + 1


def round_price(value: float, tick: float, direction: str) -> float:
    units = value / tick
    if direction == "BUY":
        units = math.floor(units + 1e-10)
    else:
        units = math.ceil(units - 1e-10)
    return round(units * tick, 2)


def process_candidate_due(p: Portfolio, entries: list[dict], now_ms: int,
                          bid: float, ask: float, latency_ms: int):
    while p.entry_index < len(entries):
        row = entries[p.entry_index]
        trigger_ms = parse_utc_epoch(row["entry_time_utc"]) * 1000
        submit_ms = trigger_ms + 60_000 + latency_ms
        if submit_ms > now_ms:
            break
        p.entry_index += 1
        if p.state != "FLAT":
            emit_candidate(p, row, "REJECTED_EXPOSURE_BUSY",
                           rejection_reason="MAX_OPEN_POSITIONS_1")
            continue
        direction = row["direction"]
        entry = float(row["entry_proxy"])
        placeable = entry < ask if direction == "BUY" else entry > bid
        if not placeable:
            emit_candidate(p, row, "REJECTED_NOT_PLACEABLE",
                           rejection_reason="LIMIT_ENTRY_NOT_PLACEABLE_AT_SUBMISSION_QUOTE",
                           submission_time_utc=datetime.fromtimestamp(now_ms/1000, timezone.utc).isoformat())
            continue
        p.pending = {"row":row, "submit_ms":now_ms,
                     "expires_ms":now_ms + int(PENDING_TTL_SECONDS*1000)}
        p.state = "PENDING"


def fill_pending(p: Portfolio, now_ms: int, bid: float, ask: float):
    q = p.pending
    if q is None:
        return
    row = q["row"]
    direction = row["direction"]
    theoretical = float(row["entry_proxy"])
    fillable = ask <= theoretical if direction == "BUY" else bid >= theoretical
    if now_ms >= q["expires_ms"]:
        emit_candidate(p, row, "UNFILLED_EXPIRED",
                       submission_time_utc=datetime.fromtimestamp(q["submit_ms"]/1000, timezone.utc).isoformat(),
                       expiry_time_utc=datetime.fromtimestamp(q["expires_ms"]/1000, timezone.utc).isoformat())
        p.pending = None
        p.state = "FLAT"
        return
    if not fillable:
        return
    fill = ask if direction == "BUY" else bid
    stop = float(row["sl_initial"])
    risk = float(row["risk_price"])
    if direction == "BUY" and not stop < theoretical or direction == "SELL" and not stop > theoretical:
        emit_candidate(p, row, "AMBIGUOUS_DATA", ambiguity="INVALID_INITIAL_STOP_GEOMETRY")
        p.pending = None
        p.state = "FLAT"
        return
    stop_distance = abs(theoretical - stop)
    if p.run.family is Family.EXACT_RUNNER:
        sized = size_run(p.run, initial_capital=INITIAL_EQUITY,
                         current_equity=p.equity, stop_distance_price=Decimal(str(stop_distance)),
                         broker=BROKER)[0]
    else:
        sized = size_run(p.run, initial_capital=INITIAL_EQUITY,
                         current_equity=p.equity, stop_distance_price=Decimal(str(stop_distance)),
                         broker=BROKER)[0]
    if not sized.feasible:
        emit_candidate(p, row, "INFEASIBLE_SIZE",
                       sizing_reason=sized.reason, requested_risk_usd=float(sized.requested_risk_usd))
        p.pending = None
        p.state = "FLAT"
        return
    lots = float(sized.volume_lots)
    if p.run.family is Family.FIXED_TP:
        tp_r = float(p.run.tp_r)
        target = theoretical + tp_r*risk if direction == "BUY" else theoretical - tp_r*risk
        is_runner = False
    else:
        target = float(row["target"])
        is_runner = True
    p.position = {
        "row":row, "fill_ms":now_ms, "fill_price":fill, "lots":lots,
        "theoretical_entry":theoretical, "sl":stop, "tp":target,
        "initial_risk":risk, "favorable_extreme":theoretical,
        "trail_active":False, "is_runner":is_runner,
        "submission_ms":q["submit_ms"], "gap_exposed":False,
    }
    p.pending = None
    p.state = "OPEN"


def process_bar_close(p: Portfolio, bar: dict, close_ms: int, bid: float, ask: float):
    pos = p.position
    if not pos or not pos["is_runner"]:
        return
    if bar["time"]*1000 <= pos["fill_ms"]:
        return
    direction = pos["row"]["direction"]
    if direction == "BUY":
        pos["favorable_extreme"] = max(pos["favorable_extreme"], bar["high"])
        move = pos["favorable_extreme"] - pos["theoretical_entry"]
    else:
        pos["favorable_extreme"] = min(pos["favorable_extreme"], bar["low"])
        move = pos["theoretical_entry"] - pos["favorable_extreme"]
    if move + 1e-12 < TRAIL_ACTIVATION:
        return
    pos["trail_active"] = True
    raw = (pos["favorable_extreme"] - TRAIL_DISTANCE if direction == "BUY"
           else pos["favorable_extreme"] + TRAIL_DISTANCE)
    candidate = round_price(raw, 0.01, direction)
    # Mirror the broker-side validity check with zero known minimum distance.
    placeable = candidate < bid - 1e-9 if direction == "BUY" else candidate > ask + 1e-9
    if not placeable:
        return
    better = candidate > pos["sl"] if direction == "BUY" else candidate < pos["sl"]
    if better:
        pos["sl"] = candidate


def close_position(p: Portfolio, now_ms: int, exit_price: float, reason: str):
    pos = p.position
    row = pos["row"]
    direction = row["direction"]
    signed = exit_price - pos["fill_price"]
    if direction == "SELL":
        signed = -signed
    pnl = (Decimal(str(signed)) / BROKER.tick_size *
           BROKER.tick_value_per_lot * Decimal(str(pos["lots"])))
    before = p.equity
    p.equity += pnl
    r_multiple = signed / pos["initial_risk"] if pos["initial_risk"] else 0.0
    out = {
        "run_id":p.run.run_id, "family":p.run.family.value,
        "candidate_entry_time_utc":row["entry_time_utc"], "direction":direction,
        "status":"FILLED_AND_CLOSED", "submission_time_utc":datetime.fromtimestamp(pos["submission_ms"]/1000, timezone.utc).isoformat(),
        "fill_time_utc":datetime.fromtimestamp(pos["fill_ms"]/1000, timezone.utc).isoformat(),
        "fill_price":pos["fill_price"], "theoretical_entry":pos["theoretical_entry"],
        "fill_deviation":pos["fill_price"]-pos["theoretical_entry"],
        "initial_sl":float(row["sl_initial"]), "final_sl":pos["sl"],
        "tp":pos["tp"], "exit_time_utc":datetime.fromtimestamp(now_ms/1000, timezone.utc).isoformat(),
        "exit_price":exit_price, "exit_reason":reason, "lots":pos["lots"],
        "gross_pnl_usd":float(pnl), "r_multiple":r_multiple,
        "equity_before":float(before), "equity_after":float(p.equity),
        "trail_activated":pos["trail_active"], "tick_gap_exposed":pos["gap_exposed"],
        "commission":"NOT_PROVIDED", "swap":"NOT_PROVIDED",
        "slippage":"NOT_CALIBRATED",
    }
    p.rows.append(out)
    p.counts["FILLED_AND_CLOSED"] += 1
    p.position = None
    p.state = "FLAT"


def process_tick(p: Portfolio, now_ms: int, bid: float, ask: float):
    if p.pending:
        fill_pending(p, now_ms, bid, ask)
    pos = p.position
    if not pos:
        return
    direction = pos["row"]["direction"]
    quote = bid if direction == "BUY" else ask
    sl_hit = quote <= pos["sl"] if direction == "BUY" else quote >= pos["sl"]
    tp_hit = quote >= pos["tp"] if direction == "BUY" else quote <= pos["tp"]
    # Tick sequence resolves order when separate ticks hit levels. If both
    # predicates are true on the same quote, stop is conservatively prioritized.
    if sl_hit:
        close_position(p, now_ms, quote, "SL_OR_TRAILING_SL")
    elif tp_hit:
        close_position(p, now_ms, quote, "TP")


def run_replay(entries, bars, tick_path: Path, latency_seconds: float):
    runs = [r for r in build_matrix() if r.family in
            (Family.FIXED_TP, Family.EXACT_RUNNER, Family.NORMALIZED_RUNNER)]
    portfolios = [Portfolio(r) for r in runs]
    bar_i = 0
    latency_ms = int(latency_seconds*1000)
    tick_count = 0
    previous_ms = -1
    gaps_gt_60 = 0
    previous_tick_ms = None
    with gzip.open(tick_path, "rt", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != TICK_FIELDS:
            raise ValueError(f"unexpected Tick header: {reader.fieldnames}")
        for line, row in enumerate(reader, 2):
            now_ms = int(row["time_msc"])
            bid, ask = float(row["bid"]), float(row["ask"])
            if now_ms < previous_ms or not all(math.isfinite(x) and x > 0 for x in (bid,ask)) or ask < bid:
                raise ValueError(f"invalid or out-of-order tick at line {line}")
            if previous_tick_ms is not None and now_ms-previous_tick_ms > 60_000:
                gaps_gt_60 += 1
            gap_now = previous_tick_ms is not None and now_ms-previous_tick_ms > 60_000
            previous_ms = previous_tick_ms = now_ms
            tick_count += 1
            while bar_i < len(bars) and (bars[bar_i]["time"]+60)*1000 <= now_ms:
                bar = bars[bar_i]
                close_ms = (bar["time"]+60)*1000
                for p in portfolios:
                    process_bar_close(p, bar, close_ms, bid, ask)
                bar_i += 1
            for p in portfolios:
                if gap_now and p.position:
                    p.position["gap_exposed"] = True
                process_candidate_due(p, entries, now_ms, bid, ask, latency_ms)
                process_tick(p, now_ms, bid, ask)
    # Anything still open/pending at end of source is censored, never force-closed.
    last_ms = previous_ms
    for p in portfolios:
        if p.pending:
            emit_candidate(p, p.pending["row"], "AMBIGUOUS_DATA",
                           ambiguity="TICK_SOURCE_ENDED_BEFORE_PENDING_RESOLUTION")
            p.pending = None
        if p.position:
            pos = p.position
            emit_candidate(p, pos["row"], "AMBIGUOUS_DATA",
                           ambiguity="TICK_SOURCE_ENDED_WITH_OPEN_POSITION",
                           fill_time_utc=datetime.fromtimestamp(pos["fill_ms"]/1000, timezone.utc).isoformat(),
                           last_tick_utc=datetime.fromtimestamp(last_ms/1000, timezone.utc).isoformat())
            p.position = None
    return portfolios, {"tick_rows":tick_count,"tick_gaps_gt_60s":gaps_gt_60,
                        "first_tick_ms":None,"last_tick_ms":last_ms,
                        "latency_seconds":latency_seconds}


def summarize(p: Portfolio):
    closed = [x for x in p.rows if x.get("status") == "FILLED_AND_CLOSED"]
    pnls = [float(x["gross_pnl_usd"]) for x in closed]
    wins = [x for x in pnls if x > 0]
    losses = [x for x in pnls if x < 0]
    gross_profit, gross_loss = sum(wins), abs(sum(losses))
    peak = float(INITIAL_EQUITY)
    equity = float(INITIAL_EQUITY)
    max_dd = 0.0
    for x in closed:
        equity = float(x["equity_after"])
        peak = max(peak, equity)
        if peak:
            max_dd = max(max_dd, (peak-equity)/peak)
    return {
        "run_id":p.run.run_id, "family":p.run.family.value,
        "closed_trades":len(closed), "gross_net_usd":sum(pnls),
        "profit_factor":gross_profit/gross_loss if gross_loss else None,
        "win_rate":len(wins)/len(closed) if closed else None,
        "average_r":sum(x["r_multiple"] for x in closed)/len(closed) if closed else None,
        "max_drawdown_fraction":max_dd, "ending_equity_gross":float(p.equity),
        "counts":p.counts,
        "cost_status":"GROSS_ONLY_COMMISSION_SWAP_SLIPPAGE_NOT_INCLUDED",
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--population",required=True)
    ap.add_argument("--population-manifest",required=True)
    ap.add_argument("--m1-csv-gz",required=True)
    ap.add_argument("--ticks-csv-gz",required=True)
    ap.add_argument("--output-dir",required=True)
    ap.add_argument("--latency-seconds",type=float,default=LATENCY_SECONDS)
    ap.add_argument("--population-sha256",default=EXPECTED_POPULATION_SHA256)
    ap.add_argument("--manifest-sha256",default=EXPECTED_MANIFEST_SHA256)
    ap.add_argument("--m1-sha256",default=EXPECTED_M1_SHA256)
    ap.add_argument("--ticks-sha256",default=EXPECTED_TICK_SHA256)
    args=ap.parse_args()
    if args.latency_seconds < 0 or args.latency_seconds > 30:
        raise ValueError("latency must be between 0 and 30 seconds")
    outdir=Path(args.output_dir).resolve()
    if outdir.exists() and (not outdir.is_dir() or any(outdir.iterdir())):
        raise FileExistsError(f"output directory must be new/empty: {outdir}")
    outdir.mkdir(parents=True,exist_ok=True)
    population_path=Path(args.population).resolve()
    manifest_path=Path(args.population_manifest).resolve()
    m1_path=Path(args.m1_csv_gz).resolve()
    tick_path=Path(args.ticks_csv_gz).resolve()
    entries,bars,pop_manifest=load_inputs(
        population_path,manifest_path,m1_path,tick_path,
        args.population_sha256,args.manifest_sha256,args.m1_sha256,args.ticks_sha256)
    portfolios,stats=run_replay(entries,bars,tick_path,args.latency_seconds)
    detail_path=outdir/"SP2L_CAPITAL_MATRIX_TRADE_REPLAY.csv"
    summary_path=outdir/"SP2L_CAPITAL_MATRIX_RUN_SUMMARY.csv"
    with detail_path.open("x",encoding="utf-8",newline="") as f:
        fields=sorted({k for p in portfolios for row in p.rows for k in row})
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for p in portfolios:
            for row in p.rows:w.writerow(row)
    with summary_path.open("x",encoding="utf-8",newline="") as f:
        summaries=[summarize(p) for p in portfolios]
        fields=list(summaries[0])
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for row in summaries:
            row=dict(row);row["counts"]=json.dumps(row["counts"],sort_keys=True);w.writerow(row)
    output_hashes={x.name:sha256_file(x) for x in (detail_path,summary_path)}
    result_manifest={
        "status":"COMPLETE_GROSS_ONLY","research_only":True,"canonical":False,
        "mt5_accessed":False,"runner_accessed":False,"orders_possible":False,
        "population_rows":len(entries),"matrix_total_runs":89,
        "replayed_runs":len(portfolios),"dual_runs":40,
        "dual_status":"NOT_EXECUTED_MAX_OPEN_POSITIONS_1",
        "execution_assumptions":{
            "latency_seconds":args.latency_seconds,
            "submission":"first_tick_at_or_after_trigger_bar_close_plus_latency",
            "pending_order":"BUY fills when Ask <= limit; SELL fills when Bid >= limit",
            "pending_ttl_seconds":PENDING_TTL_SECONDS,
            "portfolio_exposure_limit":1,
            "entry_sl_tp":"theoretical broker-submitted levels retained",
            "exit_quotes":"BUY exits use Bid; SELL exits use Ask",
            "trailing":"completed M1 bar only; activation 0.40; distance 0.40",
            "same_tick_sl_tp":"SL prioritized conservatively",
            "end_of_source":"open/pending positions censored, not force-closed",
        },
        "cost_limitations":["Commission not provided","Swap not provided",
                           "Slippage not calibrated","Historical broker stop-level not provided"],
        "input_sha256":{
            "population":args.population_sha256,"population_manifest":args.manifest_sha256,
            "m1":args.m1_sha256,"ticks":args.ticks_sha256,
        },
        "tick_stats":stats,"output_sha256":output_hashes,
        "replay_note":"This is an explicitly assumed historical execution replay, not proof of actual historical broker fills. Entry submission time is approximated from the completed trigger bar plus declared latency.",
    }
    manifest_out=outdir/"SP2L_CAPITAL_MATRIX_REPLAY_MANIFEST.json"
    with manifest_out.open("x",encoding="utf-8") as f:
        json.dump(result_manifest,f,indent=2,ensure_ascii=False);f.write("\n")
    print(json.dumps({
        "status":result_manifest["status"],"replayed_runs":len(portfolios),
        "dual_runs_blocked":40,"tick_rows":stats["tick_rows"],
        "latency_seconds":args.latency_seconds,
        "detail_csv":str(detail_path),"summary_csv":str(summary_path),
        "manifest":str(manifest_out),"summary":[summarize(p) for p in portfolios],
    },indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
