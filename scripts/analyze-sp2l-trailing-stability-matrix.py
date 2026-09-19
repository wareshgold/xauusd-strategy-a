#!/usr/bin/env python3
"""Research-only trailing-SL stability matrix for 5/10/15/20 pip variants.

Runs the existing M1-safe trailing-SL methodology on the same frozen
2026-09-14..2026-09-18 candle evidence. No TP extension is simulated.
No Strategy A rule or parameter is promoted.
"""
from __future__ import annotations
import argparse, hashlib, json, importlib.util
from pathlib import Path

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_engine():
    path = Path("scripts/analyze-sp2l-trailing-10pip-management-m1safe.py")
    spec = importlib.util.spec_from_file_location("sp2l_trailing_m1safe", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load M1-safe trailing engine")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candle-evidence", default="artifacts/SP2L_candle_level_evidence_2026-09-14_2026-09-18.json")
    ap.add_argument("--trail-pips", nargs="+", type=float, default=[5.0, 10.0, 15.0, 20.0])
    ap.add_argument("--output", default="artifacts/SP2L_trailing_stability_matrix_5_10_15_20pip_2026-09-14_2026-09-18.json")
    args = ap.parse_args()

    cp = Path(args.candle_evidence)
    evidence = json.loads(cp.read_text(encoding="utf-8"))
    engine = load_engine()

    variants = []
    for trail in args.trail_pips:
        rows = [engine.simulate(m, evidence["candles"], trail) for m in evidence["signal_mappings"]]
        summary = engine.summarize(rows)
        variants.append({"trail_pips": trail, "summary": summary})

    result = {
        "research_only": True,
        "experiment": "TRAILING_SL_STABILITY_MATRIX",
        "canonicalization_guard": "RESEARCH_ONLY; NO_STRATEGY_RULE_OR_PARAMETER_PROMOTION",
        "frozen_window_utc": "2026-09-14T00:00:00Z/2026-09-18T23:59:59Z",
        "method": {
            "source_engine": "scripts/analyze-sp2l-trailing-10pip-management-m1safe.py",
            "tp_policy": "FIXED_INITIAL_TP",
            "tp_extension": "NOT_SIMULATED_FROM_M1_OHLC; REQUIRES_INTRABAR_ORDER",
            "same_bar_policy": "AMBIGUOUS_WHEN_SL_AND_TP_BOTH_TOUCHED",
            "pip_size_price_units": 0.10
        },
        "input_sha256": sha256_file(cp),
        "variants": variants
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "ANALYZED",
        "output": str(out),
        "input_sha256": result["input_sha256"],
        "variants": [
            {
                "trail_pips": v["trail_pips"],
                "net_pips": v["summary"]["net_pips"],
                "max_drawdown_pips": v["summary"]["max_drawdown_pips"],
                "win_rate_decisive_pct": v["summary"]["win_rate_decisive_pct"],
                "profit_factor": v["summary"]["profit_factor"],
                "avg_win_pips": v["summary"]["avg_win_pips"],
                "avg_loss_pips_abs": v["summary"]["avg_loss_pips_abs"],
                "trailing_activated_count": v["summary"]["trailing_activated_count"],
                "ambiguous": v["summary"]["ambiguous"]
            }
            for v in variants
        ]
    }, indent=2))

if __name__ == "__main__":
    main()
