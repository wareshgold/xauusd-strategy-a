"""Build a validated cross-latency comparison of the local 49-run replay summaries.

Research-only reporting. Does not replay ticks, connect to MT5, or change runner settings.
The output is a descriptive robustness screen, not a canonical winner selection.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from research.capital_matrix.matrix import Family, build_matrix

LATENCIES = ("0s", "2s", "5s")
SUMMARY_NAME = "SP2L_CAPITAL_MATRIX_RUN_SUMMARY.csv"
MANIFEST_NAME = "SP2L_CAPITAL_MATRIX_REPLAY_MANIFEST.json"
EXPECTED_REPLAYED = {
    run.run_id for run in build_matrix()
    if run.family in (Family.FIXED_TP, Family.EXACT_RUNNER, Family.NORMALIZED_RUNNER)
}
EXPECTED_DUAL = {
    run.run_id for run in build_matrix()
    if run.family is Family.DUAL_INDEPENDENT
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_run(directory: Path, latency: str):
    run_dir = directory / f"capital-matrix-replay-v1-{latency}"
    summary_path = run_dir / SUMMARY_NAME
    manifest_path = run_dir / MANIFEST_NAME
    if not summary_path.is_file() or not manifest_path.is_file():
        raise FileNotFoundError(f"Missing summary or manifest for {latency}: {run_dir}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "COMPLETE_GROSS_ONLY":
        raise ValueError(f"{latency}: unexpected run status {manifest.get('status')!r}")
    if manifest.get("research_only") is not True or manifest.get("canonical") is not False:
        raise ValueError(f"{latency}: research/canonical flags are not as expected")
    if manifest.get("mt5_accessed") is not False or manifest.get("runner_accessed") is not False:
        raise ValueError(f"{latency}: source manifest indicates MT5 or runner access")
    if manifest.get("execution_assumptions", {}).get("latency_seconds") != int(latency[:-1]):
        raise ValueError(f"{latency}: latency in manifest does not match directory")
    if manifest.get("replayed_runs") != 49 or manifest.get("dual_runs") != 40:
        raise ValueError(f"{latency}: expected 49 replayed and 40 unexecuted dual runs")

    with summary_path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    by_id = {row["run_id"]: row for row in rows}
    if len(rows) != 49 or set(by_id) != EXPECTED_REPLAYED:
        missing = sorted(EXPECTED_REPLAYED - set(by_id))
        extra = sorted(set(by_id) - EXPECTED_REPLAYED)
        raise ValueError(f"{latency}: summary run IDs mismatch; missing={missing}, extra={extra}")

    for row in rows:
        for field in ("closed_trades", "gross_net_usd", "win_rate",
                      "average_r", "max_drawdown_fraction", "ending_equity_gross"):
            if row.get(field, "") == "":
                raise ValueError(f"{latency}/{row['run_id']}: missing {field}")
        counts = json.loads(row["counts"])
        if sum(int(value) for value in counts.values()) != 1518:
            raise ValueError(f"{latency}/{row['run_id']}: status counts do not sum to 1518")
        if row["cost_status"] != "GROSS_ONLY_COMMISSION_SWAP_SLIPPAGE_NOT_INCLUDED":
            raise ValueError(f"{latency}/{row['run_id']}: unexpected cost status")
    return by_id, manifest, summary_path


def number(row, key):
    value = row.get(key, "")
    return None if value in ("", "None", "null") else float(value)


def rank_for(rows, metric, reverse):
    ordered = sorted(rows, key=lambda run_id: (
        number(rows[run_id], metric) is None,
        -(number(rows[run_id], metric) or 0) if reverse
        else (number(rows[run_id], metric) if number(rows[run_id], metric) is not None else float("inf")),
        run_id,
    ))
    return {run_id: rank for rank, run_id in enumerate(ordered, 1)}


def build_report(base_dir: Path, output_dir: Path):
    loaded = {lat: read_run(base_dir, lat) for lat in LATENCIES}
    manifests = {lat: item[1] for lat, item in loaded.items()}

    # Inputs and code must be identical; only declared execution latency may differ.
    first = manifests[LATENCIES[0]]
    for lat in LATENCIES[1:]:
        current = manifests[lat]
        if current.get("input_sha256") != first.get("input_sha256"):
            raise ValueError(f"{lat}: input hashes differ from 0s run")
        if current.get("code_sha256") != first.get("code_sha256"):
            raise ValueError(f"{lat}: code hashes differ from 0s run")
        if current.get("broker_contract") != first.get("broker_contract"):
            raise ValueError(f"{lat}: broker contract differs from 0s run")

    rows_by_latency = {lat: loaded[lat][0] for lat in LATENCIES}
    rank_fields = {
        lat: {
            "gross": rank_for(rows_by_latency[lat], "gross_net_usd", True),
            "pf": rank_for(rows_by_latency[lat], "profit_factor", True),
            "dd": rank_for(rows_by_latency[lat], "max_drawdown_fraction", False),
        } for lat in LATENCIES
    }

    combined = []
    for run_id in sorted(EXPECTED_REPLAYED):
        item = {"run_id": run_id}
        for lat in LATENCIES:
            row = rows_by_latency[lat][run_id]
            prefix = lat.replace("s", "")
            item.update({
                f"closed_{prefix}s": int(row["closed_trades"]),
                f"gross_usd_{prefix}s": number(row, "gross_net_usd"),
                f"pf_{prefix}s": number(row, "profit_factor"),
                f"win_rate_{prefix}s": number(row, "win_rate"),
                f"average_r_{prefix}s": number(row, "average_r"),
                f"max_dd_{prefix}s": number(row, "max_drawdown_fraction"),
                f"ending_equity_{prefix}s": number(row, "ending_equity_gross"),
                f"rank_gross_{prefix}s": rank_fields[lat]["gross"][run_id],
                f"rank_pf_{prefix}s": rank_fields[lat]["pf"][run_id],
                f"rank_dd_{prefix}s": rank_fields[lat]["dd"][run_id],
            })
        gross_values = [item[f"gross_usd_{lat[:-1]}s"] for lat in LATENCIES]
        pf_values = [item[f"pf_{lat[:-1]}s"] for lat in LATENCIES]
        dd_values = [item[f"max_dd_{lat[:-1]}s"] for lat in LATENCIES]
        item["worst_case_gross_usd"] = min(gross_values)
        item["worst_case_pf"] = min(v for v in pf_values if v is not None) if any(v is not None for v in pf_values) else None
        item["worst_case_max_dd"] = max(dd_values)
        item["positive_gross_all_latencies"] = all(v > 0 for v in gross_values)
        item["rank_gross_mean"] = sum(item[f"rank_gross_{lat[:-1]}s"] for lat in LATENCIES) / 3
        item["rank_pf_mean"] = sum(item[f"rank_pf_{lat[:-1]}s"] for lat in LATENCIES) / 3
        item["rank_dd_mean"] = sum(item[f"rank_dd_{lat[:-1]}s"] for lat in LATENCIES) / 3
        combined.append(item)

    # Transparent ordering only: downside gross screen, not a composite score.
    combined.sort(key=lambda row: (
        not row["positive_gross_all_latencies"],
        -row["worst_case_gross_usd"],
        -(row["worst_case_pf"] if row["worst_case_pf"] is not None else -1),
        row["worst_case_max_dd"],
        row["run_id"],
    ))
    for rank, row in enumerate(combined, 1):
        row["worst_case_gross_screen_order"] = rank

    output_dir.mkdir(parents=True, exist_ok=False)
    csv_path = output_dir / "SP2L_CAPITAL_MATRIX_CROSS_LATENCY_COMPARISON.csv"
    fieldnames = list(combined[0])
    with csv_path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined)

    dual = {
        "status": "NOT_EXECUTED",
        "count": 40,
        "run_ids": sorted(EXPECTED_DUAL),
        "reason": "Current replay enforces one open/pending exposure; two independent legs are not implemented.",
    }
    report = {
        "status": "COMPLETE_COMPARISON_GROSS_ONLY",
        "research_only": True,
        "canonical": False,
        "replayed_configurations": 49,
        "dual_configurations": dual,
        "latencies": list(LATENCIES),
        "input_sha256": first["input_sha256"],
        "code_sha256": first["code_sha256"],
        "source_manifests": {
            lat: {"manifest_sha256": sha256(loaded[lat][2].parent / MANIFEST_NAME),
                  "summary_sha256": sha256(loaded[lat][2])}
            for lat in LATENCIES
        },
        "ranking_policy": {
            "scenario_ranks": "Separate descending gross/PF and ascending drawdown ranks for each latency.",
            "cross_latency_order": "Positive gross in all three scenarios first, then worst-case gross, worst-case PF, and worst-case drawdown.",
            "warning": "Descriptive robustness screen only; not the previously agreed Balanced score and not a winner selection.",
        },
        "limitations": [
            "Gross-only: commission, swap, and calibrated slippage are absent.",
            "Replay latency is an explicit assumption, not a measured historical broker latency.",
            "Broker minimum stop distance was unavailable and assumed zero for trailing placement.",
            "Validation and Fresh Holdout have not been run.",
            "40 Dual TP configurations are not executed.",
        ],
        "comparison_csv": csv_path.name,
        "comparison_csv_sha256": sha256(csv_path),
        "rows": combined,
    }
    json_path = output_dir / "SP2L_CAPITAL_MATRIX_CROSS_LATENCY_REPORT.json"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# SP2L Capital Matrix — Cross-Latency Screen",
        "",
        "**Research-only · Gross-only · Not canonical · Not a winner selection**",
        "",
        "| Rank | Configuration | Gross 0s | Gross 2s | Gross 5s | Worst gross | Worst PF | Worst DD | Positive all 3? |",
        "|---:|---|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for row in combined:
        def fmt(value, digits=2):
            return "n/a" if value is None else f"{value:.{digits}f}"
        lines.append(
            f"| {row['worst_case_gross_screen_order']} | {row['run_id']} "
            f"| {fmt(row['gross_usd_0s'])} | {fmt(row['gross_usd_2s'])} | {fmt(row['gross_usd_5s'])} "
            f"| {fmt(row['worst_case_gross_usd'])} | {fmt(row['worst_case_pf'], 3)} "
            f"| {fmt(row['worst_case_max_dd'] * 100, 2)}% | {'Yes' if row['positive_gross_all_latencies'] else 'No'} |"
        )
    lines += [
        "",
        "## Execution coverage",
        "",
        "- 49 configurations replayed: 40 Fixed TP + 1 exact Runner + 8 normalized Runner.",
        "- 40 Dual TP configurations not executed because independent two-leg exposure is not supported by this replay.",
        "- The 0s/2s/5s source manifests were checked for identical input hashes, code hashes, and broker contract metadata.",
        "",
        "## Interpretation limits",
        "",
        "- Gross-only: commission, swap, and calibrated slippage are absent.",
        "- Latency is an explicit replay assumption, not a measured historical broker latency.",
        "- Broker minimum stop distance was unavailable and assumed zero for trailing placement.",
        "- This is a descriptive robustness screen, not the agreed Balanced ranking: recovery and stability inputs are not in the replay summaries.",
        "- No configuration is promoted; chronological Validation and locked Fresh Holdout remain pending.",
        "",
        f"CSV SHA-256: `{sha256(csv_path)}`",
    ]
    (output_dir / "SP2L_CAPITAL_MATRIX_CROSS_LATENCY_REPORT.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-dir", required=True, type=Path,
                        help="Parent directory containing capital-matrix-replay-v1-{0s,2s,5s}")
    parser.add_argument("--output-dir", required=True, type=Path,
                        help="New output directory; must not already exist")
    args = parser.parse_args()
    report = build_report(args.base_dir.resolve(), args.output_dir.resolve())
    print(json.dumps({
        "status": report["status"],
        "replayed_configurations": report["replayed_configurations"],
        "dual_configurations_not_executed": report["dual_configurations"]["count"],
        "csv": str(args.output_dir / report["comparison_csv"]),
        "csv_sha256": report["comparison_csv_sha256"],
        "markdown": str(args.output_dir / "SP2L_CAPITAL_MATRIX_CROSS_LATENCY_REPORT.md"),
        "json": str(args.output_dir / "SP2L_CAPITAL_MATRIX_CROSS_LATENCY_REPORT.json"),
    }, indent=2))


if __name__ == "__main__":
    main()
