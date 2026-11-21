"""Tick-based trade behavior analyzer for the frozen V3.1 replay evidence.

Research-only. Reads six existing replay detail files and one immutable gzip tick
source. It does not replay entries, access MT5, or modify Runner/configuration.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

LATENCIES = ("0s", "2s", "5s")
FAMILIES = {
    "MATRIX49": {
        "directory": "capital-matrix-replay-v1-{latency}",
        "detail": "SP2L_CAPITAL_MATRIX_TRADE_REPLAY.csv",
        "manifest": "SP2L_CAPITAL_MATRIX_REPLAY_MANIFEST.json",
    },
    "PARTIAL27": {
        "directory": "partial-matrix-replay-v1-{latency}",
        "detail": "SP2L_PARTIAL_MATRIX_TRADE_REPLAY.csv",
        "manifest": "SP2L_PARTIAL_MATRIX_REPLAY_MANIFEST.json",
    },
}
TICK_DTYPE = np.dtype([("time_msc", "<i8"), ("bid_ticks", "<i4"), ("ask_ticks", "<i4")])
TICK_FIELDS = ["time_msc", "time_utc", "bid", "ask", "last", "volume", "flags"]
GAP_MS = 60_000
PRICE_SCALE = 100


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_ms(value: str) -> int:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"timestamp is not timezone-aware: {value}")
    dt = dt.astimezone(timezone.utc)
    return int(dt.timestamp()) * 1000 + dt.microsecond // 1000


def price_ticks(value: str | float) -> int:
    scaled = float(value) * PRICE_SCALE
    rounded = round(scaled)
    if not math.isfinite(scaled) or abs(scaled - rounded) > 1e-5:
        raise ValueError(f"price is not representable at {PRICE_SCALE} ticks per unit: {value}")
    return int(rounded)


def build_tick_index(tick_path: Path, index_path: Path, expected_rows: int):
    ticks = np.memmap(index_path, dtype=TICK_DTYPE, mode="w+", shape=(expected_rows,))
    count = 0
    previous = -1
    gaps = 0
    first = None
    last = None
    with gzip.open(tick_path, "rt", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != TICK_FIELDS:
            raise ValueError(f"unexpected tick header: {reader.fieldnames}")
        for line, row in enumerate(reader, 2):
            if count >= expected_rows:
                raise ValueError("tick source has more rows than manifest tick_stats.tick_rows")
            now = int(row["time_msc"])
            bid = price_ticks(row["bid"])
            ask = price_ticks(row["ask"])
            if now < previous or bid <= 0 or ask < bid:
                raise ValueError(f"invalid/out-of-order tick at line {line}")
            if previous >= 0 and now - previous > GAP_MS:
                gaps += 1
            ticks[count] = (now, bid, ask)
            count += 1
            if first is None:
                first = now
            previous = last = now
    if count != expected_rows:
        raise ValueError(f"tick row count mismatch: expected {expected_rows}, got {count}")
    ticks.flush()
    return ticks, {"tick_rows": count, "first_tick_ms": first,
                   "last_tick_ms": last, "gaps_gt_60s": gaps}


def reconstruct_fill(ticks, fill_ms: int, direction: str, theoretical_ticks: int):
    times = ticks["time_msc"]
    left = int(np.searchsorted(times, fill_ms, side="left"))
    right = int(np.searchsorted(times, fill_ms, side="right"))
    if left == right:
        return None
    block = ticks[left:right]
    if direction == "BUY":
        eligible = np.flatnonzero(block["ask_ticks"] <= theoretical_ticks)
        return int(block["ask_ticks"][int(eligible[0])]) if len(eligible) else None
    eligible = np.flatnonzero(block["bid_ticks"] >= theoretical_ticks)
    return int(block["bid_ticks"][int(eligible[0])]) if len(eligible) else None


def compute_path_metrics(ticks, direction: str, fill_ticks: int, risk_ticks: int,
                         start_ms: int, end_ms: int, thresholds=(0.5, 1.0, 2.0)):
    times = ticks["time_msc"]
    left = int(np.searchsorted(times, start_ms, side="left"))
    right = int(np.searchsorted(times, end_ms, side="right"))
    if left >= right or risk_ticks <= 0:
        raise ValueError("no observed ticks in trade interval or non-positive initial risk")
    block = ticks[left:right]
    quote = block["bid_ticks"] if direction == "BUY" else block["ask_ticks"]
    moves = quote.astype(np.int64) - int(fill_ticks)
    if direction == "SELL":
        moves = -moves
    best_i = int(np.argmax(moves))
    worst_i = int(np.argmin(moves))
    mfe_ticks = int(moves[best_i])
    adverse_ticks = max(0, -int(moves[worst_i]))

    # Include the tick immediately before and after the interval when testing
    # gaps, so a gap crossing either boundary is not silently missed.
    gap_left = max(0, left - 1)
    gap_right = min(len(times), right + 1)
    gap_times = times[gap_left:gap_right]
    diffs = np.diff(gap_times)
    gap_mask = diffs > GAP_MS
    gap_count = int(np.count_nonzero(gap_mask))
    start_present = bool(np.any(times[left:right] == start_ms))
    end_present = bool(np.any(times[left:right] == end_ms))
    boundary_count = int(np.searchsorted(times, start_ms, "right") -
                         np.searchsorted(times, start_ms, "left"))
    exit_boundary_count = int(np.searchsorted(times, end_ms, "right") -
                              np.searchsorted(times, end_ms, "left"))

    result = {
        "ticks_observed": int(right - left),
        "start_tick_present": start_present,
        "end_tick_present": end_present,
        "start_timestamp_tick_count": boundary_count,
        "end_timestamp_tick_count": exit_boundary_count,
        "tick_gap_count_gt_60s": gap_count,
        "tick_gap_exposed": gap_count > 0,
        "mfe_price": mfe_ticks / PRICE_SCALE,
        "mae_price": adverse_ticks / PRICE_SCALE,
        "mfe_r": mfe_ticks / risk_ticks,
        "mae_r": adverse_ticks / risk_ticks,
        "mfe_time_utc": datetime.fromtimestamp(
            int(block["time_msc"][best_i]) / 1000, timezone.utc).isoformat(),
        "mae_time_utc": datetime.fromtimestamp(
            int(block["time_msc"][worst_i]) / 1000, timezone.utc).isoformat(),
    }
    for level in thresholds:
        ticks_needed = max(1, int(math.ceil(abs(level) * risk_ticks - 1e-12)))
        if level > 0:
            hits = np.flatnonzero(moves >= ticks_needed)
            prefix = "plus"
        else:
            hits = np.flatnonzero(moves <= -ticks_needed)
            prefix = "minus"
        key = f"time_to_{prefix}_{str(abs(level)).replace('.', '_')}r_seconds"
        result[key] = (
            (int(block["time_msc"][int(hits[0])]) - start_ms) / 1000
            if len(hits) else None
        )
    return result


def read_groups(detail_path: Path, family: str):
    groups = defaultdict(list)
    status_counts = Counter()
    with detail_path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"run_id", "candidate_entry_time_utc", "direction", "status",
                    "theoretical_entry", "initial_sl", "risk_price"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"{detail_path}: required columns missing")
        for row in reader:
            status_counts[row["status"]] += 1
            key = (row["run_id"], row["candidate_entry_time_utc"], row["direction"])
            groups[key].append(row)

    records = []
    excluded = Counter()
    for key, rows in groups.items():
        statuses = [r["status"] for r in rows]
        if key[2] not in ("BUY", "SELL"):
            raise ValueError(f"invalid direction for key {key}")
        if family == "MATRIX49" and len(rows) != 1:
            raise ValueError(f"MATRIX49 duplicate trade key: {key}")
        if family == "PARTIAL27":
            if len(rows) > 2:
                raise ValueError(f"PARTIAL27 group has >2 rows: {key}")
            if statuses.count("PARTIAL_LEG_CLOSED") > 1 or statuses.count("FILLED_AND_CLOSED") > 1:
                raise ValueError(f"PARTIAL27 duplicate leg/final row: {key}")
            allowed = (
                statuses in (["FILLED_AND_CLOSED"], ["PARTIAL_LEG_CLOSED", "FILLED_AND_CLOSED"],
                             ["FILLED_AND_CLOSED", "PARTIAL_LEG_CLOSED"],
                             ["PARTIAL_LEG_CLOSED", "AMBIGUOUS_DATA"],
                             ["AMBIGUOUS_DATA", "PARTIAL_LEG_CLOSED"], ["AMBIGUOUS_DATA"])
            )
            if not allowed and not (len(statuses) == 1 and statuses[0] not in
                                    ("FILLED_AND_CLOSED", "PARTIAL_LEG_CLOSED", "AMBIGUOUS_DATA")):
                raise ValueError(f"unexpected PARTIAL27 group status shape {statuses}: {key}")

        behavior_rows = [r for r in rows if r.get("fill_time_utc")]
        if not behavior_rows:
            for row in rows:
                excluded[row["status"]] += 1
            continue
        fill_times = {r["fill_time_utc"] for r in behavior_rows}
        if len(fill_times) != 1:
            raise ValueError(f"fill timestamp mismatch in group {key}")
        fill_time = next(iter(fill_times))
        fill_ms = parse_ms(fill_time)
        final_rows = [r for r in rows if r["status"] == "FILLED_AND_CLOSED"]
        partial_rows = [r for r in rows if r["status"] == "PARTIAL_LEG_CLOSED"]
        ambiguous_rows = [r for r in rows if r["status"] == "AMBIGUOUS_DATA"]
        if len(final_rows) > 1:
            raise ValueError(f"multiple final rows for trade {key}")
        exit_row = final_rows[0] if final_rows else None
        if exit_row:
            end_ms = parse_ms(exit_row["exit_time_utc"])
            end_time = exit_row["exit_time_utc"]
            trade_status = "CLOSED"
        else:
            last_values = [r.get("last_tick_utc", "") for r in ambiguous_rows if r.get("last_tick_utc")]
            if not last_values:
                raise ValueError(f"filled ambiguous trade has no last_tick_utc: {key}")
            end_time = last_values[0]
            end_ms = parse_ms(end_time)
            trade_status = "CENSORED_OPEN"

        base = behavior_rows[0]
        for field in ("theoretical_entry", "initial_sl", "risk_price"):
            vals = {r.get(field, "") for r in behavior_rows if r.get(field, "") != ""}
            if len(vals) > 1:
                raise ValueError(f"{field} mismatch in group {key}")
        fill_values = {r.get("fill_price", "") for r in behavior_rows if r.get("fill_price", "") != ""}
        if len(fill_values) > 1:
            raise ValueError(f"fill price mismatch in group {key}")
        fill_value = next(iter(fill_values), "")
        total_lots = None
        if family == "MATRIX49":
            total_lots = float(base.get("lots", 0) or 0) if exit_row else None
        elif exit_row:
            total_lots = sum(float(r.get("lots", 0) or 0) for r in rows
                             if r["status"] in ("PARTIAL_LEG_CLOSED", "FILLED_AND_CLOSED"))
        elif partial_rows:
            # TP1 closed one half; the replay retains an equal-sized remainder.
            total_lots = 2.0 * float(partial_rows[0].get("lots", 0) or 0)

        realized = sum(float(r.get("gross_pnl_usd", 0) or 0) for r in rows
                       if r["status"] in ("PARTIAL_LEG_CLOSED", "FILLED_AND_CLOSED"))
        theoretical = price_ticks(base["theoretical_entry"])
        initial_sl = price_ticks(base["initial_sl"])
        records.append({
            "family": family, "run_id": key[0], "candidate_entry_time_utc": key[1],
            "direction": key[2], "trade_status": trade_status,
            "fill_time_utc": fill_time, "fill_time_ms": fill_ms,
            "end_time_utc": end_time, "end_time_ms": end_ms,
            "theoretical_entry_ticks": theoretical, "initial_sl_ticks": initial_sl,
            "risk_price": float(base["risk_price"]), "fill_price_ticks":
                price_ticks(fill_value) if fill_value else None,
            "total_lots": total_lots, "realized_gross_pnl_usd": realized,
            "exit_price": float(exit_row["exit_price"]) if exit_row else None,
            "exit_reason": exit_row.get("exit_reason", "") if exit_row else "",
            "exit_risk_usd_source": float(exit_row["fill_based_initial_risk_usd"])
                if family == "MATRIX49" and exit_row and exit_row.get("fill_based_initial_risk_usd") else None,
            "source_statuses": "+".join(sorted(statuses)),
            "censored_reason": ambiguous_rows[0].get("ambiguity", "") if ambiguous_rows else "",
        })
    return records, status_counts, excluded


def analyze_dataset(ticks, family, latency, detail_path, manifest_path, output_rows):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "COMPLETE_GROSS_ONLY":
        raise ValueError(f"{family}/{latency}: source replay incomplete")
    if manifest.get("research_only") is not True or manifest.get("canonical") is not False:
        raise ValueError(f"{family}/{latency}: source manifest flags invalid")
    if manifest.get("mt5_accessed") is not False or manifest.get("runner_accessed") is not False:
        raise ValueError(f"{family}/{latency}: source manifest indicates MT5/Runner access")
    if manifest.get("execution_assumptions", {}).get("latency_seconds") != int(latency[:-1]):
        raise ValueError(f"{family}/{latency}: latency mismatch")
    tick_stats = manifest.get("tick_stats", {})
    if int(tick_stats.get("tick_rows", -1)) != len(ticks):
        raise ValueError(f"{family}/{latency}: tick row count differs")
    if sha256_file(detail_path) != manifest.get("output_sha256", {}).get(detail_path.name):
        raise ValueError(f"{family}/{latency}: detail output SHA mismatch")

    records, status_counts, excluded = read_groups(detail_path, family)
    summary = {
        "family": family, "latency": latency, "candidate_rows": sum(status_counts.values()),
        "status_counts": json.dumps(dict(status_counts), sort_keys=True),
        "behavior_trades": len(records),
        "closed_trades": sum(r["trade_status"] == "CLOSED" for r in records),
        "censored_open_trades": sum(r["trade_status"] == "CENSORED_OPEN" for r in records),
        "excluded_without_fill": sum(excluded.values()),
        "excluded_status_counts": json.dumps(dict(excluded), sort_keys=True),
    }
    times = ticks["time_msc"]
    first_tick = int(times[0])
    last_tick = int(times[-1])
    for trade in records:
        start_ms = trade["fill_time_ms"]
        end_ms = trade["end_time_ms"]
        if end_ms < start_ms:
            raise ValueError(f"negative trade interval: {trade['run_id']} {trade['candidate_entry_time_utc']}")
        fill_ticks = trade["fill_price_ticks"]
        reconstructed = False
        if fill_ticks is None:
            fill_ticks = reconstruct_fill(
                ticks, start_ms, trade["direction"], trade["theoretical_entry_ticks"])
            reconstructed = fill_ticks is not None
        if fill_ticks is None:
            trade["analysis_status"] = "QUARANTINED_FILL_PRICE_UNRESOLVED"
            output_rows.append(trade)
            continue
        risk_ticks = abs(int(fill_ticks) - trade["initial_sl_ticks"])
        if risk_ticks <= 0:
            raise ValueError(f"non-positive actual initial risk: {trade['run_id']}")
        clipped_start = max(start_ms, first_tick)
        clipped_end = min(end_ms, last_tick)
        if clipped_start > clipped_end:
            trade["analysis_status"] = "QUARANTINED_NO_TICK_COVERAGE"
            output_rows.append(trade)
            continue
        path = compute_path_metrics(ticks, trade["direction"], fill_ticks,
                                    risk_ticks, clipped_start, clipped_end)
        trade.update(path)
        trade["fill_price"] = fill_ticks / PRICE_SCALE
        trade["actual_initial_risk_price"] = risk_ticks / PRICE_SCALE
        trade["fill_price_reconstructed_from_ticks"] = reconstructed
        trade["source_truncated_at_start"] = start_ms < first_tick
        trade["source_ended_before_trade_end"] = end_ms > last_tick
        trade["coverage_complete"] = (
            clipped_start == start_ms and clipped_end == end_ms and
            path["start_tick_present"] and path["end_tick_present"] and
            not path["tick_gap_exposed"] and
            path["start_timestamp_tick_count"] == 1 and
            path["end_timestamp_tick_count"] == 1
        )
        trade["analysis_status"] = "ANALYZED"
        trade["initial_risk_usd"] = (
            risk_ticks / PRICE_SCALE / 0.01 * 1.0 * trade["total_lots"]
            if trade["total_lots"] is not None else None
        )
        if trade["trade_status"] == "CLOSED" and trade["initial_risk_usd"]:
            trade["exit_r"] = trade["realized_gross_pnl_usd"] / trade["initial_risk_usd"]
            trade["giveback_r"] = path["mfe_r"] - trade["exit_r"]
            trade["giveback_fraction_of_mfe"] = (
                trade["giveback_r"] / path["mfe_r"] if path["mfe_r"] > 0 else None)
        else:
            trade["exit_r"] = None
            trade["giveback_r"] = None
            trade["giveback_fraction_of_mfe"] = None
        output_rows.append(trade)
    summary["analyzed_trades"] = sum(r.get("analysis_status") == "ANALYZED" for r in records)
    summary["quarantined_trades"] = len(records) - summary["analyzed_trades"]
    summary["trades_with_tick_gaps"] = sum(
        r.get("analysis_status") == "ANALYZED" and r.get("tick_gap_exposed", False) for r in records)
    summary["trades_with_incomplete_coverage"] = sum(
        r.get("analysis_status") == "ANALYZED" and not r.get("coverage_complete", False) for r in records)
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evidence-base", required=True, type=Path,
                    help="Parent folder containing the six existing replay output folders")
    ap.add_argument("--ticks-csv-gz", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    ap.add_argument("--scratch-root", required=True, type=Path,
                    help="Existing folder with enough free space for a temporary ~510 MB tick index")
    args = ap.parse_args()
    base = args.evidence_base.resolve()
    tick_path = args.ticks_csv_gz.resolve()
    output = args.output_dir.resolve()
    scratch = args.scratch_root.resolve()
    if output.exists():
        raise FileExistsError(f"output directory must be new: {output}")
    if not scratch.is_dir():
        raise FileNotFoundError(f"scratch root must already exist: {scratch}")

    source_files = {}
    manifests = {}
    for family, spec in FAMILIES.items():
        for latency in LATENCIES:
            folder = base / spec["directory"].format(latency=latency)
            detail = folder / spec["detail"]
            manifest_path = folder / spec["manifest"]
            if not detail.is_file() or not manifest_path.is_file():
                raise FileNotFoundError(f"missing source detail/manifest: {folder}")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("input_sha256", {}).get("ticks") != sha256_file(tick_path):
                raise ValueError(f"{family}/{latency}: tick source SHA differs")
            source_files[f"{family}_{latency}"] = {
                "detail": str(detail), "detail_sha256": sha256_file(detail),
                "manifest": str(manifest_path), "manifest_sha256": sha256_file(manifest_path)}
            manifests[f"{family}_{latency}"] = manifest

    reference = manifests["MATRIX49_0s"]
    for key, manifest in manifests.items():
        if manifest.get("input_sha256") != reference.get("input_sha256"):
            raise ValueError(f"{key}: input hashes differ from MATRIX49_0s")
        # Each family has its own replay source code hashes, so compare within family.
    for family in FAMILIES:
        ref = manifests[f"{family}_0s"]
        for latency in ("2s", "5s"):
            current = manifests[f"{family}_{latency}"]
            if current.get("code_sha256") != ref.get("code_sha256"):
                raise ValueError(f"{family}/{latency}: replay code hashes differ")
    expected_rows = int(reference["tick_stats"]["tick_rows"])
    if expected_rows != 31_852_364:
        raise ValueError(f"unexpected tick row count: {expected_rows}")
    if sha256_file(tick_path) != reference["input_sha256"]["ticks"]:
        raise ValueError("tick source SHA mismatch")

    output.mkdir(parents=True, exist_ok=False)
    summaries = []
    metrics_path = output / "SP2L_TRADE_BEHAVIOR_METRICS.csv"
    summary_path = output / "SP2L_TRADE_BEHAVIOR_SUMMARY.csv"
    all_metrics = []
    with tempfile.TemporaryDirectory(prefix="sp2l-trade-behavior-", dir=scratch) as temp:
        index_path = Path(temp) / "ticks.bin"
        ticks, tick_index_stats = build_tick_index(tick_path, index_path, expected_rows)
        for family, spec in FAMILIES.items():
            for latency in LATENCIES:
                folder = base / spec["directory"].format(latency=latency)
                rows = []
                summaries.append(analyze_dataset(
                    ticks, family, latency, folder / spec["detail"],
                    folder / spec["manifest"], rows))
                all_metrics.extend(rows)
        del ticks

    if all_metrics:
        fields = sorted({k for row in all_metrics for k in row})
        with metrics_path.open("x", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(all_metrics)
    with summary_path.open("x", encoding="utf-8", newline="") as stream:
        fields = list(summaries[0])
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summaries)

    analyzer_path = Path(__file__).resolve()
    report = {
        "status": "COMPLETE_TICK_BASED_TRADE_BEHAVIOR_ANALYSIS",
        "research_only": True, "canonical": False, "mt5_accessed": False,
        "runner_accessed": False, "orders_possible": False,
        "tick_source_sha256": sha256_file(tick_path),
        "tick_index_stats": tick_index_stats,
        "source_replay_files": source_files,
        "analyzer_sha256": sha256_file(analyzer_path),
        "families": list(FAMILIES), "latencies": list(LATENCIES),
        "thresholds_r": [0.5, 1.0, 2.0, -0.5, -1.0],
        "metric_definitions": {
            "quote_side": "BUY marks/exits on Bid; SELL marks/exits on Ask.",
            "mfe_r": "Maximum favorable executable quote move from actual fill divided by actual fill-to-initial-SL price risk.",
            "mae_r": "Maximum adverse executable quote move magnitude from actual fill divided by actual fill-to-initial-SL price risk.",
            "partial_trade": "Underlying position price path from first fill to final exit; realized PnL sums all closed legs.",
            "exit_r": "Summed realized gross PnL divided by initial risk USD for the full original position.",
            "giveback_r": "MFE_R minus final realized trade_R; not computed for censored trades.",
            "threshold_times": "First observed tick crossing the signed R threshold; no interpolation.",
            "tick_gaps": "Any observed interval >60 seconds is flagged; no interpolation across gaps.",
            "boundary_duplicates": "More than one tick at fill/exit millisecond makes coverage incomplete because detail files do not store tick sequence IDs.",
            "censored": "Open positions are measured only through last observed tick and have no exit_R or final giveback.",
        },
        "summary": summaries,
        "metrics_csv": metrics_path.name, "metrics_csv_sha256": sha256_file(metrics_path),
        "summary_csv": summary_path.name, "summary_csv_sha256": sha256_file(summary_path),
    }
    (output / "SP2L_TRADE_BEHAVIOR_MANIFEST.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"], "summary": summaries,
        "metrics_csv": str(metrics_path), "metrics_sha256": report["metrics_csv_sha256"],
        "summary_csv": str(summary_path), "manifest": str(output / "SP2L_TRADE_BEHAVIOR_MANIFEST.json"),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
