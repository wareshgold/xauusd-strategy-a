from __future__ import annotations

"""SP2L discovery -> chronological sub-window stability matrix.

Research-only. This tool consumes an already-produced controlled discovery
JSON and does not create signals, change geometry, alter the forward runner,
or authorize production.

Each variant is evaluated over independent chronological segments of the
same discovery trade population. Ambiguous trades remain excluded exactly as
they were in the discovery artifact.
"""

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path


def parse_ts(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def segment_bounds(times: list[int], count: int) -> list[tuple[int, int]]:
    if count < 2:
        raise ValueError("--segments must be >= 2")
    if len(times) < count:
        raise ValueError("not enough trades for requested segment count")
    ordered = sorted(times)
    bounds = []
    n = len(ordered)
    for i in range(count):
        lo = ordered[(i * n) // count]
        hi = ordered[((i + 1) * n) // count - 1]
        bounds.append((lo, hi))
    return bounds


def metrics(rows: list[dict]) -> dict:
    decisive = [
        r for r in rows
        if not r.get("ambiguous") and r.get("realized_R") is not None
    ]
    rs = [float(r["realized_R"]) for r in decisive]
    wins = [r for r in rs if r > 0]
    losses = [r for r in rs if r < 0]
    gp = sum(wins)
    gl = abs(sum(losses))
    equity = peak = dd = 0.0
    for r in rs:
        equity += r
        peak = max(peak, equity)
        dd = max(dd, peak - equity)
    return {
        "signals": len(rows),
        "decisive": len(decisive),
        "wins": len(wins),
        "losses": len(losses),
        "ambiguous": len(rows) - len(decisive),
        "win_rate_pct": 100.0 * len(wins) / len(decisive) if decisive else None,
        "net_R": sum(rs),
        "profit_factor": gp / gl if gl else None,
        "max_drawdown_R": dd,
        "avg_R": sum(rs) / len(rs) if rs else None,
    }


def stability_summary(segment_metrics: list[dict]) -> dict:
    net = [m["net_R"] for m in segment_metrics]
    pf = [m["profit_factor"] for m in segment_metrics if m["profit_factor"] is not None]
    wr = [m["win_rate_pct"] for m in segment_metrics if m["win_rate_pct"] is not None]
    return {
        "segments": len(segment_metrics),
        "profitable_segments": sum(1 for x in net if x > 0),
        "nonnegative_segments": sum(1 for x in net if x >= 0),
        "min_segment_net_R": min(net),
        "max_segment_net_R": max(net),
        "segment_net_R_range": max(net) - min(net),
        "mean_segment_net_R": sum(net) / len(net),
        "min_segment_pf": min(pf) if pf else None,
        "min_segment_win_rate_pct": min(wr) if wr else None,
    }


def candidate_key(row: dict) -> tuple:
    """Research-only deterministic ordering; never a production rule."""
    s = row["stability"]
    pf = row["overall"]["profit_factor"]
    return (
        row["overall"]["net_R"],
        s["profitable_segments"],
        s["min_segment_net_R"],
        pf if pf is not None else -math.inf,
        -s["segment_net_R_range"],
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--segments", type=int, default=3)
    ap.add_argument("--output-dir", default=None)
    args = ap.parse_args()

    source = Path(args.input).resolve()
    payload = json.loads(source.read_text(encoding="utf-8"))
    trades = payload.get("trades") or []
    if not trades:
        raise ValueError("discovery JSON contains no trades")

    usable = [
        r for r in trades
        if r.get("trigger_time") is not None
        and r.get("variant")
    ]
    times = [int(r["trigger_time"]) for r in usable]
    bounds = segment_bounds(times, args.segments)

    by_variant: dict[str, list[dict]] = {}
    for row in usable:
        by_variant.setdefault(str(row["variant"]), []).append(row)

    results = []
    for variant, rows in sorted(by_variant.items()):
        segments = []
        for idx, (lo, hi) in enumerate(bounds, 1):
            part = [r for r in rows if lo <= int(r["trigger_time"]) <= hi]
            m = metrics(part)
            segments.append({
                "segment": idx,
                "start_utc": datetime.fromtimestamp(lo, timezone.utc).isoformat(),
                "end_utc": datetime.fromtimestamp(hi, timezone.utc).isoformat(),
                **m,
            })
        overall = metrics(rows)
        stability = stability_summary(segments)
        results.append({
            "variant": variant,
            "overall": overall,
            "stability": stability,
            "segments": segments,
        })

    ranked = sorted(results, key=candidate_key, reverse=True)

    output_dir = Path(args.output_dir).resolve() if args.output_dir else source.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = output_dir / f"SP2L_V3_STABILITY_MATRIX_{stamp}"

    result = {
        "version": "SP2L_V3_STABILITY_MATRIX_20261007",
        "research_only": True,
        "source_discovery": str(source),
        "source_window": payload.get("window_utc"),
        "source_population": payload.get("frozen_population"),
        "segment_policy": {
            "type": "CHRONOLOGICAL_EQUAL_TRADE_COUNT",
            "segments": args.segments,
            "boundaries_are_descriptive": True,
        },
        "candidate_count": len(results),
        "matrix": ranked,
        "ranking_policy": (
            "research-only: overall net_R, profitable segment count, "
            "minimum segment net_R, overall PF, lower segment net_R range"
        ),
        "governance": {
            "canonical": False,
            "production_eligible": False,
            "source_meaning_unchanged": True,
            "forward_runner_modified": False,
        },
    }

    json_path = base.with_suffix(".json")
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    fields = [
        "variant", "net_R", "profit_factor", "max_drawdown_R",
        "win_rate_pct", "profitable_segments", "nonnegative_segments",
        "min_segment_net_R", "max_segment_net_R", "segment_net_R_range",
        "mean_segment_net_R", "min_segment_pf", "min_segment_win_rate_pct",
    ]
    csv_path = base.with_suffix(".csv")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in ranked:
            s = row["stability"]
            o = row["overall"]
            w.writerow({
                "variant": row["variant"],
                "net_R": o["net_R"],
                "profit_factor": o["profit_factor"],
                "max_drawdown_R": o["max_drawdown_R"],
                "win_rate_pct": o["win_rate_pct"],
                **s,
            })

    snapshot_path = base.with_name(base.name + "_SNAPSHOT.md")
    lines = [
        "# SP2L Stability / Sub-window Validation Snapshot",
        "",
        "Research-only. No canonical rule or production decision is created.",
        f"Source discovery: {source}",
        f"Source window: {payload.get('window_utc')}",
        f"Variants evaluated: {len(results)}",
        f"Chronological segments: {args.segments}",
        "",
        "Candidate view is descriptive only and orders variants by overall",
        "performance plus cross-segment stability. It is not a production gate.",
        "",
        "Top 15 research candidates:",
    ]
    for i, row in enumerate(ranked[:15], 1):
        o, s = row["overall"], row["stability"]
        lines.append(
            f"{i}. {row['variant']} | netR={o['net_R']:.3f} | "
            f"PF={o['profit_factor']} | WR={o['win_rate_pct']}% | "
            f"DD={o['max_drawdown_R']:.3f}R | "
            f"profitable_segments={s['profitable_segments']}/{s['segments']} | "
            f"min_segment_R={s['min_segment_net_R']:.3f} | "
            f"range={s['segment_net_R_range']:.3f}"
        )
    lines += [
        "",
        "Governance:",
        "- source meaning unchanged;",
        "- ambiguous trades remain excluded from decisive statistics;",
        "- no holdout data is used by this tool;",
        "- forward runner is not modified;",
        "- no BUY/SELL decision is generated;",
        "- candidates must still pass untouched validation and fresh holdout.",
    ]
    snapshot_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "COMPLETE",
        "source": str(source),
        "segments": args.segments,
        "variants": len(results),
        "json": str(json_path),
        "csv": str(csv_path),
        "snapshot": str(snapshot_path),
        "top5": ranked[:5],
    }, indent=2))


if __name__ == "__main__":
    main()
