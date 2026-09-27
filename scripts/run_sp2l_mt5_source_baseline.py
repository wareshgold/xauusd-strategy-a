"""Single-contract MT5 source-baseline replay for XAUUSD.

Research only. This wrapper deliberately delegates geometry/outcome mechanics to
the frozen V2 research runner while recording an immutable baseline identity.
It is a provenance wrapper, not a new Strategy A definition.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_sp2l_mt5_local_multi_symbol_backtest.py"
BASELINE_DOC = ROOT / "docs" / "research" / "SP2L_MT5_SOURCE_BASELINE_LOCK_20260927.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2026-09-14T00:00:00Z")
    parser.add_argument("--end", default="2026-09-25T23:59:59Z")
    parser.add_argument("--mt5-path", default=None)
    args = parser.parse_args()

    cmd = [
        sys.executable,
        str(RUNNER),
        "--start", args.start,
        "--end", args.end,
        "--symbols", "XAUUSD",
    ]
    if args.mt5_path:
        cmd += ["--mt5-path", args.mt5_path]

    print("[BASELINE] Single-symbol XAUUSD MT5 replay")
    print(f"[BASELINE] contract_sha256={sha256_file(BASELINE_DOC)}")
    print(f"[BASELINE] runner_sha256={sha256_file(RUNNER)}")
    print("[BASELINE] config: p_gap=1.0 spike=1.5 max_sl=10 tp=1R session=OFF 2X=OFF")
    print("[BASELINE] NOTE: current shared runner may still apply its own env defaults.")
    print("[BASELINE] This wrapper is a provenance checkpoint, not canonical geometry.")

    import os
    env = os.environ.copy()
    env.update({
        "SP2L_P_GAP_PRICE": "1.0",
        "SP2L_SPIKE_MULTIPLIER": "1.5",
        "SP2L_MAX_SL_DISTANCE": "10.0",
        "SP2L_TP_R": "1.0",
        "SP2L_SESSION_FILTER_ENABLED": "false",
    })

    return subprocess.call(cmd, cwd=ROOT, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
