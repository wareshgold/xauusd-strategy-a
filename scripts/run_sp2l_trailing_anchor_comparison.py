from __future__ import annotations

"""Canonical offline comparison of candle vs cumulative trailing anchors.

Uses the frozen M1/entry population loader and the canonical management replay
engine. No MT5 access, no signal rebuild, no broker-side fill simulation.
"""
import argparse
import csv
import hashlib
import json
import math
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import run_sp2l_v3_unified_management_matrix as matrix_loader
import strategy_factory.v3_management_engine as management_engine
from run_sp2l_v3_unified_management_matrix import load, summary, sha
from strategy_factory.v3_management_engine import (
    fixed_price_trailing_spec, replay_management_trade,
)

def _git(root: Path, *args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=root, stderr=subprocess.STDOUT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def execution_provenance(argv: list[str]) -> dict:
    """Capture source identity and worktree state before any replay begins."""
    script = Path(__file__).resolve()
    root_text = _git(script.parent.parent, "rev-parse", "--show-toplevel")
    root = Path(root_text).resolve() if root_text else script.parent.parent
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    diff = _git(root, "diff", "--binary", "HEAD")
    sources = {
        "comparison_runner": script,
        "matrix_loader": Path(matrix_loader.__file__).resolve(),
        "management_engine": Path(management_engine.__file__).resolve(),
    }
    source_hashes = {}
    for name, source in sources.items():
        source_hashes[name] = {
            "path": str(source),
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        }
    return {
        "git_root": str(root),
        "git_head": _git(root, "rev-parse", "HEAD"),
        "git_branch": _git(root, "branch", "--show-current"),
        "git_status_porcelain": status,
        "git_worktree_dirty": bool(status),
        "git_diff_head_sha256": hashlib.sha256((diff or "").encode()).hexdigest(),
        "source_files": source_hashes,
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "argv": list(argv),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("x", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--m1-csv", required=True)
    p.add_argument("--entry-csv", required=True)
    p.add_argument("--point", type=float, default=0.01)
    p.add_argument("--contract-size", type=float, default=100.0)
    p.add_argument("--volume", type=float, default=0.01)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--activation-price", type=float, default=0.40)
    p.add_argument("--distance-price", type=float, default=0.40)
    a = p.parse_args()
    if not all(math.isfinite(x) and x > 0 for x in
               (a.point, a.contract_size, a.volume, a.activation_price, a.distance_price)):
        raise ValueError("all numeric parameters must be finite and positive")
    out = Path(a.output_dir).resolve()
    if out.exists():
        raise FileExistsError(f"refusing overwrite: {out}")
    provenance = execution_provenance(sys.argv)
    bars, population, inputs = load(Path(a.m1_csv).resolve(), Path(a.entry_csv).resolve())
    profiles = [
        ("RR4_CANDLE", "CANDLE", 4.0),
        ("RR4_CUMULATIVE", "CUMULATIVE", 4.0),
        ("NO_TP_CANDLE", "CANDLE", None),
        ("NO_TP_CUMULATIVE", "CUMULATIVE", None),
    ]
    summaries, trades = [], []
    for name, anchor, rr in profiles:
        rows = []
        for index, candidate in enumerate(population):
            spec = fixed_price_trailing_spec(
                activation_price=a.activation_price,
                distance_price=a.distance_price,
                risk=float(candidate["risk"]),
                anchor_mode=anchor,
                rr=rr,
            )
            row = replay_management_trade(
                candidate, bars, spec, mt5_point=a.point,
                contract_size=a.contract_size, volume=a.volume,
            )
            row.update(population_index=index, variant=name, anchor_mode=anchor)
            rows.append(row)
        sm = summary(rows)
        sm.update(variant=name, anchor_mode=anchor, rr=rr,
                  activation_price=a.activation_price, distance_price=a.distance_price)
        summaries.append(sm)
        trades.extend(rows)
        print(f"PROFILE_COMPLETE={name} decisive={sm['decisive']} ambiguous={sm['ambiguous']} "
              f"open={sm['open_unresolved']} updates={sum(x['trailing_updates'] for x in rows)}",
              flush=True)

    by_key = {(x["population_index"], x["variant"]): x for x in trades}
    paired = []
    for i in range(len(population)):
        for prefix in ("RR4", "NO_TP"):
            left, right = by_key[(i, prefix + "_CANDLE")], by_key[(i, prefix + "_CUMULATIVE")]
            paired.append({
                "population_index": i, "management": prefix,
                "candle_reason": left["reason"], "cumulative_reason": right["reason"],
                "candle_R": left["realized_R"], "cumulative_R": right["realized_R"],
                "delta_R_cumulative_minus_candle": (
                    right["realized_R"] - left["realized_R"]
                    if left["realized_R"] is not None and right["realized_R"] is not None else None
                ),
                "outcome_changed": (
                    left["reason"], left["ambiguous"], left["realized_R"]
                ) != (
                    right["reason"], right["ambiguous"], right["realized_R"]
                ),
                "candle_updates": left["trailing_updates"],
                "cumulative_updates": right["trailing_updates"],
                "candle_deferred": left["deferred_trailing_updates"],
                "cumulative_deferred": right["deferred_trailing_updates"],
            })

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out.mkdir(parents=True, exist_ok=False)
    sp, tp, pp = out / "SUMMARY.csv", out / "TRADES.csv", out / "PAIRED.csv"
    mp = out / "MANIFEST.json"
    write_csv(sp, summaries)
    write_csv(tp, trades)
    write_csv(pp, paired)
    manifest = {
        "research_only": True, "canonical": False, "mt5_accessed": False,
        "signal_rebuild": False, "created_utc": stamp,
        "profile_count": len(profiles), "population_count": len(population),
        "trade_replays": len(trades), "paired_comparisons": len(paired),
        "parameters": {"activation_price": a.activation_price,
                       "distance_price": a.distance_price, "point": a.point,
                       "contract_size": a.contract_size, "volume": a.volume},
        "inputs": inputs,
        "execution_provenance": provenance,
        "execution": {"spread_commission_slippage": "NOT_MODELED",
                      "broker_stop_freeze_levels": "NOT_MODELED",
                      "entry_bar": "EXCLUDED", "stop_update": "NEXT_BAR",
                      "same_bar_sl_tp": "AMBIGUOUS", "m1_gap": "CANONICAL_GAP_DETECTION"},
        "semantics": {
            "CANDLE": "current completed candle high/low anchor",
            "CUMULATIVE": "best favorable high/low since entry",
            "validity": "same close-side validity test in canonical engine",
            "activation": "fixed price converted to per-trade R by activation_price/risk",
            "distance": "fixed price converted to per-trade R by distance_price/risk",
        },
        "summary": summaries,
        "paired_changed_outcomes": {
            "RR4": sum(x["outcome_changed"] for x in paired if x["management"] == "RR4"),
            "NO_TP": sum(x["outcome_changed"] for x in paired if x["management"] == "NO_TP"),
        },
        "artifacts": {},
    }
    for path in (sp, tp, pp):
        manifest["artifacts"][path.name] = {"sha256": sha(path), "bytes": path.stat().st_size}
    mp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sums = out / "SHA256SUMS.txt"
    with sums.open("x", encoding="utf-8") as f:
        for path in (sp, tp, pp, mp):
            f.write(f"{sha(path)}  {path.name}\n")
    print(json.dumps({
        "status": "COMPLETE", "output_dir": str(out),
        "profiles": summaries,
        "paired_changed_outcomes": manifest["paired_changed_outcomes"],
        "artifacts": manifest["artifacts"],
        "manifest_sha256": sha(mp), "research_only": True, "mt5_accessed": False,
    }, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
