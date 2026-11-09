from __future__ import annotations

"""Unified, fully offline management matrix over immutable V3 entries and M1 OHLC.

No MT5 import/API, signal generation, entry rebuilding, or live-runner access.
All stop updates calculated from a completed M1 bar become active on the next bar.
"""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from strategy_factory.v3_management_engine import normalize_management_spec, replay_management_trade
from strategy_factory.v3_step_lock_engine import replay_step_lock_no_tp, validate_frozen_risk
from strategy_factory.v3_exit_engine import V3ExitEngineError, summarize
from strategy_factory.m1_integrity import m1_gap_detected

M1_FIELDS = ["time_epoch_seconds", "time_utc_iso", "open", "high", "low", "close",
             "tick_volume", "spread", "real_volume"]
ENTRY_FIELDS = ["strategy", "variant", "direction", "setup_time_utc", "entry_time_utc",
                "entry_proxy", "sl_initial", "target", "risk_price", "exit_time_utc",
                "exit_price", "exit_reason", "status", "r_multiple"]
EXPECTED_ENTRY_SHA = "39ED87CD1F0BE3E59B5F064B0BCF97A9787E5266DF6E972AA07E5EA4D3608AB1"
EXPECTED_ENTRY_ROWS = 462
EXPECTED_M1_SHA = "B0782E716C7ECCBD29EF25E146C088B356F2AADF2CCD5D7EA24E6AC1488AA285"
ACTIVATION_R_GRID = (0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0)
DISTANCE_R_GRID = (0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0)
FIXED_RR_GRID = (1.0, 1.5, 2.0, 3.0, 4.0, 6.0)
STEP_TP_GRID = (2.0, 3.0, 4.0, 6.0)
TIME_EXIT_GRID = (15, 30, 60, 120)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"timestamp must include timezone: {value}")
    return parsed.astimezone(timezone.utc)


def load_bars(path: Path, expected_sha: str) -> tuple[list[dict], dict]:
    observed = digest(path)
    if observed.lower() != expected_sha.lower():
        raise ValueError(f"M1 SHA-256 mismatch: expected={expected_sha} observed={observed}")
    bars = []
    previous = None
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != M1_FIELDS:
            raise ValueError(f"M1 CSV header mismatch: {reader.fieldnames}")
        for line_no, row in enumerate(reader, 2):
            ts = int(row["time_epoch_seconds"])
            utc = parse_utc(row["time_utc_iso"])
            if int(utc.timestamp()) != ts or ts % 60:
                raise ValueError(f"M1 UTC/epoch/alignment mismatch at line {line_no}")
            if previous is not None and ts <= previous:
                raise ValueError(f"M1 duplicate/out-of-order timestamp at line {line_no}")
            values = {k: float(row[k]) for k in ("open", "high", "low", "close")}
            if not all(math.isfinite(v) and v > 0 for v in values.values()):
                raise ValueError(f"invalid OHLC at line {line_no}")
            if values["high"] < max(values.values()) or values["low"] > min(values.values()):
                raise ValueError(f"invalid OHLC range at line {line_no}")
            bars.append({"time": ts, **values, "tick_volume": int(row["tick_volume"]),
                         "spread": int(row["spread"]), "real_volume": int(row["real_volume"])})
            previous = ts
    if not bars:
        raise ValueError("M1 dataset is empty")
    gaps = []
    for left, right in zip(bars, bars[1:]):
        delta = int(right["time"]) - int(left["time"])
        if delta > 60:
            gaps.append({"from_utc": datetime.fromtimestamp(left["time"], timezone.utc).isoformat(),
                         "to_utc": datetime.fromtimestamp(right["time"], timezone.utc).isoformat(),
                         "missing_minute_slots": delta // 60 - 1})
    report = {
        "bars": len(bars),
        "first_utc": datetime.fromtimestamp(bars[0]["time"], timezone.utc).isoformat(),
        "last_utc": datetime.fromtimestamp(bars[-1]["time"], timezone.utc).isoformat(),
        "gap_count": len(gaps),
        "missing_minute_slots": sum(x["missing_minute_slots"] for x in gaps),
        "largest_gap_minutes": max((x["missing_minute_slots"] + 1 for x in gaps), default=0),
        "gaps": gaps, "sha256": observed, "byte_size": path.stat().st_size,
    }
    return bars, report


def load_population(path: Path, expected_sha: str, bars: list[dict]) -> tuple[list[dict], dict]:
    observed = digest(path)
    if observed.lower() != expected_sha.lower():
        raise ValueError(f"entry CSV SHA-256 mismatch: expected={expected_sha} observed={observed}")
    index_by_time = {int(bar["time"]): i for i, bar in enumerate(bars)}
    population, seen, strategy_values = [], set(), set()
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ENTRY_FIELDS:
            raise ValueError(f"entry CSV header mismatch: {reader.fieldnames}")
        for line_no, row in enumerate(reader, 2):
            strategy_value = row["strategy"].strip()
            if not strategy_value:
                raise ValueError(f"empty strategy at entry line {line_no}")
            strategy_values.add(strategy_value)
            if len(strategy_values) > 1:
                raise ValueError("frozen entry CSV contains multiple strategy labels")
            direction = row["direction"].strip().upper()
            if direction not in {"BUY", "SELL"}:
                raise ValueError(f"invalid direction at entry line {line_no}")
            entry_time = parse_utc(row["entry_time_utc"])
            trigger = int(entry_time.timestamp())
            if trigger not in index_by_time:
                raise ValueError(f"entry timestamp absent from M1 at line {line_no}")
            candidate = {
                "entry_idx": index_by_time[trigger], "theoretical_entry": float(row["entry_proxy"]),
                "sl": float(row["sl_initial"]), "risk": float(row["risk_price"]),
                "direction": direction, "trigger_time": trigger,
                "signal_time_utc": row["entry_time_utc"], "setup_time_utc": row["setup_time_utc"],
                "source_variant": row["variant"],
            }
            validate_frozen_risk(candidate)
            identity = (trigger, direction, candidate["theoretical_entry"], candidate["sl"])
            if identity in seen:
                raise ValueError(f"duplicate frozen trade identity at entry line {line_no}")
            seen.add(identity)
            population.append(candidate)
    if len(population) != EXPECTED_ENTRY_ROWS:
        raise ValueError(f"entry row count mismatch: expected={EXPECTED_ENTRY_ROWS}, observed={len(population)}")
    return population, {"rows": len(population), "sha256": observed,
                        "strategy": next(iter(strategy_values), None),
                        "policy": "FROZEN_ENTRY_CSV_ONLY_NO_SIGNAL_REBUILD"}


def replay_step_lock_with_tp(candidate: dict, bars: list[dict], *, rr: float,
                             contract_size: float, volume: float) -> dict:
    """Step-lock (+nR locks +(n-1)R) with an independent fixed final TP."""
    validate_frozen_risk(candidate)
    entry_idx = int(candidate["entry_idx"])
    if not 0 <= entry_idx < len(bars):
        raise V3ExitEngineError("candidate entry_idx outside M1 data")
    entry, risk = float(candidate["theoretical_entry"]), float(candidate["risk"])
    direction, initial_sl = str(candidate["direction"]).upper(), float(candidate["sl"])
    if not math.isfinite(rr) or rr <= 0:
        raise V3ExitEngineError("step-lock TP RR must be finite and positive")
    target = entry + rr * risk if direction == "BUY" else entry - rr * risk
    current_sl, milestone, updates = initial_sl, 0, 0
    max_fav = max_adverse = 0.0
    previous_time = int(bars[entry_idx]["time"])
    exit_price = exit_time = None
    reason, ambiguous, bars_held = "OPEN_OR_UNRESOLVED", False, 0
    for index in range(entry_idx + 1, len(bars)):
        bar = bars[index]
        now = int(bar["time"])
        if m1_gap_detected(previous_time, now):
            ambiguous, reason, exit_time = True, "M1_GAP_WHILE_OPEN", now
            break
        previous_time = now
        bars_held += 1
        high, low = float(bar["high"]), float(bar["low"])
        favorable = high - entry if direction == "BUY" else entry - low
        adverse = entry - low if direction == "BUY" else high - entry
        max_fav, max_adverse = max(max_fav, favorable), max(max_adverse, adverse)
        hit_sl = low <= current_sl if direction == "BUY" else high >= current_sl
        hit_tp = high >= target if direction == "BUY" else low <= target
        reached = max(0, int(math.floor((favorable + 1e-6) / risk)))
        if hit_sl and hit_tp:
            ambiguous, reason, exit_time = True, "SL_AND_TP_SAME_BAR", now
            break
        if hit_sl and reached > milestone:
            ambiguous, reason, exit_time = True, "ACTIVE_SL_AND_NEW_MILESTONE_SAME_BAR", now
            break
        if hit_sl:
            exit_price, exit_time = current_sl, now
            reason = "STEP_LOCK_SL" if milestone else "SL"
            break
        if hit_tp:
            exit_price, exit_time, reason = target, now, "TP"
            break
        if reached > milestone:
            milestone = reached
            locked_r = milestone - 1
            current_sl = entry + locked_r * risk if direction == "BUY" else entry - locked_r * risk
            updates += 1
    realized_price = None if exit_price is None else (exit_price - entry if direction == "BUY" else entry - exit_price)
    realized_r = None if realized_price is None else realized_price / risk
    return {
        "direction": direction, "trigger_time": candidate["trigger_time"],
        "signal_time_utc": candidate["signal_time_utc"], "theoretical_entry": entry,
        "risk": risk, "initial_sl": initial_sl, "initial_tp": target, "rr": rr,
        "final_sl": current_sl, "highest_milestone_R": milestone, "step_lock_updates": updates,
        "trailing_enabled": False, "trailing_activated": False, "break_even_activated": False,
        "entry_bar_excluded_from_exit_replay": True, "trailing_updates": 0,
        "deferred_trailing_updates": 0, "bars_held": bars_held,
        "max_favorable_price": max_fav, "max_adverse_price": max_adverse,
        "exit_time_utc": datetime.fromtimestamp(exit_time, timezone.utc).isoformat() if exit_time is not None else None,
        "exit_price": exit_price, "reason": reason, "ambiguous": ambiguous,
        "realized_price": realized_price, "realized_R": realized_r,
        "risk_usd": risk * volume * contract_size,
        "realized_usd": None if realized_price is None else realized_price * volume * contract_size,
        "management_mode": "STEP_LOCK_WITH_TP",
    }


def build_specs() -> list[dict]:
    specs = [{"mode": "NO_TARGET", "family": "NO_TARGET", "label": "NO_TARGET"}]
    specs += [{"mode": "FIXED_RR", "rr": rr, "family": "FIXED_RR", "label": f"FIXED_RR_{rr:g}R"}
              for rr in FIXED_RR_GRID]
    specs += [{"mode": "BREAK_EVEN", "rr": None, "activation_r": activation,
               "offset_r": 0.0, "family": "BREAK_EVEN_NO_TP",
               "label": f"BE_{activation:g}R_NO_TP"} for activation in (0.5, 1.0, 1.5)]
    specs += [{"mode": "TRAILING_R", "rr": None, "activation_r": activation,
               "distance_r": distance, "family": "TRAILING_NO_TP",
               "label": f"TRAIL_A{activation:g}_D{distance:g}_NO_TP"}
              for activation in ACTIVATION_R_GRID for distance in DISTANCE_R_GRID]
    specs += [{"mode": "BREAK_EVEN_TRAILING", "rr": None, "be_activation_r": be,
               "be_offset_r": 0.0, "trail_activation_r": activation,
               "trail_distance_r": distance, "family": "BE_PLUS_TRAILING",
               "label": f"BE{be:g}_TRAIL_A{activation:g}_D{distance:g}"}
              for be in (0.5, 1.0, 1.5) for activation in (1.0, 2.0, 3.0)
              for distance in (0.5, 1.0, 2.0)]
    specs += [{"mode": "TRAILING_R", "rr": 4.0, "activation_r": activation,
               "distance_r": distance, "family": "FIXED_TP4_PLUS_TRAILING",
               "label": f"TP4_TRAIL_A{activation:g}_D{distance:g}"}
              for activation in ACTIVATION_R_GRID for distance in DISTANCE_R_GRID]
    specs += [{"mode": "TIME_EXIT", "rr": None, "max_bars": bars,
               "family": "TIME_EXIT_NO_TP", "label": f"TIME_EXIT_{bars}_BARS"}
              for bars in TIME_EXIT_GRID]
    return specs


def add_quality_counts(summary: dict, rows: list[dict]) -> dict:
    result = dict(summary)
    result["open_unresolved"] = sum(row["reason"] == "OPEN_OR_UNRESOLVED" for row in rows)
    result["ambiguous"] = sum(bool(row["ambiguous"]) for row in rows)
    result["unresolved_total"] = result["ambiguous"] + result["open_unresolved"]
    result["gap_exposed"] = sum(row["reason"] == "M1_GAP_WHILE_OPEN" for row in rows)
    result["decisive_coverage_pct"] = 100.0 * result["decisive"] / len(rows) if rows else None
    result["usd_costs_modeled"] = False
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--m1-csv", required=True)
    parser.add_argument("--m1-sha256", default=EXPECTED_M1_SHA)
    parser.add_argument("--entry-csv", required=True)
    parser.add_argument("--entry-sha256", default=EXPECTED_ENTRY_SHA)
    parser.add_argument("--symbol", default="XAUUSD.ecn")
    parser.add_argument("--point", type=float, required=True, help="Metadata only; replay parameters are expressed in R.")
    parser.add_argument("--contract-size", type=float, required=True)
    parser.add_argument("--volume", type=float, required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    if not all(math.isfinite(x) and x > 0 for x in (args.point, args.contract_size, args.volume)):
        raise ValueError("point, contract-size and volume must be finite positive explicit values")
    m1_path, entry_path, out = Path(args.m1_csv).resolve(), Path(args.entry_csv).resolve(), Path(args.output_dir).resolve()
    if args.m1_sha256.lower() != EXPECTED_M1_SHA.lower() or args.entry_sha256.lower() != EXPECTED_ENTRY_SHA.lower():
        raise ValueError("this matrix is pinned to the audited 30-day M1 and 462-row entry SHA-256 values")
    if out.exists():
        raise FileExistsError(f"output directory already exists; refusing overwrite: {out}")
    bars, m1_report = load_bars(m1_path, args.m1_sha256)
    population, population_report = load_population(entry_path, args.entry_sha256, bars)
    if m1_report["bars"] != 29919 or m1_report["gap_count"] != 21:
        raise ValueError("M1 row count/gap count does not match the frozen audit")
    if m1_report["first_utc"] != "2026-09-24T07:57:00+00:00" or m1_report["last_utc"] != "2026-10-23T23:57:00+00:00":
        raise ValueError("M1 coverage does not match the frozen audit window")

    variants: list[tuple[str, str, dict | None]] = []
    rows_by_variant: list[tuple[str, str, dict, list[dict]]] = []
    for spec in build_specs():
        label, family = spec.pop("label"), spec.pop("family")
        normalized = normalize_management_spec(spec)
        rows = [replay_management_trade(c, bars, normalized, mt5_point=args.point,
                                        contract_size=args.contract_size, volume=args.volume)
                for c in population]
        for row in rows:
            row["variant"] = label
            row["variant_family"] = family
            row["trailing_activated"] = bool(row.get("trailing_activated", False))
        summary = add_quality_counts(summarize(rows), rows)
        variants.append((label, family, summary))
        rows_by_variant.append((label, family, normalized, rows))

    # The Step-Lock no-target result is included in this same batch, not rerun separately.
    step_rows = [replay_step_lock_no_tp(c, bars, contract_size=args.contract_size, volume=args.volume)
                 for c in population]
    for row in step_rows:
        row["variant"] = "STEP_LOCK_NO_TP"
        row["variant_family"] = "STEP_LOCK_NO_TP"
        row["trailing_activated"] = False
    step_summary = add_quality_counts(summarize(step_rows), step_rows)
    variants.append(("STEP_LOCK_NO_TP", "STEP_LOCK_NO_TP", step_summary))
    rows_by_variant.append(("STEP_LOCK_NO_TP", "STEP_LOCK_NO_TP", {"mode": "STEP_LOCK_NO_TP"}, step_rows))

    for rr in STEP_TP_GRID:
        label = f"STEP_LOCK_TP_{rr:g}R"
        rows = [replay_step_lock_with_tp(c, bars, rr=rr, contract_size=args.contract_size, volume=args.volume)
                for c in population]
        for row in rows:
            row["variant"], row["variant_family"], row["trailing_activated"] = label, "STEP_LOCK_WITH_TP", False
        summary = add_quality_counts(summarize(rows), rows)
        variants.append((label, "STEP_LOCK_WITH_TP", summary))
        rows_by_variant.append((label, "STEP_LOCK_WITH_TP", {"mode": "STEP_LOCK_WITH_TP", "rr": rr}, rows))

    # Include fixed-TP controls at each RR independently of management.
    for rr in FIXED_RR_GRID:
        label = f"FIXED_TP_CONTROL_{rr:g}R"
        spec = normalize_management_spec({"mode": "FIXED_RR", "rr": rr})
        rows = [replay_management_trade(c, bars, spec, mt5_point=args.point,
                                        contract_size=args.contract_size, volume=args.volume)
                for c in population]
        for row in rows:
            row["variant"], row["variant_family"] = label, "FIXED_TP_CONTROL"
        summary = add_quality_counts(summarize(rows), rows)
        variants.append((label, "FIXED_TP_CONTROL", summary))
        rows_by_variant.append((label, "FIXED_TP_CONTROL", spec, rows))

    # Stable, discovery-only ordering. Coverage and risk metrics break ties after gross USD/R.
    ranked = sorted(variants, key=lambda item: (
        item[2]["net_profit_usd"], item[2]["net_R"],
        item[2]["decisive_coverage_pct"], item[2]["profit_factor"] or -1.0,
        -item[2]["max_drawdown_R"]), reverse=True)

    out.mkdir(parents=True, exist_ok=False)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    stem = f"SP2L_UNIFIED_MANAGEMENT_MATRIX_{stamp}"
    summary_fields = ["rank", "name", "family", "signals", "decisive", "wins", "losses",
                      "ambiguous", "open_unresolved", "unresolved_total", "gap_exposed",
                      "decisive_coverage_pct", "net_R", "profit_factor", "max_drawdown_R",
                      "gross_profit_usd", "gross_loss_usd", "net_profit_usd",
                      "avg_R_per_decisive", "avg_usd_per_decisive", "trail_exits", "tp_exits",
                      "original_sl_exits", "usd_costs_modeled"]
    summary_path = out / f"{stem}_SUMMARY.csv"
    with summary_path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=summary_fields)
        writer.writeheader()
        for rank, (name, family, summary) in enumerate(ranked, 1):
            writer.writerow({"rank": rank, "name": name, "family": family, **summary})

    trades_path = out / f"{stem}_TRADES.csv"
    trade_fields = ["variant", "variant_family", "direction", "trigger_time", "signal_time_utc",
                    "theoretical_entry", "risk", "initial_sl", "initial_tp", "final_sl",
                    "highest_milestone_R", "step_lock_updates", "trailing_activated",
                    "break_even_activated", "trailing_updates", "deferred_trailing_updates",
                    "bars_held", "max_favorable_price", "max_adverse_price", "exit_time_utc",
                    "exit_price", "reason", "ambiguous", "realized_price", "realized_R",
                    "risk_usd", "realized_usd", "management_mode"]
    with trades_path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=trade_fields, extrasaction="ignore")
        writer.writeheader()
        for _, _, _, rows in rows_by_variant:
            writer.writerows(rows)

    top = [{"rank": i, "name": name, "family": family, **summary}
           for i, (name, family, summary) in enumerate(ranked[:20], 1)]
    manifest = {
        "research_only": True, "canonical": False, "backtest_executed": True,
        "mode": "UNIFIED_OFFLINE_MANAGEMENT_MATRIX", "symbol": args.symbol, "timeframe": "M1",
        "mt5_accessed": False, "live_runner_accessed": False,
        "execution_assumptions": {"point": args.point, "point_role": "METADATA_ONLY",
                                  "contract_size": args.contract_size, "volume": args.volume,
                                  "spread_commission_slippage": "NOT_MODELED"},
        "m1": m1_report, "frozen_population": population_report,
        "grid": {"fixed_rr": list(FIXED_RR_GRID), "activation_R": list(ACTIVATION_R_GRID),
                 "distance_R": list(DISTANCE_R_GRID), "step_lock_tp_R": list(STEP_TP_GRID),
                 "time_exit_bars": list(TIME_EXIT_GRID),
                 "families": ["NO_TARGET", "FIXED_RR", "FIXED_TP_CONTROL", "BREAK_EVEN_NO_TP",
                              "TRAILING_NO_TP", "BE_PLUS_TRAILING", "FIXED_TP4_PLUS_TRAILING",
                              "TIME_EXIT_NO_TP", "STEP_LOCK_NO_TP", "STEP_LOCK_WITH_TP"]},
        "variant_count": len(variants), "signal_count": len(population),
        "ranking_policy": "GROSS_USD_THEN_NET_R_THEN_DECISIVE_COVERAGE_THEN_PF_THEN_LOWER_DD; DISCOVERY_ONLY",
        "ohlc_policy": "same-bar SL+TP or active SL+new milestone => ambiguous; M1 gap while open => ambiguous/no fill; completed-bar stop updates active next bar",
        "excluded": ["PARTIAL_CLOSE: volume-allocation and fill ordering not yet specified",
                     "spread", "commission", "slippage", "tick-level intrabar ordering"],
        "top20": top,
        "artifacts": {},
    }
    manifest_path = out / f"{stem}_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for path in (summary_path, trades_path):
        manifest["artifacts"][path.name] = {"sha256": digest(path), "bytes": path.stat().st_size}
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sums_path = out / f"{stem}_SHA256SUMS.txt"
    with sums_path.open("x", encoding="utf-8", newline="") as stream:
        for path in (summary_path, trades_path, manifest_path):
            stream.write(f"{digest(path)}  {path.name}\n")
    print(json.dumps({"status": "COMPLETE", "variant_count": len(variants),
                      "signals_per_variant": len(population), "total_trade_rows": len(variants) * len(population),
                      "top10": top[:10], "output_dir": str(out),
                      "summary_csv": str(summary_path), "trades_csv": str(trades_path),
                      "manifest": str(manifest_path), "mt5_accessed": False,
                      "research_only": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
