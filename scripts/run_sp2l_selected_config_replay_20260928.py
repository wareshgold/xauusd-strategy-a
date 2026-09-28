"""Replay the previously selected SP2L research configs for XAU/EUR/USDJPY.

Research-only wrapper. It does not optimize or choose parameters.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


CONFIG = Path(__file__).resolve().parents[1] / "configs" / "research" / "SP2L_SELECTED_CONFIG_XAU_EUR_USDJPY_20260928.json"
REPLAY = Path(__file__).resolve().parent / "run_sp2l_mt5_local_multi_symbol_backtest.py"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--mt5-path", required=True)
    p.add_argument("--output-dir", default="artifacts/backtest-selected-20260928")
    args = p.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for symbol, values in cfg["symbols"].items():
        env = os.environ.copy()
        env["SP2L_P_GAP_PRICE"] = str(values["pGapPrice"])
        env["SP2L_SPIKE_MULTIPLIER"] = str(values["spikeMultiplier"])
        env["SP2L_MAX_SL_DISTANCE"] = str(values["maxSlDistance"])
        env["SP2L_TP_R"] = str(cfg["tpR"])
        out = out_dir / f"{symbol.replace('.', '_')}_REPLAY.json"

        cmd = [
            sys.executable, str(REPLAY),
            "--start", args.start,
            "--end", args.end,
            "--symbols", symbol.split(".", 1)[0],
            "--mt5-path", args.mt5_path,
            "--output", str(out),
        ]
        print(f"RUN {symbol}: pGap={values['pGapPrice']} spike={values['spikeMultiplier']} "
              f"maxSL={values['maxSlDistance']} tpR={cfg['tpR']}")
        completed = subprocess.run(cmd, env=env)
        if completed.returncode != 0:
            return completed.returncode
        results.append({"symbol": symbol, "config": values, "output": str(out)})

    summary = out_dir / "SELECTED_CONFIG_REPLAY_SUMMARY.json"
    summary.write_text(json.dumps({
        "status": "COMPLETE",
        "research_only": True,
        "canonical": False,
        "config_file": str(CONFIG),
        "start": args.start,
        "end": args.end,
        "results": results,
    }, indent=2), encoding="utf-8")
    print(f"SUMMARY={summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
