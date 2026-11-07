#!/usr/bin/env python
"""Paired, read-only comparison: actual V3.1 trailing vs fixed initial-SL RR1..RR6.

Reconstructs the previously reported 66-position population from the private
weekly ZIP, retrieves historical XAUUSD.ecn bid/ask ticks through MT5's
read-only Python API, and emits anonymized per-position paired outcomes.

No order APIs are called. No canonical SP2L geometry is inferred. The fixed-RR
model is a research counterfactual, not an execution/fill simulator.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import zipfile
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5
import numpy as np

SYMBOL = "XAUUSD.ecn"
MAGIC = 26092301
CUTOFF = datetime(2026, 11, 7, 0, 0, tzinfo=timezone.utc)
RRS = (1, 2, 3, 4, 5, 6)
EXPECTED = {
    1: {"tp": 23, "sl": 43, "open": 0, "net": -93.97},
    2: {"tp": 15, "sl": 50, "open": 1, "net": -112.13},
    3: {"tp": 11, "sl": 54, "open": 1, "net": -112.18},
    4: {"tp": 8, "sl": 57, "open": 1, "net": -122.41},
    5: {"tp": 8, "sl": 57, "open": 1, "net": -78.20},
    6: {"tp": 8, "sl": 57, "open": 1, "net": -33.99},
}
EXPECTED_ACTUAL_NET = -24.67
EXPECTED_TICKS = 1_803_553
TOLERANCE_USD = 0.03


def number(v):
    try:
        return float(v) if v is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def read_json(zf, name):
    with zf.open(name) as f:
        return json.load(f)


def parse_utc(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def load_population(bundle):
    with zipfile.ZipFile(bundle) as zf:
        deals = read_json(zf, "raw/mt5_history_deals.json")
        events = []
        with zf.open("raw/runner_files/forward_events.jsonl") as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except Exception:
                    continue

    by_position = defaultdict(list)
    for d in deals:
        if d.get("symbol") == SYMBOL and d.get("position_id") is not None:
            by_position[str(d["position_id"])].append(d)

    theoretical_sl = defaultdict(set)
    first_lifecycle_sl = {}
    event_by_position = defaultdict(list)

    for event in events:
        position = str(event.get("position", "") or "")
        if not position:
            continue
        event_by_position[position].append(event)

        if event.get("event") == "TELEGRAM_DEAL_LIFECYCLE":
            sl = number(event.get("theoretical_sl"))
            if sl:
                theoretical_sl[position].add(round(sl, 8))
        elif event.get("event") == "POSITION_LIFECYCLE":
            sl = number(event.get("sl"))
            ts = parse_utc(event.get("ts_utc"))
            if sl and ts:
                old = first_lifecycle_sl.get(position)
                if old is None or ts < old[0]:
                    first_lifecycle_sl[position] = (ts, sl)

    selected = []
    exclusions = defaultdict(int)
    for position, rows in by_position.items():
        entries = [d for d in rows if int(d.get("entry", -1)) == 0]
        exits = [d for d in rows if int(d.get("entry", -1)) == 1]
        if len(entries) != 1 or len(exits) != 1:
            exclusions["not_exactly_one_entry_and_exit"] += 1
            continue

        entry, exit_deal = entries[0], exits[0]
        if str(entry.get("magic")) != str(MAGIC):
            exclusions["entry_magic_mismatch"] += 1
            continue
        if int(entry.get("type", -1)) not in (0, 1):
            exclusions["unknown_direction"] += 1
            continue

        sl_values = theoretical_sl.get(position, set())
        lifecycle = first_lifecycle_sl.get(position)
        if len(sl_values) != 1 or lifecycle is None:
            exclusions["missing_or_ambiguous_initial_sl_evidence"] += 1
            continue
        sl = next(iter(sl_values))
        life_time, life_sl = lifecycle
        if abs(sl - life_sl) > 1e-7:
            exclusions["initial_sl_crosscheck_mismatch"] += 1
            continue

        entry_ms = int(entry.get("time_msc") or int(entry.get("time", 0)) * 1000)
        exit_ms = int(exit_deal.get("time_msc") or int(exit_deal.get("time", 0)) * 1000)
        if life_time.timestamp() * 1000 > entry_ms:
            exclusions["initial_sl_not_observed_before_entry"] += 1
            continue
        if exit_ms < entry_ms:
            exclusions["invalid_entry_exit_time_order"] += 1
            continue

        selected.append({
            "position": position,
            "entry": entry,
            "exit": exit_deal,
            "events": event_by_position.get(position, []),
            "sl": sl,
            "entry_ms": entry_ms,
            "exit_ms": exit_ms,
            "direction": int(entry["type"]),  # MT5 deal type: 0 BUY, 1 SELL
            "entry_price": number(entry.get("price")),
            "volume": number(entry.get("volume")),
        })

    selected.sort(key=lambda x: (x["entry_ms"], x["position"]))
    if len(selected) != 66:
        raise RuntimeError(
            f"POPULATION_GATE_FAILED expected=66 actual={len(selected)} "
            f"exclusions={dict(exclusions)}"
        )
    return selected, dict(exclusions)


def fetch_ticks(trades, terminal_path):
    if not mt5.initialize(path=terminal_path):
        raise RuntimeError(f"MT5_INITIALIZE_FAILED {mt5.last_error()}")

    info = mt5.symbol_info(SYMBOL)
    if info is None:
        raise RuntimeError(f"SYMBOL_INFO_UNAVAILABLE {mt5.last_error()}")
    contract = number(info.trade_contract_size)
    if contract <= 0:
        raise RuntimeError("INVALID_CONTRACT_SIZE")

    start_ms = min(t["entry_ms"] for t in trades)
    end_ms = int(CUTOFF.timestamp() * 1000)
    arrays = []
    cursor = start_ms - 1000
    chunk_ms = 6 * 60 * 60 * 1000
    total = 0

    while cursor < end_ms:
        next_cursor = min(cursor + chunk_ms, end_ms)
        start_dt = datetime.fromtimestamp(cursor / 1000, timezone.utc)
        end_dt = datetime.fromtimestamp(next_cursor / 1000, timezone.utc) - timedelta(milliseconds=1)
        chunk = mt5.copy_ticks_range(SYMBOL, start_dt, end_dt, mt5.COPY_TICKS_INFO)
        if chunk is None:
            raise RuntimeError(f"TICK_QUERY_FAILED at={start_dt.isoformat()} error={mt5.last_error()}")
        if len(chunk):
            arrays.append(chunk)
            total += len(chunk)
        cursor = next_cursor

    if not arrays:
        raise RuntimeError("NO_TICKS_RETURNED")
    ticks = np.concatenate(arrays)
    # The chunk windows are disjoint at millisecond precision. Sort defensively.
    ticks.sort(order="time_msc")
    if "time_msc" not in ticks.dtype.names:
        raise RuntimeError("MT5_TICK_SCHEMA_MISSING_TIME_MSC")
    return ticks, contract, total


def actual_net(trade):
    e, x = trade["entry"], trade["exit"]
    gross = number(x.get("profit"))
    commission_fee = sum(number(d.get(k)) for d in (e, x) for k in ("commission", "fee"))
    swap = sum(number(d.get("swap")) for d in (e, x))
    return gross + commission_fee + swap


def trail_counts(trade):
    updates = sum(
        1 for e in trade["events"]
        if e.get("event") == "TRAIL_UPDATE" and e.get("success") is True
    )
    deferred = sum(1 for e in trade["events"] if e.get("event") == "TRAIL_DEFERRED")
    return updates, deferred


def simulate_trade(trade, ticks, contract):
    lo = int(np.searchsorted(ticks["time_msc"], trade["entry_ms"], side="left"))
    hi = int(np.searchsorted(ticks["time_msc"], int(CUTOFF.timestamp() * 1000), side="right"))
    window = ticks[lo:hi]
    if len(window) == 0:
        raise RuntimeError("TRADE_WITHOUT_TICKS_IN_SIMULATION_WINDOW")

    buy = trade["direction"] == 0
    side = window["bid"] if buy else window["ask"]
    valid = side > 0
    window = window[valid]
    side = side[valid]
    if len(window) == 0:
        raise RuntimeError("TRADE_WITHOUT_VALID_EXECUTABLE_SIDE_QUOTES")

    entry = trade["entry_price"]
    volume = trade["volume"]
    sl = trade["sl"]
    risk = abs(entry - sl)
    if entry <= 0 or volume <= 0 or risk <= 0:
        raise RuntimeError("INVALID_ENTRY_VOLUME_OR_INITIAL_SL_RISK")

    direction_sign = 1.0 if buy else -1.0
    sl_hit = side <= sl if buy else side >= sl
    costs = sum(number(d.get(k)) for d in (trade["entry"], trade["exit"]) for k in ("commission", "fee"))
    swap = sum(number(d.get("swap")) for d in (trade["entry"], trade["exit"]))
    actual = actual_net(trade)

    result = {
        "actual_net": actual,
        "actual_gross": number(trade["exit"].get("profit")),
        "actual_costs": costs,
        "actual_swap": swap,
        "risk_cash": risk * contract * volume,
        "successful_trail_updates": trail_counts(trade)[0],
        "trail_deferred_events": trail_counts(trade)[1],
        "rr": {},
    }

    time_ms = window["time_msc"]
    for rr in RRS:
        target = entry + direction_sign * rr * risk
        tp_hit = side >= target if buy else side <= target
        sl_indices = np.flatnonzero(sl_hit)
        tp_indices = np.flatnonzero(tp_hit)
        first_sl = int(sl_indices[0]) if len(sl_indices) else None
        first_tp = int(tp_indices[0]) if len(tp_indices) else None

        outcome = "OPEN"
        gross = None
        exit_ms = None
        mark_gross = direction_sign * (float(side[-1]) - entry) * contract * volume

        if first_sl is not None and first_tp is not None and int(time_ms[first_sl]) == int(time_ms[first_tp]):
            outcome = "SAME_MS_TIE"
            exit_ms = int(time_ms[first_sl])
        elif first_sl is not None and (first_tp is None or first_sl < first_tp):
            outcome = "SL"
            gross = direction_sign * (sl - entry) * contract * volume
            exit_ms = int(time_ms[first_sl])
        elif first_tp is not None:
            outcome = "TP"
            gross = direction_sign * (target - entry) * contract * volume
            exit_ms = int(time_ms[first_tp])

        if exit_ms == trade["entry_ms"]:
            result["rr"][rr] = {
                "outcome": "ENTRY_MS_TIE", "net": None, "gross": None,
                "mark_gross": mark_gross, "exit_ms": exit_ms,
            }
        elif outcome in ("TP", "SL"):
            result["rr"][rr] = {
                "outcome": outcome, "gross": gross,
                "net": gross + costs + swap, "mark_gross": mark_gross,
                "exit_ms": exit_ms,
            }
        else:
            result["rr"][rr] = {
                "outcome": outcome, "gross": None, "net": None,
                "mark_gross": mark_gross, "exit_ms": exit_ms,
            }
    return result


def bootstrap_ci(values, seed=20261107, reps=10000):
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return None
    rng = np.random.default_rng(seed)
    means = np.empty(reps, dtype=float)
    for i in range(reps):
        means[i] = np.mean(rng.choice(values, size=len(values), replace=True))
    return [round(float(np.quantile(means, 0.025)), 4),
            round(float(np.quantile(means, 0.975)), 4)]


def paired_summary(rows, rr):
    deltas = [
        r["actual_net"] - r["rr"][rr]["net"]
        for r in rows if r["rr"][rr]["net"] is not None
    ]
    positive = sum(x > 0.005 for x in deltas)
    negative = sum(x < -0.005 for x in deltas)
    flat = len(deltas) - positive - negative
    return {
        "paired_closed_positions": len(deltas),
        "actual_minus_fixed_rr_net_usd": round(sum(deltas), 2),
        "mean_per_position_usd": round(statistics.mean(deltas), 4) if deltas else None,
        "median_per_position_usd": round(statistics.median(deltas), 4) if deltas else None,
        "actual_better_positions": positive,
        "fixed_rr_better_positions": negative,
        "approximately_equal_positions": flat,
        "bootstrap_95pct_ci_mean_usd": bootstrap_ci(deltas),
        "open_fixed_rr_positions": sum(r["rr"][rr]["outcome"] == "OPEN" for r in rows),
        "tie_positions": sum(r["rr"][rr]["outcome"] in ("SAME_MS_TIE", "ENTRY_MS_TIE") for r in rows),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle", help="Private SP2L_PRIVATE_AUDIT_20261102_20261107.zip")
    ap.add_argument("--mt5-terminal-path",
                    default=r"C:\Program Files\Otet Group MT5 Terminal\terminal64.exe")
    ap.add_argument("--output-dir", default="")
    args = ap.parse_args()

    bundle = Path(args.bundle).expanduser().resolve()
    out = Path(args.output_dir).expanduser().resolve() if args.output_dir else (
        bundle.parent / "SP2L_PAIRED_RR_TRAILING_20261107"
    )
    out.mkdir(parents=True, exist_ok=True)

    trades, exclusions = load_population(bundle)
    try:
        ticks, contract, raw_tick_count = fetch_ticks(trades, args.mt5_terminal_path)
        results = [simulate_trade(t, ticks, contract) for t in trades]
    finally:
        mt5.shutdown()

    actual_total = sum(r["actual_net"] for r in results)
    actual_check = abs(actual_total - EXPECTED_ACTUAL_NET) <= TOLERANCE_USD
    rr_reports = {}
    rr_reproduction_ok = True

    for rr in RRS:
        outcomes = [r["rr"][rr]["outcome"] for r in results]
        closed = [r["rr"][rr]["net"] for r in results if r["rr"][rr]["net"] is not None]
        gross_wins = sum(max(0.0, x) for x in closed)
        gross_losses = sum(min(0.0, x) for x in closed)
        net = sum(closed)
        tp = outcomes.count("TP")
        sl = outcomes.count("SL")
        opened = outcomes.count("OPEN")
        ties = outcomes.count("SAME_MS_TIE") + outcomes.count("ENTRY_MS_TIE")
        expected = EXPECTED[rr]
        check = (
            tp == expected["tp"] and sl == expected["sl"] and opened == expected["open"]
            and ties == 0 and abs(net - expected["net"]) <= TOLERANCE_USD
        )
        rr_reproduction_ok = rr_reproduction_ok and check
        rr_reports[f"RR{rr}"] = {
            "tp": tp, "sl": sl, "open_at_cutoff": opened, "ties": ties,
            "closed_net_usd": round(net, 2),
            "profit_factor": round(gross_wins / abs(gross_losses), 3) if gross_losses < 0 else None,
            "reproduces_previous_reference": check,
            "paired_actual_minus_fixed_rr": paired_summary(results, rr),
        }

    actual_updates = sum(r["successful_trail_updates"] > 0 for r in results)
    actual_deferred_positions = sum(r["trail_deferred_events"] > 0 for r in results)
    actual_update_events = sum(r["successful_trail_updates"] for r in results)
    actual_deferred_events = sum(r["trail_deferred_events"] for r in results)

    tick_count_reference_match = raw_tick_count == EXPECTED_TICKS
    # Tick-row count is diagnostic only: MT5 historical range retrieval can vary
    # slightly at chunk boundaries. Exact population, realized net, and all six
    # independently reproduced TP/SL/open/net results are the controlling gates.
    gate = actual_check and rr_reproduction_ok
    report = {
        "status": "REPRODUCTION_AND_PAIRED_ANALYSIS_READY" if gate else "REPRODUCTION_GATE_FAILED",
        "scope": {
            "symbol": SYMBOL, "entry_magic": MAGIC, "population": len(results),
            "fixed_sl": "initial SL cross-checked: theoretical_sl == first nonzero POSITION_LIFECYCLE sl",
            "fixed_rr_targets": list(RRS),
            "quote_side": "BUY uses Bid; SELL uses Ask",
            "cutoff_utc": CUTOFF.isoformat(),
            "contract_size": contract,
            "tick_count": raw_tick_count,
            "expected_tick_count": EXPECTED_TICKS,
            "tick_count_reference_match": tick_count_reference_match,
            "tick_count_is_diagnostic_not_a_reproduction_gate": True,
            "population_exclusions": exclusions,
        },
        "actual_trailing": {
            "net_usd": round(actual_total, 2),
            "matches_previous_reference": actual_check,
            "positions_with_successful_update": actual_updates,
            "successful_update_events": actual_update_events,
            "positions_with_deferred_event": actual_deferred_positions,
            "deferred_events": actual_deferred_events,
        },
        "fixed_rr": rr_reports,
        "paired_analysis_permitted": gate,
        "limitations": [
            "Fixed-RR exits are barrier-price proxies, not guaranteed executable fills; no slippage model.",
            "Actual entry/exit commissions and fees are reused as round-trip cost proxies for counterfactual exits.",
            "Open-at-cutoff cases are excluded from closed-net paired deltas and reported separately; mark-to-market is not realized P/L.",
            "Same-millisecond TP/SL ties are unresolved and block the reproduction gate if present.",
            "This is a historical in-sample comparison, not proof of a statistical edge or a production rule.",
            "No P-Gap, AB=CD, entry, fill, or canonical execution semantics are inferred or changed.",
            "The script uses MT5 historical tick retrieval only; it never sends, modifies, or closes orders."
        ],
    }

    # Anonymized row-level output: no position IDs, tickets, prices, or timestamps.
    csv_path = out / "paired_trade_results_anonymized.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        fields = ["trade_key", "direction", "actual_net_usd", "risk_cash_usd",
                  "successful_trail_updates", "trail_deferred_events"]
        for rr in RRS:
            fields += [f"rr{rr}_outcome", f"rr{rr}_net_usd",
                       f"rr{rr}_mark_gross_usd", f"actual_minus_rr{rr}_usd"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for i, (trade, result) in enumerate(zip(trades, results), 1):
            row = {
                "trade_key": f"T{i:03d}",
                "direction": "BUY" if trade["direction"] == 0 else "SELL",
                "actual_net_usd": round(result["actual_net"], 4),
                "risk_cash_usd": round(result["risk_cash"], 4),
                "successful_trail_updates": result["successful_trail_updates"],
                "trail_deferred_events": result["trail_deferred_events"],
            }
            for rr in RRS:
                item = result["rr"][rr]
                row[f"rr{rr}_outcome"] = item["outcome"]
                row[f"rr{rr}_net_usd"] = "" if item["net"] is None else round(item["net"], 4)
                row[f"rr{rr}_mark_gross_usd"] = round(item["mark_gross"], 4)
                row[f"actual_minus_rr{rr}_usd"] = (
                    "" if item["net"] is None else round(result["actual_net"] - item["net"], 4)
                )
            writer.writerow(row)

    report_path = out / "paired_comparison_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    digest = hashlib.sha256(report_path.read_bytes()).hexdigest()

    print("PAIRED_COMPARISON_COMPLETE" if gate else "REPRODUCTION_GATE_FAILED")
    print("TRADES=", len(results))
    print("TICK_COUNT=", raw_tick_count)
    print("ACTUAL_TRAILING_NET_USD=", round(actual_total, 2))
    print("ACTUAL_REFERENCE_MATCH=", actual_check)
    print("RR_REFERENCE_MATCH_ALL=", rr_reproduction_ok)
    print("TICK_COUNT_REFERENCE_MATCH=", tick_count_reference_match)
    print("TICK_COUNT_IS_DIAGNOSTIC_ONLY=True")
    print("SUCCESSFUL_UPDATE_POSITIONS_EVENTS=", actual_updates, actual_update_events)
    print("DEFERRED_POSITIONS_EVENTS=", actual_deferred_positions, actual_deferred_events)
    for name, item in rr_reports.items():
        p = item["paired_actual_minus_fixed_rr"]
        print(name, "TP/SL/OPEN=", item["tp"], item["sl"], item["open_at_cutoff"],
              "CLOSED_NET=", item["closed_net_usd"],
              "PAIRED_N=", p["paired_closed_positions"],
              "PAIRED_DELTA=", p["actual_minus_fixed_rr_net_usd"],
              "DELTA_MEAN_CI=", p["bootstrap_95pct_ci_mean_usd"],
              "REPRODUCES=", item["reproduces_previous_reference"])
    print("PAIRED_ANALYSIS_PERMITTED=", gate)
    print("REPORT=", report_path)
    print("REPORT_SHA256=", digest)
    print("ANONYMIZED_TRADE_CSV=", csv_path)


if __name__ == "__main__":
    main()
