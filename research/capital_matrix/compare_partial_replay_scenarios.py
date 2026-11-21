"""Cross-latency comparator for the 27 partial-close replay variants.
Research-only; no replay, MT5 access, or runner changes. Leg and trade metrics stay separate.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
from research.capital_matrix.partial_matrix import build_partial_matrix

LATENCIES = ("0s", "2s", "5s")
SUMMARY = "SP2L_PARTIAL_MATRIX_RUN_SUMMARY.csv"
DETAIL = "SP2L_PARTIAL_MATRIX_TRADE_REPLAY.csv"
MANIFEST = "SP2L_PARTIAL_MATRIX_REPLAY_MANIFEST.json"
EXPECTED = {x.run_id for x in build_partial_matrix()}

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def number(row, key):
    value = row.get(key, "")
    return None if value in ("", "None", "null") else float(value)

def read_latency(base, latency):
    folder = base / f"partial-matrix-replay-v1-{latency}"
    paths = {n: folder / n for n in (SUMMARY, DETAIL, MANIFEST)}
    for p in paths.values():
        if not p.is_file():
            raise FileNotFoundError(f"Missing {p}")
    manifest = json.loads(paths[MANIFEST].read_text(encoding="utf-8"))
    if manifest.get("status") != "COMPLETE_GROSS_ONLY":
        raise ValueError(f"{latency}: incomplete status")
    if manifest.get("research_only") is not True or manifest.get("canonical") is not False:
        raise ValueError(f"{latency}: research/canonical flags invalid")
    if manifest.get("mt5_accessed") is not False or manifest.get("runner_accessed") is not False:
        raise ValueError(f"{latency}: MT5/Runner access flag invalid")
    if manifest.get("execution_assumptions", {}).get("latency_seconds") != int(latency[:-1]):
        raise ValueError(f"{latency}: latency mismatch")
    if manifest.get("partial_matrix_runs") != 27 or manifest.get("population_rows") != 1518:
        raise ValueError(f"{latency}: run/population count mismatch")
    expected_hashes = manifest.get("output_sha256", {})
    for name in (SUMMARY, DETAIL):
        if expected_hashes.get(name) != sha(paths[name]):
            raise ValueError(f"{latency}: output SHA mismatch for {name}")
    with paths[SUMMARY].open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    by_id = {r["run_id"]: r for r in rows}
    if len(rows) != 27 or set(by_id) != EXPECTED:
        raise ValueError(f"{latency}: expected exact 27 run IDs")
    for rid, row in by_id.items():
        counts = json.loads(row["counts"])
        final_legs = int(counts.get("FILLED_AND_CLOSED", 0))
        partial_legs = int(counts.get("PARTIAL_LEG_CLOSED", 0))
        if int(row["closed_trades"]) != final_legs:
            raise ValueError(f"{latency}/{rid}: closed_trades mismatch")
        if int(row["closed_legs"]) != final_legs + partial_legs:
            raise ValueError(f"{latency}/{rid}: closed_legs mismatch")
        if row.get("cost_status") != "GROSS_ONLY_COMMISSION_SWAP_SLIPPAGE_NOT_INCLUDED":
            raise ValueError(f"{latency}/{rid}: unexpected cost status")
        for field in ("gross_net_usd", "max_drawdown_fraction", "ending_equity_gross"):
            if row.get(field, "") == "":
                raise ValueError(f"{latency}/{rid}: missing {field}")
    return by_id, manifest, paths

def rank_map(rows, metric, descending):
    def key(rid):
        v = number(rows[rid], metric)
        return (v is None, (-(v or 0) if descending else (v if v is not None else 0)), rid)
    return {rid: i for i, rid in enumerate(sorted(rows, key=key), 1)}

def build_report(base, output):
    loaded = {lat: read_latency(base, lat) for lat in LATENCIES}
    first = loaded["0s"][1]
    for lat in ("2s", "5s"):
        m = loaded[lat][1]
        for field in ("input_sha256", "code_sha256", "broker_contract"):
            if m.get(field) != first.get(field):
                raise ValueError(f"{lat}: {field} differs from 0s")
    ranks = {}
    for lat in LATENCIES:
        rows = loaded[lat][0]
        ranks[lat] = {
            "gross": rank_map(rows, "gross_net_usd", True),
            "pf": rank_map(rows, "profit_factor", True),
            "dd": rank_map(rows, "max_drawdown_fraction", False),
        }
    combined = []
    for rid in sorted(EXPECTED):
        item = {"run_id": rid}
        for lat in LATENCIES:
            row = loaded[lat][0][rid]
            s = lat[:-1]
            counts = json.loads(row["counts"])
            item.update({
                f"closed_trades_{s}s": int(row["closed_trades"]),
                f"closed_legs_{s}s": int(row["closed_legs"]),
                f"gross_usd_{s}s": number(row, "gross_net_usd"),
                f"pf_{s}s": number(row, "profit_factor"),
                f"win_rate_leg_{s}s": number(row, "win_rate"),
                f"average_r_leg_{s}s": number(row, "average_r"),
                f"max_dd_{s}s": number(row, "max_drawdown_fraction"),
                f"ending_equity_{s}s": number(row, "ending_equity_gross"),
                f"ambiguous_{s}s": int(counts.get("AMBIGUOUS_DATA", 0)),
                f"rank_gross_{s}s": ranks[lat]["gross"][rid],
                f"rank_pf_{s}s": ranks[lat]["pf"][rid],
                f"rank_dd_{s}s": ranks[lat]["dd"][rid],
            })
        gross = [item[f"gross_usd_{lat[:-1]}s"] for lat in LATENCIES]
        pfs = [item[f"pf_{lat[:-1]}s"] for lat in LATENCIES]
        dds = [item[f"max_dd_{lat[:-1]}s"] for lat in LATENCIES]
        item["worst_case_gross_usd"] = min(gross)
        item["worst_case_pf"] = min((x for x in pfs if x is not None), default=None)
        item["worst_case_max_dd"] = max(dds)
        item["positive_gross_all_latencies"] = all(x > 0 for x in gross)
        for metric in ("gross", "pf", "dd"):
            item[f"rank_{metric}_mean"] = sum(item[f"rank_{metric}_{lat[:-1]}s"] for lat in LATENCIES) / 3
        combined.append(item)
    combined.sort(key=lambda x: (
        not x["positive_gross_all_latencies"], -x["worst_case_gross_usd"],
        -(x["worst_case_pf"] if x["worst_case_pf"] is not None else -1),
        x["worst_case_max_dd"], x["run_id"]))
    for i, row in enumerate(combined, 1):
        row["worst_case_gross_screen_order"] = i
    output.mkdir(parents=True, exist_ok=False)
    csv_path = output / "SP2L_PARTIAL_MATRIX_CROSS_LATENCY_COMPARISON.csv"
    with csv_path.open("x", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(combined[0]))
        w.writeheader()
        w.writerows(combined)
    source_hashes = {lat: {name: sha(path) for name, path in loaded[lat][2].items()} for lat in LATENCIES}
    report = {
        "status": "COMPLETE_PARTIAL_CROSS_LATENCY_COMPARISON_GROSS_ONLY",
        "research_only": True, "canonical": False, "configurations": 27,
        "latencies": list(LATENCIES), "input_sha256": first["input_sha256"],
        "code_sha256": first["code_sha256"], "source_file_sha256": source_hashes,
        "metric_semantics": {
            "closed_trades": "FILLED_AND_CLOSED final trade rows",
            "closed_legs": "PARTIAL_LEG_CLOSED plus FILLED_AND_CLOSED rows",
            "win_rate_leg": "Leg-level win rate, not trade-level",
            "average_r_leg": "Mean per-leg R, not trade-level R",
            "gross_net_usd": "Realized gross PnL summed across closed legs"},
        "ranking_policy": "Descriptive screen: positive gross all latencies, then worst-case gross, PF and drawdown. Not a winner selection.",
        "limitations": [
            "Gross-only; commission, swap and calibrated slippage absent.",
            "Latency is an assumed replay parameter, not measured historical broker latency.",
            "Broker minimum stop distance unavailable; trailing assumes zero.",
            "Win rate and average R are leg-level, not trade-level.",
            "No chronological validation or locked Fresh Holdout."],
        "comparison_csv": csv_path.name, "comparison_csv_sha256": sha(csv_path),
        "rows": combined}
    (output / "SP2L_PARTIAL_MATRIX_CROSS_LATENCY_REPORT.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    def fmt(v, n=2):
        return "n/a" if v is None else f"{v:.{n}f}"
    lines = [
        "# SP2L Partial-Close Matrix — Cross-Latency Comparison", "",
        "**Research-only · Gross-only · Not canonical · 27 configurations**", "",
        "| Rank | Configuration | Trades 0s/2s/5s | Legs 0s/2s/5s | Gross 0s | Gross 2s | Gross 5s | Worst gross | Worst PF | Worst DD |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in combined:
        lines.append(
            f"| {r['worst_case_gross_screen_order']} | {r['run_id']} "
            f"| {r['closed_trades_0s']}/{r['closed_trades_2s']}/{r['closed_trades_5s']} "
            f"| {r['closed_legs_0s']}/{r['closed_legs_2s']}/{r['closed_legs_5s']} "
            f"| {fmt(r['gross_usd_0s'])} | {fmt(r['gross_usd_2s'])} | {fmt(r['gross_usd_5s'])} "
            f"| {fmt(r['worst_case_gross_usd'])} | {fmt(r['worst_case_pf'], 3)} "
            f"| {fmt(r['worst_case_max_dd'] * 100)}% |")
    lines += ["", "## Interpretation", "",
        "- Trade and leg counts are separate; TP1 and remainder legs belong to one trade.",
        "- Win rate and average R are leg-level metrics.",
        "- All results are gross-only; no model is promoted or selected.",
        "", f"CSV SHA-256: {sha(csv_path)}"]
    (output / "SP2L_PARTIAL_MATRIX_CROSS_LATENCY_REPORT.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    return report

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base-dir", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    report = build_report(args.base_dir.resolve(), args.output_dir.resolve())
    print(json.dumps({
        "status": report["status"], "configurations": report["configurations"],
        "csv": str(args.output_dir / report["comparison_csv"]),
        "csv_sha256": report["comparison_csv_sha256"],
        "markdown": str(args.output_dir / "SP2L_PARTIAL_MATRIX_CROSS_LATENCY_REPORT.md"),
        "json": str(args.output_dir / "SP2L_PARTIAL_MATRIX_CROSS_LATENCY_REPORT.json")},
        indent=2))

if __name__ == "__main__":
    main()
