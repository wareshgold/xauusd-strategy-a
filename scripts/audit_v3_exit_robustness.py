#!/usr/bin/env python3
"""Deterministic, research-only robustness audit for SP2L V3 exit Discovery.

Consumes the already-audited local evidence manifest and its Trades CSV.
Never modifies source artifacts. Outputs a separate robustness report, summary
CSV, and temporal-slice CSV. No variant is selected as canonical.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any

VARIANT_RE = re.compile(
    r"^RR(?P<rr>[0-9]+(?:\.[0-9]+)?)(?:_NO_TRAIL|_ACT(?P<act>[0-9]+(?:\.[0-9]+)?)_D(?P<dist>[0-9]+(?:\.[0-9]+)?))$"
)
REQUIRED_FIELDS = {"variant", "trigger_time", "ambiguous", "realized_R", "reason"}


class RobustnessError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def finite_float(value: str | None, label: str) -> float | None:
    if value is None or value.strip() == "":
        return None
    try:
        number = float(value)
    except ValueError as exc:
        raise RobustnessError(f"{label} is not numeric: {value!r}") from exc
    if not math.isfinite(number):
        raise RobustnessError(f"{label} is not finite")
    return number


def parse_variant(name: str) -> dict[str, float | str | None]:
    match = VARIANT_RE.fullmatch(name)
    if not match:
        raise RobustnessError(f"unsupported variant name: {name}")
    return {
        "name": name,
        "rr": float(match.group("rr")),
        "activation": float(match.group("act")) if match.group("act") else None,
        "distance": float(match.group("dist")) if match.group("dist") else None,
    }


def load_inputs(manifest_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], Path]:
    if not manifest_path.is_file():
        raise RobustnessError(f"manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "SP2L_V3_DISCOVERY_EVIDENCE_MANIFEST_V1":
        raise RobustnessError("unexpected evidence manifest schema")
    if manifest.get("audit_status") != "PASS" or manifest.get("research_only") is not True:
        raise RobustnessError("manifest is not a research-only AUDIT=PASS artifact")

    artifacts = manifest.get("artifacts") or {}
    trades_info = artifacts.get("trades_csv") or {}
    trades_path = Path(str(trades_info.get("path") or ""))
    if not trades_path.is_file():
        raise RobustnessError(f"Trades CSV missing: {trades_path}")
    expected_hash = str(trades_info.get("sha256") or "").lower()
    actual_hash = sha256_file(trades_path)
    if not expected_hash or actual_hash != expected_hash:
        raise RobustnessError("Trades CSV SHA-256 does not match evidence manifest")

    with trades_path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = set(reader.fieldnames or [])
        missing = REQUIRED_FIELDS - fields
        if missing:
            raise RobustnessError(f"Trades CSV missing fields: {sorted(missing)}")
        raw_rows = list(reader)

    expected_rows = int(trades_info.get("rows", -1))
    if len(raw_rows) != expected_rows:
        raise RobustnessError(f"Trades CSV row count mismatch: {len(raw_rows)} != {expected_rows}")

    rows: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_rows, 2):
        try:
            timestamp = int(raw["trigger_time"])
        except (TypeError, ValueError) as exc:
            raise RobustnessError(f"row {index}: invalid trigger_time") from exc
        if timestamp < 0:
            raise RobustnessError(f"row {index}: negative trigger_time")
        ambiguous_text = raw["ambiguous"].strip().lower()
        if ambiguous_text not in {"true", "false", "1", "0"}:
            raise RobustnessError(f"row {index}: invalid ambiguous flag {raw['ambiguous']!r}")
        ambiguous = ambiguous_text in {"true", "1"}
        realized = finite_float(raw.get("realized_R"), f"row {index}.realized_R")
        if ambiguous and realized is not None:
            raise RobustnessError(f"row {index}: ambiguous trade has realized_R")
        # A non-ambiguous row with no realized_R is an unresolved/open outcome,
        # not a decisive trade. Preserve it as non-decisive rather than guessing.
        variant = raw["variant"]
        rows.append({
            "variant": variant,
            "trigger_time": timestamp,
            "day": datetime.fromtimestamp(timestamp, timezone.utc).date().isoformat(),
            "ambiguous": ambiguous,
            "realized_R": realized,
            "reason": raw["reason"],
        })

    declared_variants = int((manifest.get("run") or {}).get("variants", -1))
    declared_signals = int((manifest.get("run") or {}).get("frozen_entry_rows", -1))
    names = sorted({row["variant"] for row in rows})
    if len(names) != declared_variants:
        raise RobustnessError(f"variant count mismatch: {len(names)} != {declared_variants}")
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row["variant"]] += 1
    if any(count != declared_signals for count in counts.values()):
        raise RobustnessError("not every variant has the declared frozen signal count")
    for name in names:
        parse_variant(name)
    return manifest, rows, trades_path


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    decisive = [r for r in rows if not r["ambiguous"] and r["realized_R"] is not None]
    returns = [float(r["realized_R"]) for r in decisive]
    wins = [x for x in returns if x > 0]
    losses = [x for x in returns if x < 0]
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    ordered = sorted(decisive, key=lambda r: (r["trigger_time"], r["variant"]))
    equity = peak = max_dd = 0.0
    for row in ordered:
        equity += float(row["realized_R"])
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    return {
        "signals": len(rows),
        "decisive": len(decisive),
        "ambiguous": sum(1 for r in rows if r["ambiguous"]),
        "unresolved": sum(1 for r in rows if not r["ambiguous"] and r["realized_R"] is None),
        "non_decisive": len(rows) - len(decisive),
        "net_R": sum(returns),
        "mean_R_per_decisive": mean(returns) if returns else None,
        "win_rate_pct": 100.0 * len(wins) / len(returns) if returns else None,
        "profit_factor": gross_win / gross_loss if gross_loss else None,
        "max_drawdown_R": max_dd,
        "gap_exposed": sum(1 for r in rows if r["reason"] == "M1_GAP_WHILE_OPEN"),
    }


def equal_time_slices(rows: list[dict[str, Any]], count: int = 4) -> dict[str, int]:
    times = [r["trigger_time"] for r in rows]
    low, high = min(times), max(times)
    if low == high:
        return {r["variant"]: 1 for r in rows}
    span = high - low + 1
    result: dict[str, int] = {}
    for row in rows:
        bucket = min(count - 1, ((row["trigger_time"] - low) * count) // span)
        result.setdefault(row["variant"], 0)
        result[row["variant"]] = max(result[row["variant"]], bucket + 1)
    return result


def build_daily_matrix(rows: list[dict[str, Any]]) -> tuple[list[str], list[str], list[list[float | None]], dict[str, list[dict[str, Any]]]]:
    names = sorted({r["variant"] for r in rows})
    days = sorted({r["day"] for r in rows})
    day_index = {day: i for i, day in enumerate(days)}
    name_index = {name: i for i, name in enumerate(names)}
    # A day with no triggered rows is a genuine zero-return day. A day with
    # any ambiguous or unresolved outcome is unknown, not a synthetic zero.
    matrix: list[list[float | None]] = [[0.0 for _ in days] for _ in names]
    unknown_days: set[tuple[int, int]] = set()
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["variant"]].append(row)
        key = (name_index[row["variant"]], day_index[row["day"]])
        realized = row["realized_R"]
        if row["ambiguous"] or realized is None:
            unknown_days.add(key)
        elif key not in unknown_days:
            matrix[key[0]][key[1]] += float(realized)
    for variant_index, day in unknown_days:
        matrix[variant_index][day] = None
    return names, days, matrix, grouped


def t_stat(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    sd = stdev(values)
    if sd <= 1e-15:
        return 0.0
    return mean(values) / (sd / math.sqrt(len(values)))


def max_stat_bootstrap(matrix: list[list[float | None]], *, iterations: int, seed: int) -> dict[str, Any]:
    """Missingness-preserving circular moving-block bootstrap max-t diagnostic.

    Calendar positions and their missingness masks are resampled together.
    Each replicate is reduced to a mean over its known observations, but the
    block sampler never compacts the source calendar before drawing blocks.
    Studentization uses the bootstrap standard deviation of each variant's
    resampled centered mean.
    """
    if not matrix or not matrix[0]:
        raise RobustnessError("no daily returns available for bootstrap")
    day_count = len(matrix[0])
    if day_count < 3:
        raise RobustnessError("at least three distinct UTC trade days are required")
    if any(len(row) != day_count for row in matrix):
        raise RobustnessError("daily return matrix is not rectangular")

    known_counts = [sum(value is not None for value in row) for row in matrix]
    eligible = [index for index, count in enumerate(known_counts) if count >= 3]
    excluded = len(matrix) - len(eligible)
    if not eligible:
        raise RobustnessError("no variant has at least three known daily returns")
    block_length = max(2, round(day_count ** (1.0 / 3.0)))

    centered: list[list[float | None]] = []
    observed_means: list[float] = []
    for row in matrix:
        known = [float(value) for value in row if value is not None]
        row_mean = mean(known) if known else 0.0
        observed_means.append(row_mean)
        centered.append([None if value is None else float(value) - row_mean for value in row])

    rng = random.Random(seed)
    bootstrap_means: list[list[float | None]] = [[] for _ in matrix]
    sampled_counts: list[list[int]] = [[] for _ in matrix]
    for _ in range(iterations):
        # Draw contiguous blocks in original calendar coordinates. The same
        # indices are shared by all variants, retaining cross-variant pairing.
        indices: list[int] = []
        while len(indices) < day_count:
            start = rng.randrange(day_count)
            indices.extend((start + offset) % day_count for offset in range(block_length))
        indices = indices[:day_count]

        for variant_index in eligible:
            # Keep None at its sampled calendar position. We aggregate only
            # known outcomes after resampling; we do not pre-compress dates.
            sample = [centered[variant_index][i] for i in indices]
            known = [float(value) for value in sample if value is not None]
            sampled_counts[variant_index].append(len(known))
            bootstrap_means[variant_index].append(mean(known) if len(known) >= 3 else None)

    standard_errors: dict[int, float] = {}
    valid_replicates: dict[int, list[float]] = {}
    for variant_index in eligible:
        values = [value for value in bootstrap_means[variant_index] if value is not None]
        if len(values) < max(20, iterations // 2):
            raise RobustnessError(
                f"too few bootstrap replicates retain three known days for variant index {variant_index}"
            )
        standard_error = stdev(values)
        if standard_error <= 1e-15:
            raise RobustnessError(
                f"bootstrap standard error is zero for variant index {variant_index}"
            )
        standard_errors[variant_index] = standard_error
        valid_replicates[variant_index] = values

    observed_max_t = max(
        observed_means[index] / standard_errors[index] for index in eligible
    )
    maxima: list[float] = []
    exceed = 0
    for iteration in range(iterations):
        replicate_stats = []
        for variant_index in eligible:
            value = bootstrap_means[variant_index][iteration]
            if value is not None:
                replicate_stats.append(value / standard_errors[variant_index])
        if not replicate_stats:
            raise RobustnessError("bootstrap replicate contains no eligible known outcomes")
        max_t = max(replicate_stats)
        maxima.append(max_t)
        if max_t >= observed_max_t:
            exceed += 1

    maxima.sort()
    q95 = maxima[min(len(maxima) - 1, math.ceil(0.95 * len(maxima)) - 1)]
    eligible_counts = [known_counts[index] for index in eligible]
    replicate_min = min(
        sum(value is not None for value in bootstrap_means[index])
        for index in eligible
    )
    return {
        "method": "UTC daily circular moving-block bootstrap; shared contiguous calendar-index blocks across variants; missingness masks travel with sampled dates; centered max-t null studentized by bootstrap standard error",
        "iterations": iterations,
        "seed": seed,
        "distinct_trade_days": day_count,
        "block_length_days": block_length,
        "eligible_variants": len(eligible),
        "excluded_variants_fewer_than_three_known_days": excluded,
        "known_daily_returns_by_variant_min": min(eligible_counts),
        "known_daily_returns_by_variant_max": max(eligible_counts),
        "minimum_valid_bootstrap_replicates_per_variant": replicate_min,
        "observed_max_t": observed_max_t,
        "null_max_t_95pct": q95,
        "familywise_max_t_p_value": (exceed + 1) / (iterations + 1),
        "interpretation": "Exploratory multiplicity diagnostic; calendar spacing and missingness masks are preserved during block sampling; unknown outcomes are not scored as zero; not a substitute for untouched validation or a formal guarantee under all dependence structures.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Audited V3 Discovery evidence manifest")
    parser.add_argument("--output-dir", default=None, help="New output directory; must not already exist")
    parser.add_argument("--bootstrap-iterations", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261101)
    args = parser.parse_args()
    try:
        if args.bootstrap_iterations < 200:
            raise RobustnessError("bootstrap iterations must be at least 200")
        manifest_path = Path(args.manifest).resolve()
        manifest, all_rows, trades_path = load_inputs(manifest_path)
        out_dir = Path(args.output_dir).resolve() if args.output_dir else manifest_path.parent / "robustness_20261101"
        if out_dir.exists():
            raise RobustnessError(f"refusing to overwrite existing output directory: {out_dir}")
        out_dir.mkdir(parents=True)

        names, days, daily, grouped = build_daily_matrix(all_rows)
        params = {name: parse_variant(name) for name in names}
        slice_rows: list[dict[str, Any]] = []
        summary_rows: list[dict[str, Any]] = []

        for name in names:
            rows = grouped[name]
            summary = summarize(rows)
            buckets: dict[int, list[dict[str, Any]]] = defaultdict(list)
            low = min(r["trigger_time"] for r in all_rows)
            high = max(r["trigger_time"] for r in all_rows)
            span = max(1, high - low + 1)
            for row in rows:
                bucket = min(3, ((row["trigger_time"] - low) * 4) // span)
                buckets[bucket].append(row)
            per_slice = []
            positive_slices = 0
            valid_slices = 0
            for bucket in range(4):
                part = buckets.get(bucket, [])
                stat = summarize(part)
                item = {"variant": name, "slice": bucket + 1, **stat}
                slice_rows.append(item)
                per_slice.append(item)
                if stat["decisive"] > 0:
                    valid_slices += 1
                    if float(stat["net_R"]) > 0:
                        positive_slices += 1
            summary_rows.append({
                **params[name],
                **summary,
                "positive_time_slices": positive_slices,
                "valid_time_slices": valid_slices,
                "positive_slice_fraction": positive_slices / valid_slices if valid_slices else None,
                "worst_slice_net_R": min((float(x["net_R"]) for x in per_slice if x["decisive"] > 0), default=None),
            })

        # Local parameter neighbourhood: immediate grid steps in RR/ACT/D.
        # NO_TRAIL is deliberately not treated as a neighbour of trailing variants.
        rr_grid = sorted({float(p["rr"]) for p in params.values()})
        act_grid = sorted({float(p["activation"]) for p in params.values() if p["activation"] is not None})
        dist_grid = sorted({float(p["distance"]) for p in params.values() if p["distance"] is not None})
        for row in summary_rows:
            p = params[row["name"]]
            neighbours = []
            if p["activation"] is not None:
                rr_i = rr_grid.index(float(p["rr"]))
                act_i = act_grid.index(float(p["activation"]))
                dist_i = dist_grid.index(float(p["distance"]))
                for other_name, q in params.items():
                    if q["activation"] is None:
                        continue
                    if (
                        abs(rr_grid.index(float(q["rr"])) - rr_i) <= 1
                        and abs(act_grid.index(float(q["activation"])) - act_i) <= 1
                        and abs(dist_grid.index(float(q["distance"])) - dist_i) <= 1
                        and other_name != row["name"]
                    ):
                        neighbours.append(other_name)
            neighbour_means = [
                float(next(x for x in summary_rows if x["name"] == other)["mean_R_per_decisive"])
                for other in neighbours
                if next(x for x in summary_rows if x["name"] == other)["mean_R_per_decisive"] is not None
            ]
            row["local_neighbour_count"] = len(neighbours)
            row["local_neighbour_positive_fraction"] = (
                sum(1 for x in neighbour_means if x > 0) / len(neighbour_means)
                if neighbour_means else None
            )
            row["local_neighbour_median_mean_R"] = median(neighbour_means) if neighbour_means else None

        bootstrap = max_stat_bootstrap(daily, iterations=args.bootstrap_iterations, seed=args.seed)
        # Sort for inspection only; explicitly not a candidate-selection rule.
        summary_rows.sort(key=lambda r: (float(r["net_R"]), float(r["mean_R_per_decisive"] or -1e9)), reverse=True)

        summary_path = out_dir / "V3_EXIT_ROBUSTNESS_VARIANT_SUMMARY.csv"
        slice_path = out_dir / "V3_EXIT_ROBUSTNESS_TIME_SLICES.csv"
        report_path = out_dir / "V3_EXIT_ROBUSTNESS_REPORT.json"
        with summary_path.open("w", encoding="utf-8", newline="") as stream:
            fields = list(summary_rows[0].keys())
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(summary_rows)
        with slice_path.open("w", encoding="utf-8", newline="") as stream:
            fields = list(slice_rows[0].keys())
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(slice_rows)

        report = {
            "schema": "SP2L_V3_EXIT_ROBUSTNESS_REPORT_V1",
            "research_only": True,
            "source_manifest": str(manifest_path),
            "source_manifest_sha256": sha256_file(manifest_path),
            "source_trades_csv": str(trades_path),
            "source_trades_sha256": sha256_file(trades_path),
            "source_run": manifest.get("run"),
            "variants": len(names),
            "trade_rows": len(all_rows),
            "distinct_utc_trade_days": len(days),
            "temporal_partition": "four equal-width chronological trigger-time slices; empty/low-count slices retained and reported",
            "parameter_neighbourhood": "immediate adjacent grid coordinates in RR, activation points, and distance points; NO_TRAIL isolated",
            "multiple_testing": bootstrap,
            "outputs": {
                "variant_summary_csv": str(summary_path),
                "time_slices_csv": str(slice_path),
                "variant_summary_sha256": sha256_file(summary_path),
                "time_slices_sha256": sha256_file(slice_path),
                "variant_summary_rows": len(summary_rows),
                "time_slice_rows": len(slice_rows),
            },
            "limitations": [
                "Development sample only; all 288 variants were inspected on this same sample.",
                "The circular moving-block max-t bootstrap is an exploratory family-wise multiplicity diagnostic; its short block length cannot represent every regime shift or long-memory dependence.",
                "M1 OHLC proxy, known M1 gaps, ambiguous outcomes, and omitted spread/slippage/commission remain applicable.",
                "No untouched validation or fresh holdout is performed by this script.",
                "No canonical exit geometry or production candidate is selected.",
            ],
        }
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(
            f"ROBUSTNESS=PASS variants={len(names)} trades={len(all_rows)} "
            f"days={len(days)} bootstrap={args.bootstrap_iterations} "
            f"max_t_p={bootstrap['familywise_max_t_p_value']:.6f} "
            f"report={report_path}"
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError, RobustnessError) as exc:
        print(f"ROBUSTNESS=FAIL reason={exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
