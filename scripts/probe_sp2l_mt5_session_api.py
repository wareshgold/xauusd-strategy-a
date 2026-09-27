"""Probe MT5 Python session-window API for the SP2L research symbols.

Research-only. This records what the connected Python package actually exposes.
It does not infer session windows from bar gaps.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

from discover_mt5_research_symbols import require_unique_resolution, init_mt5


SYMBOLS = (
    "XAUUSD", "USDJPY", "EURJPY", "GBPUSD",
    "GBPJPY", "EURUSD", "USDCHF", "USDCAD",
)
DAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def probe(symbol: str) -> dict:
    result = {"symbol": symbol, "quote": [], "trade": []}
    for api_name, target in (
        ("symbol_info_session_quote", result["quote"]),
        ("symbol_info_session_trade", result["trade"]),
    ):
        fn = getattr(mt5, api_name, None)
        result[api_name + "_available"] = fn is not None
        if fn is None:
            continue
        for day in range(7):
            for session_index in range(16):
                try:
                    value = fn(symbol, day, session_index)
                except Exception as exc:
                    result[api_name + "_error"] = repr(exc)
                    break
                if value in (None, False):
                    if session_index == 0:
                        break
                    break
                try:
                    start, end = value
                    start_seconds = int(start.timestamp()) if hasattr(start, "timestamp") else int(start)
                    end_seconds = int(end.timestamp()) if hasattr(end, "timestamp") else int(end)
                    target.append({
                        "day": day,
                        "day_name": DAY_NAMES[day],
                        "session_index": session_index,
                        "start_raw": start_seconds,
                        "end_raw": end_seconds,
                    })
                except Exception:
                    target.append({
                        "day": day,
                        "day_name": DAY_NAMES[day],
                        "session_index": session_index,
                        "raw": repr(value),
                    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mt5-path", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--symbols", default=",".join(SYMBOLS))
    args = parser.parse_args()

    init_mt5(args.mt5_path)
    try:
        requested = tuple(s.strip().upper() for s in args.symbols.split(",") if s.strip())
        mapping = require_unique_resolution(requested)
        payload = {
            "status": "COMPLETE",
            "mode": "RESEARCH_MT5_SESSION_API_PROBE",
            "canonical": False,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "mt5_package_version": getattr(mt5, "__version__", None),
            "symbols": mapping,
            "probe": [probe(mapping[s]) for s in requested],
        }
        output = Path(args.output) if args.output else Path("artifacts/matrix-mt5") / (
            "SP2L_MT5_SESSION_API_PROBE_"
            + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".json"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({
            "status": payload["status"],
            "package": payload["mt5_package_version"],
            "output": str(output),
            "canonical": False,
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
