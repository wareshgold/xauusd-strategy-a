"""Analyze the persisted XAUUSD Forward-style parameter matrix.

Research-only: this script describes sensitivity and stability; it never
selects or promotes a canonical Strategy A configuration.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from itertools import product


PARAMS = ["pGap", "spikeMultiplier", "maxSL", "tpR", "pendingTtlMinutes"]


def load_rows(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("results") or data.get("rows") or []
    if isinstance(rows, dict):
        rows = list(rows.values())
    if not isinstance(rows, list) or not rows:
        raise ValueError("matrix artifact has no results/rows array")
    return rows


def f(row, key):
    v = row.get(key)
    return float(v) if v is not None else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output")
    args = ap.parse_args()
    rows = load_rows(Path(args.input))

    # Normalize likely report spellings without changing values.
    aliases = {
        "pGap": ["pGap", "p_gap", "pgap"],
        "spikeMultiplier": ["spikeMultiplier", "spike_multiplier"],
        "maxSL": ["maxSL", "max_sl"],
        "tpR": ["tpR", "tp_r"],
        "pendingTtlMinutes": ["pendingTtlMinutes", "pending_ttl_minutes", "ttl", "ttlMinutes"],
        "filled": ["filled"],
        "netR": ["netR", "net_r"],
        "wins": ["wins"],
        "losses": ["losses"],
        "expired": ["expired"],
    }
    def get(row, k):
        for a in aliases[k]:
            if a in row:
                return row[a]
        return None

    clean = []
    for r in rows:
        x = {k: get(r, k) for k in aliases}
        if any(x[k] is None for k in PARAMS + ["filled", "netR"]):
            continue
        x["filled"] = int(x["filled"])
        x["netR"] = float(x["netR"])
        x["wins"] = int(x["wins"] or 0)
        x["losses"] = int(x["losses"] or 0)
        x["expired"] = int(x["expired"] or 0)
        x["wr"] = 100.0 * x["wins"] / (x["wins"] + x["losses"]) if x["wins"] + x["losses"] else None
        clean.append(x)

    if not clean:
        raise ValueError("no analyzable rows after schema normalization")

    def group(keys):
        out = []
        groups = {}
        for r in clean:
            key = tuple(r[k] for k in keys)
            groups.setdefault(key, []).append(r)
        for key, rs in sorted(groups.items(), key=lambda kv: str(kv[0])):
            out.append({
                "params": dict(zip(keys, key)),
                "n": len(rs),
                "mean_netR": sum(r["netR"] for r in rs) / len(rs),
                "median_netR": sorted(r["netR"] for r in rs)[len(rs)//2],
                "positive_share": sum(r["netR"] > 0 for r in rs) / len(rs),
                "mean_filled": sum(r["filled"] for r in rs) / len(rs),
            })
        return out

    # A stability score is deliberately descriptive, not a ranking for promotion:
    # local-neighborhood support = share of one-step parameter neighbors that are
    # positive. Only direct grid neighbors are used.
    grid = {k: sorted({r[k] for r in clean}) for k in PARAMS}
    by_key = {tuple(r[k] for k in PARAMS): r for r in clean}
    stability = []
    for r in clean:
        neighbors = []
        for k in PARAMS:
            vals = grid[k]
            i = vals.index(r[k])
            for j in (i - 1, i + 1):
                if 0 <= j < len(vals):
                    key = tuple(r[q] if q != k else vals[j] for q in PARAMS)
                    if key in by_key:
                        neighbors.append(by_key[key])
        stability.append({
            **{k: r[k] for k in PARAMS},
            "netR": r["netR"],
            "filled": r["filled"],
            "wr": r["wr"],
            "neighbor_count": len(neighbors),
            "positive_neighbor_share": (
                sum(n["netR"] > 0 for n in neighbors) / len(neighbors)
                if neighbors else None
            ),
            "neighbor_mean_netR": (
                sum(n["netR"] for n in neighbors) / len(neighbors)
                if neighbors else None
            ),
        })

    stability.sort(key=lambda x: (
        -(x["positive_neighbor_share"] or 0),
        -(x["neighbor_mean_netR"] or -1e99),
        -x["filled"],
    ))

    report = {
        "status": "COMPLETE",
        "research_only": True,
        "rows_input": len(rows),
        "rows_analyzed": len(clean),
        "parameter_levels": {k: grid[k] for k in PARAMS},
        "global": {
            "mean_netR": sum(r["netR"] for r in clean) / len(clean),
            "median_netR": sorted(r["netR"] for r in clean)[len(clean)//2],
            "positive_share": sum(r["netR"] > 0 for r in clean) / len(clean),
            "mean_filled": sum(r["filled"] for r in clean) / len(clean),
        },
        "marginal_sensitivity": {k: group([k]) for k in PARAMS},
        "pair_sensitivity": {
            f"{a}+{b}": group([a, b])
            for a, b in product(PARAMS, PARAMS)
            if PARAMS.index(a) < PARAMS.index(b)
        },
        "stable_regions_descriptive": stability[:30],
        "interpretation_guard": [
            "No row is a canonical recommendation.",
            "Positive isolated peaks are not promotion evidence.",
            "Candidate regions require source compatibility and untouched validation.",
            "This matrix uses the current research Forward-style execution approximation."
        ],
    }
    out = Path(args.output) if args.output else Path(args.input).with_name(
        Path(args.input).stem + "_ANALYSIS.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "rows_analyzed": report["rows_analyzed"],
        "output": str(out),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
