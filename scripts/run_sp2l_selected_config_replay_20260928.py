"""Run the previously selected research configs independently for XAU/EUR/USDJPY."""
from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/research/SP2L_SELECTED_CONFIG_XAU_EUR_USDJPY_20260928.json"
REPLAY = ROOT / "scripts/run_sp2l_mt5_local_multi_symbol_backtest.py"
OUT_DIR = ROOT / "artifacts/backtest-selected-20260928"

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--mt5-path", required=True)
    args = p.parse_args()
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for symbol, values in cfg["symbols"].items():
        env = os.environ.copy()
        env.update({
            "SP2L_P_GAP_PRICE": str(values["pGapPrice"]),
            "SP2L_SPIKE_MULTIPLIER": str(values["spikeMultiplier"]),
            "SP2L_MAX_SL_DISTANCE": str(values["maxSlDistance"]),
            "SP2L_TP_R": str(cfg["tpR"]),
        })
        before = {p.name for p in (ROOT / "artifacts/backtest-mt5-local").glob("SP2L_MT5_LOCAL_MULTI_SYMBOL_*.json")}
        cmd = [sys.executable, str(REPLAY), "--start", args.start, "--end", args.end,
               "--symbols", symbol.split(".", 1)[0], "--mt5-path", args.mt5_path]
        print(f"RUN {symbol}: pGap={values['pGapPrice']} spike={values['spikeMultiplier']} maxSL={values['maxSlDistance']} tpR={cfg['tpR']}", flush=True)
        rc = subprocess.run(cmd, env=env).returncode
        if rc != 0:
            return rc
        after = [p for p in (ROOT / "artifacts/backtest-mt5-local").glob("SP2L_MT5_LOCAL_MULTI_SYMBOL_*.json") if p.name not in before]
        if not after:
            raise RuntimeError(f"Replay completed but report was not found for {symbol}")
        report = max(after, key=lambda p: p.stat().st_mtime)
        results.append({"symbol": symbol, "config": values, "report": str(report)})
    summary = OUT_DIR / "SELECTED_CONFIG_REPLAY_SUMMARY.json"
    summary.write_text(json.dumps({
        "status": "COMPLETE", "research_only": True, "canonical": False,
        "config_file": str(CONFIG), "start": args.start, "end": args.end, "results": results
    }, indent=2), encoding="utf-8")
    print(f"SUMMARY={summary}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
