"""Research-only zero-signal gate audit for the selected EURUSD/USDJPY replay.

This diagnostic does not alter detector/backtest behavior and does not optimize
parameters. It decomposes the existing research detector into sequential gates
so a zero-signal result can be attributed to data/session/geometry/risk filters.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import MetaTrader5 as mt5
import numpy as np

from mt5_terminal_resolver import find_mt5_terminal
from run_sp2l_mt5_local_multi_symbol_backtest import (
    ALIASES,
    _gap_after,
    discover_symbols,
    fetch_rates,
    filter_rates_to_research_session,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "artifacts" / "forensic" / "2026-09-28"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LONDON_TZ = ZoneInfo("Europe/London")
NEW_YORK_TZ = ZoneInfo("America/New_York")


def hhmm(value: str) -> tuple[int, int]:
    h, m = (int(x) for x in value.split(":", 1))
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError(value)
    return h, m


def in_session(ts: int, opening: str, closing: str) -> bool:
    dt = datetime.fromtimestamp(int(ts), timezone.utc)
    lh, lm = hhmm(opening)
    nh, nm = hhmm(closing)
    lo = dt.astimezone(LONDON_TZ).replace(hour=lh, minute=lm, second=0, microsecond=0)
    nc = dt.astimezone(NEW_YORK_TZ).replace(hour=nh, minute=nm, second=0, microsecond=0)
    return lo.astimezone(timezone.utc) <= dt <= nc.astimezone(timezone.utc)


def audit_symbol(rates: np.ndarray, p_gap: float, spike_mult: float, max_sl: float,
                 opening: str, closing: str) -> dict:
    rates = np.sort(rates, order="time")
    _, idx = np.unique(rates["time"], return_index=True)
    rates = rates[np.sort(idx)]

    session_mask = np.array([in_session(int(t), opening, closing) for t in rates["time"]], dtype=bool)
    session_rates = rates[session_mask]

    counts = {
        "windows_considered": 0,
        "formation_gap_free": 0,
        "buy_shape": 0,
        "buy_p_gap": 0,
        "buy_spike_body": 0,
        "buy_risk": 0,
        "sell_shape": 0,
        "sell_p_gap": 0,
        "sell_spike_body": 0,
        "sell_risk": 0,
        "final_signals": 0,
    }

    examples = {"near_misses": []}

    for i in range(4, len(session_rates) - 1):
        counts["windows_considered"] += 1
        formation_gap = any(
            _gap_after(int(session_rates[j]["time"]), int(session_rates[j + 1]["time"]))
            for j in range(i - 4, i)
        )
        if formation_gap:
            continue
        counts["formation_gap_free"] += 1

        a, spike, correction, trigger = (
            session_rates[i - 4], session_rates[i - 3],
            session_rates[i - 2], session_rates[i - 1]
        )
        sbuy = float(spike["close"] - spike["open"])
        ssell = float(spike["open"] - spike["close"])

        buy_shape = (
            trigger["low"] < correction["low"]
            and correction["close"] > spike["close"]
            and correction["open"] > spike["open"]
            and spike["close"] > a["close"]
            and spike["open"] > a["open"]
            and correction["close"] > correction["open"]
            and spike["close"] > spike["open"]
            and a["close"] > a["open"]
        )
        buy_pgap = bool(correction["low"] > a["high"] + p_gap)
        buy_spike = bool(
            sbuy > spike_mult * (correction["close"] - correction["open"])
            and sbuy > spike_mult * (a["close"] - a["open"])
            and sbuy > spike_mult * (trigger["close"] - trigger["open"])
        )
        buy_risk = bool(0 < float(trigger["low"] - spike["low"]) <= max_sl)

        sell_shape = (
            trigger["high"] > correction["high"]
            and correction["close"] < spike["close"]
            and correction["open"] < spike["open"]
            and spike["close"] < a["close"]
            and spike["open"] < a["open"]
            and correction["close"] < correction["open"]
            and spike["close"] < spike["open"]
            and a["close"] < a["open"]
        )
        sell_pgap = bool(correction["high"] < a["low"] - p_gap)
        sell_spike = bool(
            ssell > spike_mult * (correction["open"] - correction["close"])
            and ssell > spike_mult * (a["open"] - a["close"])
            and ssell > spike_mult * (trigger["open"] - trigger["close"])
        )
        sell_risk = bool(0 < float(spike["high"] - trigger["high"]) <= max_sl)

        if buy_shape:
            counts["buy_shape"] += 1
            if buy_pgap:
                counts["buy_p_gap"] += 1
                if buy_spike:
                    counts["buy_spike_body"] += 1
                    if buy_risk:
                        counts["buy_risk"] += 1
        if sell_shape:
            counts["sell_shape"] += 1
            if sell_pgap:
                counts["sell_p_gap"] += 1
                if sell_spike:
                    counts["sell_spike_body"] += 1
                    if sell_risk:
                        counts["sell_risk"] += 1

        if (buy_shape and buy_pgap and buy_spike and buy_risk) or (
            sell_shape and sell_pgap and sell_spike and sell_risk
        ):
            counts["final_signals"] += 1

        # Keep only a small deterministic sample of shape candidates that fail
        # a later gate; this is for diagnosis, not parameter search.
        if len(examples["near_misses"]) < 20 and (buy_shape or sell_shape):
            examples["near_misses"].append({
                "signal_time": datetime.fromtimestamp(int(trigger["time"]), timezone.utc).isoformat(),
                "buy_shape": buy_shape,
                "buy_p_gap": buy_pgap,
                "buy_spike_body": buy_spike,
                "buy_risk": buy_risk,
                "sell_shape": sell_shape,
                "sell_p_gap": sell_pgap,
                "sell_spike_body": sell_spike,
                "sell_risk": sell_risk,
            })

    return {
        "raw_bars": int(len(rates)),
        "session_bars": int(len(session_rates)),
        "raw_first_utc": datetime.fromtimestamp(int(rates[0]["time"]), timezone.utc).isoformat(),
        "raw_last_utc": datetime.fromtimestamp(int(rates[-1]["time"]), timezone.utc).isoformat(),
        "session_first_utc": datetime.fromtimestamp(int(session_rates[0]["time"]), timezone.utc).isoformat(),
        "session_last_utc": datetime.fromtimestamp(int(session_rates[-1]["time"]), timezone.utc).isoformat(),
        "counts": counts,
        "near_miss_examples": examples["near_misses"],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--mt5-path", required=True)
    p.add_argument("--symbols", default="EURUSD,USDJPY")
    p.add_argument("--p-gap-price", type=float, default=1.0)
    p.add_argument("--spike-multiplier", type=float, default=1.25)
    p.add_argument("--max-sl-distance", type=float, default=10.0)
    p.add_argument("--usd-jpy-max-sl-distance", type=float, default=50.0)
    p.add_argument("--london-open", default="08:00")
    p.add_argument("--new-york-close", default="17:00")
    args = p.parse_args()

    if not mt5.initialize(path=str(Path(args.mt5_path))):
        print(json.dumps({"status": "MT5_INIT_FAILED", "error": mt5.last_error()}, indent=2))
        return 2

    try:
        bases = [x.strip().upper() for x in args.symbols.split(",") if x.strip()]
        discovered = discover_symbols(bases)
        end = datetime.fromisoformat(args.end.replace("Z", "+00:00"))
        start = datetime.fromisoformat(args.start.replace("Z", "+00:00"))

        report = {
            "status": "COMPLETE",
            "research_only": True,
            "canonical": False,
            "purpose": "ZERO_SIGNAL_GATE_AUDIT",
            "period": {"start_utc": start.isoformat(), "end_utc": end.isoformat()},
            "session": {
                "enabled": True,
                "london_open_local": args.london_open,
                "new_york_close_local": args.new_york_close,
                "timezones": {"london": "Europe/London", "new_york": "America/New_York"},
            },
            "geometry": {
                "p_gap_price": args.p_gap_price,
                "spike_multiplier": args.spike_multiplier,
                "max_sl_by_symbol": {},
            },
            "resolved_symbols": discovered,
            "symbols": {},
            "notes": [
                "This is a gate decomposition of the existing research detector, not a new detector.",
                "No parameter sweep or optimization is performed.",
                "Counts are descriptive diagnostics only and cannot promote unresolved geometry to canonical.",
                "The session-gated counts intentionally use the same named London/New York session used by the selected replay.",
            ],
        }

        for base in bases:
            meta = discovered.get(base, {})
            symbol = meta.get("symbol")
            if not symbol:
                report["symbols"][base] = {"status": "NOT_RESOLVED"}
                continue
            max_sl = args.usd_jpy_max_sl_distance if base == "USDJPY" else args.max_sl_distance
            report["geometry"]["max_sl_by_symbol"][base] = max_sl
            print(f"[MT5] {base} -> {symbol}: downloading M1 history ...", flush=True)
            rates = fetch_rates(symbol, start, end)
            result = audit_symbol(
                rates, args.p_gap_price, args.spike_multiplier, max_sl,
                args.london_open, args.new_york_close
            )
            result["symbol"] = symbol
            result["digits"] = meta.get("digits")
            result["point"] = meta.get("point")
            result["trade_mode"] = meta.get("trade_mode")
            report["symbols"][base] = result
            c = result["counts"]
            print(
                f"[DONE] {base} -> {symbol}: raw={c['windows_considered']} "
                f"gap_free={c['formation_gap_free']} "
                f"buy_shape={c['buy_shape']} buy_pgap={c['buy_p_gap']} "
                f"buy_spike={c['buy_spike_body']} buy_risk={c['buy_risk']} "
                f"sell_shape={c['sell_shape']} sell_pgap={c['sell_p_gap']} "
                f"sell_spike={c['sell_spike_body']} sell_risk={c['sell_risk']} "
                f"final={c['final_signals']}",
                flush=True,
            )

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = OUT_DIR / f"SP2L_ZERO_SIGNAL_GATE_AUDIT_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"REPORT={path}")
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
